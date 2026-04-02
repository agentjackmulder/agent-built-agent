"""Git-based version control for agent edits."""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class GitManager:
    """Manages git operations for agent self-edits."""
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
    
    def _run_git(self, args: List[str], capture: bool = True) -> str:
        """Run a git command and return output."""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                print(f"Git error: {result.stderr}")
                return ""
            return result.stdout if capture else ""
        except subprocess.TimeoutExpired:
            print("Git command timed out")
            return ""
        except Exception as e:
            print(f"Git command failed: {e}")
            return ""
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        output = self._run_git(["rev-parse", "--git-dir"], capture=True)
        return bool(output and ".git" in output)
    
    def init_repo(self) -> bool:
        """Initialize a new git repository."""
        result = self._run_git(["init"])
        return result is not None
    
    def add_file(self, file_path: str) -> bool:
        """Add a file to git staging."""
        result = self._run_git(["add", str(file_path)])
        return result is not None
    
    def add_all(self) -> bool:
        """Add all changes to git staging."""
        result = self._run_git(["add", "."])
        return result is not None
    
    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """Commit staged changes."""
        args = ["commit", "-m", message]
        if allow_empty:
            args.insert(1, "--allow-empty")
        result = self._run_git(args)
        return result is not None
    
    def push(self, remote: str = "origin", branch: str = "main") -> bool:
        """Push to remote repository."""
        result = self._run_git(["push", "-u", remote, branch])
        return result is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get git status."""
        status_output = self._run_git(["status", "--porcelain"])
        
        staged = []
        unstaged = []
        untracked = []
        
        for line in status_output.strip().split('\n'):
            if not line:
                continue
            status = line[:2]
            file_path = line[3:]
            
            if status[0] != ' ':  # staged
                staged.append(file_path)
            elif status[1] != ' ':  # unstaged
                unstaged.append(file_path)
            else:  # untracked
                untracked.append(file_path)
        
        return {
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked
        }
    
    def get_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commit history."""
        output = self._run_git([
            "log",
            f"--max-count={limit}",
            "--pretty=format:%H|%s|%an|%ad",
            "--date=iso"
        ])
        
        commits = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "message": parts[1],
                    "author": parts[2],
                    "date": parts[3]
                })
        
        return commits
    
    def get_branch(self) -> str:
        """Get current branch name."""
        return self._run_git(["branch", "--show-current"]).strip()
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch."""
        result = self._run_git(["checkout", "-b", branch_name])
        return result is not None
    
    def checkout(self, branch_name: str) -> bool:
        """Switch to a branch."""
        result = self._run_git(["checkout", branch_name])
        return result is not None
    
    def fetch(self, remote: str = "origin") -> bool:
        """Fetch from remote."""
        result = self._run_git(["fetch", remote])
        return result is not None
