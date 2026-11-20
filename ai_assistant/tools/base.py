"""Base tool interface with error handling, retries, metrics, and schema validation."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

from ai_assistant.config import settings

logger = logging.getLogger(__name__)

InputSchema = TypeVar("InputSchema", bound=BaseModel)
OutputSchema = TypeVar("OutputSchema", bound=BaseModel)


class ToolExecutionError(Exception):
    """Exception raised when a tool execution fails."""
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{tool_name}] {message}")
        self.tool_name = tool_name
        self.message = message
        self.details = details or {}


class BaseTool(ABC, Generic[InputSchema, OutputSchema]):
    """
    Abstract base class for all agentic study tools.
    Provides schema validation, automated retries, execution metrics,
    and failure injection for resilient workflow testing.
    """

    name: str = "base_tool"
    description: str = "Base tool description"
    input_schema: Type[InputSchema]
    output_schema: Type[OutputSchema]

    def __init__(self):
        self.execution_count = 0
        self.failure_count = 0

    @abstractmethod
    def _execute(self, validated_input: InputSchema, context: Optional[Dict[str, Any]] = None) -> OutputSchema:
        """Core tool implementation to be overridden by subclasses."""
        raise NotImplementedError

    def run(self, raw_input: Any, context: Optional[Dict[str, Any]] = None) -> OutputSchema:
        """
        Public entry point. Performs validation, retries with backoff,
        and simulated error handling.
        """
        self.execution_count += 1
        start_time = time.perf_counter()

        # Check for simulated failure injection (used in Scenario 3)
        if context and context.get("simulate_failure") == self.name:
            self.failure_count += 1
            logger.warning(f"Simulating intentional failure for tool '{self.name}' as requested by context.")
            raise ToolExecutionError(
                tool_name=self.name,
                message=f"Simulated upstream external service outage in {self.name}",
                details={"simulated": True, "tool": self.name}
            )

        # 1. Validate Input Schema
        try:
            if isinstance(raw_input, self.input_schema):
                validated_input = raw_input
            elif isinstance(raw_input, dict):
                validated_input = self.input_schema.model_validate(raw_input)
            else:
                raise ValueError(f"Invalid input type: expected {self.input_schema.__name__} or dict, got {type(raw_input)}")
        except (ValidationError, ValueError) as val_err:
            self.failure_count += 1
            logger.error(f"Input validation failed for {self.name}: {val_err}")
            raise ToolExecutionError(
                tool_name=self.name,
                message=f"Input validation failed: {str(val_err)}",
                details={"raw_input": raw_input}
            )

        # 2. Execute with Retry Policy
        last_exception: Optional[Exception] = None
        max_attempts = settings.max_tool_retries + 1

        for attempt in range(1, max_attempts + 1):
            try:
                result = self._execute(validated_input, context)
                
                # Ensure output matches expected schema
                if not isinstance(result, self.output_schema):
                    result = self.output_schema.model_validate(result)

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Tool {self.name} succeeded in {elapsed_ms:.1f}ms on attempt {attempt}.")
                return result

            except Exception as exc:
                last_exception = exc
                logger.warning(f"Attempt {attempt}/{max_attempts} failed for tool {self.name}: {exc}")
                if attempt < max_attempts:
                    time.sleep(0.1 * (2 ** (attempt - 1)))  # Exponential backoff

        self.failure_count += 1
        raise ToolExecutionError(
            tool_name=self.name,
            message=f"Tool failed after {max_attempts} attempts. Last error: {str(last_exception)}",
            details={"attempts": max_attempts, "last_error": str(last_exception)}
        )
