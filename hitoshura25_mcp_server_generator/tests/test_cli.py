"""
Tests for CLI functionality.
"""

import pytest
from hitoshura25_mcp_server_generator.cli import load_tools_from_file


def test_load_tools_from_json(tmp_path):
    """Test loading tools from JSON file."""
    tools_file = tmp_path / "tools.json"
    tools_file.write_text('''
    {
        "tools": [
            {"name": "test", "description": "Test", "parameters": []}
        ]
    }
    ''')

    tools = load_tools_from_file(str(tools_file))

    assert "tools" in tools
    assert len(tools["tools"]) == 1
    assert tools["tools"][0]["name"] == "test"


def test_load_tools_from_json_as_array(tmp_path):
    """Test loading tools from JSON file when tools is the root array."""
    tools_file = tmp_path / "tools.json"
    tools_file.write_text('''
    [
        {"name": "test1", "description": "Test 1", "parameters": []},
        {"name": "test2", "description": "Test 2", "parameters": []}
    ]
    ''')

    tools = load_tools_from_file(str(tools_file))

    assert isinstance(tools, list)
    assert len(tools) == 2
    assert tools[0]["name"] == "test1"


def test_load_tools_from_file_not_found():
    """Test that missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Tools file not found"):
        load_tools_from_file("/nonexistent/file.json")


def test_load_tools_from_file_invalid_format(tmp_path):
    """Test that invalid file format raises ValueError."""
    invalid_file = tmp_path / "tools.txt"
    invalid_file.write_text('test')

    with pytest.raises(ValueError, match="must have .json, .yaml, or .yml extension"):
        load_tools_from_file(str(invalid_file))


def test_cli_main_with_all_args(tmp_path, monkeypatch):
    """Test CLI main with all required arguments."""
    from hitoshura25_mcp_server_generator.cli import main

    tools_file = tmp_path / "tools.json"
    tools_file.write_text('{"tools": [{"name": "test", "description": "Test", "parameters": []}]}')

    # Mock sys.argv
    test_args = [
        'mcp-server-generator-cli',
        '--project-name', 'cli-test',
        '--description', 'CLI test',
        '--author', 'Test',
        '--email', 'test@test.com',
        '--tools-file', str(tools_file),
        '--output-dir', str(tmp_path),
        '--prefix', 'NONE'
    ]
    monkeypatch.setattr('sys.argv', test_args)

    result = main()

    assert result == 0
    assert (tmp_path / "cli-test").exists()
    assert (tmp_path / "cli-test" / "README.md").exists()


def test_cli_main_missing_args(monkeypatch):
    """Test that CLI fails with missing required arguments."""
    from hitoshura25_mcp_server_generator.cli import main

    # Only provide program name
    monkeypatch.setattr('sys.argv', ['mcp-server-generator-cli'])

    # Should exit with error (argparse raises SystemExit)
    with pytest.raises(SystemExit):
        main()


def test_cli_imports():
    """Test that CLI can be imported successfully."""
    from hitoshura25_mcp_server_generator.cli import main, load_tools_from_file, interactive_mode

    assert main is not None
    assert load_tools_from_file is not None
    assert interactive_mode is not None
    assert callable(main)
    assert callable(load_tools_from_file)
    assert callable(interactive_mode)
