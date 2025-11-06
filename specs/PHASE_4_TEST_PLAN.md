# Phase 4: Test Implementation Plan
## Comprehensive Unit Tests for mcp-server-generator

**Status**: Ready to Implement
**Estimated Time**: 3-4 hours
**Reference**: Based on pypi-workflow-generator test patterns

---

## Overview

We need to create actual unit tests for mcp-server-generator itself. Currently, we have:
- ✅ Templates that generate tests for other projects
- ❌ No tests for mcp-server-generator's own code

This plan details all test cases needed to achieve comprehensive coverage.

---

## Test Structure

Following pypi-workflow-generator's proven pattern:

```
mcp_server_generator/tests/
├── __init__.py                  # Already exists
├── test_generator.py            # ← TO CREATE (~8 tests)
├── test_server.py               # ← TO CREATE (~11 tests)
├── test_cli.py                  # ← TO CREATE (~5 tests)
└── test_templates.py            # ← TO CREATE (~3 tests)
```

**Total Target**: 27+ tests

---

## 1. test_generator.py (Core Business Logic)

### Test Cases

#### 1.1 validate_project_name()

```python
def test_validate_project_name_valid():
    """Test valid project names."""
    assert validate_project_name('my-mcp-server') == True
    assert validate_project_name('my_mcp_server') == True
    assert validate_project_name('mcp123') == True
    assert validate_project_name('abc') == True

def test_validate_project_name_invalid():
    """Test invalid project names."""
    # Keywords
    assert validate_project_name('class') == False
    assert validate_project_name('import') == False

    # Invalid characters
    assert validate_project_name('123-invalid') == False
    assert validate_project_name('my server') == False
    assert validate_project_name('my.server') == False

    # Empty
    assert validate_project_name('') == False
```

#### 1.2 validate_tool_name()

```python
def test_validate_tool_name_valid():
    """Test valid tool names."""
    assert validate_tool_name('my_function') == True
    assert validate_tool_name('test') == True
    assert validate_tool_name('func123') == True

def test_validate_tool_name_invalid():
    """Test invalid tool names."""
    assert validate_tool_name('class') == False  # keyword
    assert validate_tool_name('my-function') == False  # hyphen
    assert validate_tool_name('123func') == False  # starts with number
    assert validate_tool_name('') == False
```

#### 1.3 generate_tool_schema()

```python
def test_generate_tool_schema_basic():
    """Test basic tool schema generation."""
    tool_def = {
        'name': 'test_tool',
        'description': 'Test tool',
        'parameters': [
            {'name': 'param1', 'type': 'string', 'description': 'First param', 'required': True}
        ]
    }

    schema = generate_tool_schema(tool_def)

    assert schema['name'] == 'test_tool'
    assert schema['description'] == 'Test tool'
    assert 'inputSchema' in schema
    assert 'param1' in schema['inputSchema']['properties']
    assert schema['inputSchema']['properties']['param1']['type'] == 'string'
    assert 'param1' in schema['inputSchema']['required']

def test_generate_tool_schema_type_mapping():
    """Test type mapping from various formats."""
    tool_def = {
        'name': 'test',
        'description': 'Test',
        'parameters': [
            {'name': 'str_param', 'type': 'str', 'required': False},
            {'name': 'int_param', 'type': 'int', 'required': False},
            {'name': 'bool_param', 'type': 'bool', 'required': False},
        ]
    }

    schema = generate_tool_schema(tool_def)

    assert schema['inputSchema']['properties']['str_param']['type'] == 'string'
    assert schema['inputSchema']['properties']['int_param']['type'] == 'number'
    assert schema['inputSchema']['properties']['bool_param']['type'] == 'boolean'
```

#### 1.4 sanitize_description()

```python
def test_sanitize_description():
    """Test description sanitization prevents template injection."""
    assert sanitize_description('Hello {world}') == 'Hello {{world}}'
    assert sanitize_description('Test {{var}}') == 'Test {{{{var}}}}'
    assert sanitize_description('Normal text') == 'Normal text'
```

