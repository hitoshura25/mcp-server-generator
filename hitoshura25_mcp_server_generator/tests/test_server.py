"""
Tests for MCP server functionality.
"""

import json
import pytest
from hitoshura25_mcp_server_generator.server import mcp, generate_mcp_server, validate_project_name


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that the MCP server initializes correctly."""
    assert mcp.name == "mcp-server-generator"

    # Check that tools are registered
    tools = await mcp.list_tools()
    assert len(tools) == 2

    tool_names = [tool.name for tool in tools]
    assert "generate_mcp_server" in tool_names
    assert "validate_project_name" in tool_names


@pytest.mark.asyncio
async def test_list_tools_schema_validation():
    """Test that tool schemas are properly defined."""
    tools = await mcp.list_tools()

    # Verify each tool has required fields
    for tool in tools:
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'inputSchema')
        schema = tool.inputSchema
        assert 'type' in schema
        assert 'properties' in schema

    # Check generate_mcp_server schema
    gen_tool = next(t for t in tools if t.name == "generate_mcp_server")
    assert "project_name" in gen_tool.inputSchema["properties"]
    assert "description" in gen_tool.inputSchema["properties"]
    assert "author" in gen_tool.inputSchema["properties"]
    assert "tools" in gen_tool.inputSchema["properties"]

    # Check validate_project_name schema
    val_tool = next(t for t in tools if t.name == "validate_project_name")
    assert "name" in val_tool.inputSchema["properties"]


def test_generate_mcp_server_function(tmp_path):
    """Test the generate_mcp_server function directly."""
    result_json = generate_mcp_server(
        project_name="test-mcp",
        description="Test MCP server",
        author="Test Author",
        author_email="test@example.com",
        tools=[
            {
                "name": "test_tool",
                "description": "Test tool",
                "parameters": []
            }
        ],
        output_dir=str(tmp_path),
        prefix="NONE"
    )

    # Result should be a JSON string
    assert isinstance(result_json, str)
    result = json.loads(result_json)

    assert result["success"]
    assert "project_path" in result

    # Verify project was created
    assert (tmp_path / "test-mcp").exists()
    assert (tmp_path / "test-mcp" / "test_mcp" / "server.py").exists()


def test_generate_mcp_server_with_options(tmp_path):
    """Test generate_mcp_server with custom options."""
    result_json = generate_mcp_server(
        project_name="custom-mcp",
        description="Custom MCP server",
        author="Test",
        author_email="test@test.com",
        tools=[{"name": "func", "description": "Function", "parameters": []}],
        output_dir=str(tmp_path),
        python_version="3.11",
        prefix="NONE"
    )

    result = json.loads(result_json)
    assert result["success"]

    # Verify custom Python version in generated workflow files
    # Note: python_version affects workflows, not pyproject.toml (which is always >=3.10)
    workflow_content = (tmp_path / "custom-mcp" / ".github" / "workflows" / "release.yml").read_text()
    assert "python_version: '3.11'" in workflow_content


def test_generate_mcp_server_invalid_name():
    """Test that invalid project name raises error."""
    with pytest.raises(ValueError, match="Invalid project name"):
        generate_mcp_server(
            project_name="class",  # Invalid - Python keyword
            description="Test",
            author="Test",
            author_email="test@test.com",
            tools=[{"name": "test", "description": "Test", "parameters": []}]
        )


def test_validate_project_name_valid():
    """Test validating a valid project name."""
    result_json = validate_project_name(name="my-mcp-server")

    # Result should be a JSON string
    assert isinstance(result_json, str)
    data = json.loads(result_json)

    assert data["valid"] == True
    assert data["name"] == "my-mcp-server"


def test_validate_project_name_invalid():
    """Test validating an invalid project name."""
    result_json = validate_project_name(name="class")  # Python keyword

    data = json.loads(result_json)
    assert data["valid"] == False
    assert data["name"] == "class"


@pytest.mark.asyncio
async def test_all_tools_have_descriptions():
    """Test that all tools have proper descriptions."""
    tools = await mcp.list_tools()

    for tool in tools:
        assert hasattr(tool, 'description')
        assert tool.description
        assert len(tool.description) > 0


def test_mcp_server_imports():
    """Test that MCP server can be imported successfully."""
    from hitoshura25_mcp_server_generator.server import mcp, main

    assert mcp is not None
    assert main is not None
    assert callable(main)
