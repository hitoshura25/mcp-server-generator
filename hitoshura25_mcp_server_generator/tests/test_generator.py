"""
Tests for core generation logic.
"""

import pytest
import os
import subprocess
import sys
import zipfile
from hitoshura25_mcp_server_generator.generator import (
    validate_project_name,
    validate_tool_name,
    generate_tool_schema,
    sanitize_description,
    generate_mcp_server,
)


def test_validate_project_name_valid():
    """Test valid project names."""
    assert validate_project_name("my-mcp-server")
    assert validate_project_name("my_mcp_server")
    assert validate_project_name("mcp123")
    assert validate_project_name("abc")


def test_validate_project_name_invalid():
    """Test invalid project names."""
    # Keywords
    assert not validate_project_name("class")
    assert not validate_project_name("import")
    assert not validate_project_name("for")

    # Invalid characters/start
    assert not validate_project_name("123-invalid")
    assert not validate_project_name("my server")
    assert not validate_project_name("my.server")

    # Empty
    assert not validate_project_name("")
    assert not validate_project_name(None)


def test_validate_tool_name_valid():
    """Test valid tool names."""
    assert validate_tool_name("my_function")
    assert validate_tool_name("test")
    assert validate_tool_name("func123")
    assert validate_tool_name("_private")


def test_validate_tool_name_invalid():
    """Test invalid tool names."""
    assert not validate_tool_name("class")  # keyword
    assert not validate_tool_name("my-function")  # hyphen
    assert not validate_tool_name("123func")  # starts with number
    assert not validate_tool_name("")
    assert not validate_tool_name(None)


def test_generate_tool_schema_basic():
    """Test basic tool schema generation."""
    tool_def = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": [
            {
                "name": "param1",
                "type": "string",
                "description": "First param",
                "required": True,
            }
        ],
    }

    schema = generate_tool_schema(tool_def)

    assert schema["name"] == "test_tool"
    assert schema["description"] == "Test tool"
    assert "inputSchema" in schema
    assert "param1" in schema["inputSchema"]["properties"]
    assert schema["inputSchema"]["properties"]["param1"]["type"] == "string"
    assert "param1" in schema["inputSchema"]["required"]


def test_generate_tool_schema_type_mapping():
    """Test type mapping from various formats."""
    tool_def = {
        "name": "test",
        "description": "Test",
        "parameters": [
            {
                "name": "str_param",
                "type": "str",
                "description": "String param",
                "required": False,
            },
            {
                "name": "int_param",
                "type": "int",
                "description": "Int param",
                "required": False,
            },
            {
                "name": "bool_param",
                "type": "bool",
                "description": "Bool param",
                "required": False,
            },
            {
                "name": "num_param",
                "type": "number",
                "description": "Number param",
                "required": False,
            },
        ],
    }

    schema = generate_tool_schema(tool_def)

    assert schema["inputSchema"]["properties"]["str_param"]["type"] == "string"
    assert schema["inputSchema"]["properties"]["int_param"]["type"] == "number"
    assert schema["inputSchema"]["properties"]["bool_param"]["type"] == "boolean"
    assert schema["inputSchema"]["properties"]["num_param"]["type"] == "number"

    # None should be required since all are False
    assert len(schema["inputSchema"]["required"]) == 0


def test_sanitize_description():
    """Test description sanitization prevents template injection."""
    assert sanitize_description("Hello {world}") == "Hello {{world}}"
    assert sanitize_description("Test {{var}}") == "Test {{{{var}}}}"
    assert sanitize_description("Normal text") == "Normal text"
    assert sanitize_description("") == ""


def test_generate_mcp_server_success(tmp_path):
    """Test successful project generation."""
    tools = [
        {
            "name": "test_func",
            "description": "Test function",
            "parameters": [
                {
                    "name": "arg1",
                    "type": "string",
                    "description": "Arg 1",
                    "required": True,
                }
            ],
        }
    ]

    result = generate_mcp_server(
        project_name="test-server",
        description="Test MCP server",
        author="Test Author",
        author_email="test@example.com",
        tools=tools,
        output_dir=str(tmp_path),
        prefix="NONE",
    )

    assert result["success"]
    assert "project_path" in result
    assert "files_created" in result
    assert len(result["files_created"]) > 0

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
            prefix="NONE",
        )


