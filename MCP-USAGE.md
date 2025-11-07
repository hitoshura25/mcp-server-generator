# MCP Server Usage Guide

This guide explains how to configure and use mcp-server-generator as an MCP (Model Context Protocol) server with AI clients like Claude Desktop.

## What is MCP?

The Model Context Protocol (MCP) is a standard protocol for AI agents to interact with external tools and services. MCP servers expose "tools" that AI agents can discover and invoke to perform specific tasks.

## Installation

First, ensure mcp-server-generator is installed:

```bash
pip install hitoshura25-mcp-server-generator
```

Verify the installation:

```bash
which hitoshura25-mcp-server-generator
# Should output: /path/to/your/venv/bin/hitoshura25-mcp-server-generator (or similar)
```

## Claude Desktop Configuration

### macOS Configuration

1. **Locate the Claude Desktop config file:**

   ```bash
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Add mcp-server-generator to the configuration:**

   ```json
   {
     "mcpServers": {
       "mcp-server-generator": {
         "command": "hitoshura25-mcp-server-generator"
       }
     }
   }
   ```

3. **If using a virtual environment:**

   ```json
   {
     "mcpServers": {
       "mcp-server-generator": {
         "command": "/absolute/path/to/venv/bin/hitoshura25-mcp-server-generator"
       }
     }
   }
   ```

4. **Restart Claude Desktop** to load the new configuration.

### Windows Configuration

1. **Locate the Claude Desktop config file:**

   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add mcp-server-generator:**

   ```json
   {
     "mcpServers": {
       "mcp-server-generator": {
         "command": "hitoshura25-mcp-server-generator.exe"
       }
     }
   }
   ```

3. **If using a virtual environment:**

   ```json
   {
     "mcpServers": {
       "mcp-server-generator": {
         "command": "C:\\path\\to\\venv\\Scripts\\hitoshura25-mcp-server-generator.exe"
       }
     }
   }
   ```

4. **Restart Claude Desktop**.

### Linux Configuration

1. **Locate the Claude Desktop config file:**

   ```bash
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **Add mcp-server-generator:**

   ```json
   {
     "mcpServers": {
       "mcp-server-generator": {
         "command": "hitoshura25-mcp-server-generator"
       }
     }
   }
   ```

3. **Restart Claude Desktop**.

## Available Tools

Once configured, mcp-server-generator exposes the following tools to AI agents:

### 1. generate_mcp_server

Generate a complete MCP server project with dual-mode architecture.

**Parameters:**
- `project_name` (string, required): Project name (e.g., "my-mcp-server")
- `description` (string, required): Project description
- `author` (string, required): Author name
- `author_email` (string, required): Author email
- `tools` (array, required): List of tools this MCP server will provide
  - Each tool has:
    - `name` (string): Tool name (valid Python identifier)
    - `description` (string): Tool description
    - `parameters` (array): List of parameters
      - `name` (string): Parameter name
      - `type` (string): Parameter type (string, number, boolean, etc.)
      - `description` (string): Parameter description
      - `required` (boolean): Whether the parameter is required
- `output_dir` (string, optional): Output directory (default: current directory)
- `python_version` (string, optional): Python version (default: "3.8")

**Example Usage in Claude:**

```
Please generate an MCP server called "weather-tools" that provides
two tools: get_weather (takes location as string) and get_forecast
(takes location as string and days as number).

Author: Jane Doe
Email: jane@example.com
```

### 2. validate_project_name

Validate a project name for Python package compatibility.

**Parameters:**
- `name` (string, required): Project name to validate

**Example Usage in Claude:**

```
Can you check if "my-awesome-server" is a valid project name?
```

## Usage Examples

### Example 1: Generate a Simple Calculator Server

In Claude Desktop, you can say:

```
Use the mcp-server-generator tool to create an MCP server called "calc-tools"
with these tools:
1. add - takes two numbers (x and y) and returns their sum
2. subtract - takes two numbers (x and y) and returns their difference
3. multiply - takes two numbers (x and y) and returns their product

Author: John Smith
Email: john@example.com
```

Claude will invoke the `generate_mcp_server` tool with the appropriate parameters and create a complete project.

### Example 2: Generate a File Operations Server

```
Create an MCP server named "file-ops" with these capabilities:
1. read_file - takes filepath (string) and returns file contents
2. write_file - takes filepath (string) and content (string)
3. list_directory - takes dirpath (string) and returns file list

Author: Alice Johnson
Email: alice@company.com
Output directory: /Users/alice/projects
```

### Example 3: Validate Before Creating

```
First, validate that "my-data-processor" is a valid project name.
If valid, create an MCP server with that name that has one tool
called "process_data" which takes data (string) and format (string).
```

## Troubleshooting

