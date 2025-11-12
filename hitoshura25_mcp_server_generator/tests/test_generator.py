"""
Tests for core generation logic.
"""

import pytest
import os
from hitoshura25_mcp_server_generator.generator import (
    validate_project_name,
    validate_tool_name,
    generate_tool_schema,
    sanitize_description,
    generate_mcp_server,
)

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
    assert validate_project_name('for') == False

    # Invalid characters/start
    assert validate_project_name('123-invalid') == False
    assert validate_project_name('my server') == False
    assert validate_project_name('my.server') == False

    # Empty
    assert validate_project_name('') == False
    assert validate_project_name(None) == False


def test_validate_tool_name_valid():
    """Test valid tool names."""
    assert validate_tool_name('my_function') == True
    assert validate_tool_name('test') == True
    assert validate_tool_name('func123') == True
    assert validate_tool_name('_private') == True


def test_validate_tool_name_invalid():
    """Test invalid tool names."""
    assert validate_tool_name('class') == False  # keyword
    assert validate_tool_name('my-function') == False  # hyphen
    assert validate_tool_name('123func') == False  # starts with number
    assert validate_tool_name('') == False
    assert validate_tool_name(None) == False


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
            {'name': 'str_param', 'type': 'str', 'description': 'String param', 'required': False},
            {'name': 'int_param', 'type': 'int', 'description': 'Int param', 'required': False},
            {'name': 'bool_param', 'type': 'bool', 'description': 'Bool param', 'required': False},
            {'name': 'num_param', 'type': 'number', 'description': 'Number param', 'required': False},
        ]
    }

    schema = generate_tool_schema(tool_def)

    assert schema['inputSchema']['properties']['str_param']['type'] == 'string'
    assert schema['inputSchema']['properties']['int_param']['type'] == 'number'
    assert schema['inputSchema']['properties']['bool_param']['type'] == 'boolean'
    assert schema['inputSchema']['properties']['num_param']['type'] == 'number'
    
    # None should be required since all are False
    assert len(schema['inputSchema']['required']) == 0


def test_sanitize_description():
    """Test description sanitization prevents template injection."""
    assert sanitize_description('Hello {world}') == 'Hello {{world}}'
    assert sanitize_description('Test {{var}}') == 'Test {{{{var}}}}'
    assert sanitize_description('Normal text') == 'Normal text'
    assert sanitize_description('') == ''


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
        output_dir=str(tmp_path),
        prefix="NONE"
    )

    assert result['success']
    assert 'project_path' in result
    assert 'files_created' in result
    assert len(result['files_created']) > 0

    # Verify project exists
    project_path = tmp_path / "test-server"
    assert project_path.exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "setup.py").exists()
    assert (project_path / "test_server" / "server.py").exists()
    assert (project_path / "test_server" / "cli.py").exists()
    assert (project_path / "test_server" / "generator.py").exists()

    # Verify requirements.txt is NOT created (migration to pyproject.toml)
    assert not (project_path / "requirements.txt").exists()

    # Verify pyproject.toml contains dependencies
    pyproject_path = project_path / "pyproject.toml"
    assert pyproject_path.exists()
    pyproject_content = pyproject_path.read_text()
    assert "dependencies = [" in pyproject_content
    assert "mcp>=1.0.0,<2.0.0" in pyproject_content
    assert "[project.optional-dependencies]" in pyproject_content
    assert "pytest>=7.0.0" in pyproject_content
    assert "pytest-asyncio>=0.21.0" in pyproject_content


def test_generate_mcp_server_invalid_project_name():
    """Test that invalid project names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid project name"):
        generate_mcp_server(
            project_name="class",  # Python keyword
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "test", "description": "test", "parameters": []}],
            prefix="NONE"
        )


def test_generate_mcp_server_invalid_tool_name():
    """Test that invalid tool names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid tool name"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[{"name": "my-tool", "description": "test", "parameters": []}],  # hyphen invalid
            prefix="NONE"
        )


def test_generate_mcp_server_no_tools():
    """Test that empty tools list raises ValueError."""
    with pytest.raises(ValueError, match="At least one tool"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[],
            prefix="NONE"
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
            output_dir=str(tmp_path),
            prefix="NONE"
        )


