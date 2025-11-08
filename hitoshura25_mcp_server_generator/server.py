#!/usr/bin/env python3
"""
MCP Server for mcp-server-generator.

This is a meta-server: an MCP server that generates other MCP servers!
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from . import generator

# Initialize FastMCP server
mcp = FastMCP("mcp-server-generator")


@mcp.tool()
def generate_mcp_server(
    project_name: str,
    description: str,
    author: str,
    author_email: str,
    tools: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    python_version: str = "3.10",
    prefix: str = "AUTO",
) -> str:
    """Generate a complete MCP server project with dual-mode architecture

    Args:
        project_name: Project name (e.g., 'my-mcp-server')
        description: Project description
        author: Author name
        author_email: Author email
        tools: List of tools this MCP server will provide. Each tool should have:
               - name: Tool function name
               - description: What the tool does
               - parameters: List of parameter objects with name, type, description, required
        output_dir: Output directory (default: current directory)
        python_version: Python version for testing (default: '3.10')
        prefix: Package prefix - 'AUTO' (detect from git), 'NONE', or custom string (default: 'AUTO')

    Returns:
        JSON string with generation result including success status and project path
    """
    result = generator.generate_mcp_server(
        project_name=project_name,
        description=description,
        author=author,
        author_email=author_email,
        tools=tools,
        output_dir=output_dir,
        python_version=python_version,
        prefix=prefix,
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def validate_project_name(name: str) -> str:
    """Validate a project name for Python package compatibility

    Args:
        name: Project name to validate

    Returns:
        JSON string with validation result
    """
    is_valid = generator.validate_project_name(name)
    result = {
        "valid": is_valid,
        "name": name
    }
    return json.dumps(result, indent=2)


def main():
    """Main entry point for MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
