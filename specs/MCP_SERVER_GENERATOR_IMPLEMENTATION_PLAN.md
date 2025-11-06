# MCP Server Generator - Implementation Plan v2.0
## A Meta-Generator for Creating Dual-Mode MCP Servers

**Project**: `mcp-server-generator`
**Purpose**: Generate production-ready MCP servers with dual-mode architecture (MCP protocol + CLI)
**Status**: Ready to implement
**Created**: 2025-11-03
**Based on**: pypi-workflow-generator v0.2.11 (validated reference implementation)

---

## Executive Summary

Build a template-based generator that creates complete MCP server projects following the validated dual-mode architecture pattern from pypi-workflow-generator. This tool will itself be an MCP server, enabling AI agents to generate other MCP servers.

### Key Innovation
This is a **meta-generator**: an MCP server that generates MCP servers, demonstrating and validating the pattern it creates.

### What Makes This Plan Different
- ✅ Based on **actual implementation** of pypi-workflow-generator (not assumptions)
- ✅ Uses **real MCP protocol patterns** from working code
- ✅ Includes **validated template loading** mechanisms
- ✅ Reflects **actual dependency requirements** (Jinja2>=3.0 only)
- ✅ Shows **realistic time estimates** based on proven reference
- ✅ Addresses **real-world challenges** discovered during pypi-workflow-generator development

---

## Table of Contents

