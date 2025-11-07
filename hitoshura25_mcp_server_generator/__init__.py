"""
MCP Server Generator

A meta-generator for creating dual-mode MCP servers with best practices.
"""

__version__ = "0.1.0"
__author__ = "Vinayak Menon"
__license__ = "Apache-2.0"

from .generator import (
    generate_mcp_server,
    validate_project_name,
    validate_tool_name,
    generate_tool_schema,
    sanitize_description,
)

__all__ = [
    'generate_mcp_server',
    'validate_project_name',
    'validate_tool_name',
    'generate_tool_schema',
    'sanitize_description',
]
