#!/usr/bin/env python3
"""
MCP Server for mcp-server-generator.

This is a meta-server: an MCP server that generates other MCP servers!

Implements progressive disclosure pattern for efficient context usage:
- search_tools: Find relevant tools by query
- get_tool_info: Get tool details at different granularity levels
"""

import json
from typing import Any, Dict, List, Optional, Literal

from mcp.server.fastmcp import FastMCP

from . import generator

# Initialize FastMCP server
mcp = FastMCP("mcp-server-generator")

# Tool definitions for progressive disclosure
TOOL_CATALOG = {
    "search_tools": {
        "name": "search_tools",
        "category": "discovery",
        "description": "Search for relevant tools by query with progressive disclosure",
        "use_cases": [
            "Finding tools without loading full schemas",
            "Context-efficient tool discovery",
            "Searching by keywords, categories, or use cases",
        ],
        "full_description": """Search for tools using progressive disclosure pattern.

This tool allows you to discover available tools without loading all schemas upfront,
saving context window space. Supports three detail levels:
- "name": Just tool names (most efficient)
- "summary": Names + descriptions + categories
- "full": Complete information including use cases and detailed descriptions

Search matches against tool names, descriptions, categories, and use cases.""",
    },
    "get_tool_info": {
        "name": "get_tool_info",
        "category": "discovery",
        "description": "Get information about a specific tool with configurable detail levels",
        "use_cases": [
            "Learning about a specific tool",
            "Getting tool details at different granularity levels",
            "Understanding tool capabilities before use",
        ],
        "full_description": """Get detailed information about a specific tool with progressive disclosure.

Supports two detail levels:
- "summary": Name, description, and category
- "full": Complete information including use cases and full description

This allows you to get exactly the level of detail you need without loading
unnecessary information into your context window.""",
    },
    "generate_mcp_server": {
        "name": "generate_mcp_server",
        "category": "generation",
        "description": "Generate a complete MCP server project with dual-mode architecture",
        "use_cases": [
            "Creating new MCP servers from scratch",
            "Scaffolding dual-mode tools (MCP + CLI)",
            "Setting up production-ready server projects",
        ],
        "full_description": """Generate a complete, production-ready MCP server project with dual-mode architecture.

This tool creates a full project structure including:
- MCP server implementation with async support
- CLI interface for development
- Comprehensive test suite
- Documentation (README, MCP-USAGE)
- GitHub Actions workflows for PyPI publishing
- Package configuration (setup.py, pyproject.toml)

The generated server follows MCP best practices and is ready to publish to PyPI.""",
    },
    "validate_project_name": {
        "name": "validate_project_name",
        "category": "validation",
        "description": "Validate a project name for Python package compatibility",
        "use_cases": [
            "Checking if a project name is valid before generation",
            "Avoiding Python keyword conflicts",
            "Ensuring PyPI compatibility",
        ],
        "full_description": """Validate a project name to ensure it's compatible with Python packaging standards.

Checks for:
- Valid Python identifier (lowercase alphanumeric with hyphens/underscores)
- Not a Python keyword
- PyPI naming conventions""",
    },
    "generate_claude_command": {
        "name": "generate_claude_command",
        "category": "generation",
        "description": "Generate Claude Code command files (.claude/commands/*.md) for guiding MCP development",
        "use_cases": [
            "Creating slash commands for Claude Code",
            "Setting up project-specific development workflows",
            "Providing guided MCP implementation assistance",
        ],
        "full_description": """Generate Claude Code command files that guide users through MCP server development.

Creates .claude/commands/ directory with slash command files that:
- Guide through MCP server generation workflow
- Provide best practices and implementation tips
- Include context-aware development assistance
- Follow progressive disclosure patterns""",
    },
    "get_best_practices": {
        "name": "get_best_practices",
        "category": "guidance",
        "description": "Get MCP server development best practices and recommendations",
        "use_cases": [
            "Learning MCP best practices",
            "Understanding progressive disclosure",
            "Optimizing tool design",
        ],
        "full_description": """Retrieve comprehensive best practices for MCP server development.

Covers:
- Progressive disclosure strategies
- Context-efficient tool design
- Control flow optimization
- Privacy and security considerations
- State management and skills
- Testing strategies""",
    },
    "get_implementation_guide": {
        "name": "get_implementation_guide",
        "category": "guidance",
        "description": "Get step-by-step guide for implementing MCP servers",
        "use_cases": [
            "Planning MCP server implementation",
            "Understanding implementation workflow",
            "Getting started with generated projects",
        ],
        "full_description": """Get a comprehensive step-by-step guide for implementing MCP servers.

Includes:
- Project setup and initialization
- Tool implementation patterns
- Testing strategies
- Deployment and publishing
- Integration with Claude Desktop""",
    },
}


