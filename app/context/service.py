import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.context.session import SessionMemory, Turn
from app.core.logging import logger

class ContextService:
    """Manages in-memory session history and heuristic query rewriting."""
    
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}
        
    def _get_or_create(self, session_id: str) -> SessionMemory:
        self.clear_expired_sessions()
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id=session_id)
        return self.sessions[session_id]
        
    def add_turn(self, session_id: str, role: str, content: str) -> None:
        """Add a turn to the session buffer."""
        session = self._get_or_create(session_id)
        session.turns.append(Turn(role=role, content=content))
        session.last_activity = datetime.now()
        
    def get_context_window(self, session_id: str, max_turns: int = 10) -> List[Dict[str, str]]:
        """Get the recent chat history formatted for LLMs."""
        session = self._get_or_create(session_id)
        recent_turns = session.turns[-max_turns:]
        return [{"role": t.role, "content": t.content} for t in recent_turns]
        
    def format_history_text(self, session_id: str, max_turns: int = 10) -> str:
        """Format history as a simple text block."""
        window = self.get_context_window(session_id, max_turns)
        if not window:
            return "No prior conversation."
            
        lines = []
        for msg in window:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
        
    def rewrite_query(self, session_id: str, question: str) -> str:
        """
        Contextual query rewriter. Resolves pronouns and references against recent history.
        """
        session = self._get_or_create(session_id)
        session.last_activity = datetime.now()
        
        if len(session.turns) < 2:
            return question
            
        q_clean = question.strip()
        q_lower = q_clean.lower()
        
        # Check for pronoun references or follow-up indicators
        pronoun_pattern = r"\b(he|she|it|they|his|her|its|their|this|that|these|those)\b"
        followup_phrases = ["tell me more", "explain more", "give an example", "why?", "how so?", "elaborate", "continue", "what about"]
        
        has_pronoun = bool(re.search(pronoun_pattern, q_lower))
        is_followup = any(q_lower.startswith(phrase) or q_lower == phrase.rstrip("?") for phrase in followup_phrases)
        
        if not has_pronoun and not is_followup:
            return question
            
        # Find the last user question as the topic anchor
        last_user_turns = [t.content for t in session.turns if t.role == "user"]
        if not last_user_turns:
            return question
            
        last_topic = last_user_turns[-1].strip()
        
        # Build contextual standalone question
        if is_followup and len(q_clean.split()) <= 4:
            rewritten = f"{q_clean} regarding {last_topic}"
            logger.info(f"ContextService resolved follow-up: '{question}' -> '{rewritten}'")
            return rewritten
            
        if has_pronoun:
            # If the user asks something like "When was he born?" or "What are its benefits?"
            rewritten = f"{q_clean} (Context: in reference to '{last_topic}')"
            logger.info(f"ContextService resolved pronouns: '{question}' -> '{rewritten}'")
            return rewritten
            
        return question

    def clear_session(self, session_id: str) -> None:
        """Clear a session from memory."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def clear_expired_sessions(self) -> None:
        """Remove sessions that have exceeded the inactivity timeout."""
        now = datetime.now()
        timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if (now - session.last_activity) > timeout
        ]
        for sid in expired_ids:
            logger.info(f"Clearing expired session: {sid}")
            del self.sessions[sid]

# Singleton
context_service = ContextService()
