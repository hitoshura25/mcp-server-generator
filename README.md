# MCP Server Generator

> A meta-generator for creating dual-mode MCP servers with best practices

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

Generate complete, production-ready MCP (Model Context Protocol) servers that work in two modes:
- **MCP Server Mode**: For AI agents (Claude Desktop, etc.)
- **CLI Mode**: For developers

**This tool is itself an MCP server**, enabling AI agents to generate other MCP servers! It demonstrates the dual-mode architecture pattern it creates and implements progressive disclosure for context-efficient tool discovery.

## Why Use This?

- ⚡ **Fast**: Generate a complete MCP server in under 5 minutes
- 🏗️ **Complete**: Includes tests, documentation, packaging, and CI/CD
- ✅ **Tested**: Generated servers have comprehensive test suites with high coverage
- 🎯 **Best Practices**: Follows validated patterns from production MCP servers with built-in guidance
- 🔧 **Dual-Mode**: Works as both MCP server and CLI tool
- 🧠 **Smart Discovery**: Progressive disclosure tools for context-efficient AI agent usage
- 📦 **Ready to Publish**: GitHub Actions workflows included for PyPI publishing

## Features

- ✅ **Dual-mode architecture** (MCP + CLI)
- ✅ **Progressive disclosure tools** (context-efficient tool discovery for AI agents)
- ✅ **Built-in guidance** (best practices and implementation guides)
- ✅ **Claude Code integration** (generate slash commands for guided development)
- ✅ **Async/await support** (async handlers for I/O operations, avoids event loop errors)
- ✅ **Package prefix support** (avoid PyPI namespace conflicts with AUTO detection)
- ✅ **Complete project scaffolding** (tests, docs, packaging)
- ✅ **GitHub Actions workflows** (via pypi-workflow-generator)
- ✅ **Comprehensive test suite** (92+ tests with high coverage)
- ✅ **Type hints and documentation**
- ✅ **Best practices enforcement**
- ✅ **Minimal dependencies**

## Installation

### For MCP Server Usage (Recommended)

**Using uvx (no installation required):**

The easiest way to use this as an MCP server - just configure in Claude Desktop:

```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "uvx",
      "args": ["hitoshura25-mcp-server-generator"]
    }
  }
}
```

