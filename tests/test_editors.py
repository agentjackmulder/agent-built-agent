"""Tests for code editors."""

import pytest
import tempfile
from pathlib import Path

from src.editors.code_editor import CodeEditor
from src.editors.python_editor import PythonEditor
from src.editors.config_editor import ConfigEditor


class TestCodeEditor:
    """Tests for CodeEditor."""
    
    def test_load_file(self):
        """Test loading a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("print('hello')\n")
            
            editor = CodeEditor(str(file_path))
            assert editor.load()
            assert editor.current_content == "print('hello')\n"
    
    def test_save_file(self):
        """Test saving a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            
            editor = CodeEditor(str(file_path))
            editor.current_content = "print('world')\n"
            assert editor.save()
            
            assert file_path.read_text() == "print('world')\n"
    
    def test_text_replace(self):
        """Test text replacement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("print('hello')\n")
            
            editor = CodeEditor(str(file_path))
            editor.load()
            editor.apply_text_replace("hello", "world")
            
            assert "world" in editor.current_content
            assert "hello" not in editor.current_content
    
    def test_line_replace(self):
        """Test line replacement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("line1\nline2\nline3\n")
            
            editor = CodeEditor(str(file_path))
            editor.load()
            editor.apply_line_replace(2, ["modified_line2"])
            
            lines = editor.current_content.split('\n')
            assert lines[1] == "modified_line2"


class TestPythonEditor:
    """Tests for PythonEditor."""
    
    def test_add_import(self):
        """Test adding an import."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("print('hello')\n")
            
            editor = PythonEditor(str(file_path))
            editor.load()
            # Insert after line 1 (first line)
            editor.insert_after_line(1, "import os\n")
            
            assert "import os" in editor.current_content
    
    def test_add_function(self):
        """Test adding a function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("print('hello')\n")
            
            editor = PythonEditor(str(file_path))
            editor.load()
            assert editor.add_function(
                func_name="greet",
                parameters=["name"],
                body_lines=['print(f"Hello, {name}!")']
            )
            
            assert "def greet(name):" in editor.current_content
    
    def test_find_function(self):
        """Test finding a function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("""
def hello():
    pass

def world():
    pass
""")
            
            editor = PythonEditor(str(file_path))
            editor.load()
            
            line_num = editor.find_function("hello")
            assert line_num == 2


class TestConfigEditor:
    """Tests for ConfigEditor."""
    
    def test_load_yaml_config(self):
        """Test loading YAML config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.yaml"
            file_path.write_text("name: test\nversion: 1.0\n")
            
            editor = ConfigEditor(str(file_path))
            assert editor.load_config()
            assert editor.config_data["name"] == "test"
    
    def test_get_value(self):
        """Test getting nested values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.yaml"
            file_path.write_text("""
database:
  host: localhost
  port: 5432
""")
            
            editor = ConfigEditor(str(file_path))
            editor.load_config()
            
            assert editor.get_value("database.host") == "localhost"
            assert editor.get_value("database.port") == 5432
    
    def test_set_value(self):
        """Test setting nested values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.yaml"
            file_path.write_text("name: test\n")
            
            editor = ConfigEditor(str(file_path))
            editor.load_config()
            editor.set_value("version", "1.0")
            
            assert editor.get_value("version") == "1.0"
            # YAML may quote strings, so check for key and value separately
            content = editor.file_path.read_text()
            assert "version" in content
            assert "1.0" in content
