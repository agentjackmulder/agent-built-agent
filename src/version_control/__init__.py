"""Version control for agent self-edits."""
from .git_manager import GitManager
from .edit_tracker import EditTracker

__all__ = ["GitManager", "EditTracker"]
