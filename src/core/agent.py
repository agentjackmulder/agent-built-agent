"""Core self-editing agent implementation."""

import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .state import AgentState, StateManager, EditRecord
from .config import ConfigManager, AgentConfig


class SelfEditingAgent:
    """
    A self-editing AI agent that can modify its own codebase and restart itself.
    
    This agent maintains state, tracks all edits, and can persist/restore its
    complete runtime state for seamless operation.
    """
    
    def __init__(
        self,
        name: str = "SelfEditingAgent",
        config_path: Optional[str] = None,
        state_dir: Optional[str] = None
    ):
        self.name = name
        self.agent_id = str(uuid.uuid4())[:8]
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.last_edited_at: Optional[datetime] = None
        self.total_edits = 0
        self.total_restarts = 0
        self.current_version = "0.2.0"
        self.edit_history: List[EditRecord] = []
        self.metadata: Dict[str, Any] = {}
        
        # Initialize configuration
        self.config_manager = ConfigManager(config_path)
        
        # Initialize state manager
        state_dir = state_dir or self.config_manager.config.state_config.state_dir
        self.state_manager = StateManager(state_dir)
        
        # Load existing state if available
        self._load_state()
        
        # Set up hooks for extensibility
        self._edit_hooks: List[Callable[[EditRecord], bool]] = []
        self._restart_hooks: List[Callable[[], bool]] = []
    
    def _load_state(self) -> None:
        """Load state from persistent storage."""
        state = self.state_manager.load()
        if state:
            self.name = state.name
            self.started_at = state.started_at
            self.last_edited_at = state.last_edited_at
            self.total_edits = state.total_edits
            self.total_restarts = state.total_restarts
            self.current_version = state.current_version
            self.edit_history = state.edit_history
            self.metadata = state.metadata
    
    def _save_state(self) -> bool:
        """Save current state to persistent storage."""
        state = AgentState(
            agent_id=self.agent_id,
            name=self.name,
            created_at=self.created_at,
            started_at=self.started_at,
            last_edited_at=self.last_edited_at,
            total_edits=self.total_edits,
            total_restarts=self.total_restarts,
            current_version=self.current_version,
            edit_history=self.edit_history,
            metadata=self.metadata
        )
        return self.state_manager.save(state)
    
    def edit_file(
        self,
        file_path: str,
        new_content: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Edit a file and record the change in the agent's edit history.
        
        Args:
            file_path: Path to the file to edit
            new_content: New content for the file
            reason: Reason for the edit (required)
            metadata: Optional metadata to associate with the edit
        
        Returns:
            True if edit was successful, False otherwise
        """
        config = self.config_manager.config.edit_config
        
        if not config.enabled:
            print(f"[{self.name}] Editing is disabled")
            return False
        
        if config.require_reason and not reason:
            print(f"[{self.name}] Edit reason is required")
            return False
        
        if len(new_content) > config.max_edit_size:
            print(f"[{self.name}] Edit too large: {len(new_content)} > {config.max_edit_size}")
            return False
        
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
        
        # Get old content if file exists
        old_content = None
        if file_path.exists():
            try:
                old_content = file_path.read_text()
            except Exception as e:
                print(f"[{self.name}] Failed to read {file_path}: {e}")
                return False
        
        # Create backup if configured
        if config.backup_before_edit and old_content:
            backup_path = file_path.with_suffix(f".{file_path.suffix}.backup")
            try:
                backup_path.write_text(old_content)
            except Exception as e:
                print(f"[{self.name}] Failed to create backup: {e}")
        
        # Apply the edit (or dry run)
        if config.dry_run:
            print(f"[{self.name}] DRY RUN: Would edit {file_path}")
            print(f"Reason: {reason}")
            return True
        
        # Write new content
        try:
            file_path.write_text(new_content)
        except Exception as e:
            print(f"[{self.name}] Failed to write {file_path}: {e}")
            return False
        
        # Create edit record
        edit_record = EditRecord(
            edit_id=str(uuid.uuid4())[:12],
            timestamp=datetime.now(),
            file_path=str(file_path),
            old_content=old_content,
            new_content=new_content,
            reason=reason,
            metadata=metadata or {}
        )
        
        # Execute edit hooks
        for hook in self._edit_hooks:
            try:
                if not hook(edit_record):
                    print(f"[{self.name}] Edit hook failed, rolling back")
                    if old_content:
                        file_path.write_text(old_content)
                    return False
            except Exception as e:
                print(f"[{self.name}] Edit hook error: {e}")
                return False
        
        # Update state
        self.edit_history.append(edit_record)
        self.last_edited_at = datetime.now()
        self.total_edits += 1
        
        # Trim history if needed
        max_history = self.config_manager.config.state_config.max_history_entries
        if len(self.edit_history) > max_history:
            self.edit_history = self.edit_history[-max_history:]
        
        # Save state
        if self.config_manager.config.state_config.auto_save:
            self._save_state()
        
        print(f"[{self.name}] Edited {file_path}: {reason}")
        return True
    
    def edit_code(
        self,
        file_path: str,
        edit_function: Callable[[str], str],
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Edit a file by applying a transformation function to its content.
        
        Args:
            file_path: Path to the file to edit
            edit_function: Function that takes old content and returns new content
            reason: Reason for the edit
            metadata: Optional metadata
        
        Returns:
            True if edit was successful
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"[{self.name}] File does not exist: {file_path}")
            return False
        
        try:
            old_content = file_path.read_text()
        except Exception as e:
            print(f"[{self.name}] Failed to read {file_path}: {e}")
            return False
        
        try:
            new_content = edit_function(old_content)
        except Exception as e:
            print(f"[{self.name}] Edit function failed: {e}")
            return False
        
        return self.edit_file(file_path, new_content, reason, metadata)
    
    def restart(self, reason: str = "Normal restart") -> bool:
        """
        Perform a graceful restart of the agent.
        
        Args:
            reason: Reason for the restart
        
        Returns:
            True if restart was successful
        """
        print(f"[{self.name}] Restarting: {reason}")
        
        # Execute restart hooks
        for hook in self._restart_hooks:
            try:
                if not hook():
                    print(f"[{self.name}] Restart hook failed")
                    return False
            except Exception as e:
                print(f"[{self.name}] Restart hook error: {e}")
                return False
        
        self.total_restarts += 1
        self.started_at = datetime.now()
        
        # Save state before restart
        self._save_state()
        
        print(f"[{self.name}] Restart complete (edits: {self.total_edits}, restarts: {self.total_restarts})")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = None
        if self.started_at:
            uptime = str(datetime.now() - self.started_at)
        
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "version": self.current_version,
            "uptime": uptime,
            "total_edits": self.total_edits,
            "total_restarts": self.total_restarts,
            "last_edited_at": self.last_edited_at.isoformat() if self.last_edited_at else None,
            "state_hash": self._get_state_hash()
        }
    
    def _get_state_hash(self) -> str:
        """Generate current state hash for integrity checking."""
        state_data = {
            "name": self.name,
            "total_edits": self.total_edits,
            "total_restarts": self.total_restarts,
            "last_edit_id": self.edit_history[-1].edit_id if self.edit_history else None,
            "current_version": self.current_version
        }
        import json
        import hashlib
        state_json = json.dumps(state_data, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()[:16]
    
    def register_edit_hook(self, hook: Callable[[EditRecord], bool]) -> None:
        """Register a hook to be called after each edit."""
        self._edit_hooks.append(hook)
    
    def register_restart_hook(self, hook: Callable[[], bool]) -> None:
        """Register a hook to be called before restart."""
        self._restart_hooks.append(hook)
    
    def get_edit_history(
        self,
        limit: int = 10,
        file_path: Optional[str] = None
    ) -> List[EditRecord]:
        """Get recent edit history."""
        history = self.edit_history
        if file_path:
            history = [e for e in history if file_path in e.file_path]
        return history[-limit:]
    
    def rollback(self, edit_id: str) -> bool:
        """
        Rollback to a specific edit by restoring previous state.
        
        Args:
            edit_id: ID of the edit to rollback to
        
        Returns:
            True if rollback was successful
        """
        edit_record = None
        for record in reversed(self.edit_history):
            if record.edit_id == edit_id:
                edit_record = record
                break
        
        if not edit_record:
            print(f"[{self.name}] Edit not found: {edit_id}")
            return False
        
        if not edit_record.old_content:
            print(f"[{self.name}] No previous content to restore")
            return False
        
        file_path = Path(edit_record.file_path)
        try:
            file_path.write_text(edit_record.old_content)
            print(f"[{self.name}] Rolled back to {edit_id}")
            return True
        except Exception as e:
            print(f"[{self.name}] Rollback failed: {e}")
            return False
