"""Global configuration settings for the AI Study Assistant."""

import os
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    app_name: str = "Autonomous AI Study Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM Settings
    llm_provider: Literal["auto", "gemini", "mock"] = "auto"
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = "gemini-2.5-flash"
    temperature: float = 0.2

    # Agent Guardrails & Limits
    max_recursion_limit: int = 12
    max_tool_retries: int = 2
    tool_timeout_seconds: float = 15.0

    # API / Server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
