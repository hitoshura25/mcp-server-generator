# Smart File Conflict Handling - Implementation Specification

## Executive Summary

This specification details the implementation of smart file conflict handling for the MCP server generator. Instead of failing when files exist, the generator will intelligently merge, append, or skip files based on their type and criticality.

**Key Goals:**
- Reduce friction for users regenerating or updating projects
- Preserve user customizations where possible
- Maintain safety for critical files
- Enable incremental updates and template refreshes

**Approach:**
- Smart merge for configuration files (.gitignore, MANIFEST.in)
- Append strategy for documentation (README.md, MCP-USAGE.md)
- Skip non-critical files (LICENSE)
- Continue to error on critical files (pyproject.toml, setup.py, package directory)

## Current Behavior Analysis

### Existing Conflict Detection (generator.py:229-248)

**In-Place Generation Mode (output_dir = "."):**
```python
conflicting_files = [
    'pyproject.toml', 'setup.py', 'README.md',
    'MCP-USAGE.md', 'LICENSE', 'MANIFEST.in', '.gitignore'
]
```

**Current Behavior:**
- Checks for any of these files in the target directory
- Raises `FileExistsError` if any exist
- Provides helpful error message with solutions
- User must manually delete files to proceed

**Pain Points:**
1. Cannot regenerate after adding tools
2. Cannot update templates
3. Loses all customizations if forced to regenerate
4. No way to merge configuration updates

## File-by-File Handling Strategy

### Summary Table

| File | Strategy | Complexity | Critical? | User Edits? |
|------|----------|------------|-----------|-------------|
| `.gitignore` | **Smart Merge** | Low | No | Rare |
| `MANIFEST.in` | **Smart Merge** | Low | No | Rare |
| `README.md` | **Append Section** | Medium | No | Common |
| `MCP-USAGE.md` | **Append Section** | Medium | No | Moderate |
| `LICENSE` | **Skip if Exists** | None | No | Never |
| `pyproject.toml` | **Error** | N/A | **Yes** | Common |
| `setup.py` | **Error** | N/A | **Yes** | Rare |
| `{package_name}/` | **Error** | N/A | **Yes** | Very Common |

### Detailed File Strategies

#### 1. `.gitignore` - Smart Merge

**Rationale:**
- Rarely customized by users
- New entries are additive and safe
- Easy to merge without conflicts

**Algorithm:**
```python
def merge_gitignore(existing_path: str, template_content: str) -> dict:
    """
    Merge .gitignore files by appending unique entries.

    Args:
        existing_path: Path to existing .gitignore
        template_content: Content from template

    Returns:
        dict with 'added', 'skipped', 'total' counts
    """
    # Read existing file
    existing_content = Path(existing_path).read_text()
    existing_lines = set(line.strip() for line in existing_content.splitlines())

    # Parse template
    template_lines = [line.strip() for line in template_content.splitlines()]

    # Find new unique entries (ignore empty lines and comments for deduplication)
    new_entries = []
    for line in template_lines:
        stripped = line.strip()
        # Always add comments and empty lines for structure
        if not stripped or stripped.startswith('#'):
            new_entries.append(line)
        # Only add patterns if not already present
        elif stripped not in existing_lines:
            new_entries.append(line)
            existing_lines.add(stripped)  # Track to avoid duplicates within template

    if new_entries:
        # Append with clear delimiter
        merged_content = existing_content.rstrip('\n') + '\n\n'
        merged_content += f'# Added by MCP Generator on {datetime.now().strftime("%Y-%m-%d")}\n'
        merged_content += '\n'.join(new_entries) + '\n'

        Path(existing_path).write_text(merged_content)

    return {
        'added': len([e for e in new_entries if e.strip() and not e.strip().startswith('#')]),
        'skipped': len(template_lines) - len(new_entries),
        'total': len(template_lines)
    }
```

**Edge Cases:**
- Empty existing file → Treat as new file
- Malformed .gitignore → Best effort merge, log warning
- Duplicate entries with different formatting → Consider identical if stripped version matches

