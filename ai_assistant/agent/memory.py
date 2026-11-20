"""Conversational context and state memory manager across multi-turn interactions."""

import copy
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from ai_assistant.models.state import AgentState

logger = logging.getLogger(__name__)

STORAGE_DIR = Path(".sessions")
STORAGE_DIR.mkdir(exist_ok=True)


class SessionMemoryManager:
    """
    Manages state persistence across multi-turn interactions for students.
    Preserves active plans, quizzes, conversation history, and profile attributes
    in memory with persistent JSON-file backing.
    """

    def __init__(self):
        self._sessions: Dict[str, AgentState] = {}

    def _file_path(self, session_id: str) -> Path:
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_"))
        return STORAGE_DIR / f"{safe_id}.json"

    def get_or_create_state(self, session_id: str, student_id: Optional[str] = None) -> AgentState:
        """Retrieves existing state from memory or disk, or initializes a new session state."""
        if session_id in self._sessions:
            return self._sessions[session_id]

        file_p = self._file_path(session_id)
        if file_p.exists():
            try:
                with open(file_p, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._sessions[session_id] = loaded
                    logger.debug(f"Loaded session '{session_id}' from disk persistence.")
                    return loaded
            except Exception as e:
                logger.warning(f"Failed to read persisted session '{session_id}': {e}")

        logger.info(f"Initializing new AgentState session: {session_id}")
        new_state: AgentState = {
            "session_id": session_id,
            "student_id": student_id or "student_default",
            "current_input": "",
            "conversation_history": [],
            "user_goal": None,
            "subject": None,
            "current_topic": None,
            "proficiency_level": "intermediate",
            "active_plan": None,
            "active_quiz": None,
            "quiz_evaluation": None,
            "clarification": None,
            "is_clarifying": False,
            "last_action": None,
            "action_reasoning": None,
            "execution_trace": [],
            "last_tool_output": None,
            "final_response": None,
            "recursion_counter": 0,
            "retry_count": 0,
            "errors": [],
            "simulate_failure": None,
        }
        self._sessions[session_id] = new_state
        return new_state

    def save_state(self, session_id: str, state: AgentState) -> None:
        """Persists the updated agent state for a session to memory and disk."""
        self._sessions[session_id] = copy.deepcopy(state)
        file_p = self._file_path(session_id)
        try:
            with open(file_p, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error persisting session '{session_id}' to disk: {e}")

    def append_message(self, session_id: str, role: str, content: str) -> None:
        """Appends a message to conversation history."""
        state = self.get_or_create_state(session_id)
        state["conversation_history"].append({"role": role, "content": content})
        self.save_state(session_id, state)

    def reset_session(self, session_id: str) -> None:
        """Clears state for a given session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        file_p = self._file_path(session_id)
        if file_p.exists():
            file_p.unlink(missing_ok=True)


# Global memory manager instance
session_memory = SessionMemoryManager()
