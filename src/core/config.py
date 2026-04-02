"""Configuration management for the agent."""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EditConfig:
    """Configuration for code editing behavior."""
    enabled: bool = True
    dry_run: bool = False
    backup_before_edit: bool = True
    max_edit_size: int = 10000
    require_reason: bool = True
    auto_commit: bool = False


@dataclass
class StateConfig:
    """Configuration for state persistence."""
    state_dir: str = ".agent_state"
    auto_save: bool = True
    save_interval_seconds: int = 60
    max_history_entries: int = 100


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    log_file: Optional[str] = None
    log_to_console: bool = True
    include_timestamps: bool = True


@dataclass
class AgentConfig:
    """Main agent configuration."""
    name: str = "SelfEditingAgent"
    agent_id: str = "default"
    version: str = "0.2.0"
    edit_config: EditConfig = field(default_factory=EditConfig)
    state_config: StateConfig = field(default_factory=StateConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Runtime settings
    max_edits_per_session: int = 100
    enable_self_modification: bool = True
    require_confirmation_for_major_changes: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "version": self.version,
            "edit_config": {
                "enabled": self.edit_config.enabled,
                "dry_run": self.edit_config.dry_run,
                "backup_before_edit": self.edit_config.backup_before_edit,
                "max_edit_size": self.edit_config.max_edit_size,
                "require_reason": self.edit_config.require_reason,
                "auto_commit": self.edit_config.auto_commit
            },
            "state_config": {
                "state_dir": self.state_config.state_dir,
                "auto_save": self.state_config.auto_save,
                "save_interval_seconds": self.state_config.save_interval_seconds,
                "max_history_entries": self.state_config.max_history_entries
            },
            "logging_config": {
                "level": self.logging_config.level,
                "log_file": self.logging_config.log_file,
                "log_to_console": self.logging_config.log_to_console,
                "include_timestamps": self.logging_config.include_timestamps
            },
            "max_edits_per_session": self.max_edits_per_session,
            "enable_self_modification": self.enable_self_modification,
            "require_confirmation_for_major_changes": self.require_confirmation_for_major_changes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        edit_config = EditConfig(**data.get("edit_config", {}))
        state_config = StateConfig(**data.get("state_config", {}))
        logging_config = LoggingConfig(**data.get("logging_config", {}))
        
        return cls(
            name=data.get("name", "SelfEditingAgent"),
            agent_id=data.get("agent_id", "default"),
            version=data.get("version", "0.2.0"),
            edit_config=edit_config,
            state_config=state_config,
            logging_config=logging_config,
            max_edits_per_session=data.get("max_edits_per_session", 100),
            enable_self_modification=data.get("enable_self_modification", True),
            require_confirmation_for_major_changes=data.get(
                "require_confirmation_for_major_changes", True
            )
        )


class ConfigManager:
    """Manages agent configuration."""
    
    DEFAULT_CONFIG_FILE = "agent_config.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path(self.DEFAULT_CONFIG_FILE)
        self.config = AgentConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                self.config = AgentConfig.from_dict(data)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
        else:
            self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config.to_dict(), f, default_flow_style=False, sort_keys=False)
    
    def save(self) -> bool:
        """Persist configuration to disk."""
        try:
            self._save_config()
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def reload(self) -> None:
        """Reload configuration from disk."""
        self._load_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration with provided values."""
        current_dict = self.config.to_dict()
        self._merge_dict(current_dict, updates)
        self.config = AgentConfig.from_dict(current_dict)
    
    def _merge_dict(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Recursively merge updates into base dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value
