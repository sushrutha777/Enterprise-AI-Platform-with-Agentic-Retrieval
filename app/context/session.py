"""Session data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class Turn:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SessionMemory:
    session_id: str
    turns: List[Turn] = field(default_factory=list)
    entities: Dict[str, str] = field(default_factory=dict)
    last_tool_used: str = "none"
    last_sources: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
