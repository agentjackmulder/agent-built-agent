"""Tests for configuration management."""

import pytest
import tempfile
import yaml
from pathlib import Path

from src.core.config import AgentConfig, ConfigManager, EditConfig


class TestEditConfig:
    """Tests for EditConfig."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = EditConfig()
        
        assert config.enabled is True
        assert config.dry_run is False
        assert config.backup_before_edit is True
        assert config.max_edit_size == 10000
        assert config.require_reason is True
        assert config.auto_commit is False


class TestAgentConfig:
    """Tests for AgentConfig."""
    
    def test_default_values(self):
        """Test default agent configuration."""
        config = AgentConfig()
        
        assert config.name == "SelfEditingAgent"
        assert config.version == "0.2.0"
        assert config.max_edits_per_session == 100
        assert config.enable_self_modification is True
    
    def test_to_dict(self):
        """Test converting config to dict."""
        config = AgentConfig()
        data = config.to_dict()
        
        assert "name" in data
        assert "version" in data
        assert "edit_config" in data
        assert "state_config" in data
    
    def test_from_dict(self):
        """Test creating config from dict."""
        data = {
            "name": "TestAgent",
            "agent_id": "test123",
            "version": "1.0.0",
            "edit_config": {
                "enabled": False,
                "dry_run": True
            },
            "state_config": {
                "state_dir": ".test_state"
            },
            "logging_config": {
                "level": "DEBUG"
            },
            "max_edits_per_session": 50,
            "enable_self_modification": False,
            "require_confirmation_for_major_changes": False
        }
        
        config = AgentConfig.from_dict(data)
        
        assert config.name == "TestAgent"
        assert config.version == "1.0.0"
        assert config.edit_config.enabled is False
        assert config.state_config.state_dir == ".test_state"


class TestConfigManager:
    """Tests for ConfigManager."""
    
    def test_default_config_file(self):
        """Test default config file path."""
        assert ConfigManager.DEFAULT_CONFIG_FILE == "agent_config.yaml"
    
    def test_save_and_reload(self):
        """Test saving and reloading config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            manager = ConfigManager(str(config_path))
            
            # Modify config
            manager.config.name = "TestAgent"
            manager.config.edit_config.enabled = False
            
            # Save
            assert manager.save()
            
            # Reload
            manager2 = ConfigManager(str(config_path))
            assert manager2.config.name == "TestAgent"
            assert manager2.config.edit_config.enabled is False
    
    def test_update(self):
        """Test updating config."""
        manager = ConfigManager()
        
        initial_name = manager.config.name
        
        manager.update({
            "name": "UpdatedAgent",
            "edit_config": {
                "enabled": False
            }
        })
        
        assert manager.config.name == "UpdatedAgent"
        assert manager.config.edit_config.enabled is False