#### 2. `MANIFEST.in` - Smart Merge

**Rationale:**
- Similar to .gitignore
- Additive entries are safe
- Rarely customized

**Algorithm:**
```python
def merge_manifest(existing_path: str, template_content: str) -> dict:
    """
    Merge MANIFEST.in files by appending unique include patterns.

    Returns:
        dict with 'added', 'skipped' counts
    """
    existing_content = Path(existing_path).read_text()
    existing_lines = set(line.strip() for line in existing_content.splitlines())

    template_lines = [line.strip() for line in template_content.splitlines()]

    new_entries = []
    for line in template_lines:
        stripped = line.strip()
        # Keep comments and structure
        if not stripped or stripped.startswith('#'):
            new_entries.append(line)
        # Only add if not present
        elif stripped not in existing_lines:
            new_entries.append(line)
            existing_lines.add(stripped)

    if new_entries:
        merged_content = existing_content.rstrip('\n') + '\n\n'
        merged_content += f'# Added by MCP Generator on {datetime.now().strftime("%Y-%m-%d")}\n'
        merged_content += '\n'.join(new_entries) + '\n'

        Path(existing_path).write_text(merged_content)

    return {
        'added': len([e for e in new_entries if e.strip() and not e.strip().startswith('#')]),
        'skipped': len(template_lines) - len(new_entries)
    }
```

#### 3. `README.md` - Append Section

**Rationale:**
- Commonly customized by users
- Users will review and edit the result
- Clear delimiters make it safe to append

**Algorithm:**
```python
def append_to_readme(existing_path: str, template_content: str, project_name: str) -> dict:
    """
    Append generated README content to existing file with clear delimiter.

    Returns:
        dict with 'appended' status and line number
    """
    existing_content = Path(existing_path).read_text()

    # Check if already appended (avoid duplicates)
    marker = f'<!-- MCP-GENERATOR-CONTENT-START:{project_name} -->'
    if marker in existing_content:
        return {'appended': False, 'reason': 'Already contains generated content'}

    # Append with clear delimiters
    delimiter_start = f'\n\n---\n\n{marker}\n'
    delimiter_end = f'\n<!-- MCP-GENERATOR-CONTENT-END:{project_name} -->\n'

    note = (
        f'> **Note:** The following content was generated by MCP Generator on '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}.\n'
        f'> You can edit, move, or remove this section as needed.\n\n'
    )

    appended_content = delimiter_start + note + template_content + delimiter_end

    merged_content = existing_content.rstrip('\n') + appended_content

    # Calculate line number where content was added
    line_number = len(existing_content.splitlines()) + 1

    Path(existing_path).write_text(merged_content)

    return {
        'appended': True,
        'line_number': line_number,
        'bytes_added': len(appended_content)
    }
```

**Template Changes Required:**
```jinja2
{# templates/python/README.md.j2 #}
{# Add note at top indicating this is generated content #}
<!-- This README was generated by MCP Generator -->

# {{ project_name }}

{{ description }}

... rest of content ...
```

#### 4. `MCP-USAGE.md` - Append Section

**Algorithm:** Same as README.md with different marker

```python
def append_to_mcp_usage(existing_path: str, template_content: str, project_name: str) -> dict:
    """Similar to append_to_readme but for MCP-USAGE.md"""
    # Same implementation as append_to_readme
    # Different marker: <!-- MCP-GENERATOR-USAGE-START:{project_name} -->
```

#### 5. `LICENSE` - Skip if Exists

**Rationale:**
- Should never be changed once set
- User may have customized
- Legal implications of overwriting

**Algorithm:**
```python
def skip_if_exists(file_path: str) -> dict:
    """
    Simply skip file if it exists.

    Returns:
        dict with 'skipped' status
    """
    if Path(file_path).exists():
        return {'skipped': True, 'reason': 'File already exists'}
    return {'skipped': False}
```