#### 1.5 generate_mcp_server()

```python
def test_generate_mcp_server_success(tmp_path):
    """Test successful project generation."""
    tools = [
        {
            "name": "test_func",
            "description": "Test function",
            "parameters": [
                {"name": "arg1", "type": "string", "description": "Arg 1", "required": True}
            ]
        }
    ]

    result = generate_mcp_server(
        project_name="test-server",
        description="Test MCP server",
        author="Test Author",
        author_email="test@example.com",
        tools=tools,
        output_dir=str(tmp_path)
    )

    assert result['success'] == True
    assert 'project_path' in result
    assert 'files_created' in result
    assert len(result['files_created']) > 0

    # Verify project exists
    project_path = tmp_path / "test-server"
    assert project_path.exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "setup.py").exists()

def test_generate_mcp_server_invalid_project_name():
    """Test that invalid project names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid project name"):
        generate_mcp_server(
            project_name="class",  # Python keyword
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "test", "description": "test", "parameters": []}]
        )

def test_generate_mcp_server_invalid_tool_name():
    """Test that invalid tool names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid tool name"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "my-tool", "description": "test", "parameters": []}]  # hyphen invalid
        )

def test_generate_mcp_server_no_tools():
    """Test that empty tools list raises ValueError."""
    with pytest.raises(ValueError, match="At least one tool"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[]
        )

def test_generate_mcp_server_existing_directory(tmp_path):
    """Test that existing directory raises FileExistsError."""
    # Create the directory first
    (tmp_path / "test-server").mkdir()

    with pytest.raises(FileExistsError, match="Directory already exists"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "test", "description": "test", "parameters": []}],
            output_dir=str(tmp_path)
        )
```

**Expected: 8 tests**

---

## 2. test_server.py (MCP Server Protocol)

### Test Cases

Following pypi-workflow-generator's comprehensive MCP testing:

#### 2.1 List Tools

```python
@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that handle_list_tools returns correct tool definitions."""
    server = MCPServer()
    result = await server.handle_list_tools()

    assert "tools" in result
    assert len(result["tools"]) == 2

    tool_names = [tool["name"] for tool in result["tools"]]
    assert "generate_mcp_server" in tool_names
    assert "validate_project_name" in tool_names

@pytest.mark.asyncio
async def test_list_tools_schema_validation():
    """Test that tool schemas are properly defined."""
    server = MCPServer()
    result = await server.handle_list_tools()

    # Verify each tool has required fields
    for tool in result["tools"]:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert "type" in tool["inputSchema"]
        assert "properties" in tool["inputSchema"]

    # Check generate_mcp_server schema
    gen_tool = next(t for t in result["tools"] if t["name"] == "generate_mcp_server")
    assert "project_name" in gen_tool["inputSchema"]["properties"]
    assert "description" in gen_tool["inputSchema"]["properties"]
    assert "author" in gen_tool["inputSchema"]["properties"]
    assert "tools" in gen_tool["inputSchema"]["properties"]
    assert set(gen_tool["inputSchema"]["required"]) == {
        "project_name", "description", "author", "author_email", "tools"
    }

    # Check validate_project_name schema
    val_tool = next(t for t in result["tools"] if t["name"] == "validate_project_name")
    assert "name" in val_tool["inputSchema"]["properties"]
    assert val_tool["inputSchema"]["required"] == ["name"]
```

#### 2.2 Call Tool - generate_mcp_server