1. [Reference Implementation Analysis](#reference-implementation-analysis)
2. [Project Goals](#project-goals)
3. [Architecture Overview](#architecture-overview)
4. [What Gets Generated](#what-gets-generated)
5. [Implementation Phases](#implementation-phases)
6. [Template Structure](#template-structure)
7. [Testing Strategy](#testing-strategy)
8. [Documentation Plan](#documentation-plan)
9. [Security Considerations](#security-considerations)
10. [Timeline & Resources](#timeline--resources)

---

## Reference Implementation Analysis

### pypi-workflow-generator: Our Proven Foundation

**Published Package**: https://pypi.org/project/pypi-workflow-generator/ (v0.2.11)
**Repository**: https://github.com/hitoshura25/pypi-workflow-generator
**Author**: Vinayak Menon
**Status**: Production-ready, Alpha release

### Validated Architecture Pattern

```
pypi_workflow_generator/
├── __init__.py              # Public API exports
├── generator.py             # Core business logic (shared by all modes)
├── server.py                # MCP stdio server
├── main.py                  # CLI: workflow generation
├── init.py                  # CLI: project initialization
├── create_release.py        # CLI: release management
├── *.j2                     # Jinja2 templates (4 files)
└── tests/
    ├── test_generator.py    # Core logic tests
    ├── test_init.py         # Init tests
    └── test_server.py       # MCP protocol tests
```

### Key Implementation Insights

**1. MCP Protocol Implementation** (from server.py):
```python
class MCPServer:
    def __init__(self):
        self.name = "pypi-workflow-generator"
        self.version = "1.0.0"

    async def handle_list_tools(self) -> Dict[str, Any]:
        """Return tool schemas with full inputSchema definitions."""
        return {"tools": [...]}

    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Execute tool and return standardized response."""
        try:
            # Call actual implementation from generator.py
            result = function_from_generator(**arguments)
            return {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    async def handle_request(self, request: Dict[str, Any]):
        """Route JSON-RPC requests."""
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
        """Stdio communication loop."""
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
```

**2. Template Loading Pattern** (from generator.py):
```python
import os
from jinja2 import Environment, FileSystemLoader

def generate_workflow(...):
    # Get template directory relative to this module
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(script_dir))
    template = env.get_template('template_name.j2')

    # Render with context
    content = template.render(**context)

    # Write to output
    output_dir = base_output_dir or os.path.join(os.getcwd(), '.github', 'workflows')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w') as f:
        f.write(content)

    return {
        'success': True,
        'file_path': output_path,
        'message': f"Successfully generated {output_filename}"
    }
```

**3. Entry Points Configuration** (from setup.py):
```python
entry_points={
    'console_scripts': [
        'mcp-pypi-workflow-generator=pypi_workflow_generator.server:main',
        'pypi-workflow-generator=pypi_workflow_generator.main:main',
        'pypi-workflow-generator-init=pypi_workflow_generator.init:main',
        'pypi-release=pypi_workflow_generator.create_release:main',
    ],
}
```

**4. Package Manifest** (MANIFEST.in):
```
include README.md
include LICENSE
include requirements.txt
recursive-include pypi_workflow_generator *.j2
exclude *_PLAN.md
global-exclude .DS_Store
global-exclude __pycache__
```

**5. Minimal Dependencies**:
- `Jinja2>=3.0` (only required dependency)
- Python >=3.8

### Critical Learnings

✅ **What Works Well**:
1. **Simple stdio protocol**: JSON-RPC over stdin/stdout is sufficient
2. **Template co-location**: Store .j2 files alongside Python code
3. **Shared core logic**: generator.py provides reusable functions for all entry points
4. **Minimal dependencies**: Only Jinja2 required (no click, cookiecutter, etc.)
5. **Standard return format**: All functions return `{success, file_path/message}`
6. **FileSystemLoader is sufficient**: No need for PackageLoader complexity

⚠️ **What to Avoid**:
1. **Over-engineering protocol**: Basic JSON-RPC is enough
2. **Complex template discovery**: Simple `__file__` relative paths work
3. **Heavy dependencies**: Keep it minimal
4. **Different return formats**: Standardize on dict with success/message

---

## Project Goals

### Primary Goals

1. **Accelerate MCP Server Development**
   - Reduce setup from hours to < 5 minutes
   - Eliminate boilerplate duplication
   - Enforce validated best practices

2. **Standardize Architecture**
   - Consistent dual-mode pattern
   - Shared testing patterns
   - Common documentation structure

3. **Demonstrate the Pattern**
   - Self-hosting (generator is itself an MCP server)
   - Can be used by AI agents
   - Validates the architecture it creates

### Success Criteria

✅ Generate working MCP server in < 5 minutes
✅ Generated servers pass all tests
✅ Both MCP and CLI modes work
✅ Documentation is complete
✅ AI agents can use it to create servers
✅ Dogfoods itself (uses its own templates)

---

## Architecture Overview

### mcp-server-generator Structure

```
mcp-server-generator/
├── .gitignore
├── README.md
├── MCP-USAGE.md
├── LICENSE (Apache-2.0)
├── pyproject.toml
├── setup.py
├── requirements.txt
├── MANIFEST.in
│
├── mcp_server_generator/
│   ├── __init__.py           # Public API
│   ├── generator.py          # Core generation logic
│   ├── server.py             # MCP server mode
│   ├── cli.py                # CLI mode
│   │
│   ├── templates/            # Jinja2 templates
│   │   └── python/           # Python MCP server templates
│   │       ├── __init__.py.j2
│   │       ├── server.py.j2
│   │       ├── cli.py.j2
│   │       ├── generator.py.j2
│   │       ├── setup.py.j2
│   │       ├── pyproject.toml.j2
│   │       ├── README.md.j2
│   │       ├── MCP-USAGE.md.j2
│   │       ├── requirements.txt.j2
│   │       ├── MANIFEST.in.j2
│   │       ├── .gitignore.j2
│   │       ├── LICENSE.j2
│   │       └── tests/
│   │           ├── test_server.py.j2
│   │           └── test_generator.py.j2
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_generator.py
│       ├── test_server.py
│       └── test_cli.py
│
└── .github/
    └── workflows/
        └── pypi-publish.yml
```

### Dual-Mode Operation

**MCP Mode** (for AI agents):
```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "mcp-server-generator"
    }
  }
}
```

**CLI Mode** (for developers):
```bash
# Interactive mode (recommended for first-time users)
mcp-server-generator --interactive

# Command-line mode
mcp-server-generator \
  --project-name my-mcp-tool \
  --description "Does something useful" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

---

## What Gets Generated

### Generated Project Structure

```
my-mcp-tool/
├── .gitignore
├── README.md
├── MCP-USAGE.md
├── LICENSE
├── pyproject.toml
├── setup.py
├── requirements.txt
├── MANIFEST.in
│
├── my_mcp_tool/
│   ├── __init__.py
│   ├── server.py          # MCP stdio server
│   ├── cli.py             # CLI interface
│   ├── generator.py       # Core business logic (TODO stubs)
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_server.py
│       └── test_generator.py
│
└── .github/
    └── workflows/
        └── pypi-publish.yml  # Generated via pypi-workflow-generator
```

### Generated Features

✅ **Working MCP Server** - Responds to tools/list and tools/call
✅ **CLI Mode** - Standard argparse-based CLI
✅ **Proper Packaging** - Installable via pip
✅ **GitHub Actions Workflow** - CI/CD for PyPI publishing (via pypi-workflow-generator)
✅ **Complete Tests** - MCP protocol and core logic tests
✅ **Documentation** - README, MCP usage guide
✅ **Type Hints** - Full type annotations
✅ **TODO Stubs** - Placeholder implementations for tools

### Example: Generated server.py

```python
#!/usr/bin/env python3
"""MCP Server for my-mcp-tool."""

import sys
import json
import asyncio
from typing import Any, Dict

from .generator import my_function  # Generated based on tools


class MCPServer:
    """MCP server for my-mcp-tool."""

    def __init__(self):
        self.name = "my-mcp-tool"
        self.version = "1.0.0"

    async def handle_list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "my_function",
                    "description": "Does something",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string", "description": "First param"}
                        },
                        "required": ["param1"]
                    }
                }
            ]
        }

    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Execute a tool."""
        try:
            if tool_name == "my_function":
                result = my_function(**arguments)
                return {
                    "content": [{"type": "text", "text": str(result)}],
                    "isError": False
                }

            return {
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    async def handle_request(self, request: Dict[str, Any]):
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
```

---

## Implementation Phases

### Phase 1: Project Setup & Core Generator (6-8 hours)

**Goal**: Create the basic project structure and core generation logic.

#### 1.1 Project Initialization

**Create base structure**:
```bash
mcp-server-generator/
├── .gitignore
├── README.md
├── LICENSE
├── pyproject.toml
├── setup.py
├── requirements.txt
├── MANIFEST.in
└── mcp_server_generator/
    └── __init__.py
```

**pyproject.toml**:
```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
version_scheme = "post-release"

[project]
name = "mcp-server-generator"
description = "Generate dual-mode MCP servers with best practices"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "Apache-2.0"}
authors = [
    {name = "Vinayak Menon", email = "vinayakmenon+pypi@users.noreply.github.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "Jinja2>=3.0",
    "pypi-workflow-generator>=0.2.0",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/mcp-server-generator"
Repository = "https://github.com/YOUR_USERNAME/mcp-server-generator"
Issues = "https://github.com/YOUR_USERNAME/mcp-server-generator/issues"
```

**setup.py**:
```python
from setuptools import setup, find_packages
import os


def local_scheme(version):
    if os.environ.get("IS_PULL_REQUEST"):
        return f".dev{os.environ.get('GITHUB_RUN_ID', 'local')}"
    return ""


try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""


setup(
    name='mcp-server-generator',
    author='Vinayak Menon',
    author_email='vinayakmenon+pypi@users.noreply.github.com',
    description='Generate dual-mode MCP servers with best practices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/YOUR_USERNAME/mcp-server-generator',
    use_scm_version={"local_scheme": local_scheme},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Jinja2>=3.0',
        'pypi-workflow-generator>=0.2.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        'console_scripts': [
            'mcp-server-generator=mcp_server_generator.server:main',
            'mcp-server-generator-cli=mcp_server_generator.cli:main',
        ],
    },
)
```

**MANIFEST.in**:
```
include README.md
include LICENSE
include requirements.txt
recursive-include mcp_server_generator *.j2
exclude *_PLAN.md
global-exclude .DS_Store
global-exclude __pycache__
global-exclude *.pyc
global-exclude *.pyo
```

**requirements.txt**:
```
Jinja2>=3.0
pypi-workflow-generator>=0.2.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

#### 1.2 Core Generator Implementation

**File**: `mcp_server_generator/__init__.py`
```python
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
    generate_tool_schema,
)

__all__ = [
    'generate_mcp_server',
    'validate_project_name',
    'generate_tool_schema',
]
```

**File**: `mcp_server_generator/generator.py`
```python
"""
Core MCP server generation logic.
"""

import os
import keyword
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def validate_project_name(name: str) -> bool:
    """
    Validate Python package name.

    Args:
        name: Project name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False

    # Convert to package name (hyphens to underscores)
    package_name = name.replace('-', '_')

    # Check valid Python identifier
    if not package_name.isidentifier():
        return False

    # Check not a keyword
    if keyword.iskeyword(package_name):
        return False

    return True


def validate_tool_name(name: str) -> bool:
    """
    Validate tool/function name.

    Args:
        name: Tool name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False

    # Must be valid Python identifier
    if not name.isidentifier():
        return False

    # Cannot be a keyword
    if keyword.iskeyword(name):
        return False

    return True


def generate_tool_schema(tool_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate MCP tool schema from simplified definition.

    Args:
        tool_definition: {
            "name": "my_tool",
            "description": "Does something",
            "parameters": [
                {
                    "name": "param1",
                    "type": "string",
                    "description": "First parameter",
                    "required": True
                }
            ]
        }

    Returns:
        Full MCP tool schema with inputSchema
    """
    # Map JSON Schema types to ensure compatibility
    TYPE_MAPPING = {
        'string': 'string',
        'str': 'string',
        'number': 'number',
        'int': 'number',
        'integer': 'number',
        'float': 'number',
        'boolean': 'boolean',
        'bool': 'boolean',
        'array': 'array',
        'list': 'array',
        'object': 'object',
        'dict': 'object',
    }

    schema = {
        "name": tool_definition["name"],
        "description": tool_definition.get("description", ""),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    for param in tool_definition.get("parameters", []):
        param_type = TYPE_MAPPING.get(param["type"].lower(), "string")

        schema["inputSchema"]["properties"][param["name"]] = {
            "type": param_type,
            "description": param.get("description", "")
        }

        if param.get("required", False):
            schema["inputSchema"]["required"].append(param["name"])

    return schema


def sanitize_description(text: str) -> str:
    """
    Sanitize user input for use in templates.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Remove any potential template injection characters
    # but keep it readable for documentation
    return text.replace('{', '{{').replace('}', '}}')


def generate_mcp_server(
    project_name: str,
    description: str,
    author: str,
    author_email: str,
    tools: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    python_version: str = "3.8",
    license_type: str = "Apache-2.0",
) -> Dict[str, Any]:
    """
    Generate a complete MCP server project.

    Args:
        project_name: Project name (e.g., "my-mcp-server")
        description: Project description
        author: Author name
        author_email: Author email
        tools: List of tool definitions
        output_dir: Where to create project (default: current directory)
        python_version: Python version for testing (default: "3.8")
        license_type: License type (default: "Apache-2.0")

    Returns:
        {
            "success": bool,
            "project_path": str,
            "files_created": List[str],
            "message": str
        }
    """
    # Validate inputs
    if not validate_project_name(project_name):
        raise ValueError(
            f"Invalid project name: '{project_name}'. "
            "Must be lowercase alphanumeric with hyphens/underscores, "
            "and not a Python keyword."
        )

    # Validate tool names
    for tool in tools:
        if not validate_tool_name(tool["name"]):
            raise ValueError(
                f"Invalid tool name: '{tool['name']}'. "
                "Must be a valid Python identifier and not a keyword."
            )

    if not tools:
        raise ValueError("At least one tool must be defined.")

    # Convert project name to package name
    package_name = project_name.replace('-', '_')

    # Determine output directory
    if output_dir is None:
        output_dir = os.getcwd()

    project_path = os.path.join(output_dir, project_name)

    # Check if directory exists
    if os.path.exists(project_path):
        raise FileExistsError(f"Directory already exists: {project_path}")

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates', 'python')

    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Templates not found at {template_dir}")

    # Prepare template context
    context = {
        'project_name': project_name,
        'package_name': package_name,
        'description': sanitize_description(description),
        'author': author,
        'author_email': author_email,
        'python_version': python_version,
        'license': license_type,
        'tools': tools,
        'tool_schemas': [generate_tool_schema(tool) for tool in tools],
        'year': '2025',
    }

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Files to generate
    files_to_generate = [
        # Root files
        ('README.md.j2', 'README.md'),
        ('MCP-USAGE.md.j2', 'MCP-USAGE.md'),
        ('LICENSE.j2', 'LICENSE'),
        ('setup.py.j2', 'setup.py'),
        ('pyproject.toml.j2', 'pyproject.toml'),
        ('requirements.txt.j2', 'requirements.txt'),
        ('MANIFEST.in.j2', 'MANIFEST.in'),
        ('.gitignore.j2', '.gitignore'),

        # Package files
        ('__init__.py.j2', f'{package_name}/__init__.py'),
        ('server.py.j2', f'{package_name}/server.py'),
        ('cli.py.j2', f'{package_name}/cli.py'),
        ('generator.py.j2', f'{package_name}/generator.py'),

        # Tests
        ('tests/__init__.py.j2', f'{package_name}/tests/__init__.py'),
        ('tests/test_server.py.j2', f'{package_name}/tests/test_server.py'),
        ('tests/test_generator.py.j2', f'{package_name}/tests/test_generator.py'),
    ]

    files_created = []

    # Generate files
    for template_file, output_file in files_to_generate:
        try:
            template = env.get_template(template_file)
            content = template.render(**context)

            output_path = os.path.join(project_path, output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            files_created.append(output_file)
        except Exception as e:
            raise RuntimeError(f"Failed to generate {output_file}: {str(e)}")

    # Generate GitHub Actions workflow (required)
    try:
        from pypi_workflow_generator import generate_workflow

        # Change to project directory
        original_dir = os.getcwd()
        os.chdir(project_path)

        try:
            workflow_result = generate_workflow(
                python_version=python_version,
                output_filename='pypi-publish.yml',
                test_path=package_name,
            )

            if workflow_result['success']:
                files_created.append('.github/workflows/pypi-publish.yml')
        finally:
            os.chdir(original_dir)

    except ImportError:
        raise ImportError(
            "pypi-workflow-generator is required but not installed. "
            "Install with: pip install pypi-workflow-generator"
        )

    return {
        'success': True,
        'project_path': project_path,
        'files_created': files_created,
        'message': f"Successfully generated MCP server project at {project_path}"
    }
```

#### 1.3 Success Criteria for Phase 1

- [ ] Project structure created
- [ ] Core generator logic implemented
- [ ] Validation functions working
- [ ] Tool schema generation working
- [ ] Type mapping correct
- [ ] Input sanitization working

---

### Phase 2: Template Development (8-10 hours)

**Goal**: Create all Jinja2 templates for generating MCP server projects.

#### 2.1 Key Templates

**Template Directory Structure**:
```
templates/python/
├── __init__.py.j2
├── server.py.j2              # MCP server implementation
├── cli.py.j2                 # CLI implementation
├── generator.py.j2           # Business logic stubs
├── setup.py.j2               # Package setup
├── pyproject.toml.j2         # Build configuration
├── requirements.txt.j2       # Dependencies
├── MANIFEST.in.j2            # Package manifest
├── .gitignore.j2             # Git ignore
├── LICENSE.j2                # License file
├── README.md.j2              # Main documentation
├── MCP-USAGE.md.j2           # MCP usage guide
└── tests/
    ├── __init__.py.j2
    ├── test_server.py.j2     # MCP protocol tests
    └── test_generator.py.j2  # Core logic tests
```

**Critical Template Features**:

1. **server.py.j2**: Must generate valid MCP server following pypi-workflow-generator pattern
2. **cli.py.j2**: Must support all tools as subcommands
3. **generator.py.j2**: Must create TODO stubs for all tools
4. **test_server.py.j2**: Must test MCP protocol compliance
5. **README.md.j2**: Must document both MCP and CLI usage

#### 2.2 Template Examples

See detailed template implementations in Phase 2 implementation section below.

#### 2.3 Success Criteria for Phase 2

- [ ] All templates created
- [ ] Templates render without errors
- [ ] Generated code has valid Python syntax
- [ ] Generated tests pass
- [ ] Generated README is accurate

---

### Phase 3: MCP Server & CLI Implementation (4-6 hours)

**Goal**: Implement the dual-mode interface for mcp-server-generator itself.

#### 3.1 MCP Server Implementation

**File**: `mcp_server_generator/server.py`
```python
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
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "parameters": {
                                            "type": "array",
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
                                    }
                                }
                            },
                            "output_dir": {
                                "type": "string",
                                "description": "Output directory (default: current directory)"
                            },
                            "python_version": {
                                "type": "string",
                                "description": "Python version (default: '3.8')"
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

    async def handle_call_tool(self, tool_name: str, arguments: Dict[str, Any]):
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

    async def handle_request(self, request: Dict[str, Any]):
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
```

#### 3.2 CLI Implementation

**File**: `mcp_server_generator/cli.py`

See detailed implementation in Phase 3 section below.

#### 3.3 Success Criteria for Phase 3

- [ ] MCP server responds to tools/list
- [ ] MCP server executes generate_mcp_server
- [ ] CLI interactive mode works
- [ ] CLI command-line mode works
- [ ] Error handling is robust

---

### Phase 4: Testing (3-4 hours)

**Goal**: Comprehensive test coverage for all components.
**Status**: In Progress
**Detailed Specifications**: See [PHASE_4_TEST_PLAN.md](./PHASE_4_TEST_PLAN.md) for complete test case definitions and implementation details.

#### 4.1 Test Structure

```
mcp_server_generator/tests/
├── __init__.py
├── test_generator.py       # Core logic tests
├── test_server.py          # MCP protocol tests
├── test_cli.py             # CLI tests
└── test_templates.py       # Template rendering tests
```

#### 4.2 Key Test Cases

**test_generator.py**:
- [ ] `test_validate_project_name_valid`
- [ ] `test_validate_project_name_invalid`
- [ ] `test_validate_tool_name`
- [ ] `test_generate_tool_schema`
- [ ] `test_generate_mcp_server_basic`
- [ ] `test_generate_mcp_server_creates_files`
- [ ] `test_generate_mcp_server_fails_on_existing_dir`
- [ ] `test_sanitize_description`

**test_server.py**:
- [ ] `test_handle_list_tools`
- [ ] `test_handle_call_tool_generate`
- [ ] `test_handle_call_tool_validate`
- [ ] `test_handle_unknown_method`
- [ ] `test_json_rpc_error_handling`

**test_templates.py**:
- [ ] `test_all_templates_render`
- [ ] `test_generated_code_syntax_valid`
- [ ] `test_generated_tests_pass`

#### 4.3 Success Criteria for Phase 4

- [ ] All tests pass
- [ ] Test coverage > 80%
- [ ] Generated projects pass their own tests
- [ ] MCP protocol compliance verified

---

### Phase 5: Documentation (2-3 hours)

**Goal**: Complete, accurate documentation.

#### 5.1 Documentation Files

1. **README.md** - Main usage guide
2. **MCP-USAGE.md** - MCP server configuration
3. **CONTRIBUTING.md** - Contribution guidelines
4. **EXAMPLES.md** - Example projects

#### 5.2 Success Criteria for Phase 5

- [ ] README explains both modes clearly
- [ ] MCP-USAGE has complete config examples
- [ ] Examples are tested and working
- [ ] Installation instructions are accurate

---

### Phase 6: Integration & Polish (2-3 hours)

**Goal**: Final integration, testing, and polish.

#### 6.0 Setup mcp-server-generator Workflows

**Use pypi-workflow-generator to create workflows for THIS project:**

This demonstrates dogfooding: using our dependency to set up our own CI/CD.

```bash
# Generate PyPI publishing workflow
python3 -m pypi_workflow_generator.main \
  --python-version 3.8 \
  --test-path mcp_server_generator \
  --output-filename pypi-publish.yml

# Verify workflows were created
ls .github/workflows/
```

**Expected output:**
- `.github/workflows/pypi-publish.yml` - PyPI publishing workflow
- `.github/workflows/create-release.yml` - Release creation workflow (auto-generated)

**Success criteria:**
- [ ] Workflows generated successfully
- [ ] Workflows are valid YAML
- [ ] Workflows reference correct Python version and test path

#### 6.1 Tasks

- [ ] Generate GitHub workflows for mcp-server-generator (see 6.0 above)
- [ ] Verify pypi-workflow-generator integration works in generated projects
- [ ] Error messages improved
- [ ] Edge cases handled
- [ ] Dogfooding (generate own templates)
- [ ] Final testing on clean environment

#### 6.2 Success Criteria for Phase 6

- [ ] mcp-server-generator has GitHub Actions workflows
- [ ] Dogfooding works (can regenerate itself)
- [ ] All edge cases handled gracefully
- [ ] Error messages are helpful
- [ ] Ready for PyPI publication

---

## Security Considerations

### Input Validation

1. **Project Names**: Validated against Python identifier rules
2. **Tool Names**: Must be valid Python identifiers
3. **Descriptions**: Sanitized to prevent template injection
4. **Email Addresses**: Basic format validation

### Template Injection Prevention

```python
def sanitize_description(text: str) -> str:
    """Prevent Jinja2 template injection."""
    return text.replace('{', '{{').replace('}', '}}')
```

### File System Safety

1. **Path Traversal**: Only create files in specified output directory
2. **Overwrite Protection**: Fail if directory exists
3. **Permission Errors**: Handle gracefully with clear messages

---

## Timeline & Resources

### Time Estimates

| Phase | Description | Time | Priority |
|-------|-------------|------|----------|
| Phase 1 | Project setup & core generator | 6-8 hrs | CRITICAL |
| Phase 2 | Template development | 8-10 hrs | HIGH |
| Phase 3 | MCP server & CLI | 4-6 hrs | HIGH |
| Phase 4 | Testing | 3-4 hrs | HIGH |
| Phase 5 | Documentation | 2-3 hrs | MEDIUM |
| Phase 6 | Integration & polish | 2-3 hrs | MEDIUM |
| **Total** | **Full implementation** | **25-34 hrs** | - |

### Milestones

**Week 1** (16 hours):
- ✅ Phase 1: Core generator complete
- ✅ Phase 2: 50% of templates done

**Week 2** (16 hours):
- ✅ Phase 2: All templates complete
- ✅ Phase 3: MCP server & CLI done
- ✅ Phase 4: Tests passing

**Week 3** (8 hours):
- ✅ Phase 5: Documentation complete
- ✅ Phase 6: Ready for release

---

## Success Metrics

### Phase 1 Success
- [ ] Can generate a basic project structure
- [ ] Core functions have unit tests
- [ ] Validation works correctly

### Phase 2 Success
- [ ] All templates render without errors
- [ ] Generated code is syntactically valid
- [ ] Generated tests exist and pass

### Phase 3 Success
- [ ] MCP mode works with AI agents
- [ ] CLI mode works for developers
- [ ] Both modes produce identical output

### Overall Success
- [ ] Generate working MCP server in < 5 minutes
- [ ] Generated servers install and run
- [ ] Tests pass in generated projects
- [ ] Documentation is complete
- [ ] Published to PyPI
- [ ] Dogfooding works

---

## Next Steps

1. **Review this plan** - Validate approach and estimates
2. **Begin Phase 1** - Set up project structure
3. **Create first template** - Start with simplest template
4. **Test early, test often** - Validate each phase
5. **Dogfood continuously** - Use tool to improve itself

---

## Appendix: Differences from Original Plan

### What Changed

1. **Removed Click dependency** - Use stdlib argparse (following pypi-workflow-generator)
2. **Simplified MCP protocol** - Removed initialization handshake (not needed for basic stdio)
3. **Template loading** - Use simple FileSystemLoader with `__file__` (proven to work)
4. **Required dependencies** - Jinja2>=3.0 and pypi-workflow-generator>=0.2.0
5. **GitHub Actions required** - Workflow generation is mandatory, not optional
6. **Realistic time estimates** - Based on actual pypi-workflow-generator development
7. **Security focus** - Added input sanitization and validation
8. **Type mapping** - Proper JSON Schema to Python type conversion
9. **Entry points** - Simplified to 2 commands (MCP + CLI)

### Why These Changes

- **Based on real implementation**: pypi-workflow-generator proves these patterns work
- **Simpler is better**: Fewer dependencies = fewer problems
- **Security first**: Prevent template injection and path traversal
- **Developer experience**: Clear error messages, good documentation

---

**Document Version**: 2.0
**Created**: 2025-11-03
**Status**: Ready for implementation
**Reference**: pypi-workflow-generator v0.2.11