def test_generate_mcp_server_invalid_tool_name():
    """Test that invalid tool names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid tool name"):
        generate_mcp_server(
            project_name="test-server",
            description="Test",
            author="Test",
            author_email="test@example.com",
            tools=[
                {"name": "my-tool", "description": "test", "parameters": []}
            ],  # hyphen invalid
            prefix="NONE",
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
            prefix="NONE",
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
            prefix="NONE",
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
        prefix="NONE",
    )

    assert result["success"]

    # Should have enforced minimum 3.10
    pyproject_path = tmp_path / "test-old-python" / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert 'requires-python = ">=3.10"' in pyproject_content
    assert 'requires-python = ">=3.9"' not in pyproject_content


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
        prefix="NONE",
    )

    assert result["success"]

    # Should use the specified version
    pyproject_path = tmp_path / "test-new-python" / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert 'requires-python = ">=3.12"' in pyproject_content


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
            tools=[
                {"name": "test_func", "description": "Test function", "parameters": []}
            ],
            output_dir=".",  # In-place generation
            prefix="NONE",
        )

        assert result["success"]

        # Files should be in tmp_path directly, not in a subdirectory
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "test_server" / "server.py").exists()
        assert (tmp_path / ".github" / "workflows" / "release.yml").exists()

        # Verify project_path is the current directory
        assert result["project_path"] == str(tmp_path)

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
                prefix="NONE",
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
        prefix="NONE",
    )

    assert result["success"]

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

    assert result["added"] == 2  # .venv/ and dist/
    assert result["skipped"] > 0

    content = existing.read_text()
    assert ".venv/" in content
    assert "dist/" in content
    # Original content preserved
    assert "*.pyc" in content
    assert "__pycache__/" in content


def test_merge_gitignore_no_duplicates(tmp_path):
    """Test merging .gitignore avoids duplicates."""
    from hitoshura25_mcp_server_generator.generator import merge_gitignore

    existing = tmp_path / ".gitignore"
    existing.write_text("*.pyc\n.venv/\n")

    template = "*.pyc\n.venv/\n"

    result = merge_gitignore(str(existing), template)

    assert result["added"] == 0

    content = existing.read_text()
    # Should not have duplicate entries
    assert content.count("*.pyc") == 1
    assert content.count(".venv/") == 1


def test_merge_manifest(tmp_path):
    """Test merging MANIFEST.in adds unique patterns."""
    from hitoshura25_mcp_server_generator.generator import merge_manifest

    existing = tmp_path / "MANIFEST.in"
    existing.write_text("include README.md\ninclude LICENSE\n")

    template = "include README.md\ninclude LICENSE\ninclude *.txt\n"

    result = merge_manifest(str(existing), template)

    assert result["added"] == 1  # include *.txt
    assert result["skipped"] > 0

    content = existing.read_text()
    assert "include *.txt" in content
    assert "include README.md" in content
    assert "include LICENSE" in content


def test_append_to_readme(tmp_path):
    """Test appending to README with delimiters."""
    from hitoshura25_mcp_server_generator.generator import append_to_readme

    existing = tmp_path / "README.md"
    existing.write_text("# My Project\n\nCustom content here.\n")

    template = "## Generated Section\n\nThis is generated.\n"

    result = append_to_readme(str(existing), template, "test-project")

    assert result["appended"]
    assert result["line_number"] > 0

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

    assert not result["appended"]
    assert "Already contains" in result["reason"]


def test_append_to_mcp_usage(tmp_path):
    """Test appending to MCP-USAGE.md with delimiters."""
    from hitoshura25_mcp_server_generator.generator import append_to_mcp_usage

    existing = tmp_path / "MCP-USAGE.md"
    existing.write_text("# Usage\n\nCustom usage here.\n")

    template = "## Generated Usage\n\nThis is generated.\n"

    result = append_to_mcp_usage(str(existing), template, "test-project")

    assert result["appended"]
    assert result["line_number"] > 0

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
            prefix="NONE",
        )

        assert result["success"]
        assert len(result["files_merged"]) > 0  # .gitignore merged
        assert len(result["files_appended"]) > 0  # README appended
        assert len(result["files_skipped"]) > 0  # LICENSE skipped

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
                prefix="NONE",
            )
    finally:
        os.chdir(original_dir)


def test_generated_project_builds(tmp_path):
    """Test that a generated project can be built successfully."""
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Initialize git repo for setuptools_scm
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        # Generate a basic project
        result = generate_mcp_server(
            project_name="test-build-project",
            description="Test build project",
            author="Test Author",
            author_email="test@example.com",
            tools=[
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": [
                        {
                            "name": "param1",
                            "type": "string",
                            "description": "Test parameter",
                            "required": True,
                        }
                    ],
                }
            ],
            output_dir=".",
            prefix="NONE",
        )

        assert result["success"]

        # Disable gpg signing for test commits
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        # Commit files and create tag for setuptools_scm
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "tag", "0.1.0"], cwd=tmp_path, capture_output=True, check=True
        )

        # Install build dependencies
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "build"],
            check=True,
            capture_output=True,
        )

        # Build the project
        build_result = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Verify build succeeded
        assert build_result.returncode == 0, f"Build failed: {build_result.stderr}"
        assert (tmp_path / "dist").exists()

        # Verify distribution files were created
        dist_files = list((tmp_path / "dist").iterdir())
        assert len(dist_files) > 0, "No distribution files created"
        assert any(f.suffix == ".whl" for f in dist_files), "No wheel file created"
        assert any(f.suffix == ".gz" for f in dist_files), "No source distribution created"

    finally:
        os.chdir(original_dir)


def test_build_with_additional_directories(tmp_path):
    """Test that project builds successfully even with additional directories."""
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Initialize git repo for setuptools_scm
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        # Generate a basic project
        result = generate_mcp_server(
            project_name="test-extra-dirs",
            description="Test with extra directories",
            author="Test Author",
            author_email="test@example.com",
            tools=[
                {
                    "name": "calculate",
                    "description": "Calculate something",
                    "parameters": [],
                }
            ],
            output_dir=".",
            prefix="NONE",
        )

        assert result["success"]

        # Add common directories that should be excluded (use exist_ok for scripts)
        (tmp_path / "specs").mkdir(exist_ok=True)
        (tmp_path / "specs" / "implementation.md").write_text("# Implementation Spec")

        (tmp_path / "docs").mkdir(exist_ok=True)
        (tmp_path / "docs" / "guide.md").write_text("# User Guide")

        (tmp_path / "examples").mkdir(exist_ok=True)
        (tmp_path / "examples" / "example.py").write_text("# Example usage")

        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "deploy.sh").write_text("#!/bin/bash\necho 'deploy'")

        # Disable gpg signing for test commits
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        # Commit files and create tag for setuptools_scm
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "tag", "0.1.0"], cwd=tmp_path, capture_output=True, check=True
        )

        # Install build dependencies
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "build"],
            check=True,
            capture_output=True,
        )

        # Build the project
        build_result = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Verify build succeeded
        assert (
            build_result.returncode == 0
        ), f"Build failed with additional directories: {build_result.stderr}"
        assert (tmp_path / "dist").exists()

    finally:
        os.chdir(original_dir)


def test_package_only_includes_package_code(tmp_path):
    """Test that built distribution only includes the package, not extra directories."""
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Initialize git repo for setuptools_scm
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        # Generate project
        result = generate_mcp_server(
            project_name="test-package-contents",
            description="Test package contents",
            author="Test Author",
            author_email="test@example.com",
            tools=[{"name": "test_func", "description": "Test", "parameters": []}],
            output_dir=".",
            prefix="NONE",
        )

        assert result["success"]

        # Add directories that should be excluded
        (tmp_path / "specs").mkdir(exist_ok=True)
        (tmp_path / "specs" / "secret.txt").write_text("Should not be in package")

        (tmp_path / "private").mkdir()
        (tmp_path / "private" / "credentials.json").write_text('{"key": "secret"}')

        # Disable gpg signing for test commits
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )

        # Commit files and create tag for setuptools_scm
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "tag", "0.1.0"], cwd=tmp_path, capture_output=True, check=True
        )

        # Install build dependencies
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "build"],
            check=True,
            capture_output=True,
        )

        # Build the project
        subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Find the wheel file
        wheel_files = list((tmp_path / "dist").glob("*.whl"))
        assert len(wheel_files) > 0, "No wheel file created"
        wheel_file = wheel_files[0]

        # Extract and verify contents
        with zipfile.ZipFile(wheel_file, "r") as z:
            names = z.namelist()

        # Should include the package
        assert any(
            "test_package_contents/" in n for n in names
        ), "Package not found in wheel"

        # Should NOT include excluded directories
        assert not any("specs/" in n for n in names), "specs/ should be excluded"
        assert not any("private/" in n for n in names), "private/ should be excluded"
        assert not any("examples/" in n for n in names), "examples/ should be excluded"

    finally:
        os.chdir(original_dir)


def test_github_url_with_spaces_in_author(tmp_path):
    """Test that GitHub URLs are properly sanitized when author name has spaces."""
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Generate project with author name containing spaces
        result = generate_mcp_server(
            project_name="test-url-sanitization",
            description="Test URL sanitization",
            author="John Q. Public",
            author_email="john@example.com",
            tools=[{"name": "test_tool", "description": "Test", "parameters": []}],
            output_dir=".",
            prefix="NONE",
        )

        assert result["success"]

        # Read the generated pyproject.toml
        pyproject_content = (tmp_path / "pyproject.toml").read_text()

        # Verify URLs don't contain spaces
        assert "github.com/john-q-public/" in pyproject_content, (
            "GitHub URL should be sanitized (spaces replaced with hyphens)"
        )
        assert "John Q. Public" not in pyproject_content.split("[project.urls]")[1].split("\n")[0:4], (
            "Raw author name with spaces should not appear in URLs section"
        )

    finally:
        os.chdir(original_dir)