```python
@pytest.mark.asyncio
async def test_call_tool_generate_mcp_server(tmp_path):
    """Test calling generate_mcp_server tool via MCP."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "generate_mcp_server",
        {
            "project_name": "test-mcp",
            "description": "Test MCP server",
            "author": "Test Author",
            "author_email": "test@example.com",
            "tools": [
                {
                    "name": "test_tool",
                    "description": "Test tool",
                    "parameters": []
                }
            ],
            "output_dir": str(tmp_path)
        }
    )

    assert "content" in result
    assert len(result["content"]) > 0
    assert result["content"][0]["type"] == "text"
    assert result.get("isError") == False

    # Verify project was created
    assert (tmp_path / "test-mcp").exists()

@pytest.mark.asyncio
async def test_call_tool_generate_mcp_server_with_options(tmp_path):
    """Test generate_mcp_server with custom options."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "generate_mcp_server",
        {
            "project_name": "custom-mcp",
            "description": "Custom MCP server",
            "author": "Test",
            "author_email": "test@test.com",
            "tools": [{"name": "func", "description": "Function", "parameters": []}],
            "output_dir": str(tmp_path),
            "python_version": "3.11"
        }
    )

    assert result.get("isError") == False

    # Verify custom Python version in generated files
    setup_content = (tmp_path / "custom-mcp" / "setup.py").read_text()
    assert "3.11" in setup_content

@pytest.mark.asyncio
async def test_call_tool_generate_mcp_server_invalid_name():
    """Test that invalid project name returns error."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "generate_mcp_server",
        {
            "project_name": "class",  # Invalid
            "description": "Test",
            "author": "Test",
            "author_email": "test@test.com",
            "tools": [{"name": "test", "description": "Test", "parameters": []}]
        }
    )

    assert result.get("isError") == True
    assert "Invalid project name" in result["content"][0]["text"]
```

#### 2.3 Call Tool - validate_project_name

```python
@pytest.mark.asyncio
async def test_call_tool_validate_project_name_valid():
    """Test validating a valid project name."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "validate_project_name",
        {"name": "my-mcp-server"}
    )

    assert result.get("isError") == False
    assert "content" in result

    import json
    data = json.loads(result["content"][0]["text"])
    assert data["valid"] == True
    assert data["name"] == "my-mcp-server"

@pytest.mark.asyncio
async def test_call_tool_validate_project_name_invalid():
    """Test validating an invalid project name."""
    server = MCPServer()

    result = await server.handle_call_tool(
        "validate_project_name",
        {"name": "class"}  # Python keyword
    )

    assert result.get("isError") == False

    import json
    data = json.loads(result["content"][0]["text"])
    assert data["valid"] == False
```

#### 2.4 Error Handling

```python
@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool returns error."""
    server = MCPServer()

    result = await server.handle_call_tool("unknown_tool", {})

    assert result.get("isError") == True
    assert "Unknown tool" in result["content"][0]["text"]

@pytest.mark.asyncio
async def test_handle_request_unknown_method():
    """Test handling unknown method returns error."""
    server = MCPServer()

    request = {
        "method": "unknown/method",
        "params": {}
    }

    response = await server.handle_request(request)

    assert "error" in response
    assert response["error"]["code"] == -32601
    assert "Method not found" in response["error"]["message"]
```

#### 2.5 Full Request Handling

```python
@pytest.mark.asyncio
async def test_handle_request_list_tools():
    """Test handling a full JSON-RPC request for tools/list."""
    server = MCPServer()

    request = {
        "method": "tools/list",
        "id": 1
    }

    response = await server.handle_request(request)

    assert "tools" in response
    assert len(response["tools"]) == 2

@pytest.mark.asyncio
async def test_handle_request_call_tool():
    """Test handling a full JSON-RPC request for tools/call."""
    server = MCPServer()

    request = {
        "method": "tools/call",
        "id": 2,
        "params": {
            "name": "validate_project_name",
            "arguments": {"name": "test-server"}
        }
    }

    response = await server.handle_request(request)

    assert "content" in response
    assert response.get("isError") == False
```

#### 2.6 Imports

```python
def test_mcp_server_imports():
    """Test that MCP server can be imported successfully."""
    from mcp_server_generator.server import MCPServer, main

    assert MCPServer is not None
    assert main is not None
    assert callable(main)
```

