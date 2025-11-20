import pytest
import subprocess
import sys
import os
from rigby.cli import main

def test_cli_help():
    """Test that --help works."""
    result = subprocess.run(
        [sys.executable, "-m", "rigby", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Rigby: The code raccoon" in result.stdout

def test_cli_parse_file(tmp_path):
    """Test parsing a single file via CLI."""
    d = tmp_path / "test_project"
    d.mkdir()
    p = d / "hello.py"
    p.write_text("def hello(): pass")

    result = subprocess.run(
        [sys.executable, "-m", "rigby", "parse", str(p)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "FUNC hello():" in result.stdout
    # Check stderr for personality logs
    assert "Ugh, fine. Scanning" in result.stderr
    assert "Ooooooh! Done!" in result.stderr

def test_cli_parse_directory(tmp_path):
    """Test parsing a directory via CLI."""
    d = tmp_path / "test_project"
    d.mkdir()
    (d / "a.py").write_text("class A: pass")
    (d / "b.py").write_text("def b(): pass")

    result = subprocess.run(
        [sys.executable, "-m", "rigby", "parse", str(d)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "CLS A:" in result.stdout
    assert "FUNC b():" in result.stdout

def test_cli_invalid_command():
    """Test that invalid commands fail."""
    result = subprocess.run(
        [sys.executable, "-m", "rigby", "invalid_cmd"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0

