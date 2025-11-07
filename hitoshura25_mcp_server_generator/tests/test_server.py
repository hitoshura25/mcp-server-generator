"""
Tests for MCP server functionality.
"""

import json
import pytest
from hitoshura25_mcp_server_generator.server import MCPServer


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that handle_list_tools returns correct tool definitions."""
    server = MCPServer()
    result = await server.handle_list_tools()

    assert "tools" in result
    assert len(result["tools"]) == 2

    tool_names = [tool["name"] for tool in result["tools"]]
    assert "generate_mcp_server" in tool_names
    assert "validate_project_name" in tool_names


@pytest.mark.asyncio
async def test_list_tools_schema_validation():
    """Test that tool schemas are properly defined."""
    server = MCPServer()
    result = await server.handle_list_tools()

    # Verify each tool has required fields
    for tool in result["tools"]:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert "type" in tool["inputSchema"]
        assert "properties" in tool["inputSchema"]

    # Check generate_mcp_server schema
    gen_tool = next(t for t in result["tools"] if t["name"] == "generate_mcp_server")
    assert "project_name" in gen_tool["inputSchema"]["properties"]
    assert "description" in gen_tool["inputSchema"]["properties"]
    assert "author" in gen_tool["inputSchema"]["properties"]
    assert "tools" in gen_tool["inputSchema"]["properties"]
    assert set(gen_tool["inputSchema"]["required"]) == {
        "project_name", "description", "author", "author_email", "tools"
    }

    # Check validate_project_name schema
    val_tool = next(t for t in result["tools"] if t["name"] == "validate_project_name")
    assert "name" in val_tool["inputSchema"]["properties"]
    assert val_tool["inputSchema"]["required"] == ["name"]


@pytest.mark.asyncio
async def test_call_tool_generate_mcp_server(tmp_path):
    """Test calling generate_mcp_server tool via MCP."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "generate_mcp_server",
        {
            "project_name": "test-mcp",
            "description": "Test MCP server",
            "author": "Test Author",
            "author_email": "test@example.com",
            "tools": [
                {
                    "name": "test_tool",
                    "description": "Test tool",
                    "parameters": []
                }
            ],
            "output_dir": str(tmp_path),
            "prefix": "NONE"
        }
    )

    assert "content" in result
    assert len(result["content"]) > 0
    assert result["content"][0]["type"] == "text"
    assert result.get("isError") == False

    # Verify project was created
    assert (tmp_path / "test-mcp").exists()


@pytest.mark.asyncio
async def test_call_tool_generate_mcp_server_with_options(tmp_path):
    """Test generate_mcp_server with custom options."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "generate_mcp_server",
        {
            "project_name": "custom-mcp",
            "description": "Custom MCP server",
            "author": "Test",
            "author_email": "test@test.com",
            "tools": [{"name": "func", "description": "Function", "parameters": []}],
            "output_dir": str(tmp_path),
            "python_version": "3.11",
            "prefix": "NONE"
        }
    )

    assert result.get("isError") == False

    # Verify custom Python version in generated files
    setup_content = (tmp_path / "custom-mcp" / "setup.py").read_text()
    assert "3.11" in setup_content


@pytest.mark.asyncio
async def test_call_tool_generate_mcp_server_invalid_name():
    """Test that invalid project name returns error."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "generate_mcp_server",
        {
            "project_name": "class",  # Invalid
            "description": "Test",
            "author": "Test",
            "author_email": "test@test.com",
            "tools": [{"name": "test", "description": "Test", "parameters": []}]
        }
    )

    assert result.get("isError") == True
    assert "Invalid project name" in result["content"][0]["text"]


@pytest.mark.asyncio
async def test_call_tool_validate_project_name_valid():
    """Test validating a valid project name."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "validate_project_name",
        {"name": "my-mcp-server"}
    )

    assert result.get("isError") == False
    assert "content" in result

    data = json.loads(result["content"][0]["text"])
    assert data["valid"] == True
    assert data["name"] == "my-mcp-server"


@pytest.mark.asyncio
async def test_call_tool_validate_project_name_invalid():
    """Test validating an invalid project name."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "validate_project_name",
        {"name": "class"}  # Python keyword
    )

    assert result.get("isError") == False

    data = json.loads(result["content"][0]["text"])
    assert data["valid"] == False


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool returns error."""
    server = MCPServer()

    result = await server.handle_call_tool("unknown_tool", {})

    assert result.get("isError") == True
    assert "Unknown tool" in result["content"][0]["text"]


@pytest.mark.asyncio
async def test_handle_request_unknown_method():
    """Test handling unknown method returns error."""
    server = MCPServer()

    request = {
        "method": "unknown/method",
        "params": {}
    }

    response = await server.handle_request(request)

    assert "error" in response
    assert response["error"]["code"] == -32601
    assert "Method not found" in response["error"]["message"]


@pytest.mark.asyncio
async def test_handle_request_list_tools():
    """Test handling a full JSON-RPC request for tools/list."""
    server = MCPServer()

    request = {
        "method": "tools/list",
        "id": 1
    }

    response = await server.handle_request(request)

    assert "tools" in response
    assert len(response["tools"]) == 2


@pytest.mark.asyncio
async def test_handle_request_call_tool():
    """Test handling a full JSON-RPC request for tools/call."""
    server = MCPServer()

    request = {
        "method": "tools/call",
        "id": 2,
        "params": {
            "name": "validate_project_name",
            "arguments": {"name": "test-server"}
        }
    }

    response = await server.handle_request(request)

    assert "content" in response
    assert response.get("isError") == False


def test_mcp_server_imports():
    """Test that MCP server can be imported successfully."""
    from hitoshura25_mcp_server_generator.server import MCPServer, main

    assert MCPServer is not None
    assert main is not None
    assert callable(main)
