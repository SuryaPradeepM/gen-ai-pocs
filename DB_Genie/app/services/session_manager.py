import uuid
from typing import Dict, List, Optional


class SessionManager:
    """Manages chat sessions and conversation history"""

    def __init__(self):
        # In-memory session storage (consider using Redis or database for production)
        self.sessions: Dict[str, List[dict]] = {}

    def create_session(self) -> str:
        """Create a new session and return its ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id

    def get_session(self, session_id: str) -> Optional[List[dict]]:
        """Get conversation history for a session"""
        return self.sessions.get(session_id)

    def ensure_session(self, session_id: str) -> None:
        """Ensure a session exists, create it if it doesn't"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []

    def add_message(self, session_id: str, message: dict) -> None:
        """Add a message to the session history"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(message)

    def add_messages(self, session_id: str, messages: List[dict]) -> None:
        """Add multiple messages to the session history"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].extend(messages)

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session"""
        if session_id in self.sessions:
            self.sessions[session_id] = []

    def delete_session(self, session_id: str) -> None:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
