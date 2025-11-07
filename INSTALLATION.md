# Installation Guide

Complete guide for installing `hitoshura25-mcp-server-generator` for different use cases.

## Quick Start (Recommended)

**For MCP Server usage** - Use uvx (zero installation):

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

**Prerequisites:** Install [uv](https://docs.astral.sh/uv/) once:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Installation Methods

### 1. uvx (Recommended for MCP Servers)

**What is uvx?**
- Python's equivalent to `npx`
- Automatically downloads and runs packages in isolated environments
- Zero manual installation required
- 10-100x faster than pip
- Official pattern used by Anthropic MCP servers

**Prerequisites:**
```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

**Usage:**
No package installation needed! Just configure in Claude Desktop/Code:

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

**How it works:**
1. First run: uvx downloads package from PyPI into isolated environment
2. Subsequent runs: Uses cached version (instant startup)
3. Updates: Use `uvx --upgrade hitoshura25-mcp-server-generator`

**Pros:**
✅ Zero friction - no manual installation
✅ Automatic isolation - no dependency conflicts
✅ Fast - Rust-powered package manager
✅ Modern - official MCP server pattern
✅ Auto-updates available

**Cons:**
❌ Requires uv to be installed first
❌ First run is slower (downloads package)

---

### 2. pipx (Recommended for CLI Usage)

**What is pipx?**
- Installs Python CLI tools in isolated environments
- Global command availability
- Traditional approach, widely adopted

**Installation:**
```bash
# Install pipx
python -m pip install --user pipx
python -m pipx ensurepath

# Install mcp-server-generator
pipx install hitoshura25-mcp-server-generator
```

**Verification:**
```bash
which hitoshura25-mcp-server-generator
# Should output: ~/.local/bin/hitoshura25-mcp-server-generator

hitoshura25-mcp-server-generator-cli --help
```

**For MCP usage:**
```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "hitoshura25-mcp-server-generator"
    }
  }
}
```

**Updating:**
```bash
pipx upgrade hitoshura25-mcp-server-generator
```

**Uninstalling:**
```bash
pipx uninstall hitoshura25-mcp-server-generator
```

**Pros:**
✅ Established tool (widely used since 2018)
✅ Isolated environments
✅ Global command availability
✅ Clean uninstall

**Cons:**
❌ Requires manual installation
❌ Slower than uvx
❌ Requires pipx itself to be installed

---

### 3. pip (For Development)

**When to use:**
- Contributing to the project
- Integrating into other Python projects
- Development and testing

**Global installation:**
```bash
pip install hitoshura25-mcp-server-generator
```

**Virtual environment (recommended for development):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install hitoshura25-mcp-server-generator
```

**For MCP usage (requires absolute path):**
```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "/absolute/path/to/venv/bin/hitoshura25-mcp-server-generator"
    }
  }
}
```

**Development installation (editable):**
```bash
git clone https://github.com/hitoshura25/mcp-server-generator.git
cd mcp-server-generator
pip install -e .
```

**Pros:**
✅ Standard Python package manager
✅ Works everywhere Python is installed
✅ Can install from source
✅ Editable installs for development

**Cons:**
❌ No isolation (can cause dependency conflicts)
❌ Requires absolute paths for MCP with venvs
❌ Pollutes global Python environment

---

## Comparison Table

| Feature | uvx | pipx | pip |
|---------|-----|------|-----|
| **Installation required** | No (ephemeral) | Yes | Yes |
| **Isolation** | ✅ Automatic | ✅ Yes | ❌ No* |
| **Speed** | ⚡ Very Fast | 🐢 Standard | 🐢 Standard |
| **MCP recommendation** | ⭐ Primary | ✅ Alternative | ⚠️ Dev only |
| **Update mechanism** | `--upgrade` flag | `pipx upgrade` | `pip install -U` |
| **Uninstall** | N/A (ephemeral) | `pipx uninstall` | `pip uninstall` |
| **Best for** | MCP servers | CLI tools | Development |

\* Unless using virtual environment

---

## Troubleshooting

### uvx: command not found

**Problem:** `uvx` command not available after installing uv

**Solution:**
```bash
# Restart shell or reload PATH
source ~/.bashrc  # or ~/.zshrc

# Verify uv is installed
uv --version

# Try using `uv tool run` directly
uv tool run hitoshura25-mcp-server-generator
```

### pipx: No apps associated with package

**Problem:** pipx says "No apps associated with package"

**Solution:** This is fixed in v1.0+. Ensure you're using the latest version:
```bash
pip install --upgrade hitoshura25-mcp-server-generator
```

The package now properly defines `[project.scripts]` in `pyproject.toml`.

### MCP Server not starting

**Problem:** Claude Desktop shows "Server connection failed"

**Solutions:**

1. **Check command availability:**
```bash
# For uvx
uv --version

# For pipx/pip
which hitoshura25-mcp-server-generator
hitoshura25-mcp-server-generator --help
```

2. **Check configuration syntax:**
- Ensure JSON is valid (no trailing commas)
- Verify command path is correct
- Check logs: `~/Library/Application Support/Claude/logs/`

3. **Test command manually:**
```bash
# Should start MCP server (Ctrl+C to exit)
hitoshura25-mcp-server-generator

# Or with uvx
uvx hitoshura25-mcp-server-generator
```

### Virtual environment issues with MCP

**Problem:** MCP can't find command in virtual environment

**Solution:** Use absolute paths:
```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "/Users/you/project/venv/bin/hitoshura25-mcp-server-generator"
    }
  }
}
```

**Better solution:** Use uvx or pipx instead (no venv needed for MCP usage).

---

## Platform-Specific Notes

### macOS

**Config location:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Recommended:** uvx or pipx

### Windows

**Config location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Note:** Use `.exe` extension for pipx/pip installations:
```json
{
  "command": "hitoshura25-mcp-server-generator.exe"
}
```

**Recommended:** uvx (no .exe needed with uvx)

### Linux

**Config location:**
```bash
~/.config/Claude/claude_desktop_config.json
```

**Recommended:** uvx or pipx

---

## For Generated Projects

All projects generated by this tool will have the same installation options:

```json
{
  "mcpServers": {
    "your-project": {
      "command": "uvx",
      "args": ["your-project-name"]
    }
  }
}
```

See the generated `README.md` for project-specific instructions.

---

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [pipx Documentation](https://pipx.pypa.io/)
- [MCP Configuration Guide](./MCP-USAGE.md)
- [Package on PyPI](https://pypi.org/project/hitoshura25-mcp-server-generator/)
- [GitHub Repository](https://github.com/hitoshura25/mcp-server-generator)
