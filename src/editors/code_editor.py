"""Base code editor for the agent."""

from pathlib import Path
from typing import Optional, Dict, Any, List
import re


class CodeEditor:
    """Base class for code editors."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.original_content: Optional[str] = None
        self.current_content: Optional[str] = None
        self.edits_applied: List[Dict[str, Any]] = []
    
    def load(self) -> bool:
        """Load file content."""
        if not self.file_path.exists():
            print(f"File not found: {self.file_path}")
            return False
        
        try:
            self.original_content = self.file_path.read_text()
            self.current_content = self.original_content
            return True
        except Exception as e:
            print(f"Failed to load {self.file_path}: {e}")
            return False
    
    def save(self) -> bool:
        """Save current content to file."""
        if not self.current_content:
            print("No content to save")
            return False
        
        try:
            self.file_path.write_text(self.current_content)
            return True
        except Exception as e:
            print(f"Failed to save {self.file_path}: {e}")
            return False
    
    def apply_text_replace(
        self,
        old_text: str,
        new_text: str,
        replace_all: bool = True
    ) -> bool:
        """Replace text in the file."""
        if not self.current_content:
            print("No content loaded")
            return False
        
        flags = 0
        if not replace_all:
            flags = re.MULTILINE
        
        try:
            if replace_all:
                self.current_content = self.current_content.replace(old_text, new_text)
            else:
                self.current_content = re.sub(old_text, new_text, self.current_content, flags=flags)
            
            self.edits_applied.append({
                "type": "replace",
                "old": old_text[:50] + "..." if len(old_text) > 50 else old_text,
                "new": new_text[:50] + "..." if len(new_text) > 50 else new_text
            })
            
            return True
        except Exception as e:
            print(f"Text replace failed: {e}")
            return False
    
    def apply_line_replace(
        self,
        line_number: int,
        new_lines: List[str]
    ) -> bool:
        """Replace a specific line with new lines."""
        if not self.current_content:
            print("No content loaded")
            return False
        
        lines = self.current_content.split('\n')
        
        if line_number < 1 or line_number > len(lines):
            print(f"Invalid line number: {line_number}")
            return False
        
        # Replace the line (1-indexed)
        lines[line_number - 1] = new_lines[0] if len(new_lines) == 1 else '\n'.join(new_lines)
        
        self.current_content = '\n'.join(lines)
        self.edits_applied.append({
            "type": "line_replace",
            "line": line_number,
            "new": new_lines[0][:50] + "..." if len(new_lines[0]) > 50 else new_lines[0]
        })
        
        return True
    
    def insert_after_line(
        self,
        line_number: int,
        text: str
    ) -> bool:
        """Insert text after a specific line."""
        if not self.current_content:
            print("No content loaded")
            return False
        
        lines = self.current_content.split('\n')
        
        if line_number < 1 or line_number > len(lines):
            print(f"Invalid line number: {line_number}")
            return False
        
        lines.insert(line_number, text)
        self.current_content = '\n'.join(lines)
        self.edits_applied.append({
            "type": "insert",
            "after_line": line_number,
            "text": text[:50] + "..." if len(text) > 50 else text
        })
        
        return True
    
    def insert_before_line(
        self,
        line_number: int,
        text: str
    ) -> bool:
        """Insert text before a specific line."""
        if not self.current_content:
            print("No content loaded")
            return False
        
        lines = self.current_content.split('\n')
        
        if line_number < 1 or line_number > len(lines) + 1:
            print(f"Invalid line number: {line_number}")
            return False
        
        lines.insert(line_number - 1, text)
        self.current_content = '\n'.join(lines)
        self.edits_applied.append({
            "type": "insert_before",
            "before_line": line_number,
            "text": text[:50] + "..." if len(text) > 50 else text
        })
        
        return True
    
    def get_content(self) -> str:
        """Get current content."""
        return self.current_content or ""
    
    def get_diff(self) -> str:
        """Get diff between original and current content."""
        if not self.original_content or not self.current_content:
            return ""
        
        original_lines = self.original_content.split('\n')
        current_lines = self.current_content.split('\n')
        
        diff_lines = []
        for i, (orig, curr) in enumerate(zip(original_lines, current_lines)):
            if orig != curr:
                diff_lines.append(f"Line {i+1}:")
                diff_lines.append(f"  - {orig}")
                diff_lines.append(f"  + {curr}")
        
        return '\n'.join(diff_lines)