**Prerequisites:** Install [uv](https://docs.astral.sh/uv/):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### For CLI Usage (Alternative)

**Using pipx (isolated installation):**

```bash
pipx install hitoshura25-mcp-server-generator
```

**Using pip:**

```bash
pip install hitoshura25-mcp-server-generator
```

### From Source (Development)

```bash
git clone https://github.com/hitoshura25/mcp-server-generator.git
cd mcp-server-generator
pip install -e .
```

## Quick Start

### Interactive Mode (Recommended)

The easiest way to get started:

```bash
hitoshura25-mcp-server-generator-cli --interactive
```

This will guide you through:
1. Project naming
2. Author information
3. Tool definitions
4. Configuration options

### Command-Line Mode

For automation or when you have a tool definition file:

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name my-mcp-tool \
  --description "Does something useful" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### MCP Server Mode (For AI Agents)

Configure mcp-server-generator as an MCP server in Claude Desktop to let Claude generate MCP servers for you:

**Using uvx (recommended):**
```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "uvx",
      "args": ["hitoshura25-mcp-server-generator"]
    }
  }
}
```

**Using pipx/pip installation:**
```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "hitoshura25-mcp-server-generator"
    }
  }
}
```

**For detailed MCP configuration, see [MCP-USAGE.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/MCP-USAGE.md)**

## MCP Server Tools

When used as an MCP server (in Claude Desktop or other MCP clients), mcp-server-generator provides powerful tools with **progressive disclosure** support - allowing AI agents to discover and use tools efficiently without loading all schemas upfront.

### Discovery Tools

**search_tools** - Find relevant tools by query
- Search by keywords, categories, or use cases
- Three detail levels for context efficiency:
  - `name`: Just tool names (most efficient)
  - `summary`: Names + descriptions + categories
  - `full`: Complete information including use cases
- Example: `search_tools(query="generate", detail_level="summary")`

**get_tool_info** - Get detailed information about a specific tool
- Two detail levels: `summary` or `full`
- Progressive disclosure for context efficiency
- Example: `get_tool_info(tool_name="generate_mcp_server", detail_level="full")`

### Generation Tools

**generate_mcp_server** - Generate complete MCP server projects
- Creates dual-mode architecture (MCP + CLI)
- Includes tests, documentation, and CI/CD workflows
- Production-ready scaffolding with best practices
- Supports async/await patterns

**generate_claude_command** - Create Claude Code command files
- Generates `.claude/commands/` directory structure
- Creates slash commands for guided MCP development
- Templates for common workflows: `mcp_generator`, `best_practices`, `implementation_helper`, `custom`
- Enables guided development experience

### Validation Tools

**validate_project_name** - Validate project names
- Check Python package compatibility
- Avoid Python keyword conflicts
- Ensure PyPI naming conventions

### Guidance Tools

**get_best_practices** - MCP development best practices
- Progressive disclosure strategies
- Context-efficient tool design
- Control flow optimization
- Security and privacy considerations
- State management patterns
- Testing strategies

**get_implementation_guide** - Step-by-step implementation guide
- Project setup and initialization
- Tool implementation patterns
- Testing strategies
- Deployment and publishing
- Claude Desktop integration

### Why Progressive Disclosure?

Progressive disclosure allows AI agents to:
- Discover tools without loading full schemas upfront
- Save context window space for actual work
- Scale to hundreds or thousands of tools
- Get exactly the level of detail needed

**Example workflow (MCP tool invocations):**
```
# 1. Search for relevant tools
search_tools(query="generate", detail_level="name")
# Returns: ["generate_mcp_server", "generate_claude_command"]

# 2. Get summary of specific tool
get_tool_info(tool_name="generate_mcp_server", detail_level="summary")
# Returns: name, description, category

# 3. Get full details when ready to use
get_tool_info(tool_name="generate_mcp_server", detail_level="full")
# Returns: complete information including use cases and parameters
```

## Package Prefix

To avoid namespace conflicts on PyPI, mcp-server-generator supports prefixing package names. This is **highly recommended** for unique package names.

### Prefix Modes

**AUTO (Recommended)**
- Automatically detects your GitHub username from git config
- Priority: `github.user` → remote URL → `user.name` (sanitized)
- Example: `my-tool` → `username-my-tool`

**Custom Prefix**
- Use your own prefix (organization name, brand, etc.)
- Example: `--prefix acme` → `acme-my-tool`

**NONE**
- No prefix applied (only if you have a truly unique name)
- Example: `unique-server-name` → `unique-server-name`

### Usage Examples

**Interactive Mode:**
```bash
hitoshura25-mcp-server-generator-cli --interactive
# You'll be prompted: "Prefix (default: AUTO): "
# - Press Enter for AUTO detection
# - Type "NONE" for no prefix
# - Type "acme" for custom prefix
```

**Command-Line:**
```bash
# AUTO mode (default)
hitoshura25-mcp-server-generator-cli --project-name calculator --prefix AUTO ...

# Custom prefix
hitoshura25-mcp-server-generator-cli --project-name calculator --prefix acme ...

# No prefix
hitoshura25-mcp-server-generator-cli --project-name unique-calculator --prefix NONE ...
```

**MCP Server Mode:**
```json
{
  "project_name": "calculator",
  "prefix": "AUTO",
  ...
}
```

### Generated Names

With prefix `username` and project `my-tool`:
- **PyPI Package**: `username-my-tool` (install with `pip install username-my-tool`)
- **Python Import**: `username_my_tool` (use in code as `import username_my_tool`)
- **CLI Command**: `username-my-tool` (run as `username-my-tool --help`)
- **MCP Command**: `mcp-username-my-tool` (use in config)

**For detailed MCP configuration, see [MCP-USAGE.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/MCP-USAGE.md)**

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

**For complete examples, see [EXAMPLES.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/EXAMPLES.md)**

## Documentation

- **[MCP-USAGE.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/MCP-USAGE.md)** - Detailed MCP server configuration guide
- **[ASYNC_GUIDE.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/ASYNC_GUIDE.md)** - Complete guide for using async/await in generated MCP servers
- **[EXAMPLES.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/EXAMPLES.md)** - Example projects and use cases
- **[SECURITY.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/SECURITY.md)** - **Security guidelines and best practices**
- **[CONTRIBUTING.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/CONTRIBUTING.md)** - Development and contribution guidelines

## Security

🔒 **Important**: MCP servers can be exploited for malicious purposes if not properly secured. See [SECURITY.md](SECURITY.md) for comprehensive security guidelines.

### Key Security Features

Generated MCP servers include:

- **Security utilities module** (`security_utils.py`) with ready-to-use functions for:
  - Input validation and sanitization
  - Path traversal protection
  - Command injection prevention
  - Rate limiting to prevent high-speed automated attacks
  - Audit logging for security-relevant operations
  - Sensitive data redaction (PII, credentials, API keys)

- **Automated security analysis** - The generator analyzes your tool definitions and warns about:
  - High-risk patterns (command execution, code evaluation)
  - Medium-risk patterns (file operations, network access, credential handling)
  - Recommendations for secure implementation

- **Comprehensive security documentation** - Every generated project includes SECURITY.md with:
  - Threat model based on real-world AI-orchestrated cyber espionage
  - Secure coding patterns and examples
  - Security checklist for deployment
  - Incident response procedures

### Best Practices

When creating MCP servers:

1. **Validate all inputs** - Use whitelists, not blacklists
2. **Apply principle of least privilege** - Tools should do the minimum necessary
3. **Implement rate limiting** - Protect against high-speed automated attacks
4. **Add audit logging** - Track all security-relevant operations
5. **Redact sensitive data** - Don't expose PII, credentials, or secrets
6. **Use security utilities** - Leverage the built-in `security_utils.py` module

### Threat Model

MCP servers can be targeted for:
- AI-orchestrated cyber espionage campaigns
- Jailbreak attempts through task decomposition
- High-speed reconnaissance and exploitation
- Credential harvesting through tool chaining
- Data exfiltration at scale

**Reference**: [Anthropic's research on AI-orchestrated cyber espionage](https://www.anthropic.com/news/disrupting-AI-espionage)

## Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=hitoshura25_mcp_server_generator --cov-report=term-missing

# Run specific test file
pytest hitoshura25_mcp_server_generator/tests/test_server.py -v
```

**Test Statistics:**
- 92+ comprehensive tests covering all functionality
- All async MCP protocol tests passing
- Progressive disclosure and discovery tools tests passing
- Template validation tests passing

## Requirements

- Python ≥3.8
- Jinja2 ≥3.0
- hitoshura25-pypi-workflow-generator ==0.6.0

## Development

See [CONTRIBUTING.md](https://github.com/hitoshura25/mcp-server-generator/blob/main/CONTRIBUTING.md) for detailed development instructions.

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
│  ┌──────────┐      ┌──────────┐     │
│  │ MCP Mode │      │ CLI Mode │     │
│  └────┬─────┘      └────┬─────┘     │
│       │                 │           │
│       └────────┬────────┘           │
│                │                    │
│         ┌──────▼───────┐            │
│         │ generator.py │            │
│         │ (Core Logic) │            │
│         └──────────────┘            │
│                                     │
└─────────────────────────────────────┘
```

Both modes use the same core generator logic, ensuring consistency.

## License

Apache-2.0

## Author

Vinayak Menon

## Links

- **PyPI**: https://pypi.org/project/hitoshura25-mcp-server-generator/
- **GitHub**: https://github.com/hitoshura25/mcp-server-generator
- **Issues**: https://github.com/hitoshura25/mcp-server-generator/issues
- **Reference Implementation**: [pypi-workflow-generator](https://github.com/hitoshura25/pypi-workflow-generator)

## Acknowledgments

This project is based on patterns validated in [pypi-workflow-generator](https://pypi.org/project/pypi-workflow-generator/), a production MCP server for generating GitHub Actions workflows.

Progressive disclosure implementation follows best practices from:
- [Anthropic's MCP Engineering Blog: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
