"""Python-specific code editor with AST-based editing."""

import ast
from pathlib import Path
from typing import Optional, List, Dict, Any
from .code_editor import CodeEditor


class PythonEditor(CodeEditor):
    """Editor for Python files with AST-based capabilities."""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.ast_tree: Optional[ast.AST] = None
    
    def load_ast(self) -> bool:
        """Parse file into AST."""
        if not self.load():
            return False
        
        try:
            self.ast_tree = ast.parse(self.current_content)
            return True
        except SyntaxError as e:
            print(f"Syntax error in {self.file_path}: {e}")
            return False
    
    def add_import(self, module: str, names: Optional[List[str]] = None) -> bool:
        """Add an import statement."""
        if not self.load_ast():
            return False
        
        if names:
            import_stmt = f"from {module} import {', '.join(names)}"
        else:
            import_stmt = f"import {module}"
        
        # Check if import already exists
        if import_stmt in self.current_content:
            print(f"Import already exists: {import_stmt}")
            return True
        
        # Add to top of file
        self.insert_after_line(0, import_stmt)
        return True
    
    def remove_import(self, module: str) -> bool:
        """Remove an import statement."""
        if not self.load_ast():
            return False
        
        lines = self.current_content.split('\n')
        new_lines = []
        removed = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(f"import {module}") or stripped.startswith(f"from {module}"):
                removed = True
                continue
            new_lines.append(line)
        
        if not removed:
            print(f"Import not found: {module}")
            return False
        
        self.current_content = '\n'.join(new_lines)
        self.edits_applied.append({
            "type": "remove_import",
            "module": module
        })
        
        return True
    
    def find_function(self, func_name: str) -> Optional[int]:
        """Find line number of a function definition."""
        if not self.load_ast():
            return None
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return node.lineno
        
        return None
    
    def add_function(
        self,
        func_name: str,
        parameters: List[str],
        body_lines: List[str],
        decorator: Optional[str] = None
    ) -> bool:
        """Add a new function to the file."""
        if not self.load_ast():
            return False
        
        # Build function signature
        params = ', '.join(parameters)
        func_sig = f"def {func_name}({params}):"
        
        # Build function body
        body = '\n'.join(f"    {line}" for line in body_lines)
        func_def = f"{func_sig}\n{body}"
        
        if decorator:
            func_def = f"{decorator}\n{func_def}"
        
        # Find end of file and insert
        lines = self.current_content.split('\n')
        
        # Insert before last line (assuming it's empty or __name__ check)
        insert_line = len(lines)
        self.insert_before_line(insert_line, func_def)
        
        self.edits_applied.append({
            "type": "add_function",
            "name": func_name,
            "params": params
        })
        
        return True
    
    def modify_function_signature(
        self,
        func_name: str,
        new_parameters: List[str]
    ) -> bool:
        """Modify function parameters."""
        if not self.load_ast():
            return False
        
        line_num = self.find_function(func_name)
        if not line_num:
            print(f"Function not found: {func_name}")
            return False
        
        params = ', '.join(new_parameters)
        new_sig = f"def {func_name}({params}):"
        
        self.apply_line_replace(line_num, [new_sig])
        
        self.edits_applied.append({
            "type": "modify_signature",
            "function": func_name,
            "new_params": params
        })
        
        return True
    
    def add_method_to_class(
        self,
        class_name: str,
        method_name: str,
        parameters: List[str],
        body_lines: List[str]
    ) -> bool:
        """Add a method to a specific class."""
        if not self.load_ast():
            return False
        
        # Find class line number
        class_line = None
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_line = node.lineno
                break
        
        if not class_line:
            print(f"Class not found: {class_name}")
            return False
        
        # Build method
        params = ', '.join(parameters)
        method_sig = f"    def {method_name}(self, {params}):"
        body = '\n'.join(f"        {line}" for line in body_lines)
        method_def = f"{method_sig}\n{body}"
        
        # Insert after class definition (need to find end of class)
        lines = self.current_content.split('\n')
        
        # Simple approach: insert after class line
        insert_line = class_line
        self.insert_after_line(insert_line, method_def)
        
        self.edits_applied.append({
            "type": "add_method",
            "class": class_name,
            "method": method_name
        })
        
        return True
