"""
Tests for template validation.
"""

import py_compile
from hitoshura25_mcp_server_generator import generate_mcp_server, generate_tool_schema
from jinja2 import Environment, FileSystemLoader


def test_all_templates_render(tmp_path):
    """Test that all templates render without errors."""
    template_dir = 'hitoshura25_mcp_server_generator/templates/python'
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
        'setup.py.j2', 'pyproject.toml.j2', 'MANIFEST.in.j2',
        '__init__.py.j2', 'server.py.j2', 'cli.py.j2', 'generator.py.j2',
        'tests/__init__.py.j2', 'tests/test_server.py.j2', 'tests/test_generator.py.j2'
    ]

    for template_name in templates:
        template = env.get_template(template_name)
        content = template.render(**context)
        assert len(content) > 0, f"{template_name} rendered empty"


def test_generated_python_syntax(tmp_path):
    """Test that generated Python files have valid syntax."""
    result = generate_mcp_server(
        project_name="syntax-test",
        description="Syntax test",
        author="Test",
        author_email="test@test.com",
        tools=[{"name": "test", "description": "Test", "parameters": []}],
        output_dir=str(tmp_path),
        prefix="NONE"
    )
    assert result['success'] == True

    project_path = tmp_path / "syntax-test"

    # Find all Python files
    python_files = []
    for py_file in project_path.rglob("*.py"):
        python_files.append(py_file)
        # Should compile without errors
        py_compile.compile(str(py_file), doraise=True)

    # Ensure we found some Python files
    assert len(python_files) > 0, "No Python files found in generated project"


def test_generated_files_contain_project_info(tmp_path):
    """Test that generated files contain the correct project information."""
    result = generate_mcp_server(
        project_name="content-test",
        description="Content test server",
        author="Test Author",
        author_email="test@test.com",
        tools=[{"name": "func", "description": "Function", "parameters": []}],
        output_dir=str(tmp_path),
        prefix="NONE"
    )
    assert result['success'] == True

    project_path = tmp_path / "content-test"

    # Check README contains project name and description
    readme = (project_path / "README.md").read_text()
    assert "content-test" in readme
    assert "Content test server" in readme

    # Check setup.py contains project name and author
    setup = (project_path / "setup.py").read_text()
    assert "content-test" in setup
    assert "Test Author" in setup

    # Check author in LICENSE
    license_file = (project_path / "LICENSE").read_text()
    assert "Test Author" in license_file
    assert "2025" in license_file

    # Check package __init__.py imports the function
    init_file = (project_path / "content_test" / "__init__.py").read_text()
    assert "func" in init_file
