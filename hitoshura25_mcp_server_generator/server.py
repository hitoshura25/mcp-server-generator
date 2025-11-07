#!/usr/bin/env python3
"""
MCP Server for mcp-server-generator.

This is a meta-server: an MCP server that generates other MCP servers!
"""

import sys
import json
import asyncio
from typing import Any, Dict

from .generator import generate_mcp_server, validate_project_name


class MCPServer:
    """MCP server for mcp-server-generator."""

    def __init__(self):
        self.name = "mcp-server-generator"
        self.version = "1.0.0"

    async def handle_list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "generate_mcp_server",
                    "description": "Generate a complete MCP server project with dual-mode architecture",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Project name (e.g., 'my-mcp-server')"
                            },
                            "description": {
                                "type": "string",
                                "description": "Project description"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author name"
                            },
                            "author_email": {
                                "type": "string",
                                "description": "Author email"
                            },
                            "tools": {
                                "type": "array",
                                "description": "List of tools this MCP server will provide",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "Tool function name"},
                                        "description": {"type": "string", "description": "What the tool does"},
                                        "parameters": {
                                            "type": "array",
                                            "description": "Tool parameters",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {"type": "string"},
                                                    "type": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "required": {"type": "boolean"}
                                                }
                                            }
                                        }
                                    },
                                    "required": ["name", "description"]
                                }
                            },
                            "output_dir": {
                                "type": "string",
                                "description": "Output directory (default: current directory)"
                            },
                            "python_version": {
                                "type": "string",
                                "description": "Python version (default: '3.8')"
                            },
                            "prefix": {
                                "type": "string",
                                "description": "Package prefix: 'AUTO' (detect from git), 'NONE', or custom string (default: 'AUTO')"
                            }
                        },
                        "required": ["project_name", "description", "author", "author_email", "tools"]
                    }
                },
                {
                    "name": "validate_project_name",
                    "description": "Validate a project name for Python package compatibility",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Project name to validate"
                            }
                        },
                        "required": ["name"]
                    }
                }
            ]
        }

    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        try:
            if tool_name == "generate_mcp_server":
                result = generate_mcp_server(**arguments)
                return {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                    "isError": False
                }
            elif tool_name == "validate_project_name":
                is_valid = validate_project_name(arguments["name"])
                result = {
                    "valid": is_valid,
                    "name": arguments["name"]
                }
                return {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                    "isError": False
                }
            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    "isError": True
                }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return await self.handle_list_tools()
        elif method == "tools/call":
            return await self.handle_call_tool(
                params.get("name"),
                params.get("arguments", {})
            )
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def run(self):
        """Run MCP server on stdio."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)

                if "id" in request:
                    response["id"] = request["id"]

                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point."""
    server = MCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
