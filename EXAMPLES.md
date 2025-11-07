# MCP Server Generator Examples

This document provides realistic examples of MCP servers you can generate with mcp-server-generator. Each example includes the complete tool definition and explains the use case.

## Table of Contents

- [Example 1: Calculator MCP Server](#example-1-calculator-mcp-server)
- [Example 2: File Operations MCP Server](#example-2-file-operations-mcp-server)
- [Example 3: Text Processing MCP Server](#example-3-text-processing-mcp-server)
- [Example 4: Web API Client MCP Server](#example-4-web-api-client-mcp-server)
- [Example 5: Database Query MCP Server](#example-5-database-query-mcp-server)
- [Example 6: System Information MCP Server](#example-6-system-information-mcp-server)
- [Using the Examples](#using-the-examples)

---

## Example 1: Calculator MCP Server

**Use Case**: Simple mathematical operations for AI agents.

### Tool Definition (tools.json)

```json
{
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers together",
      "parameters": [
        {
          "name": "x",
          "type": "number",
          "description": "First number",
          "required": true
        },
        {
          "name": "y",
          "type": "number",
          "description": "Second number",
          "required": true
        }
      ]
    },
    {
      "name": "subtract",
      "description": "Subtract second number from first",
      "parameters": [
        {
          "name": "x",
          "type": "number",
          "description": "First number",
          "required": true
        },
        {
          "name": "y",
          "type": "number",
          "description": "Second number",
          "required": true
        }
      ]
    },
    {
      "name": "multiply",
      "description": "Multiply two numbers",
      "parameters": [
        {
          "name": "x",
          "type": "number",
          "description": "First number",
          "required": true
        },
        {
          "name": "y",
          "type": "number",
          "description": "Second number",
          "required": true
        }
      ]
    },
    {
      "name": "divide",
      "description": "Divide first number by second",
      "parameters": [
        {
          "name": "x",
          "type": "number",
          "description": "Numerator",
          "required": true
        },
        {
          "name": "y",
          "type": "number",
          "description": "Denominator",
          "required": true
        }
      ]
    },
    {
      "name": "power",
      "description": "Raise first number to the power of second",
      "parameters": [
        {
          "name": "base",
          "type": "number",
          "description": "Base number",
          "required": true
        },
        {
          "name": "exponent",
          "type": "number",
          "description": "Exponent",
          "required": true
        }
      ]
    }
  ]
}
```

### Generate the Server

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name calc-tools \
  --description "Mathematical calculation tools for AI agents" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### Expected Output

```
✓ Generated project: calc-tools/
✓ Files created: 18
✓ Tests: 27 passing
✓ Ready to implement business logic in calc_tools/generator.py
```

### Implementation Notes

After generation, you'll need to implement the functions in `calc_tools/generator.py`:

```python
def add(x: float, y: float) -> float:
    """Add two numbers together."""
    return x + y

def divide(x: float, y: float) -> float:
    """Divide first number by second."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y
```

---

## Example 2: File Operations MCP Server

**Use Case**: Safe file system operations for AI agents.

### Tool Definition (tools.json)

```json
{
  "tools": [
    {
      "name": "read_file",
      "description": "Read contents of a text file",
      "parameters": [
        {
          "name": "filepath",
          "type": "string",
          "description": "Path to the file to read",
          "required": true
        },
        {
          "name": "encoding",
          "type": "string",
          "description": "File encoding (default: utf-8)",
          "required": false
        }
      ]
    },
    {
      "name": "write_file",
      "description": "Write content to a text file",
      "parameters": [
        {
          "name": "filepath",
          "type": "string",
          "description": "Path to the file to write",
          "required": true
        },
        {
          "name": "content",
          "type": "string",
          "description": "Content to write to the file",
          "required": true
        },
        {
          "name": "append",
          "type": "boolean",
          "description": "Append to file instead of overwriting",
          "required": false
        }
      ]
    },
    {
      "name": "list_directory",
      "description": "List files and directories in a given path",
      "parameters": [
        {
          "name": "dirpath",
          "type": "string",
          "description": "Path to directory",
          "required": true
        },
        {
          "name": "pattern",
          "type": "string",
          "description": "Glob pattern to filter files (e.g., '*.txt')",
          "required": false
        }
      ]
    },
    {
      "name": "file_exists",
      "description": "Check if a file or directory exists",
      "parameters": [
        {
          "name": "filepath",
          "type": "string",
          "description": "Path to check",
          "required": true
        }
      ]
    },
    {
      "name": "get_file_info",
      "description": "Get metadata about a file",
      "parameters": [
        {
          "name": "filepath",
          "type": "string",
          "description": "Path to file",
          "required": true
        }
      ]
    }
  ]
}
```

### Generate the Server

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name file-ops \
  --description "Safe file system operations for AI agents" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### Security Considerations

When implementing, add path validation:
- Restrict to specific directories
- Prevent path traversal attacks
- Check file permissions
- Limit file sizes

---

## Example 3: Text Processing MCP Server

**Use Case**: Text transformation and analysis tools.

### Tool Definition (tools.json)

```json
{
  "tools": [
    {
      "name": "count_words",
      "description": "Count words in a text",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "Text to analyze",
          "required": true
        }
      ]
    },
    {
      "name": "to_uppercase",
      "description": "Convert text to uppercase",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "Text to convert",
          "required": true
        }
      ]
    },
    {
      "name": "to_lowercase",
      "description": "Convert text to lowercase",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "Text to convert",
          "required": true
        }
      ]
    },
    {
      "name": "reverse_text",
      "description": "Reverse the characters in text",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "Text to reverse",
          "required": true
        }
      ]
    },
    {
      "name": "extract_emails",
      "description": "Extract email addresses from text",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "Text to search for emails",
          "required": true
        }
      ]
    },
    {
      "name": "truncate_text",
      "description": "Truncate text to specified length",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "Text to truncate",
          "required": true
        },
        {
          "name": "max_length",
          "type": "number",
          "description": "Maximum length",
          "required": true
        },
        {
          "name": "suffix",
          "type": "string",
          "description": "Suffix to add (e.g., '...')",
          "required": false
        }
      ]
    }
  ]
}
```

### Generate the Server

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name text-tools \
  --description "Text processing and transformation tools" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

---

## Example 4: Web API Client MCP Server

**Use Case**: Wrapper for a REST API to make it accessible to AI agents.

### Tool Definition (tools.json)

```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": [
        {
          "name": "location",
          "type": "string",
          "description": "City name or coordinates",
          "required": true
        },
        {
          "name": "units",
          "type": "string",
          "description": "Temperature units (metric/imperial)",
          "required": false
        }
      ]
    },
    {
      "name": "get_forecast",
      "description": "Get weather forecast for upcoming days",
      "parameters": [
        {
          "name": "location",
          "type": "string",
          "description": "City name or coordinates",
          "required": true
        },
        {
          "name": "days",
          "type": "number",
          "description": "Number of days to forecast",
          "required": true
        }
      ]
    },
    {
      "name": "search_location",
      "description": "Search for location coordinates",
      "parameters": [
        {
          "name": "query",
          "type": "string",
          "description": "Location search query",
          "required": true
        }
      ]
    }
  ]
}
```

### Generate the Server

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name weather-api \
  --description "Weather API client for AI agents" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### Implementation Tips

```python
import requests

def get_weather(location: str, units: str = "metric") -> dict:
    """Get current weather for a location."""
    # TODO: Add your API key
    api_key = "YOUR_API_KEY"
    url = f"https://api.weatherapi.com/v1/current.json"

    params = {
        "key": api_key,
        "q": location,
        "units": units
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()
```

---

## Example 5: Database Query MCP Server

**Use Case**: Safe database queries for AI agents.

### Tool Definition (tools.json)

```json
{
  "tools": [
    {
      "name": "query_users",
      "description": "Query users from database",
      "parameters": [
        {
          "name": "limit",
          "type": "number",
          "description": "Maximum number of results",
          "required": false
        },
        {
          "name": "offset",
          "type": "number",
          "description": "Number of results to skip",
          "required": false
        }
      ]
    },
    {
      "name": "get_user_by_id",
      "description": "Get user details by ID",
      "parameters": [
        {
          "name": "user_id",
          "type": "number",
          "description": "User ID",
          "required": true
        }
      ]
    },
    {
      "name": "search_users",
      "description": "Search users by name or email",
      "parameters": [
        {
          "name": "query",
          "type": "string",
          "description": "Search query",
          "required": true
        }
      ]
    },
    {
      "name": "get_statistics",
      "description": "Get database statistics",
      "parameters": []
    }
  ]
}
```

### Generate the Server

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name db-query-tools \
  --description "Safe database query tools for AI agents" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### Security Best Practices

- Use parameterized queries (never string concatenation)
- Implement rate limiting
- Read-only database user
- Whitelist allowed queries
- Sanitize all inputs

---

## Example 6: System Information MCP Server

**Use Case**: Retrieve system information safely.

### Tool Definition (tools.json)

```json
{
  "tools": [
    {
      "name": "get_disk_usage",
      "description": "Get disk usage information",
      "parameters": [
        {
          "name": "path",
          "type": "string",
          "description": "Path to check (default: /)",
          "required": false
        }
      ]
    },
    {
      "name": "get_memory_info",
      "description": "Get memory usage information",
      "parameters": []
    },
    {
      "name": "get_cpu_info",
      "description": "Get CPU usage information",
      "parameters": []
    },
    {
      "name": "get_network_info",
      "description": "Get network interfaces information",
      "parameters": []
    },
    {
      "name": "get_process_list",
      "description": "Get list of running processes",
      "parameters": [
        {
          "name": "limit",
          "type": "number",
          "description": "Maximum number of processes to return",
          "required": false
        }
      ]
    }
  ]
}
```

### Generate the Server

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name system-info \
  --description "System information tools for monitoring" \
  --author "Your Name" \
  --email "you@example.com" \
  --tools-file tools.json
```

### Dependencies

You'll likely need additional packages:

```bash
pip install psutil
```

---

## Using the Examples

### 1. Save Tool Definition

Copy any example tool definition above to a file named `tools.json`.

### 2. Choose Your Prefix (Recommended)

To avoid PyPI namespace conflicts, use a package prefix:

**AUTO (Recommended)**: Automatically detects your GitHub username
```bash
# Just add --prefix AUTO (or omit it, as AUTO is the default)
hitoshura25-mcp-server-generator-cli --project-name calculator --prefix AUTO ...
```

**Custom Prefix**: Use your own prefix
```bash
# Use your organization or brand name
hitoshura25-mcp-server-generator-cli --project-name calculator --prefix acme ...
# Generates: acme-calculator
```

**NONE**: No prefix (only if you have a truly unique name)
```bash
hitoshura25-mcp-server-generator-cli --project-name unique-tool-name --prefix NONE ...
```

### 3. Generate the Project

Run the generator command shown in each example, adding your chosen prefix option.

### 4. Implement Business Logic

Navigate to the generated project and implement the TODO stubs:

```bash
# If using prefix "username" and project "calculator"
cd username-calculator
```

Edit `username_calculator/generator.py` and replace TODOs with actual implementation.

### 5. Run Tests

```bash
pytest
```

### 6. Install and Use

```bash
# Install locally
pip install -e .

# Use as MCP server (with prefix "username" and project "calculator")
mcp-username-calculator

# Or use CLI mode
username-calculator --help
```

### 7. Configure in Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "username-calculator": {
      "command": "mcp-username-calculator"
    }
  }
}
```

## Tips for Creating Your Own Examples

### Start Simple

Begin with 1-2 tools and add more as needed.

### Clear Descriptions

Make tool and parameter descriptions clear and specific.

### Proper Types

Use appropriate types for parameters:
- `string` for text, paths, identifiers
- `number` for counts, amounts, IDs
- `boolean` for flags
- `array` for lists
- `object` for structured data

### Validation

Add validation in your implementation:
```python
def my_tool(param: str) -> dict:
    """My tool implementation."""
    if not param:
        raise ValueError("Parameter cannot be empty")

    # Your logic here
    return {"result": "success"}
```

### Error Handling

Handle errors gracefully:
```python
def risky_operation(data: str) -> dict:
    """Operation that might fail."""
    try:
        # Your logic
        result = process(data)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Documentation

Document your implementation:
```python
def complex_function(x: int, y: str) -> dict:
    """
    Perform complex operation.

    Args:
        x: Integer input between 1-100
        y: String identifier (alphanumeric only)

    Returns:
        Dictionary with 'status' and 'data' keys

    Raises:
        ValueError: If x is out of range
        TypeError: If y contains invalid characters
    """
    pass
```

## Real-World Use Cases

### For AI Agents

- **Code Analysis**: Parse and analyze code files
- **Data Processing**: Transform and validate data
- **API Integration**: Wrap external APIs
- **Content Generation**: Generate templates or boilerplate

### For Developers

- **Automation**: Automate repetitive tasks
- **DevOps**: System monitoring and management
- **Testing**: Test data generation
- **Utilities**: Project-specific utility tools

## Next Steps

1. **Try an Example**: Generate one of the example servers
2. **Customize It**: Modify the tool definition for your needs
3. **Implement Logic**: Add your business logic
4. **Test Thoroughly**: Write tests for your implementation
5. **Share**: Publish to PyPI or share with your team

## Resources

- **Main Documentation**: [README.md](./README.md)
- **MCP Configuration**: [MCP-USAGE.md](./MCP-USAGE.md)
- **Contributing**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Test Plan**: [PHASE_4_TEST_PLAN.md](./PHASE_4_TEST_PLAN.md)

## Get Help

- **Questions**: Open a [Discussion](https://github.com/hitoshura25/mcp-server-generator/discussions)
- **Issues**: Report [Issues](https://github.com/hitoshura25/mcp-server-generator/issues)
- **Examples**: Share your examples in Discussions

---

**Happy generating!** 🚀
