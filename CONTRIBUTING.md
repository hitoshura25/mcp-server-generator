# Contributing to MCP Server Generator

Thank you for your interest in contributing to mcp-server-generator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

This project follows a standard code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- Familiarity with MCP (Model Context Protocol)

### Finding Issues

Good ways to start contributing:

1. **Good First Issues**: Look for issues labeled `good-first-issue`
2. **Documentation**: Improve docs, fix typos, add examples
3. **Tests**: Add missing test cases, improve coverage
4. **Templates**: Enhance Jinja2 templates for better code generation
5. **Bug Fixes**: Fix reported bugs

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/mcp-server-generator.git
cd mcp-server-generator

# Add upstream remote
git remote add upstream https://github.com/hitoshura25/mcp-server-generator.git
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov
```

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest

# Check that entry points work
mcp-server-generator --help  # This may fail until built
mcp-server-generator-cli --help
```

## Project Structure

```
mcp-server-generator/
├── mcp_server_generator/          # Main package
│   ├── __init__.py                # Public API exports
│   ├── generator.py               # Core generation logic
│   ├── server.py                  # MCP server implementation
│   ├── cli.py                     # CLI implementation
│   ├── templates/                 # Jinja2 templates
│   │   └── python/                # Python MCP server templates
│   │       ├── *.j2               # Template files
│   │       └── tests/             # Test templates
│   └── tests/                     # Test suite
│       ├── test_generator.py      # Core logic tests
│       ├── test_server.py         # MCP protocol tests
│       ├── test_cli.py            # CLI tests
│       └── test_templates.py      # Template tests
├── README.md                      # Main documentation
├── MCP-USAGE.md                   # MCP configuration guide
├── CONTRIBUTING.md                # This file
├── EXAMPLES.md                    # Example projects
├── setup.py                       # Package setup
├── pyproject.toml                 # Build configuration
├── requirements.txt               # Dependencies
└── MANIFEST.in                    # Package manifest
```

## Development Workflow

### 1. Create a Branch

```bash
# Update your local main
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clear, focused commits
- Follow the code style guidelines
- Add/update tests as needed
- Update documentation if needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server_generator --cov-report=term-missing

# Run specific test file
pytest mcp_server_generator/tests/test_generator.py -v

# Run only async tests
pytest -m asyncio
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "Add feature: brief description"

# Or for bug fixes
git commit -m "Fix: issue description"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and PRs when relevant

Examples:
```
Add support for custom Python versions in templates
Fix template injection vulnerability in descriptions
Update documentation for MCP configuration
Test: Add coverage for error handling
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=mcp_server_generator --cov-report=html
open htmlcov/index.html  # View coverage report

# Specific test file
pytest mcp_server_generator/tests/test_generator.py

# Specific test function
pytest mcp_server_generator/tests/test_generator.py::test_validate_project_name_valid

# Run only failed tests from last run
pytest --lf
```

### Writing Tests

All new features should include tests. Follow these guidelines:

**1. Test Location:**
- Core logic tests: `test_generator.py`
- MCP protocol tests: `test_server.py`
- CLI tests: `test_cli.py`
- Template tests: `test_templates.py`

**2. Test Structure:**

```python
def test_descriptive_name():
    """Clear docstring explaining what is tested."""
    # Arrange
    input_data = "test"

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected_value
```

**3. Async Tests:**

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_function()
    assert result is not None
```

**4. Temporary Files:**

```python
def test_file_creation(tmp_path):
    """Test file creation using tmp_path fixture."""
    output_dir = tmp_path / "test_project"
    # Your test here
```

### Test Coverage Goals

- Overall coverage: >80% (currently 82%)
- New features: 100% coverage required
- Bug fixes: Add test that reproduces the bug

## Code Style

### Python Style

Follow PEP 8 with these specifics:

**1. Imports:**
```python
# Standard library
import os
import sys

# Third-party
from jinja2 import Environment

# Local
from .generator import validate_project_name
```

**2. Type Hints:**
```python
def generate_mcp_server(
    project_name: str,
    description: str,
    tools: List[Dict[str, Any]],
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Generate MCP server project."""
    pass
```

**3. Docstrings:**
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
    """
    pass
```

**4. Line Length:**
- Maximum 100 characters per line
- Break long lines logically

**5. Naming:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Template Style

For Jinja2 templates:

**1. Variable Access:**
```jinja2
{{ project_name }}
{{ package_name }}
```

**2. Conditionals:**
```jinja2
{% if condition %}
    content
{% endif %}
```

**3. Loops:**
```jinja2
{% for tool in tools %}
    {{ tool.name }}
{% endfor %}
```

**4. Comments:**
```jinja2
{# This is a comment #}
```

## Pull Request Process

### Before Submitting

1. **Update from upstream:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run tests:**
   ```bash
   pytest
   ```

3. **Check coverage:**
   ```bash
   pytest --cov=mcp_server_generator --cov-report=term-missing
   ```

4. **Update documentation** if needed

### Submitting a PR

1. **Push your branch:**
   ```bash
   git push origin your-branch
   ```

2. **Create Pull Request** on GitHub

3. **Fill out the PR template:**
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots if applicable

4. **PR Title Format:**
   ```
   Add: Brief description of feature
   Fix: Brief description of bug fix
   Docs: Brief description of doc changes
   Test: Brief description of test changes
   ```

### PR Review Process

1. Automated checks must pass:
   - All tests pass
   - Code coverage maintained
   - No merge conflicts

2. Code review by maintainer(s)

3. Address feedback:
   ```bash
   # Make changes
   git add .
   git commit -m "Address review feedback"
   git push origin your-branch
   ```

4. Approval and merge by maintainer

## Release Process

Releases are managed by project maintainers:

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Steps (Maintainers)

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions publishes to PyPI

## Areas for Contribution

### High Priority

- **Templates**: Improve generated code quality
- **Tests**: Increase coverage above 85%
- **Documentation**: Add more examples
- **Error Messages**: Make errors more helpful

### Medium Priority

- **CLI**: Add more interactive features
- **Validation**: Stricter input validation
- **Templates**: Support for more languages (Node.js, Go)
- **Examples**: Real-world example projects

### Low Priority

- **Performance**: Optimize template rendering
- **Logging**: Add debug logging
- **Configuration**: Support config files

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/hitoshura25/mcp-server-generator/discussions)
- **Bugs**: Open an [Issue](https://github.com/hitoshura25/mcp-server-generator/issues)
- **Features**: Open an [Issue](https://github.com/hitoshura25/mcp-server-generator/issues) with "enhancement" label
- **Chat**: Join discussions on existing issues/PRs

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- README acknowledgments section (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.

---

Thank you for contributing to mcp-server-generator! 🎉
