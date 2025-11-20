import os
import pytest
from rigby.core import process_path

def test_integration_ignore_dirs(tmp_path, capsys):
    """Test that ignored directories like node_modules are skipped."""
    root = tmp_path / "project"
    root.mkdir()
    
    # Valid file
    (root / "main.py").write_text("def main(): pass")
    
    # Ignored directory
    nm = root / "node_modules"
    nm.mkdir()
    (nm / "ignored.py").write_text("def should_not_see_this(): pass")
    
    # .git directory
    git = root / ".git"
    git.mkdir()
    (git / "config.py").write_text("def git_config(): pass")
    
    # Run rigby
    process_path(str(root))
    
    captured = capsys.readouterr()
    stdout = captured.out
    
    assert "FUNC main():" in stdout
    assert "FUNC should_not_see_this():" not in stdout
    assert "FUNC git_config():" not in stdout
    
    # Verify item count in stderr log
    assert "Found 1 items" in captured.err

def test_integration_nested_structure(tmp_path, capsys):
    """Test recursive traversal of nested directories."""
    root = tmp_path / "nested_project"
    root.mkdir()
    
    src = root / "src"
    src.mkdir()
    
    utils = src / "utils"
    utils.mkdir()
    
    (root / "app.py").write_text("class App: pass")
    (src / "lib.py").write_text("def lib_func(): pass")
    # Need explicit type annotation for VAR detection
    (utils / "helpers.py").write_text("CONST: int = 1")
    
    process_path(str(root))
    
    captured = capsys.readouterr()
    stdout = captured.out
    
    assert "CLS App:" in stdout
    assert "FUNC lib_func():" in stdout
    assert "VAR CONST: int" in stdout

def test_integration_syntax_error_fault_tolerance(tmp_path, capsys):
    """Test that a syntax error in one file doesn't stop processing others."""
    root = tmp_path / "faulty_project"
    root.mkdir()
    
    (root / "good.py").write_text("def good(): pass")
    (root / "bad.py").write_text("def bad( THIS IS SYNTAX ERROR")
    
    process_path(str(root))
    
    captured = capsys.readouterr()
    
    # Should have output for good.py
    assert "FUNC good():" in captured.out
    
    # Should have error log for bad.py
    assert "bad.py" in captured.err
    assert "SyntaxError" in captured.err or "invalid syntax" in captured.err