### Issue: Claude doesn't see the mcp-server-generator tool

**Solutions:**
1. Verify the config file is in the correct location
2. Check JSON syntax (use a JSON validator)
3. Ensure mcp-server-generator is installed and accessible
4. Try using the absolute path to the executable
5. Restart Claude Desktop

### Issue: "Command not found" error

**Solutions:**
1. Use the absolute path to mcp-server-generator:
   ```bash
   which mcp-server-generator  # macOS/Linux
   where mcp-server-generator  # Windows
   ```
2. If using a virtual environment, use the full path to the venv binary
3. Check that the executable has execute permissions (macOS/Linux):
   ```bash
   chmod +x /path/to/mcp-server-generator
   ```

### Issue: Tool execution fails

**Solutions:**
1. Check Claude Desktop's logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
   - Linux: `~/.config/Claude/logs/`
2. Verify all required parameters are provided
3. Ensure project name is valid (no spaces, special characters, or Python keywords)
4. Check that the output directory exists and has write permissions

### Issue: Generated project has issues

**Solutions:**
1. Verify tool definitions have valid Python identifiers for names
2. Check that parameter types are supported (string, number, boolean, array, object)
3. Ensure email format is valid
4. Try generating with default options first

## Viewing Logs

To see detailed logs of MCP server communication:

### macOS
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Windows
```powershell
Get-Content "$env:APPDATA\Claude\logs\mcp*.log" -Wait
```

### Linux
```bash
tail -f ~/.config/Claude/logs/mcp*.log
```

## Advanced Configuration

### Setting Working Directory

```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "mcp-server-generator",
      "cwd": "/path/to/project/directory"
    }
  }
}
```

### Environment Variables

```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "mcp-server-generator",
      "env": {
        "PYTHONPATH": "/custom/python/path",
        "DEBUG": "true"
      }
    }
  }
}
```

### Multiple MCP Servers

You can configure multiple MCP servers alongside mcp-server-generator:

```json
{
  "mcpServers": {
    "mcp-server-generator": {
      "command": "mcp-server-generator"
    },
    "pypi-workflow-generator": {
      "command": "mcp-pypi-workflow-generator"
    },
    "my-custom-server": {
      "command": "/path/to/my-custom-server"
    }
  }
}
```

## Security Considerations

### Input Validation

mcp-server-generator validates all inputs:
- Project names must be valid Python identifiers
- Tool names must be valid Python identifiers
- Descriptions are sanitized to prevent template injection
- Paths are validated to prevent directory traversal

### File System Access

- Only creates files in the specified output directory
- Fails if directory already exists (no overwriting)
- Requires explicit write permissions

### Execution Environment

- Runs in the context of the Claude Desktop application
- Has the same permissions as Claude Desktop
- Accesses the same Python environment as configured

## Best Practices

1. **Use Absolute Paths**: When configuring, use absolute paths for reliability
2. **Virtual Environments**: Install in a dedicated venv for isolation
3. **Version Pinning**: Pin specific versions in production environments
4. **Test First**: Test with simple projects before complex ones
5. **Validate Names**: Use the validate_project_name tool before generating
6. **Check Logs**: Monitor logs during initial setup
7. **Backup Configs**: Keep a backup of your claude_desktop_config.json

## Integration with Other Tools

### With pypi-workflow-generator

Generated projects automatically include GitHub Actions workflows via pypi-workflow-generator. If you have pypi-workflow-generator configured as an MCP server, Claude can:

1. Generate an MCP server with mcp-server-generator
2. Update its workflows with pypi-workflow-generator
3. Manage releases with pypi-workflow-generator

### With Version Control

After generating a project:

```bash
cd my-generated-project
git init
git add .
git commit -m "Initial commit from mcp-server-generator"
git remote add origin <your-repo-url>
git push -u origin main
```

## Next Steps

After configuring mcp-server-generator:

1. **Test the Configuration**: Ask Claude to validate a project name
2. **Generate a Sample Project**: Create a simple calculator server
3. **Explore Examples**: See [EXAMPLES.md](./EXAMPLES.md) for more ideas
4. **Read the API**: Check the [README.md](./README.md) for CLI usage
5. **Contribute**: See [CONTRIBUTING.md](./CONTRIBUTING.md) to contribute

## Support

- **Issues**: https://github.com/hitoshura25/mcp-server-generator/issues
- **Discussions**: https://github.com/hitoshura25/mcp-server-generator/discussions
- **Documentation**: https://github.com/hitoshura25/mcp-server-generator

## Related Documentation

- [README.md](./README.md) - Main documentation
- [EXAMPLES.md](./EXAMPLES.md) - Example projects
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Development guide
- [MCP Protocol Specification](https://modelcontextprotocol.io/) - Official MCP docs
