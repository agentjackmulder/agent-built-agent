"""Agent state management and persistence."""

import json
import hashlib
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class EditRecord:
    """Record of a single code edit."""
    edit_id: str
    timestamp: datetime
    file_path: str
    old_content: Optional[str]
    new_content: Optional[str]
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "edit_id": self.edit_id,
            "timestamp": self.timestamp.isoformat(),
            "file_path": self.file_path,
            "old_content": self.old_content,
            "new_content": self.new_content,
            "reason": self.reason,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EditRecord":
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class AgentState:
    """Complete agent state for persistence and restart."""
    agent_id: str
    name: str
    created_at: datetime
    started_at: Optional[datetime] = None
    last_edited_at: Optional[datetime] = None
    total_edits: int = 0
    total_restarts: int = 0
    current_version: str = "1.0.0"
    edit_history: List[EditRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_edited_at": self.last_edited_at.isoformat() if self.last_edited_at else None,
            "total_edits": self.total_edits,
            "total_restarts": self.total_restarts,
            "current_version": self.current_version,
            "edit_history": [e.to_dict() for e in self.edit_history],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data["started_at"]:
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data["last_edited_at"]:
            data["last_edited_at"] = datetime.fromisoformat(data["last_edited_at"])
        if data["edit_history"]:
            data["edit_history"] = [EditRecord.from_dict(e) for e in data["edit_history"]]
        return cls(**data)
    
    def get_hash(self) -> str:
        """Generate state hash for integrity checking."""
        state_json = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()[:16]


class StateManager:
    """Manages agent state persistence and loading."""
    
    def __init__(self, state_dir: str = ".agent_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "state.json"
    
    def save(self, state: AgentState) -> bool:
        """Save agent state to disk."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save state: {e}")
            return False
    
    def load(self) -> Optional[AgentState]:
        """Load agent state from disk."""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            return AgentState.from_dict(data)
        except Exception as e:
            print(f"Failed to load state: {e}")
            return None
    
    def get_latest_edit(self) -> Optional[EditRecord]:
        """Get the most recent edit record."""
        state = self.load()
        if state and state.edit_history:
            return state.edit_history[-1]
        return None
    
    def clear(self) -> bool:
        """Clear all state data."""
        try:
            self.state_file.unlink()
            return True
        except Exception as e:
            print(f"Failed to clear state: {e}")
            return False