#### 6. `pyproject.toml`, `setup.py`, `{package_name}/` - Error (No Change)

**Rationale:**
- Core to project structure
- Complex to merge safely
- User likely has customizations
- Better to error and let user decide

**Behavior:** Keep current error behavior unchanged

## Implementation Details

### Code Changes in `generator.py`

#### 1. Add Merge Utility Functions

Insert before `generate_mcp_server()` function:

```python
from datetime import datetime
from typing import Dict, Any

def merge_gitignore(existing_path: str, template_content: str) -> Dict[str, Any]:
    """Merge .gitignore by appending unique entries."""
    # Implementation from above

def merge_manifest(existing_path: str, template_content: str) -> Dict[str, Any]:
    """Merge MANIFEST.in by appending unique patterns."""
    # Implementation from above

def append_to_readme(existing_path: str, template_content: str, project_name: str) -> Dict[str, Any]:
    """Append to README.md with clear delimiters."""
    # Implementation from above

def append_to_mcp_usage(existing_path: str, template_content: str, project_name: str) -> Dict[str, Any]:
    """Append to MCP-USAGE.md with clear delimiters."""
    # Implementation from above
```

#### 2. Update Conflict Detection Logic

Replace lines 229-248 in `generate_mcp_server()`:

```python
# Determine project path
if normalized_output == current_dir:
    project_path = os.getcwd()

    # Check only for CRITICAL conflicting files
    critical_files = [
        'pyproject.toml',
        'setup.py',
    ]

    existing_critical = [f for f in critical_files
                        if os.path.exists(os.path.join(project_path, f))]

    # Also check if package directory already exists
    if os.path.exists(os.path.join(project_path, package_name)):
        existing_critical.append(f'{package_name}/ directory')

    if existing_critical:
        raise FileExistsError(
            f"Cannot generate in-place: critical files exist: {', '.join(existing_critical)}\n"
            f"These files are essential to project structure and cannot be safely merged.\n"
            f"Solutions:\n"
            f"  1. Use a different output directory (don't use '.')\n"
            f"  2. Remove or backup these files: {', '.join(existing_critical)}\n"
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

#### 3. Update File Generation Loop

Replace lines 330-344 with smarter generation logic:

```python
files_created = []
files_merged = []
files_appended = []
files_skipped = []

