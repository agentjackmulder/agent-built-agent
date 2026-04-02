"""Tests for state management."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from src.core.state import AgentState, StateManager, EditRecord


class TestEditRecord:
    """Tests for EditRecord."""
    
    def test_create_edit_record(self):
        """Test creating an edit record."""
        record = EditRecord(
            edit_id="test123",
            timestamp=datetime.now(),
            file_path="/test/file.py",
            old_content="old",
            new_content="new",
            reason="test edit"
        )
        
        assert record.edit_id == "test123"
        assert record.file_path == "/test/file.py"
        assert record.reason == "test edit"
    
    def test_to_dict(self):
        """Test converting edit record to dict."""
        record = EditRecord(
            edit_id="test123",
            timestamp=datetime.now(),
            file_path="/test/file.py",
            old_content="old",
            new_content="new",
            reason="test edit"
        )
        
        data = record.to_dict()
        
        assert data["edit_id"] == "test123"
        assert data["file_path"] == "/test/file.py"
        assert "timestamp" in data
    
    def test_from_dict(self):
        """Test creating edit record from dict."""
        data = {
            "edit_id": "test123",
            "timestamp": datetime.now().isoformat(),
            "file_path": "/test/file.py",
            "old_content": "old",
            "new_content": "new",
            "reason": "test edit",
            "metadata": {}
        }
        
        record = EditRecord.from_dict(data)
        
        assert record.edit_id == "test123"
        assert isinstance(record.timestamp, datetime)


class TestAgentState:
    """Tests for AgentState."""
    
    def test_create_state(self):
        """Test creating agent state."""
        state = AgentState(
            agent_id="test123",
            name="TestAgent",
            created_at=datetime.now()
        )
        
        assert state.agent_id == "test123"
        assert state.name == "TestAgent"
        assert state.total_edits == 0
    
    def test_to_dict(self):
        """Test converting state to dict."""
        state = AgentState(
            agent_id="test123",
            name="TestAgent",
            created_at=datetime.now()
        )
        
        data = state.to_dict()
        
        assert data["agent_id"] == "test123"
        assert data["name"] == "TestAgent"
        assert "created_at" in data
    
    def test_from_dict(self):
        """Test creating state from dict."""
        data = {
            "agent_id": "test123",
            "name": "TestAgent",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "last_edited_at": None,
            "total_edits": 0,
            "total_restarts": 0,
            "current_version": "1.0.0",
            "edit_history": [],
            "metadata": {}
        }
        
        state = AgentState.from_dict(data)
        
        assert state.agent_id == "test123"
        assert isinstance(state.created_at, datetime)


class TestStateManager:
    """Tests for StateManager."""
    
    def test_save_and_load(self):
        """Test saving and loading state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            manager = StateManager(str(state_dir))
            
            state = AgentState(
                agent_id="test123",
                name="TestAgent",
                created_at=datetime.now()
            )
            
            # Save
            assert manager.save(state)
            
            # Load
            loaded = manager.load()
            assert loaded is not None
            assert loaded.agent_id == "test123"
    
    def test_clear(self):
        """Test clearing state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            manager = StateManager(str(state_dir))
            
            state = AgentState(
                agent_id="test123",
                name="TestAgent",
                created_at=datetime.now()
            )
            
            manager.save(state)
            assert manager.state_file.exists()
            
            manager.clear()
            assert not manager.state_file.exists()
    
    def test_get_latest_edit(self):
        """Test getting latest edit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            manager = StateManager(str(state_dir))
            
            state = AgentState(
                agent_id="test123",
                name="TestAgent",
                created_at=datetime.now(),
                edit_history=[
                    EditRecord(
                        edit_id="edit1",
                        timestamp=datetime.now(),
                        file_path="/test.py",
                        old_content=None,
                        new_content="new",
                        reason="test"
                    )
                ]
            )
            
            manager.save(state)
            
            latest = manager.get_latest_edit()
            assert latest is not None
            assert latest.edit_id == "edit1"
