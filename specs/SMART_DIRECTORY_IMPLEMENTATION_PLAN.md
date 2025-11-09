# Implementation Plan: Smart Directory Handling

## Problem Statement

Currently, the MCP server generator always creates a subdirectory for the generated project, even when `output_dir="."` is specified. This creates an awkward nested structure when users want to generate files into an existing repository.

**Current behavior:**
```
~/my-existing-repo/
  └── hitoshura25-my-project/    ← Unwanted subdirectory
      ├── pyproject.toml
      ├── .github/workflows/
      └── hitoshura25_my_project/
```

**Desired behavior:**
```
~/my-existing-repo/
  ├── pyproject.toml
  ├── .github/workflows/
  └── hitoshura25_my_project/
```

## Solution

When `output_dir="."`, generate files directly in the current directory without creating a subdirectory. This is intuitive because:
- `"."` explicitly signals "put it HERE in this directory"
- Any other path means "create a NEW project directory"

## Implementation Steps

### 1. Update `generator.py`

**Location:** `hitoshura25_mcp_server_generator/generator.py:213-227`

**Current code:**
```python
# Determine output directory
if output_dir is None:
    output_dir = os.getcwd()

project_path = os.path.join(output_dir, project_name)

# Check if directory exists
if os.path.exists(project_path):
    raise FileExistsError(...)
```

**New code:**
```python
# Determine output directory
if output_dir is None:
    output_dir = os.getcwd()

# Determine project path
# If output_dir is ".", generate in-place (current directory)
# Otherwise, create a subdirectory named after the project
if output_dir == ".":
    project_path = os.getcwd()
    # For in-place generation, check for conflicting files instead of directory
    conflicting_files = ['pyproject.toml', 'setup.py', 'README.md']
    existing = [f for f in conflicting_files if os.path.exists(os.path.join(project_path, f))]
    if existing:
        raise FileExistsError(
            f"Cannot generate in-place: conflicting files exist: {', '.join(existing)}\n"
            f"Solutions:\n"
            f"  1. Use a different output directory (don't use '.')\n"
            f"  2. Remove or backup the existing files\n"
            f"  3. Generate in a subdirectory by omitting --output-dir"
        )
else:
    project_path = os.path.join(output_dir, project_name)
    # Check if directory exists
    if os.path.exists(project_path):
        raise FileExistsError(
            f"Directory already exists: {project_path}\n"
            f"Solutions:\n"
            f"  1. Choose a different project name\n"
            f"  2. Remove the existing directory: rm -rf {project_path}\n"
            f"  3. Specify a different output directory with --output-dir"
        )
```

**Update docstring:** (around line 160)
```python
"""
Generate a complete MCP server project.

Args:
    project_name: Base project name (e.g., "my-mcp-server")
    description: Project description
    author: Author name
    author_email: Author email
    tools: List of tool definitions
    output_dir: Where to create project. Special cases:
               - None (default): Creates subdirectory in current directory
               - "." : Generates files directly in current directory (in-place)
               - Any other path: Creates subdirectory in specified path
    python_version: Python version for GitHub Actions workflows (default: "3.10").
                   Note: Package requires-python is always ">=3.10" (MCP SDK requirement).
    license_type: License type (default: "Apache-2.0")
    prefix: Prefix mode - "AUTO" (detect from git), custom string, or "NONE"

Returns:
    {
        "success": bool,
        "project_path": str,
        "files_created": List[str],
        "message": str
    }
"""
```

### 2. Update Tests

**Add new test in `hitoshura25_mcp_server_generator/tests/test_generator.py`:**

```python
def test_generate_mcp_server_in_place(tmp_path):
    """Test in-place generation with output_dir='.'"""
    # Change to temp directory
    import os
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

        assert result['success'] == True

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
    """Test that in-place generation fails if conflicting files exist."""
    import os
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create a conflicting file
        (tmp_path / "pyproject.toml").write_text("existing content")

        with pytest.raises(FileExistsError, match="conflicting files exist"):
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
```

**Update existing test to verify subdirectory behavior:**

```python
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

    assert result['success'] == True

    # Should create subdirectory
    project_dir = tmp_path / "test-server"
    assert project_dir.exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "pyproject.toml").exists()
```