**Expected: 11 tests**

---

## 3. test_cli.py (CLI Interface)

### Test Cases

#### 3.1 Load Tools from File

```python
def test_load_tools_from_json(tmp_path):
    """Test loading tools from JSON file."""
    from mcp_server_generator.cli import load_tools_from_file

    tools_file = tmp_path / "tools.json"
    tools_file.write_text('''
    {
        "tools": [
            {"name": "test", "description": "Test", "parameters": []}
        ]
    }
    ''')

    tools = load_tools_from_file(str(tools_file))

    assert "tools" in tools
    assert len(tools["tools"]) == 1
    assert tools["tools"][0]["name"] == "test"

def test_load_tools_from_file_not_found():
    """Test that missing file raises FileNotFoundError."""
    from mcp_server_generator.cli import load_tools_from_file

    with pytest.raises(FileNotFoundError):
        load_tools_from_file("/nonexistent/file.json")

def test_load_tools_from_file_invalid_format():
    """Test that invalid file format raises ValueError."""
    from mcp_server_generator.cli import load_tools_from_file
    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'test')
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="must be .json"):
            load_tools_from_file(temp_path)
    finally:
        os.unlink(temp_path)
```

#### 3.2 CLI Main Function

```python
def test_cli_main_with_all_args(tmp_path, monkeypatch):
    """Test CLI main with all required arguments."""
    from mcp_server_generator.cli import main

    tools_file = tmp_path / "tools.json"
    tools_file.write_text('{"tools": [{"name": "test", "description": "Test", "parameters": []}]}')

    monkeypatch.setattr('sys.argv', [
        'mcp-server-generator-cli',
        '--project-name', 'cli-test',
        '--description', 'CLI test',
        '--author', 'Test',
        '--email', 'test@test.com',
        '--tools-file', str(tools_file),
        '--output-dir', str(tmp_path)
    ])

    result = main()

    assert result == 0
    assert (tmp_path / "cli-test").exists()

def test_cli_main_missing_args(monkeypatch):
    """Test that CLI fails with missing required arguments."""
    from mcp_server_generator.cli import main

    monkeypatch.setattr('sys.argv', ['mcp-server-generator-cli'])

    # Should exit with error (returns 2 for argparse errors)
    with pytest.raises(SystemExit):
        main()
```

#### 3.3 Imports

```python
def test_cli_imports():
    """Test that CLI can be imported successfully."""
    from mcp_server_generator.cli import main, load_tools_from_file, interactive_mode

    assert main is not None
    assert load_tools_from_file is not None
    assert interactive_mode is not None
```

**Expected: 5 tests**

---

## 4. test_templates.py (Template Validation)

### Test Cases

#### 4.1 Template Rendering

```python
def test_all_templates_render(tmp_path):
    """Test that all templates render without errors."""
    from jinja2 import Environment, FileSystemLoader
    from mcp_server_generator import generate_tool_schema

    template_dir = 'mcp_server_generator/templates/python'
    env = Environment(loader=FileSystemLoader(template_dir))

    context = {
        'project_name': 'test-server',
        'package_name': 'test_server',
        'description': 'Test server',
        'author': 'Test',
        'author_email': 'test@test.com',
        'python_version': '3.8',
        'license': 'Apache-2.0',
        'tools': [
            {
                'name': 'test_func',
                'description': 'Test',
                'parameters': [
                    {'name': 'arg', 'type': 'string', 'description': 'Arg', 'required': True}
                ]
            }
        ],
        'tool_schemas': [generate_tool_schema({
            'name': 'test_func',
            'description': 'Test',
            'parameters': [
                {'name': 'arg', 'type': 'string', 'description': 'Arg', 'required': True}
            ]
        })],
        'year': '2025',
    }

    templates = [
        'README.md.j2', 'LICENSE.j2', '.gitignore.j2', 'MCP-USAGE.md.j2',
        'setup.py.j2', 'pyproject.toml.j2', 'requirements.txt.j2', 'MANIFEST.in.j2',
        '__init__.py.j2', 'server.py.j2', 'cli.py.j2', 'generator.py.j2',
        'tests/__init__.py.j2', 'tests/test_server.py.j2', 'tests/test_generator.py.j2'
    ]

    for template_name in templates:
        template = env.get_template(template_name)
        content = template.render(**context)
        assert len(content) > 0, f"{template_name} rendered empty"
```

