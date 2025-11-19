"""
Tests for MCP server functionality.
"""

import json
import pytest
from hitoshura25_mcp_server_generator.server import (
    mcp,
    generate_mcp_server,
    validate_project_name,
)


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that the MCP server initializes correctly."""
    assert mcp.name == "mcp-server-generator"

    # Check that tools are registered
    tools = await mcp.list_tools()
    assert len(tools) == 7  # Updated count for new tools

    tool_names = [tool.name for tool in tools]
    # Original tools
    assert "generate_mcp_server" in tool_names
    assert "validate_project_name" in tool_names
    # Progressive disclosure tools
    assert "search_tools" in tool_names
    assert "get_tool_info" in tool_names
    # Guidance tools
    assert "get_best_practices" in tool_names
    assert "get_implementation_guide" in tool_names
    # Claude Code command generator
    assert "generate_claude_command" in tool_names


@pytest.mark.asyncio
async def test_list_tools_schema_validation():
    """Test that tool schemas are properly defined."""
    tools = await mcp.list_tools()

    # Verify each tool has required fields
    for tool in tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "inputSchema")
        schema = tool.inputSchema
        assert "type" in schema
        assert "properties" in schema

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
        tools=[{"name": "test_tool", "description": "Test tool", "parameters": []}],
        output_dir=str(tmp_path),
        prefix="NONE",
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
        prefix="NONE",
    )

    result = json.loads(result_json)
    assert result["success"]

    # Verify custom Python version in generated files
    # python_version affects both workflows AND package requirements
    pyproject_content = (tmp_path / "custom-mcp" / "pyproject.toml").read_text()
    assert 'requires-python = ">=3.11"' in pyproject_content

    workflow_content = (
        tmp_path / "custom-mcp" / ".github" / "workflows" / "release.yml"
    ).read_text()
    assert "python_version: '3.11'" in workflow_content


def test_generate_mcp_server_invalid_name():
    """Test that invalid project name raises error."""
    with pytest.raises(ValueError, match="Invalid project name"):
        generate_mcp_server(
            project_name="class",  # Invalid - Python keyword
            description="Test",
            author="Test",
            author_email="test@test.com",
            tools=[{"name": "test", "description": "Test", "parameters": []}],
        )


def test_validate_project_name_valid():
    """Test validating a valid project name."""
    result_json = validate_project_name(name="my-mcp-server")

    # Result should be a JSON string
    assert isinstance(result_json, str)
    data = json.loads(result_json)

    assert data["valid"]
    assert data["name"] == "my-mcp-server"


def test_validate_project_name_invalid():
    """Test validating an invalid project name."""
    result_json = validate_project_name(name="class")  # Python keyword

    data = json.loads(result_json)
    assert not data["valid"]
    assert data["name"] == "class"


@pytest.mark.asyncio
async def test_all_tools_have_descriptions():
    """Test that all tools have proper descriptions."""
    tools = await mcp.list_tools()

    for tool in tools:
        assert hasattr(tool, "description")
        assert tool.description
        assert len(tool.description) > 0


def test_mcp_server_imports():
    """Test that MCP server can be imported successfully."""
    from hitoshura25_mcp_server_generator.server import mcp, main

    assert mcp is not None
    assert main is not None
    assert callable(main)


# Tests for progressive disclosure features


def test_search_tools_with_query():
    """Test searching for tools with a query."""
    from hitoshura25_mcp_server_generator.server import search_tools

    result_json = search_tools(query="generate", detail_level="summary")
    data = json.loads(result_json)

    assert data["query"] == "generate"
    assert data["detail_level"] == "summary"
    assert data["count"] > 0
    assert len(data["matches"]) > 0

    # Check that generate_mcp_server is in results
    tool_names = [match["name"] for match in data["matches"]]
    assert "generate_mcp_server" in tool_names


def test_search_tools_detail_levels():
    """Test different detail levels for search_tools."""
    from hitoshura25_mcp_server_generator.server import search_tools

    # Test "name" detail level
    result_json = search_tools(query="mcp", detail_level="name")
    data = json.loads(result_json)
    assert data["detail_level"] == "name"
    assert all(isinstance(match, str) for match in data["matches"])

    # Test "summary" detail level
    result_json = search_tools(query="mcp", detail_level="summary")
    data = json.loads(result_json)
    assert data["detail_level"] == "summary"
    assert all(isinstance(match, dict) for match in data["matches"])
    if data["matches"]:
        assert "name" in data["matches"][0]
        assert "description" in data["matches"][0]
        assert "category" in data["matches"][0]

    # Test "full" detail level
    result_json = search_tools(query="mcp", detail_level="full")
    data = json.loads(result_json)
    assert data["detail_level"] == "full"
    if data["matches"]:
        assert "use_cases" in data["matches"][0]
        assert "full_description" in data["matches"][0]


def test_get_tool_info_valid_tool():
    """Test getting information about a valid tool."""
    from hitoshura25_mcp_server_generator.server import get_tool_info

    result_json = get_tool_info(tool_name="generate_mcp_server", detail_level="summary")
    data = json.loads(result_json)

    assert data["name"] == "generate_mcp_server"
    assert "description" in data
    assert "category" in data


def test_get_tool_info_full_detail():
    """Test getting full information about a tool."""
    from hitoshura25_mcp_server_generator.server import get_tool_info

    result_json = get_tool_info(tool_name="generate_mcp_server", detail_level="full")
    data = json.loads(result_json)

    assert data["name"] == "generate_mcp_server"
    assert "use_cases" in data
    assert "full_description" in data
    assert isinstance(data["use_cases"], list)


def test_get_tool_info_invalid_tool():
    """Test getting information about an invalid tool."""
    from hitoshura25_mcp_server_generator.server import get_tool_info

    result_json = get_tool_info(tool_name="nonexistent_tool")
    data = json.loads(result_json)

    assert "error" in data
    assert "available_tools" in data


def test_get_best_practices_all():
    """Test getting all best practices."""
    from hitoshura25_mcp_server_generator.server import get_best_practices

    result_json = get_best_practices()
    data = json.loads(result_json)

    assert "best_practices" in data
    assert "count" in data
    assert data["count"] > 0

    # Check that key topics are present
    practices = data["best_practices"]
    assert "progressive_disclosure" in practices
    assert "tool_design" in practices
    assert "security" in practices
    assert "testing" in practices


def test_get_best_practices_specific_topic():
    """Test getting a specific best practice topic."""
    from hitoshura25_mcp_server_generator.server import get_best_practices

    result_json = get_best_practices(topic="progressive_disclosure")
    data = json.loads(result_json)

    assert data["topic"] == "progressive_disclosure"
    assert "practice" in data

    practice = data["practice"]
    assert "title" in practice
    assert "summary" in practice
    assert "principles" in practice


def test_get_best_practices_invalid_topic():
    """Test getting an invalid best practice topic."""
    from hitoshura25_mcp_server_generator.server import get_best_practices

    result_json = get_best_practices(topic="invalid_topic")
    data = json.loads(result_json)

    assert "error" in data
    assert "available_topics" in data


def test_get_implementation_guide_overview():
    """Test getting implementation guide overview."""
    from hitoshura25_mcp_server_generator.server import get_implementation_guide

    result_json = get_implementation_guide()
    data = json.loads(result_json)

    assert "overview" in data
    assert "setup" in data
    assert "implementation" in data
    assert "testing" in data
    assert "deployment" in data
    assert "integration" in data


def test_get_implementation_guide_specific_step():
    """Test getting a specific implementation guide step."""
    from hitoshura25_mcp_server_generator.server import get_implementation_guide

    result_json = get_implementation_guide(step="setup")
    data = json.loads(result_json)

    assert data["step"] == "setup"
    assert "guide" in data

    guide = data["guide"]
    assert "title" in guide
    assert "description" in guide
    assert "steps" in guide


def test_get_implementation_guide_invalid_step():
    """Test getting an invalid implementation guide step."""
    from hitoshura25_mcp_server_generator.server import get_implementation_guide

    result_json = get_implementation_guide(step="invalid_step")
    data = json.loads(result_json)

    assert "error" in data
    assert "available_steps" in data


def test_generate_claude_command_mcp_generator(tmp_path):
    """Test generating an MCP generator Claude command."""
    from hitoshura25_mcp_server_generator.server import generate_claude_command

    output_dir = str(tmp_path / "commands")
    result_json = generate_claude_command(
        command_name="test-mcp-gen",
        command_type="mcp_generator",
        output_dir=output_dir,
    )
    data = json.loads(result_json)

    assert data["success"]
    assert data["command_name"] == "test-mcp-gen"
    assert data["command_type"] == "mcp_generator"
    assert "file_path" in data
    assert data["usage"] == "/test-mcp-gen"

    # Verify file was created
    command_file = tmp_path / "commands" / "test-mcp-gen.md"
    assert command_file.exists()

    # Verify content
    content = command_file.read_text()
    assert "description:" in content
    assert "MCP server" in content


def test_generate_claude_command_all_types(tmp_path):
    """Test generating all types of Claude commands."""
    from hitoshura25_mcp_server_generator.server import generate_claude_command

    output_dir = str(tmp_path / "commands")

    command_types = ["mcp_generator", "best_practices", "implementation_helper"]

    for cmd_type in command_types:
        result_json = generate_claude_command(
            command_name=f"test-{cmd_type}",
            command_type=cmd_type,
            output_dir=output_dir,
        )
        data = json.loads(result_json)

        assert data["success"], f"Failed for type {cmd_type}"
        assert data["command_type"] == cmd_type

        # Verify file exists
        command_file = tmp_path / "commands" / f"test-{cmd_type}.md"
        assert command_file.exists()


def test_generate_claude_command_custom(tmp_path):
    """Test generating a custom Claude command."""
    from hitoshura25_mcp_server_generator.server import generate_claude_command

    output_dir = str(tmp_path / "commands")
    custom_prompt = "This is a custom prompt for testing."

    result_json = generate_claude_command(
        command_name="test-custom",
        command_type="custom",
        custom_prompt=custom_prompt,
        output_dir=output_dir,
    )
    data = json.loads(result_json)

    assert data["success"]
    assert data["command_type"] == "custom"

    # Verify content includes custom prompt
    command_file = tmp_path / "commands" / "test-custom.md"
    content = command_file.read_text()
    assert custom_prompt in content


def test_generate_claude_command_custom_without_prompt(tmp_path):
    """Test that custom command type requires a prompt."""
    from hitoshura25_mcp_server_generator.server import generate_claude_command

    output_dir = str(tmp_path / "commands")

    result_json = generate_claude_command(
        command_name="test-fail", command_type="custom", output_dir=output_dir
    )
    data = json.loads(result_json)

    assert not data["success"]
    assert "error" in data
    assert "custom_prompt is required" in data["error"]