### 3. Update `server.py` (MCP Tool)

**Location:** `hitoshura25_mcp_server_generator/server.py`

No changes needed - the MCP tool already passes `output_dir` through to `generate_mcp_server()`.

### 4. Update `cli.py`

**Location:** `hitoshura25_mcp_server_generator/cli.py`

Update the help text for `--output-dir` to document the new behavior:

```python
parser.add_argument(
    '--output-dir',
    help='Output directory. Use "." to generate in current directory (in-place), '
         'or specify a path to create a subdirectory (default: current directory)'
)
```

### 5. Dogfooding Test

After implementing the changes, test the updated generator on this project itself:

**Scenario 1: Test in-place generation (should fail with conflict)**
```bash
cd /tmp/test-dogfood
git clone <this-repo>
cd mcp-server-generator

# Try in-place generation - should fail because files exist
python -m hitoshura25_mcp_server_generator.server # call generate_mcp_server with output_dir="."
# Expected: FileExistsError about conflicting files
```

**Scenario 2: Test subdirectory generation (current behavior)**
```bash
cd /tmp/test-dogfood

# Generate in subdirectory (default behavior)
python -m hitoshura25_mcp_server_generator.cli \
  --project-name test-mcp \
  --description "Test" \
  --author "Test" \
  --email "test@test.com" \
  --tools-file tools.json \
  --output-dir /tmp/test-dogfood

# Expected: Creates /tmp/test-dogfood/test-mcp/ directory
ls -la /tmp/test-dogfood/test-mcp/
```

**Scenario 3: Test in-place generation (fresh directory)**
```bash
cd /tmp/test-dogfood-inplace
mkdir new-project
cd new-project
git init

# Generate in-place
python -m hitoshura25_mcp_server_generator.cli \
  --project-name my-mcp \
  --description "Test" \
  --author "Test" \
  --email "test@test.com" \
  --tools-file ../tools.json \
  --output-dir .

# Expected: Files generated directly in current directory
ls -la  # Should show pyproject.toml, .github/, etc.
```

### 6. Run Tests

```bash
cd /Users/vinayakmenon/mcp-server-generator
source venv/bin/activate
python -m pytest hitoshura25_mcp_server_generator/tests/ -v

# Should see:
# - All existing 65 tests pass
# - 2 new tests pass (in-place generation + conflict detection)
# Total: 67 tests
```

## Edge Cases to Handle

1. **Absolute path for output_dir** - Should create subdirectory (not in-place)
   - `output_dir="/tmp/foo"` → Creates `/tmp/foo/project-name/`

2. **Relative path (not ".")** - Should create subdirectory
   - `output_dir="./foo"` → Creates `./foo/project-name/`

3. **Workflow generation with in-place** - Must handle `os.chdir(project_path)` correctly
   - When `project_path` is current directory, `os.chdir()` is a no-op
   - This should work fine as-is

4. **Conflict detection** - Check for key files that would be overwritten
   - `pyproject.toml`, `setup.py`, `README.md`, `requirements.txt`
   - Allow generation if only `.git/` or other non-conflicting files exist

## Success Criteria

- ✅ `output_dir="."` generates files in current directory
- ✅ `output_dir=None` or `output_dir="/path"` creates subdirectory (existing behavior)
- ✅ In-place generation detects and prevents file conflicts
- ✅ All existing 65 tests pass
- ✅ 2 new tests pass (in-place generation scenarios)
- ✅ Dogfooding scenarios work as expected
- ✅ Documentation updated (docstrings, CLI help text)

## Files to Modify

1. `hitoshura25_mcp_server_generator/generator.py` - Core logic
2. `hitoshura25_mcp_server_generator/cli.py` - Help text
3. `hitoshura25_mcp_server_generator/tests/test_generator.py` - Tests

## Files to Review (no changes needed)

1. `hitoshura25_mcp_server_generator/server.py` - Already passes output_dir through
2. Templates - No changes needed

## Rollout Plan

1. Implement changes to `generator.py`
2. Update tests in `test_generator.py`
3. Update CLI help text
4. Run full test suite - verify all pass
5. Run dogfooding scenarios
6. Commit changes
7. Test in the `gemini-workflow-bridge-mcp` repo as final validation