def test_generate_mcp_server_python_version_minimum(tmp_path):
    """Test that Python version is enforced to minimum 3.10."""
    # Try to create a project with Python 3.9 (below minimum)
    result = generate_mcp_server(
        project_name="test-old-python",
        description="Test",
        author="Test",
        author_email="test@test.com",
        tools=[{"name": "test", "description": "Test", "parameters": []}],
        output_dir=str(tmp_path),
        python_version="3.9",  # Below minimum
        prefix="NONE"
    )

    assert result["success"]

    # Should have enforced minimum 3.10
    pyproject_path = tmp_path / "test-old-python" / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert "requires-python = \">=3.10\"" in pyproject_content
    assert "requires-python = \">=3.9\"" not in pyproject_content


def test_generate_mcp_server_python_version_custom(tmp_path):
    """Test that custom Python version above 3.10 is honored."""
    result = generate_mcp_server(
        project_name="test-new-python",
        description="Test",
        author="Test",
        author_email="test@test.com",
        tools=[{"name": "test", "description": "Test", "parameters": []}],
        output_dir=str(tmp_path),
        python_version="3.12",  # Above minimum
        prefix="NONE"
    )

    assert result["success"]

    # Should use the specified version
    pyproject_path = tmp_path / "test-new-python" / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert "requires-python = \">=3.12\"" in pyproject_content


def test_generate_mcp_server_in_place(tmp_path):
    """Test in-place generation with output_dir='.'"""
    # Change to temp directory
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = generate_mcp_server(
            project_name="test-server",
            description="Test MCP server",
            author="Test Author",
            author_email="test@example.com",
            tools=[{"name": "test_func", "description": "Test function", "parameters": []}],
            output_dir=".",  # In-place generation
            prefix="NONE"
        )

        assert result['success']

        # Files should be in tmp_path directly, not in a subdirectory
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "test_server" / "server.py").exists()
        assert (tmp_path / ".github" / "workflows" / "release.yml").exists()

        # Verify project_path is the current directory
        assert result['project_path'] == str(tmp_path)

    finally:
        os.chdir(original_dir)


def test_generate_mcp_server_in_place_conflict(tmp_path):
    """Test that in-place generation fails if critical files exist."""

    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create a critical file
        (tmp_path / "pyproject.toml").write_text("existing content")

        with pytest.raises(FileExistsError, match="critical files exist"):
            generate_mcp_server(
                project_name="test-server",
                description="Test",
                author="Test",
                author_email="test@example.com",
                tools=[{"name": "test", "description": "test", "parameters": []}],
                output_dir=".",
                prefix="NONE"
            )
    finally:
        os.chdir(original_dir)


def test_generate_mcp_server_with_output_dir(tmp_path):
    """Test that non-'.' output_dir creates subdirectory."""
    result = generate_mcp_server(
        project_name="test-server",
        description="Test",
        author="Test",
        author_email="test@example.com",
        tools=[{"name": "test", "description": "test", "parameters": []}],
        output_dir=str(tmp_path),
        prefix="NONE"
    )

    assert result['success']

    # Should create subdirectory
    project_dir = tmp_path / "test-server"
    assert project_dir.exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "pyproject.toml").exists()


def test_merge_gitignore_new_entries(tmp_path):
    """Test merging .gitignore adds unique entries."""
    from hitoshura25_mcp_server_generator.generator import merge_gitignore

    existing = tmp_path / ".gitignore"
    existing.write_text("*.pyc\n__pycache__/\n")

    template = "*.pyc\n__pycache__/\n.venv/\ndist/\n"

    result = merge_gitignore(str(existing), template)

    assert result['added'] == 2  # .venv/ and dist/
    assert result['skipped'] > 0

    content = existing.read_text()
    assert '.venv/' in content
    assert 'dist/' in content
    # Original content preserved
    assert '*.pyc' in content
    assert '__pycache__/' in content


def test_merge_gitignore_no_duplicates(tmp_path):
    """Test merging .gitignore avoids duplicates."""
    from hitoshura25_mcp_server_generator.generator import merge_gitignore

    existing = tmp_path / ".gitignore"
    existing.write_text("*.pyc\n.venv/\n")

    template = "*.pyc\n.venv/\n"

    result = merge_gitignore(str(existing), template)

    assert result['added'] == 0

    content = existing.read_text()
    # Should not have duplicate entries
    assert content.count('*.pyc') == 1
    assert content.count('.venv/') == 1


