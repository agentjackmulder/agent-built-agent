"""Tests for version control."""

import pytest
import tempfile
import subprocess
from pathlib import Path

from src.version_control.git_manager import GitManager
from src.version_control.edit_tracker import EditTracker


class TestGitManager:
    """Tests for GitManager."""
    
    def test_init_repo(self):
        """Test initializing a git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(tmpdir)
            
            # Create a test file first
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            
            assert git_manager.init_repo()
            assert (Path(tmpdir) / ".git").exists()
    
    def test_add_and_commit(self):
        """Test adding and committing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(tmpdir)
            
            # Initialize repo
            git_manager.init_repo()
            
            # Configure git
            subprocess.run(["git", "config", "user.email", "test@example.com"], 
                          cwd=tmpdir, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], 
                          cwd=tmpdir, check=True)
            
            # Create test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            # Add and commit
            git_manager.add_file("test.txt")
            assert git_manager.commit("Initial commit")
    
    def test_get_status(self):
        """Test getting git status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(tmpdir)
            git_manager.init_repo()
            
            # Create untracked file
            test_file = Path(tmpdir) / "untracked.txt"
            test_file.write_text("test")
            
            status = git_manager.get_status()
            # Check if file appears in any status category
            all_files = status["staged"] + status["unstaged"] + status["untracked"]
            assert "untracked.txt" in all_files
    
    def test_get_commits(self):
        """Test getting commit history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(tmpdir)
            git_manager.init_repo()
            
            # Configure git
            subprocess.run(["git", "config", "user.email", "test@example.com"], 
                          cwd=tmpdir, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], 
                          cwd=tmpdir, check=True)
            
            # Create and commit file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            git_manager.add_file("test.txt")
            git_manager.commit("Test commit")
            
            commits = git_manager.get_commits()
            assert len(commits) >= 1
            assert commits[0]["message"] == "Test commit"


class TestEditTracker:
    """Tests for EditTracker."""
    
    def test_track_edit(self):
        """Test tracking an edit."""
        tracker = EditTracker(auto_commit=False)
        
        from src.core.state import EditRecord
        from datetime import datetime
        
        edit = EditRecord(
            edit_id="test123",
            timestamp=datetime.now(),
            file_path="/test.py",
            old_content=None,
            new_content="new",
            reason="test"
        )
        
        assert tracker.track_edit(edit)
        assert len(tracker.pending_edits) == 1
    
    def test_commit_pending(self):
        """Test committing pending edits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_manager = GitManager(tmpdir)
            git_manager.init_repo()
            
            # Configure git
            subprocess.run(["git", "config", "user.email", "test@example.com"], 
                          cwd=tmpdir, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], 
                          cwd=tmpdir, check=True)
            
            tracker = EditTracker(git_manager=git_manager, auto_commit=False)
            
            # Create a file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("old")
            
            from src.core.state import EditRecord
            from datetime import datetime
            
            edit = EditRecord(
                edit_id="test123",
                timestamp=datetime.now(),
                file_path=str(test_file),
                old_content=None,
                new_content="new",
                reason="test edit"
            )
            
            tracker.track_edit(edit)
            
            # Manually add file to git
            git_manager.add_file("test.py")
            git_manager.commit("Test commit")
            
            assert tracker.commit_pending()
    
    def test_get_pending_files(self):
        """Test getting pending files."""
        tracker = EditTracker(auto_commit=False)
        
        from src.core.state import EditRecord
        from datetime import datetime
        
        edit1 = EditRecord(
            edit_id="edit1",
            timestamp=datetime.now(),
            file_path="/file1.py",
            old_content=None,
            new_content="new",
            reason="test"
        )
        
        edit2 = EditRecord(
            edit_id="edit2",
            timestamp=datetime.now(),
            file_path="/file2.py",
            old_content=None,
            new_content="new",
            reason="test"
        )
        
        tracker.track_edit(edit1)
        tracker.track_edit(edit2)
        
        pending = tracker.get_pending_files()
        assert len(pending) == 2