# Generate files with smart handling
for template_file, output_file in files_to_generate:
    try:
        template = env.get_template(template_file)
        content = template.render(**context)

        output_path = os.path.join(project_path, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Determine handling strategy based on file
        file_exists = os.path.exists(output_path)

        # Strategy 1: Smart merge for .gitignore
        if output_file == '.gitignore' and file_exists:
            result = merge_gitignore(output_path, content)
            if result['added'] > 0:
                files_merged.append(f".gitignore ({result['added']} entries added)")
            else:
                files_skipped.append(".gitignore (no new entries)")

        # Strategy 2: Smart merge for MANIFEST.in
        elif output_file == 'MANIFEST.in' and file_exists:
            result = merge_manifest(output_path, content)
            if result['added'] > 0:
                files_merged.append(f"MANIFEST.in ({result['added']} patterns added)")
            else:
                files_skipped.append("MANIFEST.in (no new patterns)")

        # Strategy 3: Append to README.md
        elif output_file == 'README.md' and file_exists:
            result = append_to_readme(output_path, content, project_name)
            if result['appended']:
                files_appended.append(f"README.md (line {result['line_number']})")
            else:
                files_skipped.append(f"README.md ({result['reason']})")

        # Strategy 4: Append to MCP-USAGE.md
        elif output_file == 'MCP-USAGE.md' and file_exists:
            result = append_to_mcp_usage(output_path, content, project_name)
            if result['appended']:
                files_appended.append(f"MCP-USAGE.md (line {result['line_number']})")
            else:
                files_skipped.append(f"MCP-USAGE.md ({result['reason']})")

        # Strategy 5: Skip LICENSE if exists
        elif output_file == 'LICENSE' and file_exists:
            files_skipped.append("LICENSE (preserving existing)")

        # Default: Create file normally
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            files_created.append(output_file)

    except Exception as e:
        raise RuntimeError(f"Failed to generate {output_file}: {str(e)}")
```

#### 4. Add Generation Summary

After file generation loop, before workflow generation:

```python
# Print generation summary
summary_parts = []
if files_created:
    summary_parts.append(f"Created {len(files_created)} files")
if files_merged:
    summary_parts.append(f"Merged {len(files_merged)} files")
if files_appended:
    summary_parts.append(f"Appended to {len(files_appended)} files")
if files_skipped:
    summary_parts.append(f"Skipped {len(files_skipped)} files")

print(f"\n{'='*60}")
print(f"Generation Summary: {', '.join(summary_parts)}")
print(f"{'='*60}")

if files_merged:
    print("\nMerged files:")
    for f in files_merged:
        print(f"  ✓ {f}")

if files_appended:
    print("\nAppended to files (please review):")
    for f in files_appended:
        print(f"  ⚠ {f}")

if files_skipped:
    print("\nSkipped files:")
    for f in files_skipped:
        print(f"  ⊘ {f}")

if files_appended:
    print("\n⚠️  Please review appended files and edit as needed.")

print(f"{'='*60}\n")
```

#### 5. Update Return Value

Modify return statement to include merge statistics:

```python
return {
    'success': True,
    'project_path': project_path,
    'files_created': files_created,
    'files_merged': files_merged,
    'files_appended': files_appended,
    'files_skipped': files_skipped,
    'message': f"Successfully generated MCP server project at {project_path}"
}
```

## User Experience Examples

### Example 1: Fresh Generation (No Conflicts)

**Command:**
```bash
mcp-server-generator generate --project-name my-tool --tools '[...]'
```

**Output:**
```
============================================================
Generation Summary: Created 18 files
============================================================

Successfully generated MCP server project at /path/to/my-tool
```

**Behavior:** Same as current - no change

### Example 2: Regeneration with Existing Files

**Scenario:** User has existing .gitignore and README.md with customizations

**Command:**
```bash
cd my-tool
mcp-server-generator generate --project-name my-tool --tools '[...new tool...]' --output-dir .
```

**Output:**
```
============================================================
Generation Summary: Created 14 files, Merged 2 files, Appended to 1 file, Skipped 1 file
============================================================

Merged files:
  ✓ .gitignore (3 entries added)
  ✓ MANIFEST.in (1 pattern added)

Appended to files (please review):
  ⚠ README.md (line 87)

Skipped files:
  ⊘ LICENSE (preserving existing)

⚠️  Please review appended files and edit as needed.
============================================================

Successfully generated MCP server project at /path/to/my-tool
```

**Behavior:**
- .gitignore gets new entries appended
- README.md has generated content appended at end
- LICENSE is preserved
- User can review and clean up as needed

### Example 3: Critical File Conflict

**Scenario:** User has existing pyproject.toml

**Command:**
```bash
cd my-tool
mcp-server-generator generate --project-name my-tool --tools '[...]' --output-dir .
```

**Output:**
```
Error: Cannot generate in-place: critical files exist: pyproject.toml
These files are essential to project structure and cannot be safely merged.
Solutions:
  1. Use a different output directory (don't use '.')
  2. Remove or backup these files: pyproject.toml
  3. Generate in a subdirectory by omitting --output-dir
```

**Behavior:** Same as current - safety first for critical files

## Testing Strategy

### Unit Tests

Add to `hitoshura25_mcp_server_generator/tests/test_generator.py`:

```python
def test_merge_gitignore_new_entries(tmp_path):
    """Test merging .gitignore adds unique entries."""
    existing = tmp_path / ".gitignore"
    existing.write_text("*.pyc\n__pycache__/\n")

    template = "*.pyc\n__pycache__/\n.venv/\ndist/\n"

    from hitoshura25_mcp_server_generator.generator import merge_gitignore
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
    existing = tmp_path / ".gitignore"
    existing.write_text("*.pyc\n.venv/\n")

    template = "*.pyc\n.venv/\n"

    from hitoshura25_mcp_server_generator.generator import merge_gitignore
    result = merge_gitignore(str(existing), template)

    assert result['added'] == 0

    content = existing.read_text()
    # Should not have duplicate entries
    assert content.count('*.pyc') == 1
    assert content.count('.venv/') == 1


def test_append_to_readme(tmp_path):
    """Test appending to README with delimiters."""
    existing = tmp_path / "README.md"
    existing.write_text("# My Project\n\nCustom content here.\n")

    template = "## Generated Section\n\nThis is generated.\n"

    from hitoshura25_mcp_server_generator.generator import append_to_readme
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
    existing = tmp_path / "README.md"
    content = "# Test\n<!-- MCP-GENERATOR-CONTENT-START:test-project -->\nOld\n<!-- MCP-GENERATOR-CONTENT-END:test-project -->\n"
    existing.write_text(content)

    template = "New content\n"

    from hitoshura25_mcp_server_generator.generator import append_to_readme
    result = append_to_readme(str(existing), template, "test-project")

    assert result['appended'] == False
    assert 'Already contains' in result['reason']


def test_generate_with_smart_merge(tmp_path):
    """Test full generation with smart merge."""
    # Create existing files
    (tmp_path / ".gitignore").write_text("*.pyc\n")
    (tmp_path / "README.md").write_text("# Custom README\n")
    (tmp_path / "LICENSE").write_text("MIT License\nCustom text\n")

    result = generate_mcp_server(
        project_name="test-server",
        description="Test",
        author="Test",
        author_email="test@test.com",
        tools=[{"name": "test", "description": "Test", "parameters": []}],
        output_dir=str(tmp_path),
        prefix="NONE"
    )

    assert result['success']
    assert len(result['files_merged']) > 0  # .gitignore merged
    assert len(result['files_appended']) > 0  # README appended
    assert len(result['files_skipped']) > 0  # LICENSE skipped

    # Verify .gitignore was merged
    gitignore = (tmp_path / "test-server" / ".gitignore").read_text()
    assert "*.pyc" in gitignore  # Original preserved

    # Verify README was appended
    readme = (tmp_path / "test-server" / "README.md").read_text()
    assert "Custom README" in readme  # Original preserved
    assert "MCP-GENERATOR-CONTENT" in readme  # New content added

    # Verify LICENSE was skipped (not overwritten)
    license_file = (tmp_path / "test-server" / "LICENSE").read_text()
    assert "Custom text" in license_file


def test_generate_errors_on_critical_files(tmp_path):
    """Test that critical files still cause errors."""
    # Create in temp dir first
    os.chdir(tmp_path)

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
```

### Integration Tests

```python
def test_full_workflow_with_customizations(tmp_path):
    """Test realistic workflow: generate, customize, regenerate with new tool."""

    # Step 1: Initial generation
    result1 = generate_mcp_server(
        project_name="my-tool",
        description="My Tool v1",
        author="Dev",
        author_email="dev@test.com",
        tools=[{"name": "tool1", "description": "First tool", "parameters": []}],
        output_dir=str(tmp_path),
        prefix="NONE"
    )
    assert result1['success']

    project_path = tmp_path / "my-tool"

    # Step 2: User customizes files
    readme = project_path / "README.md"
    original_readme = readme.read_text()
    customized_readme = original_readme + "\n## My Custom Section\n\nCustom content.\n"
    readme.write_text(customized_readme)

    gitignore = project_path / ".gitignore"
    gitignore.write_text(gitignore.read_text() + "\n.custom/\n")

    # Step 3: Regenerate with new tool (simulate output_dir pointing to existing)
    # Change to project directory
    os.chdir(project_path)

    result2 = generate_mcp_server(
        project_name="my-tool",
        description="My Tool v2",
        author="Dev",
        author_email="dev@test.com",
        tools=[
            {"name": "tool1", "description": "First tool", "parameters": []},
            {"name": "tool2", "description": "Second tool", "parameters": []}
        ],
        output_dir=".",
        prefix="NONE"
    )

    assert result2['success']
    assert len(result2['files_merged']) > 0
    assert len(result2['files_appended']) > 0

    # Verify customizations preserved
    final_readme = readme.read_text()
    assert "My Custom Section" in final_readme  # Custom content preserved
    assert "Custom content" in final_readme

    final_gitignore = gitignore.read_text()
    assert ".custom/" in final_gitignore  # Custom entry preserved
```

## Edge Cases and Solutions

### Edge Case 1: Malformed Existing Files

**Problem:** Existing .gitignore has invalid syntax or encoding issues

**Solution:**
```python
def merge_gitignore(existing_path: str, template_content: str) -> dict:
    try:
        existing_content = Path(existing_path).read_text()
    except UnicodeDecodeError:
        # Try different encodings
        try:
            existing_content = Path(existing_path).read_text(encoding='latin-1')
        except:
            # If all fails, log warning and treat as empty
            print(f"Warning: Could not read {existing_path}, treating as empty")
            existing_content = ""
    except Exception as e:
        print(f"Warning: Error reading {existing_path}: {e}")
        existing_content = ""

    # Continue with merge...
```

### Edge Case 2: README Already Has Generated Content

**Problem:** User runs generator twice, appends duplicate content

**Solution:** Check for marker before appending (already in algorithm):
```python
marker = f'<!-- MCP-GENERATOR-CONTENT-START:{project_name} -->'
if marker in existing_content:
    return {'appended': False, 'reason': 'Already contains generated content'}
```

### Edge Case 3: Empty Existing Files

**Problem:** File exists but is empty

**Solution:** Treat as new file, write content normally:
```python
if file_exists and os.path.getsize(output_path) == 0:
    # Empty file, just write
    with open(output_path, 'w') as f:
        f.write(content)
```

### Edge Case 4: File Permissions

**Problem:** Existing file is read-only

**Solution:** Catch permission errors and provide helpful message:
```python
try:
    Path(existing_path).write_text(merged_content)
except PermissionError:
    raise PermissionError(
        f"Cannot write to {existing_path}: Permission denied\n"
        f"Please check file permissions and try again"
    )
```

### Edge Case 5: Very Large Existing Files

**Problem:** README.md is 10MB, appending makes it unwieldy

**Solution:** Add size check before appending:
```python
def append_to_readme(existing_path: str, template_content: str, project_name: str) -> dict:
    file_size = os.path.getsize(existing_path)
    if file_size > 1_000_000:  # 1MB
        return {
            'appended': False,
            'reason': f'File too large ({file_size/1024:.1f}KB), skipping to avoid unwieldy file'
        }
    # Continue with append...
```

## Migration Guide

### For New Projects
No changes - works exactly as before.

### For Existing Projects

**Scenario 1: User wants to add a new tool**

Before (current):
```bash
# User must delete everything and regenerate
rm -rf my-project
mcp-server-generator generate --project-name my-project --tools '[...old tools..., ...new tool...]'
# All customizations lost!
```

After (with smart merge):
```bash
cd my-project
mcp-server-generator generate --project-name my-project --tools '[...old tools..., ...new tool...]' --output-dir .
# Config files merged, docs appended, customizations preserved!
# User just needs to review README.md and edit as needed
```

**Scenario 2: User wants to update to latest templates**

Before (current):
```bash
# No mechanism - must manually diff and copy
```

After (with smart merge):
```bash
cd my-project
mcp-server-generator generate --project-name my-project --tools '[...]' --output-dir .
# Template files regenerated
# Config merged with new patterns
# User reviews and cleans up appended docs
```

## Future Enhancements

### Phase 1 (Current Spec)
- Smart merge for .gitignore, MANIFEST.in
- Append strategy for README.md, MCP-USAGE.md
- Skip strategy for LICENSE
- Continue error for critical files

### Phase 2 (Future)
- `--force` flag: Overwrite all non-critical files
- `--skip-existing` flag: Skip all existing files
- `--dry-run` flag: Preview what would be generated/merged
- Better conflict summary showing diffs

### Phase 3 (Advanced)
- Interactive mode: Prompt per file
- `--update` mode: Specifically for updating existing projects
- Smart pyproject.toml merging (dependencies, optional-dependencies)
- Backup creation (`.bak` files before overwrite)

### Phase 4 (Enterprise)
- Configuration file (.mcpgeneratorrc) for default behaviors
- Template versioning (track template version, enable targeted updates)
- Rollback support
- Custom merge strategies per file type

## Implementation Checklist

- [ ] Add merge utility functions to generator.py
- [ ] Update conflict detection logic (reduce critical file list)
- [ ] Modify file generation loop with smart handling
- [ ] Add generation summary output
- [ ] Update return value with merge statistics
- [ ] Add HTML comment markers to README.md.j2 template
- [ ] Add HTML comment markers to MCP-USAGE.md.j2 template
- [ ] Write unit tests for merge_gitignore
- [ ] Write unit tests for merge_manifest
- [ ] Write unit tests for append_to_readme
- [ ] Write unit tests for append_to_mcp_usage
- [ ] Write integration test for full generation with merges
- [ ] Write test for critical file errors still working
- [ ] Update README.md with new behavior documentation
- [ ] Update error messages with new approach
- [ ] Test with real projects
- [ ] Handle edge cases (encoding, permissions, size)
- [ ] Add logging for debug purposes
- [ ] Performance testing (large files)
- [ ] Documentation examples
- [ ] Release notes

## Success Criteria

1. **Functionality:**
   - .gitignore merges correctly without duplicates
   - MANIFEST.in merges correctly without duplicates
   - README.md appends with clear delimiters
   - MCP-USAGE.md appends with clear delimiters
   - LICENSE is skipped if exists
   - Critical files still error appropriately

2. **Safety:**
   - Never overwrites critical files without explicit user action
   - Preserves user customizations in merged files
   - Clear markers prevent duplicate appends
   - Good error messages for edge cases

3. **User Experience:**
   - Clear summary of what was merged/appended/skipped
   - Users can easily find and review appended content
   - Workflow is faster than manual regeneration
   - Documentation is clear and helpful

4. **Testing:**
   - 100% code coverage for merge functions
   - All edge cases have tests
   - Integration tests cover realistic workflows
   - Tests run on multiple platforms

5. **Documentation:**
   - README explains new behavior
   - Examples show common scenarios
   - Migration guide for existing users
   - Error messages are helpful

## Risk Assessment

**Low Risk:**
- .gitignore merging (simple, safe, easy to verify)
- MANIFEST.in merging (simple, safe, rare edge cases)
- LICENSE skipping (no-op, very safe)

**Medium Risk:**
- README.md appending (user may not like format, but easy to edit)
- MCP-USAGE.md appending (same as README)

**Mitigations:**
- Clear delimiters make it easy to find/remove appended content
- User reviews and edits as needed
- Comprehensive testing
- Good documentation

**Overall Risk:** Low to Medium - Changes are additive and reversible

## Open Questions

1. Should we add a `--no-merge` flag to disable all smart merging and revert to old behavior?
2. Should generated content in README have a specific style (callout box, different heading level)?
3. Should we validate that markers in README are balanced before appending?
4. How do we handle if user deletes end marker but not start marker?
5. Should we support custom merge strategies via config file in future?

## Conclusion

This implementation provides a practical, low-risk solution to file conflict handling that preserves user customizations while enabling regeneration and updates. The phased approach allows for future enhancements based on user feedback.

The focus on smart merging for configuration files and appending for documentation strikes a good balance between safety and convenience. Critical files maintain their error behavior, ensuring users don't accidentally overwrite important project structure.