@mcp.tool()
def search_tools(
    query: str, detail_level: Literal["name", "summary", "full"] = "summary"
) -> str:
    """Search for relevant tools by query with progressive disclosure

    This tool implements the progressive disclosure pattern - allowing you to
    discover tools without loading full schemas upfront, saving context window space.

    Args:
        query: Search query (matches against name, description, categories, use cases)
        detail_level: Level of detail to return:
            - "name": Just tool names (most context-efficient)
            - "summary": Names + descriptions + categories
            - "full": Complete information including use cases and detailed descriptions

    Returns:
        JSON string with matching tools at requested detail level
    """
    query_lower = query.lower()
    matches = []

    for tool_id, tool_info in TOOL_CATALOG.items():
        # Search in name, description, category, and use cases
        searchable = (
            f"{tool_info['name']} {tool_info['description']} "
            f"{tool_info['category']} {' '.join(tool_info['use_cases'])}"
        ).lower()

        if query_lower in searchable:
            if detail_level == "name":
                matches.append(tool_info["name"])
            elif detail_level == "summary":
                matches.append(
                    {
                        "name": tool_info["name"],
                        "description": tool_info["description"],
                        "category": tool_info["category"],
                    }
                )
            else:  # full
                matches.append(tool_info)

    result = {
        "query": query,
        "detail_level": detail_level,
        "matches": matches,
        "count": len(matches),
    }

    return json.dumps(result, indent=2)


@mcp.tool()
def get_tool_info(
    tool_name: str, detail_level: Literal["summary", "full"] = "summary"
) -> str:
    """Get information about a specific tool with progressive disclosure

    Args:
        tool_name: Name of the tool to get information about
        detail_level: Level of detail:
            - "summary": Name, description, and category
            - "full": Complete information including use cases and full description

    Returns:
        JSON string with tool information at requested detail level
    """
    if tool_name not in TOOL_CATALOG:
        return json.dumps(
            {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(TOOL_CATALOG.keys()),
            },
            indent=2,
        )

    tool_info = TOOL_CATALOG[tool_name]

    if detail_level == "summary":
        result = {
            "name": tool_info["name"],
            "description": tool_info["description"],
            "category": tool_info["category"],
        }
    else:  # full
        result = tool_info

    return json.dumps(result, indent=2)