#### 4.2 Generated Code Syntax

```python
def test_generated_python_syntax(tmp_path):
    """Test that generated Python files have valid syntax."""
    from mcp_server_generator import generate_mcp_server
    import py_compile

    result = generate_mcp_server(
        project_name="syntax-test",
        description="Syntax test",
        author="Test",
        author_email="test@test.com",
        tools=[{"name": "test", "description": "Test", "parameters": []}],
        output_dir=str(tmp_path)
    )

    project_path = tmp_path / "syntax-test"

    # Find all Python files
    for py_file in project_path.rglob("*.py"):
        # Should compile without errors
        py_compile.compile(str(py_file), doraise=True)
```

#### 4.3 Generated Content

```python
def test_generated_files_contain_project_name(tmp_path):
    """Test that generated files contain the project name."""
    from mcp_server_generator import generate_mcp_server

    result = generate_mcp_server(
        project_name="content-test",
        description="Content test server",
        author="Test Author",
        author_email="test@test.com",
        tools=[{"name": "func", "description": "Function", "parameters": []}],
        output_dir=str(tmp_path)
    )

    project_path = tmp_path / "content-test"

    # Check README contains project name
    readme = (project_path / "README.md").read_text()
    assert "content-test" in readme

    # Check setup.py contains project name
    setup = (project_path / "setup.py").read_text()
    assert "content-test" in setup

    # Check author in LICENSE
    license_file = (project_path / "LICENSE").read_text()
    assert "Test Author" in license_file
```

**Expected: 3 tests**

---

## Success Criteria

### Minimum Requirements

✅ **At least 27 tests total**
- test_generator.py: 8+ tests
- test_server.py: 11+ tests
- test_cli.py: 5+ tests
- test_templates.py: 3+ tests

✅ **All tests pass**
- No failures
- No errors
- Proper async test handling

✅ **Proper test structure**
- Uses pytest
- Uses pytest-asyncio for async tests
- Uses tmp_path fixture for filesystem operations
- Follows pypi-workflow-generator patterns

✅ **Coverage of critical paths**
- All validation functions
- All MCP protocol methods
- Template rendering
- Error handling
- Edge cases

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server_generator --cov-report=term-missing

# Run specific test file
pytest mcp_server_generator/tests/test_generator.py -v

# Run async tests only
pytest -m asyncio
```

---

## Implementation Order

1. **test_generator.py** (Core logic, no async)
   - Easiest to start with
   - No dependencies on other components

2. **test_server.py** (MCP protocol)
   - Uses async/await
   - Tests integration of generator with MCP

3. **test_cli.py** (CLI interface)
   - Tests argument parsing
   - Tests file loading

4. **test_templates.py** (Template validation)
   - Tests template rendering
   - Tests generated code quality

---

## Reference: pypi-workflow-generator Test Stats

From the reference implementation:
- **Total tests**: 15
- **test_server.py**: 11 tests (all async)
- **test_generator.py**: 2 tests
- **test_init.py**: 1 test
- **test_release_workflow.py**: 1 test

Our goal: **27 tests** (80% more comprehensive)

---

## Next Steps

1. Create test files in order listed above
2. Run tests after each file
3. Fix any failures
4. Check coverage
5. Update main implementation plan with completion status

**Estimated time**: 3-4 hours for complete implementation and verification
