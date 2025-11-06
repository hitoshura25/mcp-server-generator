"""
Tests for core generation logic.
"""

import os
import pytest
from mcp_server_generator.generator import (
    validate_project_name,
    validate_tool_name,
    generate_tool_schema,
    sanitize_description,
    generate_mcp_server,
)


def test_validate_project_name_valid():
    """Test valid project names."""
    assert validate_project_name('my-mcp-server') == True
    assert validate_project_name('my_mcp_server') == True
    assert validate_project_name('mcp123') == True
    assert validate_project_name('abc') == True


def test_validate_project_name_invalid():
    """Test invalid project names."""
    # Keywords
    assert validate_project_name('class') == False
    assert validate_project_name('import') == False
    assert validate_project_name('for') == False

    # Invalid characters/start
    assert validate_project_name('123-invalid') == False
    assert validate_project_name('my server') == False
    assert validate_project_name('my.server') == False

    # Empty
    assert validate_project_name('') == False
    assert validate_project_name(None) == False


def test_validate_tool_name_valid():
    """Test valid tool names."""
    assert validate_tool_name('my_function') == True
    assert validate_tool_name('test') == True
    assert validate_tool_name('func123') == True
    assert validate_tool_name('_private') == True


def test_validate_tool_name_invalid():
    """Test invalid tool names."""
    assert validate_tool_name('class') == False  # keyword
    assert validate_tool_name('my-function') == False  # hyphen
    assert validate_tool_name('123func') == False  # starts with number
    assert validate_tool_name('') == False
    assert validate_tool_name(None) == False


def test_generate_tool_schema_basic():
    """Test basic tool schema generation."""
    tool_def = {
        'name': 'test_tool',
        'description': 'Test tool',
        'parameters': [
            {'name': 'param1', 'type': 'string', 'description': 'First param', 'required': True}
        ]
    }

    schema = generate_tool_schema(tool_def)

    assert schema['name'] == 'test_tool'
    assert schema['description'] == 'Test tool'
    assert 'inputSchema' in schema
    assert 'param1' in schema['inputSchema']['properties']
    assert schema['inputSchema']['properties']['param1']['type'] == 'string'
    assert 'param1' in schema['inputSchema']['required']


def test_generate_tool_schema_type_mapping():
    """Test type mapping from various formats."""
    tool_def = {
        'name': 'test',
        'description': 'Test',
        'parameters': [
            {'name': 'str_param', 'type': 'str', 'description': 'String param', 'required': False},
            {'name': 'int_param', 'type': 'int', 'description': 'Int param', 'required': False},
            {'name': 'bool_param', 'type': 'bool', 'description': 'Bool param', 'required': False},
            {'name': 'num_param', 'type': 'number', 'description': 'Number param', 'required': False},
        ]
    }

    schema = generate_tool_schema(tool_def)

    assert schema['inputSchema']['properties']['str_param']['type'] == 'string'
    assert schema['inputSchema']['properties']['int_param']['type'] == 'number'
    assert schema['inputSchema']['properties']['bool_param']['type'] == 'boolean'
    assert schema['inputSchema']['properties']['num_param']['type'] == 'number'
    
    # None should be required since all are False
    assert len(schema['inputSchema']['required']) == 0


def test_sanitize_description():
    """Test description sanitization prevents template injection."""
    assert sanitize_description('Hello {world}') == 'Hello {{world}}'
    assert sanitize_description('Test {{var}}') == 'Test {{{{var}}}}'
    assert sanitize_description('Normal text') == 'Normal text'
    assert sanitize_description('') == ''


def test_generate_mcp_server_success(tmp_path):
    """Test successful project generation."""
    tools = [
        {
            "name": "test_func",
            "description": "Test function",
            "parameters": [
                {"name": "arg1", "type": "string", "description": "Arg 1", "required": True}
            ]
        }
    ]

    result = generate_mcp_server(
        project_name="test-server",
        description="Test MCP server",
        author="Test Author",
        author_email="test@example.com",
        tools=tools,
        output_dir=str(tmp_path)
    )

    assert result['success'] == True
    assert 'project_path' in result
    assert 'files_created' in result
    assert len(result['files_created']) > 0

    # Verify project exists
    project_path = tmp_path / "test-server"
    assert project_path.exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "setup.py").exists()
    assert (project_path / "test_server" / "server.py").exists()
    assert (project_path / "test_server" / "cli.py").exists()
    assert (project_path / "test_server" / "generator.py").exists()


def test_generate_mcp_server_invalid_project_name():
    """Test that invalid project names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid project name"):
        generate_mcp_server(
            project_name="class",  # Python keyword
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "test", "description": "test", "parameters": []}]
        )


def test_generate_mcp_server_invalid_tool_name():
    """Test that invalid tool names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid tool name"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "my-tool", "description": "test", "parameters": []}]  # hyphen invalid
        )


def test_generate_mcp_server_no_tools():
    """Test that empty tools list raises ValueError."""
    with pytest.raises(ValueError, match="At least one tool"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[]
        )


def test_generate_mcp_server_existing_directory(tmp_path):
    """Test that existing directory raises FileExistsError."""
    # Create the directory first
    (tmp_path / "test-server").mkdir()

    with pytest.raises(FileExistsError, match="Directory already exists"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "test", "description": "test", "parameters": []}],
            output_dir=str(tmp_path)
        )