@mcp.tool()
def get_best_practices(topic: Optional[str] = None) -> str:
    """Get MCP server development best practices

    Args:
        topic: Optional specific topic (e.g., "progressive_disclosure", "tool_design",
               "control_flow", "security", "state_management", "testing").
               If None, returns all best practices.

    Returns:
        JSON string with best practices information
    """
    best_practices = {
        "progressive_disclosure": {
            "title": "Progressive Disclosure",
            "summary": "Present tools as discoverable rather than loading all definitions upfront",
            "principles": [
                "Implement search_tools capability to find relevant services by query",
                "Include detail-level parameters (name only, name+description, full schema)",
                "Let agents read tool definitions on-demand instead of upfront",
                "Models are great at navigating filesystem-like structures",
            ],
            "benefits": [
                "Reduces initial context window usage",
                "Enables scaling to hundreds or thousands of tools",
                "Improves agent efficiency in tool discovery",
            ],
        },
        "tool_design": {
            "title": "Context-Efficient Tool Design",
            "summary": "Filter and transform data before returning to the model",
            "principles": [
                "Process data in the execution environment before returning results",
                "Apply aggregations, joins, and filtering client-side",
                "Return only relevant data to the model",
                "Avoid passing large datasets through context window",
            ],
            "example": "Process a 10,000-row spreadsheet locally, return only the 5 rows matching criteria",
        },
        "control_flow": {
            "title": "Control Flow Optimization",
            "summary": "Implement logic in code rather than chaining tool calls",
            "principles": [
                "Use loops, conditionals, and error handling in tool implementations",
                "Reduce latency by handling logic in execution environment",
                "Avoid alternating between tool calls and model reasoning for repetitive tasks",
            ],
            "benefits": [
                "More efficient than sequential tool calls",
                "Lower latency",
                "Reduced token usage",
            ],
        },
        "security": {
            "title": "Privacy and Security",
            "summary": "Keep sensitive data in execution environment by default",
            "principles": [
                "Only explicit logs/returns should reach the model",
                "Implement automatic PII tokenization",
                "Define deterministic security rules for data flow",
                "Use secure sandboxing for code execution",
            ],
        },
        "state_management": {
            "title": "State Persistence and Skills",
            "summary": "Enable resumable workflows and reusable capabilities",
            "principles": [
                "Allow agents to write intermediate results to files",
                "Support persisting reusable functions as 'skills'",
                "Include documentation (e.g., SKILL.md) with skills",
                "Build evolving toolboxes of higher-level capabilities",
            ],
        },
        "testing": {
            "title": "Testing and Validation",
            "summary": "Ensure reliability through comprehensive testing",
            "principles": [
                "Test both MCP protocol compliance and business logic",
                "Include async/await test coverage",
                "Validate tool schemas and parameter handling",
                "Test error cases and edge conditions",
            ],
        },
    }

    if topic:
        if topic in best_practices:
            result = {"topic": topic, "practice": best_practices[topic]}
        else:
            result = {
                "error": f"Topic '{topic}' not found",
                "available_topics": list(best_practices.keys()),
            }
    else:
        result = {"best_practices": best_practices, "count": len(best_practices)}

    return json.dumps(result, indent=2)


