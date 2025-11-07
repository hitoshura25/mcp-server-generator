# Project Prefix Implementation Plan

**Version**: 1.0
**Created**: 2025-11-06
**Target Release**: v1.0.0 (Breaking Change)
**Status**: APPROVED - Ready for Implementation

---

## Table of Contents

1. [Problem Overview](#1-problem-overview)
2. [Solution Overview](#2-solution-overview)
3. [Changes to mcp-server-generator](#3-changes-to-mcp-server-generator-itself)
4. [Changes to Generation Logic](#4-changes-to-generation-logic)
5. [Changes to Templates](#5-changes-to-templates)
6. [Changes to Documentation](#6-changes-to-documentation)
7. [Testing Strategy](#7-testing-strategy)
8. [Migration Path](#8-migration-path-for-existing-users)
9. [Implementation Order](#9-implementation-order)
10. [Rollback Plan](#10-rollback-plan)
11. [Success Criteria](#11-success-criteria)
12. [Timeline Estimate](#12-timeline-estimate)
13. [Risks & Mitigation](#13-risks--mitigation)
14. [Post-Migration Tasks](#14-post-migration-tasks)

---

## 1. PROBLEM OVERVIEW

### The Issue

**PyPI Namespace Conflict**: When attempting to publish `mcp-server-generator` to PyPI, the publication failed because a package with that name already exists. PyPI has a flat global namespace where package names must be unique across all users.

### Why This Matters

As the MCP ecosystem grows, common descriptive names like:
- `mcp-server-generator`
- `mcp-tool`
- `workflow-generator`

...are prone to conflicts. Multiple developers may independently create tools with similar purposes and names.

### Current State

- **Package name**: `mcp-server-generator` (conflicts with existing package)
- **Import path**: `mcp_server_generator`
- **Dependency**: `pypi-workflow-generator>=0.3.0`
- **Git repository**: `github.com:hitoshura25/mcp-server-generator`
- **Status**: Cannot publish to PyPI

### Impact Without Fix

- Tool cannot be distributed via PyPI
- Users must install from source
- No versioning, dependency management, or easy updates
- Generated projects face same naming conflicts

---

## 2. SOLUTION OVERVIEW

### Strategy

Adopt the **project prefix naming convention** introduced in `hitoshura25-pypi-workflow-generator` v0.3.1, which solves namespace conflicts by prefixing package names with the author's username.

### The Prefix Pattern

**For mcp-server-generator itself**:
- PyPI package name: `hitoshura25-mcp-server-generator`
- Python import: `hitoshura25_mcp_server_generator`
- CLI command: `hitoshura25-mcp-server-generator-cli`

**For generated projects**:
- Users can choose prefix mode:
  - **AUTO** (default): Auto-detect from git config
  - **Custom** (e.g., `acme`): User-specified prefix
  - **NONE**: No prefix for truly unique names

### How Prefixes Work

```
User: jsmith
Project: my-tool
Prefix Mode: AUTO

Result:
  PyPI package:  jsmith-my-tool
  Import:        jsmith_my_tool
  Command:       jsmith-my-tool
  Directory:     jsmith-my-tool/
```

### Git Username Detection

Priority order (from hitoshura25-pypi-workflow-generator v0.3.1):

1. `git config --get github.user` (most specific)
2. Parse GitHub username from remote URL (e.g., `git@github.com:username/repo.git`)
3. `git config --get user.name` (sanitized to lowercase-hyphenated format)
4. Fallback: No prefix if detection fails

### Benefits

✅ **Clear Ownership**: Package names indicate the author
✅ **No Conflicts**: Each user has their own namespace
✅ **Grouping**: Related packages from same author are grouped
✅ **PyPI Best Practice**: Follows recommended namespace isolation
✅ **Flexibility**: Users can opt-in or opt-out

### Key Dependencies

**New Dependency**: `hitoshura25-pypi-workflow-generator>=0.3.1`
- Replaces: `pypi-workflow-generator>=0.3.0`
- Adds prefix support via new parameter
- Maintains workflow generation compatibility

---

## 3. CHANGES TO MCP-SERVER-GENERATOR ITSELF

This section details changes needed to rename and republish mcp-server-generator with the `hitoshura25-` prefix.

### 3.1 Package Renaming

#### Current Structure
```
mcp-server-generator/
├── pyproject.toml (name = "mcp-server-generator")
├── setup.py (name = 'mcp-server-generator')
├── mcp_server_generator/
│   ├── __init__.py
│   ├── generator.py
│   ├── server.py
│   ├── cli.py
│   └── tests/
```

#### After Renaming
```
mcp-server-generator/  # Repository name stays the same
├── pyproject.toml (name = "hitoshura25-mcp-server-generator")
├── setup.py (name = 'hitoshura25-mcp-server-generator')
├── hitoshura25_mcp_server_generator/  # Directory renamed!
│   ├── __init__.py
│   ├── generator.py
│   ├── server.py
│   ├── cli.py
│   └── tests/
```

#### Files to Modify

**File: `pyproject.toml`**

```diff
[project]
-name = "mcp-server-generator"
+name = "hitoshura25-mcp-server-generator"
description = "Generate dual-mode MCP servers with best practices"
# ... rest unchanged ...

[project.urls]
-Homepage = "https://github.com/hitoshura25/mcp-server-generator"
-Repository = "https://github.com/hitoshura25/mcp-server-generator"
-Issues = "https://github.com/hitoshura25/mcp-server-generator/issues"
+Homepage = "https://github.com/hitoshura25/mcp-server-generator"  # Same
+Repository = "https://github.com/hitoshura25/mcp-server-generator"  # Same
+Issues = "https://github.com/hitoshura25/mcp-server-generator/issues"  # Same
```

**File: `setup.py`**

```diff
setup(
-    name='mcp-server-generator',
+    name='hitoshura25-mcp-server-generator',
    author='Vinayak Menon',
    # ... other config ...
    entry_points={
        'console_scripts': [
-            'mcp-server-generator=mcp_server_generator.server:main',
-            'mcp-server-generator-cli=mcp_server_generator.cli:main',
+            'hitoshura25-mcp-server-generator-server=hitoshura25_mcp_server_generator.server:main',
+            'hitoshura25-mcp-server-generator-cli=hitoshura25_mcp_server_generator.cli:main',
+            # Deprecated aliases for migration (remove in v2.0.0)
+            'mcp-server-generator-cli=hitoshura25_mcp_server_generator.cli:main',
        ],
    },
)
```

#### Directory Rename

**Critical**: The package directory must be renamed from underscores:

```bash
# In repository root
mv mcp_server_generator/ hitoshura25_mcp_server_generator/
```

**Impact**:
- All imports must be updated throughout the codebase
- Test discovery paths must be updated
- GitHub workflow paths must be updated

### 3.2 Dependency Updates

#### Update pyproject.toml

```diff
dependencies = [
    "Jinja2>=3.0",
-    "pypi-workflow-generator>=0.3.0",
+    "hitoshura25-pypi-workflow-generator>=0.3.1",
]
```

#### Update requirements.txt

```diff
Jinja2>=3.0
-pypi-workflow-generator>=0.3.0
+hitoshura25-pypi-workflow-generator>=0.3.1
pytest>=7.0.0
pytest-asyncio>=0.21.0
build>=0.10.0
```

#### Update setup.py

```diff
install_requires=[
    'Jinja2>=3.0',
-    'pypi-workflow-generator>=0.3.0',
+    'hitoshura25-pypi-workflow-generator>=0.3.1',
],
```

### 3.3 Import Path Updates

All Python files must update imports:

**Pattern to Find**: `from pypi_workflow_generator import`
**Replace With**: `from hitoshura25_pypi_workflow_generator import`

**Pattern to Find**: `import pypi_workflow_generator`
**Replace With**: `import hitoshura25_pypi_workflow_generator`

**Files Affected**:
- `hitoshura25_mcp_server_generator/generator.py`

**Specific Changes in generator.py**:

```diff
# Generate GitHub Actions workflow (required)
try:
-    from pypi_workflow_generator import generate_workflows
+    from hitoshura25_pypi_workflow_generator import generate_workflows

    # Change to project directory
    original_dir = os.getcwd()
    os.chdir(project_path)

    try:
        workflow_result = generate_workflows(
            python_version=python_version,
            test_path=package_name,
+            prefix=prefix,  # NEW: Pass prefix to workflow generator
        )
```

### 3.4 GitHub Workflows Update

Update all workflow files to use new test path:

**File: `.github/workflows/_reusable-test-build.yml`**

```diff
inputs:
  test_path:
    description: 'Path to tests'
    required: false
    type: string
-    default: 'mcp_server_generator'
+    default: 'hitoshura25_mcp_server_generator'
```

**File: `.github/workflows/release.yml`**

```diff
with:
  python_version: '3.8'
-  test_path: 'mcp_server_generator'
+  test_path: 'hitoshura25_mcp_server_generator'
```

**File: `.github/workflows/test-pr.yml`**

```diff
with:
  python_version: '3.8'
-  test_path: 'mcp_server_generator'
+  test_path: 'hitoshura25_mcp_server_generator'
```

### 3.5 Test Files Update

All test imports must be updated:

**Pattern**:
```diff
-from mcp_server_generator import generate_mcp_server
-from mcp_server_generator.generator import validate_project_name
-from mcp_server_generator.cli import main
-import mcp_server_generator.server as server
+from hitoshura25_mcp_server_generator import generate_mcp_server
+from hitoshura25_mcp_server_generator.generator import validate_project_name
+from hitoshura25_mcp_server_generator.cli import main
+import hitoshura25_mcp_server_generator.server as server
```

**Files to Update**:
- `hitoshura25_mcp_server_generator/tests/test_generator.py`
- `hitoshura25_mcp_server_generator/tests/test_server.py`
- `hitoshura25_mcp_server_generator/tests/test_cli.py`
- `hitoshura25_mcp_server_generator/tests/test_templates.py`
- Any new test files created for prefix functionality

### 3.6 Documentation Updates

#### README.md

Update all references:

```diff
# MCP Server Generator
+> **Package**: `hitoshura25-mcp-server-generator`
+> **Import**: `hitoshura25_mcp_server_generator`

## Installation

```bash
-pip install mcp-server-generator
+pip install hitoshura25-mcp-server-generator
```

## Quick Start

### CLI Mode
```bash
-mcp-server-generator-cli --interactive
+hitoshura25-mcp-server-generator-cli --interactive
```

### MCP Server Mode
```json
{
  "mcpServers": {
-    "mcp-server-generator": {
-      "command": "mcp-server-generator"
+    "hitoshura25-mcp-server-generator": {
+      "command": "hitoshura25-mcp-server-generator-server"
    }
  }
}
```

### Python API
```python
-from mcp_server_generator import generate_mcp_server
+from hitoshura25_mcp_server_generator import generate_mcp_server
```
```

#### MCP-USAGE.md

Update command examples and configuration snippets.

#### CONTRIBUTING.md

Update development setup instructions:

```diff
```bash
git clone https://github.com/hitoshura25/mcp-server-generator
cd mcp-server-generator
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run tests
-pytest mcp_server_generator/tests/
+pytest hitoshura25_mcp_server_generator/tests/
```
```

#### EXAMPLES.md

Update all code examples to use new package name and imports.

---

## 4. CHANGES TO GENERATION LOGIC

This section details how to add prefix support to the project generation functionality.

### 4.1 Create Git Utilities Module

**New File**: `hitoshura25_mcp_server_generator/git_utils.py`

```python
"""
Git username detection and prefix application utilities.
"""

import subprocess
from typing import Optional
import re


def get_github_username() -> Optional[str]:
    """
    Detect GitHub username from git configuration.

    Priority order:
    1. git config --get github.user (most specific)
    2. Username from remote URL (git@github.com:username/repo.git)
    3. git config --get user.name (sanitized)

    Returns:
        GitHub username or None if not detected
    """
    # Priority 1: github.user config
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'github.user'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        username = result.stdout.strip()
        if username:
            return username
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Priority 2: Parse from remote URL
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        url = result.stdout.strip()

        # Match: git@github.com:username/repo.git
        # Or: https://github.com/username/repo.git
        match = re.search(r'github\.com[:/]([^/]+)/', url)
        if match:
            return match.group(1)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Priority 3: user.name (sanitized)
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'user.name'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        name = result.stdout.strip()
        if name:
            return sanitize_username(name)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def sanitize_username(name: str) -> str:
    """
    Sanitize username for use as package prefix.

    Converts to lowercase, replaces spaces with hyphens,
    removes invalid characters for PyPI package names.

    Args:
        name: Raw username string

    Returns:
        Sanitized username suitable for package prefix

    Examples:
        >>> sanitize_username("John Smith")
        "john-smith"
        >>> sanitize_username("John Q. Public")
        "john-q-public"
    """
    # Convert to lowercase
    name = name.lower()

    # Replace spaces and dots with hyphens
    name = name.replace(' ', '-').replace('.', '-')

    # Keep only alphanumeric and hyphens
    name = re.sub(r'[^a-z0-9-]', '', name)

    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)

    # Remove leading/trailing hyphens
    name = name.strip('-')

    return name


def apply_prefix(
    base_name: str,
    prefix: str = "AUTO"
) -> tuple[str, str]:
    """
    Apply prefix to package name.

    Args:
        base_name: Base package name without prefix (e.g., "my-tool")
        prefix: Prefix mode - "AUTO", custom string, or "NONE"

    Returns:
        Tuple of (package_name, import_name)
        - package_name: For PyPI, uses hyphens (e.g., "jsmith-my-tool")
        - import_name: For Python imports, uses underscores (e.g., "jsmith_my_tool")

    Examples:
        >>> apply_prefix("my-tool", "AUTO")  # Assuming git user is "jsmith"
        ("jsmith-my-tool", "jsmith_my_tool")

        >>> apply_prefix("my-tool", "acme")
        ("acme-my-tool", "acme_my_tool")

        >>> apply_prefix("my-tool", "NONE")
        ("my-tool", "my_tool")
    """
    if prefix == "NONE":
        package_name = base_name
    elif prefix == "AUTO":
        detected = get_github_username()
        if detected:
            package_name = f"{detected}-{base_name}"
        else:
            # Fallback to no prefix if detection fails
            package_name = base_name
    else:
        # Custom prefix provided
        sanitized_prefix = sanitize_username(prefix)
        package_name = f"{sanitized_prefix}-{base_name}"

    # Convert package name to import name (hyphens to underscores)
    import_name = package_name.replace('-', '_')

    return package_name, import_name
```

### 4.2 Update Generator Function Signature

**File**: `hitoshura25_mcp_server_generator/generator.py`

Add `prefix` parameter to `generate_mcp_server()`:

```python
def generate_mcp_server(
    project_name: str,
    description: str,
    author: str,
    author_email: str,
    tools: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    python_version: str = "3.8",
    license_type: str = "Apache-2.0",
    prefix: str = "AUTO",  # NEW PARAMETER
) -> Dict[str, Any]:
    """
    Generate a complete MCP server project.

    Args:
        project_name: Base project name (e.g., "my-tool")
        description: Project description
        author: Author name
        author_email: Author email
        tools: List of tool definitions
        output_dir: Where to create project (default: current directory)
        python_version: Python version for testing (default: "3.8")
        license_type: License type (default: "Apache-2.0")
        prefix: Package name prefix mode (default: "AUTO")
                - "AUTO": Auto-detect from git config
                - Custom string (e.g., "acme"): Use specified prefix
                - "NONE": No prefix

    Returns:
        {
            "success": bool,
            "project_path": str,
            "package_name": str,  # Full name with prefix
            "import_name": str,   # Import name with underscores
            "files_created": List[str],
            "message": str
        }
    """
    # ... implementation below ...
```

### 4.3 Update Generator Implementation

**File**: `hitoshura25_mcp_server_generator/generator.py`

Add prefix logic:

```python
from .git_utils import apply_prefix

def generate_mcp_server(..., prefix: str = "AUTO") -> Dict[str, Any]:
    # Apply prefix to project name
    full_package_name, import_name = apply_prefix(project_name, prefix)

    # Validate the prefixed name
    if not validate_project_name(import_name):
        raise ValueError(
            f"Invalid project name after prefix application: '{full_package_name}'. "
            f"Import name '{import_name}' must be a valid Python identifier."
        )

    # Validate tool names (unchanged)
    for tool in tools:
        if not validate_tool_name(tool["name"]):
            raise ValueError(
                f"Invalid tool name: '{tool['name']}'. "
                "Must be a valid Python identifier and not a keyword."
            )

    if not tools:
        raise ValueError("At least one tool must be defined.")

    # Determine output directory - use full package name
    if output_dir is None:
        output_dir = os.getcwd()

    project_path = os.path.join(output_dir, full_package_name)

    # Check if directory exists
    if os.path.exists(project_path):
        raise FileExistsError(f"Directory already exists: {project_path}")

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates', 'python')

    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Templates not found at {template_dir}")

    # Prepare template context
    context = {
        'project_name': full_package_name,  # For pyproject.toml, setup.py (hyphens)
        'package_name': import_name,         # For directory name (underscores)
        'import_name': import_name,          # For entry points (underscores)
        'base_name': project_name,           # Original name without prefix
        'description': sanitize_description(description),
        'author': author,
        'author_email': author_email,
        'python_version': python_version,
        'license': license_type,
        'tools': tools,
        'tool_schemas': [generate_tool_schema(tool) for tool in tools],
        'year': '2025',
    }

    # ... rest of file generation logic ...

    # Generate GitHub Actions workflow
    try:
        from hitoshura25_pypi_workflow_generator import generate_workflows

        # Change to project directory
        original_dir = os.getcwd()
        os.chdir(project_path)

        try:
            workflow_result = generate_workflows(
                python_version=python_version,
                test_path=import_name,  # Use import_name for test path
                prefix=prefix,           # Pass prefix to workflow generator
            )

            # In 0.3.1+, generate_workflows creates 3 workflows and 1 script
            if workflow_result['success']:
                files_created.append('.github/workflows/_reusable-test-build.yml')
                files_created.append('.github/workflows/release.yml')
                files_created.append('.github/workflows/test-pr.yml')
                files_created.append('scripts/calculate_version.sh')
        finally:
            os.chdir(original_dir)

    except ImportError:
        raise ImportError(
            "hitoshura25-pypi-workflow-generator is required but not installed. "
            "Install with: pip install hitoshura25-pypi-workflow-generator"
        )

    return {
        'success': True,
        'project_path': project_path,
        'package_name': full_package_name,  # Include in return for reference
        'import_name': import_name,
        'files_created': files_created,
        'message': f"Successfully generated MCP server project '{full_package_name}' at {project_path}"
    }
```

### 4.4 Update CLI

**File**: `hitoshura25_mcp_server_generator/cli.py`

Add prefix arguments:

```python
def main():
    parser = argparse.ArgumentParser(
        description='Generate MCP server projects'
    )

    # ... existing arguments ...

    # Add prefix arguments
    parser.add_argument(
        '--prefix',
        default='AUTO',
        help=(
            'Package name prefix mode (default: AUTO). '
            'Options: AUTO (detect from git), NONE (no prefix), '
            'or custom string (e.g., "acme")'
        )
    )
    parser.add_argument(
        '--no-prefix',
        action='store_const',
        const='NONE',
        dest='prefix',
        help='Disable package name prefix (equivalent to --prefix NONE)'
    )

    args = parser.parse_args()

    # ... rest of CLI logic ...

    # When calling generate_mcp_server:
    result = generate_mcp_server(
        project_name=args.project_name,
        description=args.description,
        author=args.author,
        author_email=args.email,
        tools=tools,
        output_dir=args.output_dir,
        prefix=args.prefix,  # Pass prefix
    )
```

Update interactive mode:

```python
def interactive_mode():
    """Interactive mode for generating MCP servers."""
    print("MCP Server Generator - Interactive Mode\n")

    # ... existing prompts ...

    # Add prefix prompt
    print("\n=== Package Naming ===")
    print("Choose how to name your package on PyPI:")
    print("  1. AUTO   - Auto-detect prefix from git (recommended)")
    print("  2. Custom - Specify your own prefix (e.g., 'acme')")
    print("  3. NONE   - No prefix (only for truly unique names)")
    print()

    prefix_choice = input("Prefix mode (1/2/3) [1]: ").strip() or "1"

    if prefix_choice == "1":
        prefix = "AUTO"
    elif prefix_choice == "2":
        prefix = input("Enter your prefix: ").strip()
        if not prefix:
            print("Error: Prefix cannot be empty")
            return 1
    elif prefix_choice == "3":
        prefix = "NONE"
    else:
        print("Invalid choice")
        return 1

    # Show what will be generated
    from .git_utils import apply_prefix
    full_name, import_name = apply_prefix(project_name, prefix)

    print(f"\nPackage will be named:")
    print(f"  PyPI package: {full_name}")
    print(f"  Python import: {import_name}")
    print(f"  Command: {full_name}")

    confirm = input("\nContinue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return 1

    # ... rest of generation ...
```

### 4.5 Update MCP Server

**File**: `hitoshura25_mcp_server_generator/server.py`

Update tool definition:

```python
async def handle_list_tools(self) -> Dict[str, Any]:
    """List available tools."""
    return {
        "tools": [
            {
                "name": "generate_mcp_server",
                "description": "Generate a complete MCP server project with dual-mode architecture",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Base project name (e.g., 'my-mcp-server')"
                        },
                        # ... other existing properties ...
                        "prefix": {
                            "type": "string",
                            "description": (
                                "Package name prefix mode. Options:\n"
                                "- 'AUTO' (default): Auto-detect from git config (recommended)\n"
                                "- Custom string (e.g., 'acme'): Use specified prefix\n"
                                "- 'NONE': No prefix (for unique package names)\n\n"
                                "Examples:\n"
                                "- prefix='AUTO' with git user 'jsmith' → 'jsmith-my-tool'\n"
                                "- prefix='acme' → 'acme-my-tool'\n"
                                "- prefix='NONE' → 'my-tool'"
                            ),
                            "default": "AUTO"
                        }
                    },
                    "required": ["project_name", "description", "author", "author_email", "tools"]
                }
            },
            # ... other tools ...
        ]
    }
```

---

## 5. CHANGES TO TEMPLATES

All templates in `hitoshura25_mcp_server_generator/templates/python/` must be updated to use the new context variables.

### 5.1 Template Variable Changes

**New Context Variables**:
- `project_name`: Full PyPI package name with prefix (e.g., "acme-my-tool")
- `package_name`: Directory/import name with underscores (e.g., "acme_my_tool")
- `import_name`: Same as package_name, for clarity in entry points
- `base_name`: Original name without prefix (e.g., "my-tool")

### 5.2 pyproject.toml Template

**File**: `hitoshura25_mcp_server_generator/templates/python/pyproject.toml.j2`

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
version_scheme = "post-release"

[project]
name = "{{ project_name }}"  # Full name with prefix
description = "{{ description }}"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "Apache-2.0"}
authors = [
    {name = "{{ author }}", email = "{{ author_email }}"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "Jinja2>=3.0",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://github.com/{{ author }}/{{ project_name }}"
Repository = "https://github.com/{{ author }}/{{ project_name }}"
Issues = "https://github.com/{{ author }}/{{ project_name }}/issues"

[project.scripts]
"{{ project_name }}" = "{{ import_name }}.cli:main"
"mcp-{{ project_name }}" = "{{ import_name }}.server:main"
```

### 5.3 setup.py Template

**File**: `hitoshura25_mcp_server_generator/templates/python/setup.py.j2`

**CRITICAL**: Entry points must use `import_name` (underscores), not `project_name` (hyphens)!

```python
from setuptools import setup, find_packages
import os


def local_scheme(version):
    if os.environ.get("IS_PULL_REQUEST"):
        return f".dev{os.environ.get('GITHUB_RUN_ID', 'local')}"
    return ""


try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""


setup(
    name='{{ project_name }}',  # PyPI package name (hyphens)
    author='{{ author }}',
    author_email='{{ author_email }}',
    description='{{ description }}',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/{{ author }}/{{ project_name }}',
    use_scm_version={"local_scheme": local_scheme},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Jinja2>=3.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': [
            # CRITICAL: Use import_name (underscores) here, not project_name!
            '{{ project_name }}={{ import_name }}.cli:main',
            'mcp-{{ project_name }}={{ import_name }}.server:main',
        ],
    },
)
```

### 5.4 README Template

**File**: `hitoshura25_mcp_server_generator/templates/python/README.md.j2`

```markdown
# {{ project_name }}

{{ description }}

## Installation

```bash
pip install {{ project_name }}
```

## Usage

### CLI Mode

```bash
{{ project_name }} --help
```

### MCP Server Mode

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "{{ project_name }}": {
      "command": "mcp-{{ project_name }}"
    }
  }
}
```

### Python API

```python
from {{ import_name }} import my_function

result = my_function()
```

## Development

```bash
git clone https://github.com/{{ author }}/{{ project_name }}
cd {{ project_name }}
python3 -m venv venv
source venv/bin/activate
pip install -e .
pytest
```

## License

{{ license }}
```

### 5.5 MCP-USAGE Template

**File**: `hitoshura25_mcp_server_generator/templates/python/MCP-USAGE.md.j2`

Update command examples to use `project_name`:

```markdown
# MCP Usage Guide for {{ project_name }}

## Installation

```bash
pip install {{ project_name }}
```

## Configuration

### macOS/Linux

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "{{ project_name }}": {
      "command": "mcp-{{ project_name }}"
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "{{ project_name }}": {
      "command": "mcp-{{ project_name }}"
    }
  }
}
```

## Testing

```bash
# Install
pip install {{ project_name }}

# Verify command exists
which mcp-{{ project_name }}

# Test in Claude Desktop
# (Restart Claude Desktop after configuration change)
```
```

### 5.6 Other Templates

Similar updates needed for:
- `__init__.py.j2`: Update package metadata
- `cli.py.j2`: Update help text references
- `server.py.j2`: Update server name property
- `tests/test_server.py.j2`: Update import paths in tests
- `tests/test_generator.py.j2`: Update import paths in tests

---

## 6. CHANGES TO DOCUMENTATION

### 6.1 README.md - Add Prefix Section

Add after "Overview" section:

```markdown
## Package Naming Convention

This tool uses **prefixed package names** to avoid PyPI namespace conflicts:

- **Package name**: `hitoshura25-mcp-server-generator` (on PyPI)
- **Import name**: `hitoshura25_mcp_server_generator` (in Python)
- **CLI command**: `hitoshura25-mcp-server-generator-cli`

### Why Prefixes?

PyPI has a flat global namespace where package names must be unique across all users. Using prefixes:

✅ Prevents naming conflicts
✅ Makes ownership clear
✅ Groups related packages by author
✅ Follows PyPI best practices

### Prefix Options for Generated Projects

When generating a new MCP server, you can control the package naming:

#### AUTO Mode (Recommended)

Automatically detects your GitHub username from git configuration:

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name my-tool \
  --prefix AUTO  # Or omit, it's the default
  # ... other args
```

**Detection Priority**:
1. `git config --get github.user`
2. GitHub username from remote URL
3. `git config --get user.name` (sanitized)

**Example**: If your git user is "jsmith", generates → `jsmith-my-tool`

#### Custom Prefix

Specify your own prefix:

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name my-tool \
  --prefix acme \
  # ... other args
```

**Example**: Generates → `acme-my-tool`

#### No Prefix

For truly unique package names:

```bash
hitoshura25-mcp-server-generator-cli \
  --project-name unique-tool-name \
  --no-prefix \
  # ... other args
```

**Example**: Generates → `unique-tool-name`

⚠️ **Warning**: Only use `--no-prefix` if you're confident your package name is globally unique on PyPI.

### Package Naming Example

```bash
# Given:
User: jsmith (from git)
Command: --project-name my-tool --prefix AUTO

# Creates:
PyPI Package:   jsmith-my-tool
Import:         jsmith_my_tool
CLI Command:    jsmith-my-tool
Directory:      jsmith-my-tool/
```
```

### 6.2 README.md - Add Migration Guide

Add new section before "License":

```markdown
## Migration from Pre-1.0.0 Versions

If you're upgrading from `mcp-server-generator` (without prefix):

### 1. Uninstall Old Version

```bash
pip uninstall mcp-server-generator
```

### 2. Install New Version

```bash
pip install hitoshura25-mcp-server-generator
```

### 3. Update Your Code

#### Command Line

```diff
# Old
-mcp-server-generator-cli --interactive
+hitoshura25-mcp-server-generator-cli --interactive
```

#### Python Imports

```diff
# Old
-from mcp_server_generator import generate_mcp_server
+from hitoshura25_mcp_server_generator import generate_mcp_server
```

#### MCP Configuration

```diff
{
  "mcpServers": {
-    "mcp-server-generator": {
-      "command": "mcp-server-generator"
+    "hitoshura25-mcp-server-generator": {
+      "command": "hitoshura25-mcp-server-generator-server"
    }
  }
}
```

### 4. Generated Projects Now Use Prefixes

Projects generated with v1.0.0+ will include prefixes by default (AUTO mode). To opt out:

```bash
hitoshura25-mcp-server-generator-cli --no-prefix --project-name my-tool
```

### Backward Compatibility

For migration ease, v1.0.0 includes **deprecated command aliases**:

- `mcp-server-generator-cli` → Shows deprecation warning, still works
- Will be removed in v2.0.0

### Need Help?

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) or [open an issue](https://github.com/hitoshura25/mcp-server-generator/issues).
```

### 6.3 Create MIGRATION_GUIDE.md

**New File**: `/Users/vinayakmenon/mcp-server-generator/MIGRATION_GUIDE.md`

Create comprehensive migration guide with:
- Detailed before/after comparisons
- Troubleshooting section
- FAQ about prefix usage
- Example migration scenarios

(Full content omitted for brevity - see separate document)

### 6.4 Update Other Documentation

- **MCP-USAGE.md**: Update all command examples
- **CONTRIBUTING.md**: Update development setup
- **EXAMPLES.md**: Add prefix examples

---

## 7. TESTING STRATEGY

### 7.1 New Unit Tests

**New File**: `hitoshura25_mcp_server_generator/tests/test_git_utils.py`

Test all git utility functions:

```python
"""Tests for git username detection and prefix application."""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
from hitoshura25_mcp_server_generator.git_utils import (
    get_github_username,
    sanitize_username,
    apply_prefix,
)


class TestGetGitHubUsername:
    """Tests for username detection."""

    def test_github_user_config(self):
        """Test detection from github.user config."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='hitoshura25\n',
                returncode=0
            )
            assert get_github_username() == 'hitoshura25'

    def test_remote_url_ssh(self):
        """Test detection from SSH remote URL."""
        # Test implementation
        pass

    def test_remote_url_https(self):
        """Test detection from HTTPS remote URL."""
        # Test implementation
        pass

    def test_user_name_fallback(self):
        """Test fallback to user.name."""
        # Test implementation
        pass

    def test_no_git_available(self):
        """Test when git is not available."""
        # Test implementation
        pass


class TestSanitizeUsername:
    """Tests for username sanitization."""

    def test_lowercase_conversion(self):
        assert sanitize_username('JOHN') == 'john'

    def test_space_to_hyphen(self):
        assert sanitize_username('John Smith') == 'john-smith'

    def test_remove_invalid_chars(self):
        assert sanitize_username('john@example.com') == 'johnexamplecom'

    def test_combined_transformations(self):
        assert sanitize_username('John Q. Smith Jr.') == 'john-q-smith-jr'


class TestApplyPrefix:
    """Tests for prefix application."""

    def test_auto_mode_with_detection(self):
        """Test AUTO mode when username detected."""
        with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock:
            mock.return_value = 'testuser'
            pkg, imp = apply_prefix('my-tool', 'AUTO')
            assert pkg == 'testuser-my-tool'
            assert imp == 'testuser_my_tool'

    def test_auto_mode_no_detection(self):
        """Test AUTO mode when username not detected."""
        with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock:
            mock.return_value = None
            pkg, imp = apply_prefix('my-tool', 'AUTO')
            assert pkg == 'my-tool'
            assert imp == 'my_tool'

    def test_custom_prefix(self):
        """Test custom prefix."""
        pkg, imp = apply_prefix('my-tool', 'acme')
        assert pkg == 'acme-my-tool'
        assert imp == 'acme_my_tool'

    def test_none_mode(self):
        """Test NONE mode (no prefix)."""
        pkg, imp = apply_prefix('my-tool', 'NONE')
        assert pkg == 'my-tool'
        assert imp == 'my_tool'
```

### 7.2 Integration Tests

**Update**: `hitoshura25_mcp_server_generator/tests/test_generator.py`

Add prefix integration tests:

```python
def test_generate_with_auto_prefix(tmp_path):
    """Test generation with AUTO prefix detection."""
    with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock:
        mock.return_value = 'testuser'

        result = generate_mcp_server(
            project_name='my-tool',
            description='Test',
            author='Test',
            author_email='test@test.com',
            tools=[{'name': 'test', 'description': 'Test', 'parameters': []}],
            output_dir=str(tmp_path),
            prefix='AUTO'
        )

        assert result['success']
        assert result['package_name'] == 'testuser-my-tool'
        assert result['import_name'] == 'testuser_my_tool'

        # Verify directory created with correct name
        assert (tmp_path / 'testuser-my-tool').exists()
        assert (tmp_path / 'testuser-my-tool' / 'testuser_my_tool').exists()


def test_generate_with_custom_prefix(tmp_path):
    """Test generation with custom prefix."""
    result = generate_mcp_server(
        project_name='my-tool',
        description='Test',
        author='Test',
        author_email='test@test.com',
        tools=[{'name': 'test', 'description': 'Test', 'parameters': []}],
        output_dir=str(tmp_path),
        prefix='acme'
    )

    assert result['success']
    assert result['package_name'] == 'acme-my-tool'
    assert (tmp_path / 'acme-my-tool').exists()


def test_generate_with_no_prefix(tmp_path):
    """Test generation without prefix."""
    result = generate_mcp_server(
        project_name='my-tool',
        description='Test',
        author='Test',
        author_email='test@test.com',
        tools=[{'name': 'test', 'description': 'Test', 'parameters': []}],
        output_dir=str(tmp_path),
        prefix='NONE'
    )

    assert result['success']
    assert result['package_name'] == 'my-tool'
    assert (tmp_path / 'my-tool').exists()


def test_entry_points_use_underscores(tmp_path):
    """Test that entry points use import_name (underscores), not hyphens."""
    result = generate_mcp_server(
        project_name='my-tool',
        description='Test',
        author='Test',
        author_email='test@test.com',
        tools=[{'name': 'test', 'description': 'Test', 'parameters': []}],
        output_dir=str(tmp_path),
        prefix='acme'
    )

    setup_py = tmp_path / 'acme-my-tool' / 'setup.py'
    content = setup_py.read_text()

    # Entry points MUST use underscore import name
    assert 'acme-my-tool=acme_my_tool.cli:main' in content
    # Should NOT have hyphens in import path
    assert 'acme-my-tool.cli:main' not in content
```

### 7.3 CLI Tests

**Update**: `hitoshura25_mcp_server_generator/tests/test_cli.py`

```python
def test_cli_prefix_flag(tmp_path, monkeypatch):
    """Test --prefix flag."""
    # Implementation
    pass

def test_cli_no_prefix_flag(tmp_path, monkeypatch):
    """Test --no-prefix flag."""
    # Implementation
    pass

def test_interactive_prefix_selection(tmp_path, monkeypatch):
    """Test interactive prefix prompt."""
    # Implementation
    pass
```

### 7.4 Test Coverage Goals

- Git utils: **95%+ coverage**
- Prefix application: **100% coverage**
- Template rendering: **100% coverage with prefix variables**
- CLI arguments: **90%+ coverage**
- MCP server tool: **100% coverage for new parameter**

### 7.5 Manual Testing Checklist

- [ ] Generate project with AUTO prefix (verify git detection)
- [ ] Generate project with custom prefix
- [ ] Generate project with NONE prefix
- [ ] Verify generated project installs correctly
- [ ] Verify generated entry points work
- [ ] Test MCP server mode with prefixed package
- [ ] Test CLI mode with prefixed package
- [ ] Verify workflow generation includes prefix parameter

---

## 8. MIGRATION PATH FOR EXISTING USERS

### 8.1 Version Strategy

**Target Version**: v1.0.0 (major version bump for breaking change)

**Breaking Changes**:
1. Package name: `mcp-server-generator` → `hitoshura25-mcp-server-generator`
2. Import path: `mcp_server_generator` → `hitoshura25_mcp_server_generator`
3. CLI command: `mcp-server-generator-cli` → `hitoshura25-mcp-server-generator-cli`
4. MCP command: `mcp-server-generator` → `hitoshura25-mcp-server-generator-server`
5. Dependency: `pypi-workflow-generator` → `hitoshura25-pypi-workflow-generator`
6. Generated projects use prefixes by default

### 8.2 Deprecation Timeline

**v1.0.0** (Current Release):
- Introduce prefixed package
- Keep backward-compatible command aliases:
  ```python
  entry_points={
      'console_scripts': [
          # New (primary)
          'hitoshura25-mcp-server-generator-server=hitoshura25_mcp_server_generator.server:main',
          'hitoshura25-mcp-server-generator-cli=hitoshura25_mcp_server_generator.cli:main',

          # Deprecated (for migration)
          'mcp-server-generator-cli=hitoshura25_mcp_server_generator.cli:main',
      ],
  }
  ```
- Add deprecation warnings when old commands are used
- Full documentation of migration path

**v2.0.0** (Future):
- Remove deprecated command aliases
- Full break from old naming

### 8.3 Communication Strategy

#### Release Announcement

Create GitHub Release with:

**Title**: `v1.0.0: Breaking Change - Prefix Adoption`

**Body**:
```markdown
# Version 1.0.0 - Breaking Changes: Prefix Adoption

## ⚠️ Breaking Changes

This release adopts prefixed package naming to solve PyPI namespace conflicts.

**New Package Name**: `hitoshura25-mcp-server-generator`

### What You Need to Do

1. **Uninstall old version**:
   ```bash
   pip uninstall mcp-server-generator
   ```

2. **Install new version**:
   ```bash
   pip install hitoshura25-mcp-server-generator
   ```

3. **Update imports**:
   ```python
   # Before
   from mcp_server_generator import generate_mcp_server

   # After
   from hitoshura25_mcp_server_generator import generate_mcp_server
   ```

4. **Update CLI commands**:
   ```bash
   # Before
   mcp-server-generator-cli --interactive

   # After
   hitoshura25-mcp-server-generator-cli --interactive
   ```

5. **Update MCP config**:
   ```json
   {
     "mcpServers": {
       "hitoshura25-mcp-server-generator": {
         "command": "hitoshura25-mcp-server-generator-server"
       }
     }
   }
   ```

## New Feature: Prefix Support

Generated projects now support automatic prefix detection:

```bash
# Auto-detect from git (default)
hitoshura25-mcp-server-generator-cli --project-name my-tool

# Custom prefix
hitoshura25-mcp-server-generator-cli --project-name my-tool --prefix acme

# No prefix
hitoshura25-mcp-server-generator-cli --project-name unique-tool --no-prefix
```

## Migration Help

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions.

## Questions?

Open an issue: https://github.com/hitoshura25/mcp-server-generator/issues
```

#### PyPI Description Update

Update PyPI project description to mention the prefix and link to migration guide.

#### README Badge

Add prominent notice in README:

```markdown
> **⚠️ Version 1.0.0 Breaking Change**
> This package has been renamed to `hitoshura25-mcp-server-generator`.
> See [Migration Guide](MIGRATION_GUIDE.md) for upgrade instructions.
```

### 8.4 User Support

**Prepare for common questions**:

1. **"Why the name change?"**
   - PyPI namespace conflicts
   - Best practice for package isolation
   - Follows industry patterns

2. **"Do I have to use a prefix for my projects?"**
   - No, use `--no-prefix` flag
   - But AUTO is recommended to avoid conflicts

3. **"Can I use the old package name?"**
   - No, must upgrade to prefixed version
   - Old aliases work in v1.0.0 for migration period

4. **"Will my existing generated projects work?"**
   - Yes, they're unaffected
   - Only new projects will use prefixes by default

---

## 9. IMPLEMENTATION ORDER

### Recommended Phased Approach

#### Phase 1: Foundation (No Breaking Changes)
**Goal**: Add prefix functionality without breaking existing code
**Duration**: 4-6 hours

1. Create `git_utils.py` module
2. Write tests for `git_utils.py` (test_git_utils.py)
3. Add `prefix` parameter to `generate_mcp_server()` with default "AUTO"
4. Update CLI to accept `--prefix` and `--no-prefix` flags
5. Update MCP server tool schema to include prefix parameter
6. Run tests to verify no regressions

**Deliverable**: Prefix support works, but package still named `mcp-server-generator`

#### Phase 2: Template Updates
**Goal**: Update templates to handle prefixed names
**Duration**: 3-4 hours

7. Update all `.j2` templates to use new context variables
8. Add template validation tests
9. Test generation with AUTO, custom, and NONE prefixes
10. Verify entry points use correct import names (underscores)
11. Manual testing of generated projects

**Deliverable**: Generated projects correctly use prefixes

#### Phase 3: Documentation
**Goal**: Document the prefix feature
**Duration**: 2-3 hours

12. Update README.md with prefix explanation
13. Update MCP-USAGE.md examples
14. Update EXAMPLES.md with prefix examples
15. Create MIGRATION_GUIDE.md
16. Write v1.0.0 release notes

**Deliverable**: Complete documentation ready

#### Phase 4: Self-Application (BREAKING CHANGE)
**Goal**: Rename mcp-server-generator itself
**Duration**: 4-5 hours

17. **Update dependencies**:
    - Change `pypi-workflow-generator>=0.3.0` → `hitoshura25-pypi-workflow-generator>=0.3.1`
    - Update in: pyproject.toml, setup.py, requirements.txt

18. **Rename package directory**:
    ```bash
    git mv mcp_server_generator/ hitoshura25_mcp_server_generator/
    ```

19. **Update all imports**:
    - In all Python files: `mcp_server_generator` → `hitoshura25_mcp_server_generator`
    - In all test files
    - In documentation code examples

20. **Update pyproject.toml**:
    - Change package name to `hitoshura25-mcp-server-generator`

21. **Update setup.py**:
    - Change package name
    - Update entry points with new primary commands
    - Add deprecated aliases

22. **Update GitHub workflows**:
    - Change test paths from `mcp_server_generator` → `hitoshura25_mcp_server_generator`

23. **Update all documentation references**

24. Run full test suite and fix any import errors

**Deliverable**: Package successfully renamed, all tests pass

#### Phase 5: Testing & Validation
**Goal**: Comprehensive validation before release
**Duration**: 2-3 hours

25. **Manual testing**:
    - Test CLI interactive mode
    - Test CLI with all prefix modes
    - Test MCP server mode
    - Generate sample projects and verify they work
    - Test that generated projects can be installed
    - Verify entry points execute correctly

26. **Automated testing**:
    - Run full test suite
    - Check test coverage (>= 82%)
    - Run tests with different Python versions

27. **Integration testing**:
    - Test with hitoshura25-pypi-workflow-generator 0.3.1
    - Verify workflow generation works
    - Test generated projects' workflows

28. **Documentation review**:
    - Verify all examples work
    - Check all links
    - Review migration guide

**Deliverable**: Fully tested and validated

#### Phase 6: Release
**Goal**: Publish to PyPI
**Duration**: 1-2 hours

29. Create release branch: `release/v1.0.0`
30. Final version bump if needed
31. Create annotated git tag: `v1.0.0`
32. Push tag to GitHub
33. Trigger release workflow (automated PyPI publish)
34. Verify package appears on PyPI: `pip install hitoshura25-mcp-server-generator`
35. Test installation from PyPI
36. Publish GitHub Release with announcement
37. Update repository description and topics
38. Monitor for issues

**Deliverable**: v1.0.0 published and available

---

## 10. ROLLBACK PLAN

### If Issues Found Before PyPI Publication

**Action**: Revert all changes

```bash
git reset --hard <commit-before-changes>
git push --force
```

**Impact**: No users affected, can retry

### If Issues Found After PyPI Publication

**Problem**: Cannot un-publish from PyPI

**Options**:

1. **Hotfix Release** (Preferred):
   ```bash
   # Fix the issue
   git commit -m "Fix: Critical bug in v1.0.0"
   # Tag v1.0.1
   git tag v1.0.1
   # Push and publish
   ```

2. **Yanked Release**:
   - Mark v1.0.0 as "yanked" on PyPI (prevents new installs)
   - Publish fixed v1.0.1
   - Document issues in release notes

3. **Parallel Non-Prefixed Version** (Last Resort):
   - If critical, could publish non-prefixed version temporarily
   - Not recommended - causes confusion

### Mitigation Strategies

**To minimize rollback risk**:

1. **Thorough Testing**: Complete Phase 5 thoroughly
2. **Beta Release**: Consider publishing v1.0.0b1 first for testing
3. **Staged Rollout**:
   - Announce beta release
   - Request community testing
   - Monitor feedback before official 1.0.0
4. **Clear Documentation**: Ensure migration guide is comprehensive
5. **Quick Response**: Monitor issues closely after release

---

## 11. SUCCESS CRITERIA

The migration is successful when all criteria are met:

### Functionality
- [ ] Package publishes to PyPI as `hitoshura25-mcp-server-generator`
- [ ] CLI works: `hitoshura25-mcp-server-generator-cli --interactive`
- [ ] MCP server works with Claude Desktop using new command
- [ ] Generated projects correctly apply prefixes (AUTO, custom, NONE)
- [ ] Generated projects can be published to PyPI without conflicts
- [ ] All entry points execute correctly
- [ ] No import errors in any mode
- [ ] Workflow generation passes prefix to hitoshura25-pypi-workflow-generator

### Testing
- [ ] All existing tests pass (34/34)
- [ ] New prefix tests added and passing (>10 new tests)
- [ ] Test coverage maintained >= 82%
- [ ] Manual testing complete for all modes
- [ ] Generated projects' tests pass
- [ ] No regressions in existing functionality

### Documentation
- [ ] README updated with new package name and prefix guide
- [ ] MIGRATION_GUIDE.md created and comprehensive
- [ ] Examples updated with prefix scenarios
- [ ] MCP-USAGE.md updated with new commands
- [ ] CONTRIBUTING.md updated with new paths
- [ ] Release notes written and clear

### Quality
- [ ] No breaking changes to API (except package name)
- [ ] Backward compatibility maintained via deprecated aliases
- [ ] Clear, helpful error messages
- [ ] User feedback incorporated (if beta tested)
- [ ] Code follows existing style and conventions
- [ ] All templates render correctly with prefix variables

### User Experience
- [ ] Installation instructions clear and accurate
- [ ] Migration path well-documented
- [ ] Common questions addressed in FAQ
- [ ] Troubleshooting guide available
- [ ] Deprecation warnings visible but not disruptive

### Release
- [ ] Git tag created: v1.0.0
- [ ] Published to PyPI successfully
- [ ] GitHub Release created with full notes
- [ ] Repository description updated
- [ ] Old package name updated to point to new package

---

## 12. TIMELINE ESTIMATE

### Conservative Estimate: 2-3 Days

**Day 1: Foundation + Templates** (9-10 hours)
- Morning (4 hours):
  - Phase 1: Create git_utils.py
  - Write tests for git utilities
  - Add prefix parameter to generator
- Afternoon (3 hours):
  - Update CLI with prefix flags
  - Update MCP server tool schema
  - Test Phase 1 completion
- Evening (2-3 hours):
  - Phase 2: Update all templates
  - Test template rendering

**Day 2: Self-Application + Testing** (9-10 hours)
- Morning (2 hours):
  - Phase 3: Update documentation
  - Write migration guide
- Afternoon (4-5 hours):
  - Phase 4: Rename package directory
  - Update all imports
  - Update dependencies
  - Fix breaking changes
- Evening (3 hours):
  - Phase 5: Testing and validation
  - Manual testing all modes
  - Fix any issues found

**Day 3: Buffer + Release** (4-8 hours)
- Morning (2 hours):
  - Final testing
  - Documentation review
- Afternoon (1-2 hours):
  - Phase 6: Create release
  - Publish to PyPI
  - Monitor for issues
- Buffer (4 hours):
  - Reserved for unexpected issues
  - User support if needed

### Aggressive Estimate: 1 Day (8-10 hours)

**Only if**:
- No major issues encountered
- No feedback/review cycles needed
- All phases go smoothly

**Risk**: Higher chance of missing issues

### Recommended Approach: 2-Day Timeline

**Day 1**: Phases 1-3 (Feature complete, not breaking)
**Day 2**: Phases 4-6 (Breaking change, testing, release)

This allows testing the prefix feature before applying it to the package itself.

---

## 13. RISKS & MITIGATION

### Risk 1: Import Path Changes Break Users

**Impact**: HIGH
**Probability**: CERTAIN (it's a breaking change)

**Mitigation**:
- Provide clear, detailed migration guide
- Include deprecated command aliases in v1.0.0
- Add prominent warnings in README
- Communicate breaking changes in release notes
- Offer to help users with migration issues
- Consider beta release for community testing

**Contingency**:
- Quick hotfix for critical issues
- Support users via GitHub issues

### Risk 2: PyPI Workflow Generator Compatibility

**Impact**: HIGH
**Probability**: LOW

**Issue**: hitoshura25-pypi-workflow-generator 0.3.1 might have incompatibilities

**Mitigation**:
- Test thoroughly with 0.3.1 before release
- Verify `generate_workflows()` API is stable
- Check that prefix parameter works as expected
- Have fallback plan to vendor workflow templates if needed

**Contingency**:
- Temporarily vendor workflow templates
- Work with pypi-workflow-generator maintainer (yourself!)

### Risk 3: Template Rendering Errors with Prefixes

**Impact**: MEDIUM
**Probability**: MEDIUM

**Issue**: Templates might not handle prefix variables correctly

**Mitigation**:
- Comprehensive template tests
- Manual testing with all prefix modes
- Test with various project names
- Verify entry points use underscores, not hyphens

**Contingency**:
- Hotfix template bugs
- Clear error messages guide users to issues

### Risk 4: Git Detection Failures

**Impact**: LOW (users can use custom prefix)
**Probability**: MEDIUM

**Issue**: Auto-detection might fail in some git configurations

**Mitigation**:
- Graceful fallback to no prefix
- Clear error messages explaining detection
- Document manual prefix specification
- Test in various git environments
- Handle edge cases (detached HEAD, no remotes, etc.)

**Contingency**:
- Users can always use custom prefix or --no-prefix

### Risk 5: Entry Point Import Errors

**Impact**: HIGH (would break generated projects)
**Probability**: LOW (if tested correctly)

**Critical Issue**: Entry points must use underscores (`import_name`), not hyphens (`project_name`)

**Mitigation**:
- **Explicit testing** of entry point execution
- Verify generated projects' commands work
- Test with prefixed package names
- Review template carefully: `'{{ project_name }}={{ import_name }}.cli:main'`

**Contingency**:
- Immediate hotfix if discovered
- Template correction

### Risk 6: User Confusion About Prefixes

**Impact**: MEDIUM
**Probability**: MEDIUM

**Issue**: Users might not understand when to use prefixes

**Mitigation**:
- Clear documentation with examples
- Interactive mode explains prefix options
- Default to AUTO (sensible default)
- Provide guidance on when to use --no-prefix
- Add FAQ section

**Contingency**:
- Add more examples based on user questions
- Update documentation iteratively

### Risk 7: Abandoned Old Package Name

**Impact**: LOW
**Probability**: HIGH

**Issue**: `mcp-server-generator` (without prefix) remains on PyPI but becomes stale

**Mitigation**:
- Update PyPI description to redirect users
- Point to new package in old package README
- Cannot transfer ownership (PyPI limitation)

**Contingency**:
- Monitor old package page
- Update description with redirect

---

## 14. POST-MIGRATION TASKS

### Immediate (Within 24 Hours)

1. **Monitor PyPI**:
   - Check download statistics
   - Monitor for error reports
   - Verify package metadata displays correctly

2. **Monitor GitHub Issues**:
   - Watch for user-reported problems
   - Respond quickly to migration questions
   - Track common issues for FAQ updates

3. **Test Installation**:
   - Verify installation works on clean systems
   - Test on macOS, Linux, Windows
   - Confirm MCP server mode works in Claude Desktop

### Short-Term (Within 1 Week)

4. **Update External References**:
   - GitHub repository description
   - PyPI project description
   - Any blog posts or articles
   - Social media announcements

5. **Community Engagement**:
   - Post announcement in relevant channels
   - Help users with migration
   - Gather feedback on prefix feature

6. **Documentation Improvements**:
   - Add FAQ entries based on user questions
   - Update troubleshooting guide
   - Add more examples if needed

7. **Analytics**:
   - Track adoption rate
   - Monitor for migration issues
   - Assess user sentiment

### Medium-Term (Within 1 Month)

8. **Address Feedback**:
   - Fix reported bugs
   - Improve documentation based on feedback
   - Consider feature requests

9. **Evaluate Deprecation Timeline**:
   - Assess if deprecated aliases can be removed in v2.0.0
   - Gather data on alias usage

10. **Performance Review**:
    - Check if prefix detection is reliable
    - Optimize git operations if needed
    - Review error rates

### Long-Term (Ongoing)

11. **Plan v2.0.0**:
    - Remove deprecated command aliases
    - Consider additional prefix features
    - Evaluate user adoption metrics

12. **Continuous Improvement**:
    - Update dependencies
    - Add new features
    - Maintain documentation

13. **Support Old Package**:
    - Keep old `mcp-server-generator` PyPI page updated with redirect
    - Monitor for confusion

---

## APPENDIX A: Quick Reference

### Before Migration

```bash
# Package
pip install mcp-server-generator

# Import
from mcp_server_generator import generate_mcp_server

# CLI
mcp-server-generator-cli --interactive

# MCP
"command": "mcp-server-generator"
```

### After Migration (v1.0.0)

```bash
# Package
pip install hitoshura25-mcp-server-generator

# Import
from hitoshura25_mcp_server_generator import generate_mcp_server

# CLI
hitoshura25-mcp-server-generator-cli --interactive

# CLI with prefix options
hitoshura25-mcp-server-generator-cli --prefix AUTO  # Default
hitoshura25-mcp-server-generator-cli --prefix acme  # Custom
hitoshura25-mcp-server-generator-cli --no-prefix    # None

# MCP
"command": "hitoshura25-mcp-server-generator-server"
```

---

## APPENDIX B: Checklist

### Pre-Implementation
- [ ] Review and approve this plan
- [ ] Create implementation branch: `feat/prefix-adoption`
- [ ] Set up development environment
- [ ] Backup current stable version

### Implementation
- [ ] Phase 1: Foundation complete
- [ ] Phase 2: Templates complete
- [ ] Phase 3: Documentation complete
- [ ] Phase 4: Self-application complete
- [ ] Phase 5: Testing complete
- [ ] Phase 6: Release complete

### Post-Implementation
- [ ] Monitor PyPI and GitHub
- [ ] Respond to user issues
- [ ] Update documentation as needed
- [ ] Plan v2.0.0 deprecation

---

**END OF IMPLEMENTATION PLAN**

**Status**: APPROVED - Ready to begin Phase 1
**Next Action**: Create `git_utils.py` and begin implementation
**Target Completion**: November 8-9, 2025
**Release Date**: November 9, 2025 (estimated)