def test_merge_manifest(tmp_path):
    """Test merging MANIFEST.in adds unique patterns."""
    from hitoshura25_mcp_server_generator.generator import merge_manifest

    existing = tmp_path / "MANIFEST.in"
    existing.write_text("include README.md\ninclude LICENSE\n")

    template = "include README.md\ninclude LICENSE\ninclude *.txt\n"

    result = merge_manifest(str(existing), template)

    assert result['added'] == 1  # include *.txt
    assert result['skipped'] > 0

    content = existing.read_text()
    assert 'include *.txt' in content
    assert 'include README.md' in content
    assert 'include LICENSE' in content


def test_append_to_readme(tmp_path):
    """Test appending to README with delimiters."""
    from hitoshura25_mcp_server_generator.generator import append_to_readme

    existing = tmp_path / "README.md"
    existing.write_text("# My Project\n\nCustom content here.\n")

    template = "## Generated Section\n\nThis is generated.\n"

    result = append_to_readme(str(existing), template, "test-project")

    assert result['appended'] == True
    assert result['line_number'] > 0

    content = existing.read_text()
    assert "Custom content here" in content  # Preserved
    assert "Generated Section" in content  # Added
    assert "MCP-GENERATOR-CONTENT-START" in content  # Delimiter
    assert "MCP-GENERATOR-CONTENT-END" in content


def test_append_to_readme_already_appended(tmp_path):
    """Test that appending twice doesn't duplicate."""
    from hitoshura25_mcp_server_generator.generator import append_to_readme

    existing = tmp_path / "README.md"
    content = "# Test\n<!-- MCP-GENERATOR-CONTENT-START:test-project -->\nOld\n<!-- MCP-GENERATOR-CONTENT-END:test-project -->\n"
    existing.write_text(content)

    template = "New content\n"

    result = append_to_readme(str(existing), template, "test-project")

    assert result['appended'] == False
    assert 'Already contains' in result['reason']


def test_append_to_mcp_usage(tmp_path):
    """Test appending to MCP-USAGE.md with delimiters."""
    from hitoshura25_mcp_server_generator.generator import append_to_mcp_usage

    existing = tmp_path / "MCP-USAGE.md"
    existing.write_text("# Usage\n\nCustom usage here.\n")

    template = "## Generated Usage\n\nThis is generated.\n"

    result = append_to_mcp_usage(str(existing), template, "test-project")

    assert result['appended'] == True
    assert result['line_number'] > 0

    content = existing.read_text()
    assert "Custom usage here" in content  # Preserved
    assert "Generated Usage" in content  # Added
    assert "MCP-GENERATOR-USAGE-START" in content  # Delimiter
    assert "MCP-GENERATOR-USAGE-END" in content


def test_generate_with_smart_merge(tmp_path):
    """Test full generation with smart merge."""
    # Create existing files
    (tmp_path / ".gitignore").write_text("*.pyc\n")
    (tmp_path / "README.md").write_text("# Custom README\n\nMy custom content.\n")
    (tmp_path / "LICENSE").write_text("MIT License\nCustom text\n")

    # Change to temp directory for in-place generation
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@test.com",
            tools=[{"name": "test", "description": "Test", "parameters": []}],
            output_dir=".",
            prefix="NONE"
        )

        assert result['success']
        assert len(result['files_merged']) > 0  # .gitignore merged
        assert len(result['files_appended']) > 0  # README appended
        assert len(result['files_skipped']) > 0  # LICENSE skipped

        # Verify .gitignore was merged
        gitignore = (tmp_path / ".gitignore").read_text()
        assert "*.pyc" in gitignore  # Original preserved

        # Verify README was appended
        readme = (tmp_path / "README.md").read_text()
        assert "Custom README" in readme  # Original preserved
        assert "My custom content" in readme
        assert "MCP-GENERATOR-CONTENT" in readme  # New content added

        # Verify LICENSE was skipped (not overwritten)
        license_file = (tmp_path / "LICENSE").read_text()
        assert "Custom text" in license_file

    finally:
        os.chdir(original_dir)


def test_generate_errors_on_critical_files(tmp_path):
    """Test that critical files still cause errors."""
    # Change to temp dir
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create critical file
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        with pytest.raises(FileExistsError, match="critical files exist"):
            generate_mcp_server(
                project_name="test-server",
                description="Test",
                author="Test",
                author_email="test@test.com",
                tools=[{"name": "test", "description": "Test", "parameters": []}],
                output_dir=".",
                prefix="NONE"
            )
    finally:
        os.chdir(original_dir)