@mcp.tool()
def get_implementation_guide(step: Optional[str] = None) -> str:
    """Get step-by-step guide for implementing MCP servers

    Args:
        step: Optional specific step (e.g., "setup", "implementation", "testing",
              "deployment", "integration"). If None, returns overview of all steps.

    Returns:
        JSON string with implementation guide
    """
    guide = {
        "overview": {
            "title": "MCP Server Implementation Overview",
            "description": "Complete workflow for building and deploying MCP servers",
            "steps": [
                "setup",
                "implementation",
                "testing",
                "deployment",
                "integration",
            ],
        },
        "setup": {
            "title": "Project Setup",
            "description": "Initialize your MCP server project",
            "steps": [
                "Use generate_mcp_server tool to create project structure",
                "Review generated files and documentation",
                "Install dependencies: pip install -e .",
                "Verify project structure and configuration",
            ],
            "files_created": [
                "server.py (MCP server implementation)",
                "cli.py (CLI interface)",
                "generator.py (business logic with TODO stubs)",
                "tests/ (comprehensive test suite)",
                "README.md and MCP-USAGE.md",
                ".github/workflows/ (CI/CD pipelines)",
            ],
        },
        "implementation": {
            "title": "Tool Implementation",
            "description": "Implement your MCP server tools",
            "steps": [
                "Locate TODO stubs in generator.py",
                "Implement business logic for each tool",
                "Follow async/await patterns for I/O operations",
                "Add proper error handling and validation",
                "Update docstrings with implementation details",
            ],
            "best_practices": [
                "Keep tool functions focused and single-purpose",
                "Filter data before returning to model",
                "Implement control flow in code, not through tool chaining",
                "Add logging for debugging",
            ],
        },
        "testing": {
            "title": "Testing Your Server",
            "description": "Validate functionality and reliability",
            "steps": [
                "Run test suite: pytest",
                "Check coverage: pytest --cov",
                "Test MCP protocol compliance",
                "Test business logic and edge cases",
                "Test with Claude Desktop integration",
            ],
            "commands": [
                "pytest (run all tests)",
                "pytest -v (verbose output)",
                "pytest --cov=<package> --cov-report=term-missing",
            ],
        },
        "deployment": {
            "title": "Deployment and Publishing",
            "description": "Publish your MCP server to PyPI",
            "steps": [
                "Ensure all tests pass",
                "Update version in setup.py",
                "Create GitHub release tag",
                "GitHub Actions will automatically publish to PyPI",
                "Verify package on PyPI",
            ],
            "requirements": [
                "GitHub repository with code",
                "PyPI account and API token",
                "PYPI_API_TOKEN secret configured in GitHub",
            ],
        },
        "integration": {
            "title": "Claude Desktop Integration",
            "description": "Configure your server with Claude Desktop",
            "steps": [
                "Install using uvx (recommended): uvx <package-name>",
                "Or install with pipx: pipx install <package-name>",
                "Configure in Claude Desktop config JSON",
                "Restart Claude Desktop",
                "Test tools in Claude chat",
            ],
            "config_example": {
                "mcpServers": {
                    "your-server": {
                        "command": "uvx",
                        "args": ["your-package-name"],
                    }
                }
            },
        },
    }

    if step:
        if step in guide:
            result = {"step": step, "guide": guide[step]}
        else:
            result = {
                "error": f"Step '{step}' not found",
                "available_steps": [k for k in guide.keys() if k != "overview"],
            }
    else:
        result = guide

    return json.dumps(result, indent=2)


