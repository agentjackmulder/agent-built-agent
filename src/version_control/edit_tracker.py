"""Track and manage agent edits with version control integration."""

from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..core.state import EditRecord
from .git_manager import GitManager


class EditTracker:
    """Tracks agent edits and integrates with git version control."""
    
    def __init__(
        self,
        git_manager: Optional[GitManager] = None,
        auto_commit: bool = False
    ):
        self.git_manager = git_manager or GitManager()
        self.auto_commit = auto_commit
        self.pending_edits: List[EditRecord] = []
    
    def track_edit(self, edit: EditRecord) -> bool:
        """
        Track an edit and optionally commit it to git.
        
        Args:
            edit: The edit record to track
        
        Returns:
            True if tracking was successful
        """
        self.pending_edits.append(edit)
        
        if self.auto_commit:
            return self._commit_edit(edit)
        
        return True
    
    def _commit_edit(self, edit: EditRecord) -> bool:
        """Commit a single edit to git."""
        if not self.git_manager.is_git_repo():
            print("Not a git repository, skipping commit")
            return False
        
        # Add the edited file
        if not self.git_manager.add_file(edit.file_path):
            print(f"Failed to add {edit.file_path}")
            return False
        
        # Create commit message
        timestamp = edit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"[Agent Edit] {timestamp}: {edit.reason}"
        
        # Commit the changes
        if not self.git_manager.commit(commit_msg):
            print(f"Failed to commit {edit.file_path}")
            return False
        
        print(f"Committed: {commit_msg}")
        return True
    
    def commit_pending(self, message: Optional[str] = None) -> bool:
        """Commit all pending edits."""
        if not self.pending_edits:
            print("No pending edits to commit")
            return True
        
        if not self.git_manager.is_git_repo():
            print("Not a git repository")
            return False
        
        # Add all pending files
        files_to_add = set()
        for edit in self.pending_edits:
            files_to_add.add(edit.file_path)
        
        for file_path in files_to_add:
            if not self.git_manager.add_file(file_path):
                print(f"Failed to add {file_path}")
                return False
        
        # Create commit message
        if not message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[Agent Batch Edit] {timestamp}: {len(self.pending_edits)} edits"
        
        # Commit
        if not self.git_manager.commit(message):
            return False
        
        print(f"Committed {len(self.pending_edits)} edits: {message}")
        
        # Clear pending edits
        self.pending_edits.clear()
        return True
    
    def get_pending_files(self) -> List[str]:
        """Get list of files with pending edits."""
        return list(set(edit.file_path for edit in self.pending_edits))
    
    def sync_with_git(self) -> bool:
        """Sync tracked edits with git repository."""
        if not self.pending_edits:
            return True
        
        # Commit all pending edits
        return self.commit_pending()
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get git status of tracked files."""
        return self.git_manager.get_status()
    
    def push_to_remote(self, remote: str = "origin", branch: str = "main") -> bool:
        """Push changes to remote repository."""
        if not self.pending_edits:
            print("No changes to push")
            return True
        
        # Commit first
        if not self.commit_pending():
            return False
        
        # Push
        return self.git_manager.push(remote, branch)
