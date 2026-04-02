"""Configuration file editor for YAML and JSON configs."""

import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from .code_editor import CodeEditor


class ConfigEditor(CodeEditor):
    """Editor for configuration files (YAML/JSON)."""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.config_data: Optional[Dict[str, Any]] = None
        self.file_format: str = "yaml"  # 'yaml' or 'json'
    
    def detect_format(self) -> str:
        """Detect configuration file format."""
        if self.file_path.suffix.lower() == '.json':
            return "json"
        elif self.file_path.suffix.lower() in ['.yaml', '.yml']:
            return "yaml"
        else:
            # Try to detect from content
            content = self.file_path.read_text()
            if content.strip().startswith('{'):
                return "json"
            return "yaml"
    
    def load_config(self) -> bool:
        """Load configuration file into data structure."""
        if not self.load():
            return False
        
        self.file_format = self.detect_format()
        
        try:
            if self.file_format == "json":
                self.config_data = json.loads(self.current_content)
            else:
                self.config_data = yaml.safe_load(self.current_content)
            return True
        except Exception as e:
            print(f"Failed to parse config: {e}")
            return False
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """Get a value from nested config using dot notation."""
        if not self.config_data:
            return default
        
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_value(self, key_path: str, value: Any) -> bool:
        """Set a value in nested config using dot notation."""
        if not self.config_data:
            if not self.load_config():
                return False
        
        keys = key_path.split('.')
        
        # Navigate to parent
        current = self.config_data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set value
        current[keys[-1]] = value
        
        # Save
        return self._save_config()
    
    def delete_value(self, key_path: str) -> bool:
        """Delete a value from config."""
        if not self.config_data:
            return False
        
        keys = key_path.split('.')
        
        # Navigate to parent
        current = self.config_data
        for key in keys[:-1]:
            if key not in current:
                return False
            current = current[key]
        
        # Delete
        if keys[-1] in current:
            del current[keys[-1]]
            return self._save_config()
        
        return False
    
    def merge_config(self, updates: Dict[str, Any], path: str = "") -> bool:
        """Recursively merge updates into config."""
        if not self.config_data:
            if not self.load_config():
                return False
        
        self._merge_dict(self.config_data, updates, path)
        return self._save_config()
    
    def _merge_dict(self, base: Dict[str, Any], updates: Dict[str, Any], path: str = "") -> None:
        """Recursively merge updates into base dictionary."""
        for key, value in updates.items():
            full_path = f"{path}.{key}" if path else key
            
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value, full_path)
            else:
                base[key] = value
    
    def _save_config(self) -> bool:
        """Save config data back to file."""
        if not self.config_data:
            return False
        
        try:
            if self.file_format == "json":
                content = json.dumps(self.config_data, indent=2)
            else:
                content = yaml.dump(self.config_data, default_flow_style=False, sort_keys=False)
            
            self.file_path.write_text(content)
            self.current_content = content
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def validate(self) -> List[str]:
        """Validate configuration file."""
        errors = []
        
        if not self.config_data:
            if not self.load_config():
                errors.append("Failed to load config")
                return errors
        
        # Basic validation
        if not isinstance(self.config_data, dict):
            errors.append("Config must be a dictionary")
        
        return errors
    
    def get_structure(self, depth: int = 0, max_depth: int = 3) -> str:
        """Get configuration structure as string."""
        if not self.config_data or depth > max_depth:
            return ""
        
        lines = []
        for key, value in self.config_data.items():
            if isinstance(value, dict):
                lines.append(f"{'  ' * depth}{key}:")
                lines.append(self.get_structure(value, depth + 1, max_depth))
            elif isinstance(value, list):
                lines.append(f"{'  ' * depth}{key}: [{len(value)} items]")
            else:
                lines.append(f"{'  ' * depth}{key}: {value}")
        
        return '\n'.join(lines)