@mcp.tool()
def generate_claude_command(
    command_name: str,
    command_type: Literal[
        "mcp_generator", "best_practices", "implementation_helper", "custom"
    ] = "mcp_generator",
    description: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    output_dir: str = ".claude/commands",
) -> str:
    """Generate Claude Code command files for guided MCP development

    Creates .claude/commands/ directory with slash command files that guide
    users through MCP server development using this generator.

    Args:
        command_name: Name for the command (e.g., "mcp-generate", "mcp-help")
        command_type: Type of command to generate:
            - "mcp_generator": Guide through MCP server generation workflow
            - "best_practices": Provide MCP best practices reference
            - "implementation_helper": Help implement generated MCP server
            - "custom": Use custom_prompt for fully custom command
        description: Optional description for the command (auto-generated if not provided)
        custom_prompt: Required if command_type is "custom"
        output_dir: Directory to create command file (default: .claude/commands)

    Returns:
        JSON string with generation result
    """
    from pathlib import Path

    # Validate inputs
    if command_type == "custom" and not custom_prompt:
        return json.dumps(
            {
                "success": False,
                "error": "custom_prompt is required when command_type is 'custom'",
            },
            indent=2,
        )

    # Command templates
    templates = {
        "mcp_generator": {
            "description": "Generate a new MCP server with guided workflow",
            "prompt": """You are helping the user generate a new MCP (Model Context Protocol) server using the mcp-server-generator.

Follow this guided workflow:

1. **Understand the Goal**
   - Ask the user what functionality they want their MCP server to provide
   - Clarify the tools/capabilities the server should offer
   - Discuss use cases and target users

2. **Gather Project Information**
   - Project name (lowercase, hyphen-separated)
   - Description (clear, concise purpose statement)
   - Author name and email
   - Desired prefix (AUTO for git username, NONE, or custom)

3. **Define Tools**
   For each tool the server will provide:
   - Tool name (valid Python identifier)
   - Description (what it does)
   - Parameters (name, type, description, required)

   Use the search_tools function to check if similar tools exist for reference.

4. **Validate and Generate**
   - Use validate_project_name to check the project name
   - Use get_best_practices topic="tool_design" for design guidance
   - Call generate_mcp_server with all collected information

5. **Next Steps Guidance**
   After generation, use get_implementation_guide to show the user:
   - How to implement the TODO stubs
   - How to run tests
   - How to deploy to PyPI
   - How to integrate with Claude Desktop

Remember to follow progressive disclosure - don't overwhelm the user with all options at once.
Ask questions incrementally and provide guidance at each step.
""",
        },
        "best_practices": {
            "description": "Get MCP server development best practices and guidance",
            "prompt": """You are providing MCP server development best practices and guidance.

Use the available tools to help the user:

1. **Discover Best Practices**
   - Use get_best_practices() to show all available topics
   - Use get_best_practices(topic="...") for specific guidance
   - Explain practices in context of the user's questions

2. **Key Topics to Cover**
   - Progressive disclosure for scalable tool design
   - Context-efficient tool results
   - Control flow optimization
   - Security and privacy considerations
   - State management and skills
   - Testing strategies

3. **Practical Application**
   - Relate best practices to the user's specific MCP server
   - Provide examples and code snippets
   - Suggest improvements to existing implementations

4. **Implementation Guidance**
   - Use get_implementation_guide() for step-by-step workflows
   - Help troubleshoot common issues
   - Guide through testing and deployment

Focus on practical, actionable advice that improves the user's MCP server implementation.
""",
        },
        "implementation_helper": {
            "description": "Help implement and improve generated MCP servers",
            "prompt": """You are helping the user implement their generated MCP server.

Your role:

1. **Implementation Assistance**
   - Help implement TODO stubs in generator.py
   - Suggest async/await patterns for I/O operations
   - Review tool implementations for best practices
   - Add proper error handling and validation

2. **Use Available Guidance**
   - Use get_best_practices() for design patterns
   - Use get_implementation_guide() for workflow steps
   - Use search_tools() to find relevant examples

3. **Testing Support**
   - Help write and run tests
   - Explain test failures and fixes
   - Guide pytest and coverage usage
   - Test MCP protocol compliance

4. **Optimization**
   - Identify opportunities for progressive disclosure
   - Suggest context-efficient data filtering
   - Recommend control flow improvements
   - Review security and privacy considerations

5. **Deployment Help**
   - Guide through PyPI publishing
   - Help configure GitHub Actions
   - Assist with Claude Desktop integration
   - Troubleshoot installation issues

Be proactive in suggesting improvements based on MCP best practices.
Focus on making the server production-ready, well-tested, and efficient.
""",
        },
    }

    # Select template or use custom
    if command_type == "custom":
        prompt = custom_prompt
        if not description:
            description = f"Custom Claude Code command: {command_name}"
    else:
        template = templates[command_type]
        prompt = template["prompt"]
        if not description:
            description = template["description"]

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create command file
    command_file = output_path / f"{command_name}.md"

    # Command file content with frontmatter
    content = f"""---
description: {description}
---

{prompt}
"""

    try:
        command_file.write_text(content, encoding="utf-8")

        result = {
            "success": True,
            "command_name": command_name,
            "command_type": command_type,
            "file_path": str(command_file),
            "usage": f"/{command_name}",
            "description": description,
            "message": f"Successfully created command file: {command_file}",
        }
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "message": f"Failed to create command file: {e}",
        }

    return json.dumps(result, indent=2)


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

    This is the main generation tool. Consider using search_tools or get_tool_info
    first to understand the full workflow, or use the generated Claude commands
    for guided assistance.

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
    result = {"valid": is_valid, "name": name}
    return json.dumps(result, indent=2)


def main():
    """Main entry point for MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
