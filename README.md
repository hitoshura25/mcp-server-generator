# MCP Server Generator

> A meta-generator for creating dual-mode MCP servers with best practices

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Test Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen.svg)](./PHASE_4_TEST_PLAN.md)

## Overview

Generate complete, production-ready MCP (Model Context Protocol) servers that work in two modes:
- **MCP Server Mode**: For AI agents (Claude Desktop, etc.)
- **CLI Mode**: For developers

**This tool is itself an MCP server**, enabling AI agents to generate other MCP servers! It demonstrates the dual-mode architecture pattern it creates.

## Why Use This?

- ⚡ **Fast**: Generate a complete MCP server in under 5 minutes
- 🏗️ **Complete**: Includes tests, documentation, packaging, and CI/CD
- ✅ **Tested**: Generated servers have 82% test coverage with comprehensive test suites
- 🎯 **Best Practices**: Follows validated patterns from production MCP servers
- 🔧 **Dual-Mode**: Works as both MCP server and CLI tool
- 📦 **Ready to Publish**: GitHub Actions workflows included for PyPI publishing

## Features

- ✅ **Dual-mode architecture** (MCP + CLI)
- ✅ **Complete project scaffolding** (tests, docs, packaging)
- ✅ **GitHub Actions workflows** (via pypi-workflow-generator)
- ✅ **Comprehensive test suite** (82% coverage with 27+ tests)
- ✅ **Type hints and documentation**
- ✅ **Best practices enforcement**
- ✅ **Minimal dependencies**

## Installation

### From PyPI

```bash
pip install mcp-server-generator
```

### From Source

```bash
git clone https://github.com/hitoshura25/mcp-server-generator.git
cd mcp-server-generator
pip install -e .
```

## Quick Start

### Interactive Mode (Recommended)

The easiest way to get started:

```bash
mcp-server-generator-cli --interactive
```

This will guide you through:
1. Project naming
2. Author information
3. Tool definitions
4. Configuration options

### Command-Line Mode

For automation or when you have a tool definition file:

```bash
mcp-server-generator-cli \
  --project-name my-mcp-tool \
  --description "Does something useful" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### MCP Server Mode (For AI Agents)

Configure mcp-server-generator as an MCP server in Claude Desktop to let Claude generate MCP servers for you:

```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "mcp-server-generator"
    }
  }
}
```

**For detailed MCP configuration, see [MCP-USAGE.md](./MCP-USAGE.md)**

## What Gets Generated

A complete, production-ready MCP server project:

```
my-mcp-tool/
├── .gitignore
├── README.md
├── MCP-USAGE.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── requirements.txt
├── MANIFEST.in
├── my_mcp_tool/
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   ├── cli.py             # CLI interface
│   ├── generator.py       # Business logic (TODO stubs)
│   └── tests/
│       ├── __init__.py
│       ├── test_server.py  # MCP protocol tests
│       └── test_generator.py  # Core logic tests
└── .github/
    └── workflows/
        └── pypi-publish.yml  # PyPI publishing workflow
```

### Generated Features

- ✅ Working MCP server with proper JSON-RPC over stdio
- ✅ CLI interface with argparse
- ✅ Complete test suite (MCP protocol + business logic)
- ✅ GitHub Actions workflow for PyPI publishing
- ✅ Comprehensive documentation (README, MCP-USAGE)
- ✅ Proper Python packaging (setup.py, pyproject.toml)
- ✅ TODO stubs for easy implementation

## Tool Definition Format

Create a `tools.json` file to define your MCP server's tools:

```json
{
  "tools": [
    {
      "name": "my_function",
      "description": "Does something useful",
      "parameters": [
        {
          "name": "input_text",
          "type": "string",
          "description": "Text to process",
          "required": true
        },
        {
          "name": "max_length",
          "type": "number",
          "description": "Maximum length",
          "required": false
        }
      ]
    }
  ]
}
```

### Supported Types

- `string` / `str`
- `number` / `int` / `integer` / `float`
- `boolean` / `bool`
- `array` / `list`
- `object` / `dict`

**For complete examples, see [EXAMPLES.md](./EXAMPLES.md)**

## Documentation

- **[MCP-USAGE.md](./MCP-USAGE.md)** - Detailed MCP server configuration guide
- **[EXAMPLES.md](./EXAMPLES.md)** - Example projects and use cases
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Development and contribution guidelines
- **[PHASE_4_TEST_PLAN.md](./PHASE_4_TEST_PLAN.md)** - Test specifications and coverage

## Testing

The project includes a comprehensive test suite with 82% coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=mcp_server_generator --cov-report=term-missing

# Run specific test file
pytest mcp_server_generator/tests/test_server.py -v
```

**Test Statistics:**
- Total tests: 34 (exceeds target of 27+)
- Coverage: 82%
- All async MCP protocol tests passing
- Template validation tests passing

## Requirements

- Python ≥3.8
- Jinja2 ≥3.0
- pypi-workflow-generator ≥0.2.0

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed development instructions.

Quick setup:

```bash
# Clone the repository
git clone https://github.com/hitoshura25/mcp-server-generator.git
cd mcp-server-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest
```

## Architecture

mcp-server-generator follows a dual-mode architecture pattern:

```
┌─────────────────────────────────────┐
│     mcp-server-generator            │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐      ┌──────────┐   │
│  │ MCP Mode │      │ CLI Mode │   │
│  └────┬─────┘      └────┬─────┘   │
│       │                 │          │
│       └────────┬────────┘          │
│                │                   │
│         ┌──────▼───────┐          │
│         │  generator.py │          │
│         │  (Core Logic) │          │
│         └──────────────┘          │
│                                     │
└─────────────────────────────────────┘
```

Both modes use the same core generator logic, ensuring consistency.

## License

Apache-2.0

## Author

Vinayak Menon

## Links

- **PyPI**: https://pypi.org/project/mcp-server-generator/
- **GitHub**: https://github.com/hitoshura25/mcp-server-generator
- **Issues**: https://github.com/hitoshura25/mcp-server-generator/issues
- **Reference Implementation**: [pypi-workflow-generator](https://github.com/hitoshura25/pypi-workflow-generator)

## Acknowledgments

This project is based on patterns validated in [pypi-workflow-generator](https://pypi.org/project/pypi-workflow-generator/), a production MCP server for generating GitHub Actions workflows.
