"""
Core MCP server generation logic.
"""

import os
import keyword
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader
from .git_utils import apply_prefix


def validate_project_name(name: Optional[str]) -> bool:
    """
    Validate Python package name.

    Args:
        name: Project name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False

    # Convert to package name (hyphens to underscores)
    package_name = name.replace('-', '_')

    # Check valid Python identifier
    if not package_name.isidentifier():
        return False

    # Check not a keyword
    if keyword.iskeyword(package_name):
        return False

    return True


def validate_tool_name(name: Optional[str]) -> bool:
    """
    Validate tool/function name.

    Args:
        name: Tool name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False

    # Must be valid Python identifier
    if not name.isidentifier():
        return False

    # Cannot be a keyword
    if keyword.iskeyword(name):
        return False

    return True


def generate_tool_schema(tool_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate MCP tool schema from simplified definition.

    Args:
        tool_definition: {
            "name": "my_tool",
            "description": "Does something",
            "parameters": [
                {
                    "name": "param1",
                    "type": "string",
                    "description": "First parameter",
                    "required": True
                }
            ]
        }

    Returns:
        Full MCP tool schema with inputSchema
    """
    # Map JSON Schema types to ensure compatibility
    TYPE_MAPPING = {
        'string': 'string',
        'str': 'string',
        'number': 'number',
        'int': 'number',
        'integer': 'number',
        'float': 'number',
        'boolean': 'boolean',
        'bool': 'boolean',
        'array': 'array',
        'list': 'array',
        'object': 'object',
        'dict': 'object',
    }

    schema = {
        "name": tool_definition["name"],
        "description": tool_definition.get("description", ""),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    for param in tool_definition.get("parameters", []):
        param_type = TYPE_MAPPING.get(param["type"].lower(), "string")

        schema["inputSchema"]["properties"][param["name"]] = {
            "type": param_type,
            "description": param.get("description", "")
        }

        if param.get("required", False):
            schema["inputSchema"]["required"].append(param["name"])

    return schema


def sanitize_description(text: str) -> str:
    """
    Sanitize user input for use in templates.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Remove any potential template injection characters
    # but keep it readable for documentation
    return text.replace('{', '{{').replace('}', '}}')


def generate_mcp_server(
    project_name: str,
    description: str,
    author: str,
    author_email: str,
    tools: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    python_version: str = "3.10",
    license_type: str = "Apache-2.0",
    prefix: str = "AUTO",
) -> Dict[str, Any]:
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
    # Validate inputs
    if not validate_project_name(project_name):
        raise ValueError(
            f"Invalid project name: '{project_name}'. "
            "Must be lowercase alphanumeric with hyphens/underscores, "
            "and not a Python keyword.\n"
            "Examples of valid names: 'my-mcp-server', 'calc_tools', 'api-wrapper'\n"
            "Examples of invalid names: 'class', '123-server', 'my server', 'my.server'"
        )

    # Validate tool names
    for tool in tools:
        if not validate_tool_name(tool["name"]):
            raise ValueError(
                f"Invalid tool name: '{tool['name']}'. "
                "Must be a valid Python identifier and not a keyword.\n"
                "Examples of valid names: 'add_numbers', 'get_data', 'process_file'\n"
                "Examples of invalid names: 'class', '123func', 'my-function', 'my function'"
            )

    if not tools:
        raise ValueError("At least one tool must be defined.")

    # Store original name
    base_name = project_name

    # Apply prefix to generate full package and import names
    full_package_name, import_name = apply_prefix(project_name, prefix)

    # Validate the full package name
    if not validate_project_name(full_package_name):
        raise ValueError(
            f"Invalid generated package name: '{full_package_name}'. "
            f"This may be due to an invalid prefix. Try using a different prefix."
        )

    # Use the full names for the project
    project_name = full_package_name
    package_name = import_name

    # Determine output directory
    if output_dir is None:
        output_dir = os.getcwd()

    # Normalize paths for comparison to handle ".", "./", absolute paths, etc.
    normalized_output = os.path.normpath(os.path.abspath(output_dir))
    current_dir = os.path.normpath(os.path.abspath(os.getcwd()))

    # Determine project path
    # If normalized output_dir matches current directory, generate in-place
    # Otherwise, create a subdirectory named after the project
    if normalized_output == current_dir:
        project_path = os.getcwd()
        # For in-place generation, check for conflicting files instead of directory
        conflicting_files = [
            'pyproject.toml', 'setup.py', 'README.md',
            'MCP-USAGE.md', 'LICENSE', 'MANIFEST.in', '.gitignore'
        ]
        existing = [f for f in conflicting_files if os.path.exists(os.path.join(project_path, f))]

        # Also check if package directory already exists
        if os.path.exists(os.path.join(project_path, package_name)):
            existing.append(f'{package_name}/ directory')

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

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates', 'python')

    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Templates not found at {template_dir}")

    # Validate and enforce minimum Python version
    # MCP SDK requires Python 3.10+
    def parse_version(version_str: str) -> tuple:
        """Parse version string like '3.10' into tuple (3, 10)"""
        try:
            parts = version_str.split('.')
            return tuple(int(p) for p in parts[:2])  # Use major.minor only
        except (ValueError, AttributeError):
            return (3, 10)  # Default to 3.10 if parsing fails

    user_version = parse_version(python_version)
    min_version = (3, 10)

    # Use the higher of user's version or minimum required version
    validated_version = max(user_version, min_version)
    validated_python_version = f"{validated_version[0]}.{validated_version[1]}"

    # Prepare template context
    context = {
        'project_name': project_name,     # Full name with hyphens (e.g., "hitoshura25-my-tool")
        'package_name': package_name,     # Full name with underscores (e.g., "hitoshura25_my_tool")
        'import_name': import_name,       # Same as package_name (for clarity in entry points)
        'base_name': base_name,           # Original name without prefix (e.g., "my-tool")
        'description': sanitize_description(description),
        'author': author,
        'author_email': author_email,
        'python_version': validated_python_version,
        'license': license_type,
        'tools': tools,
        'tool_schemas': [generate_tool_schema(tool) for tool in tools],
        'year': '2025',
    }

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Files to generate
    files_to_generate = [
        # Root files
        ('README.md.j2', 'README.md'),
        ('MCP-USAGE.md.j2', 'MCP-USAGE.md'),
        ('LICENSE.j2', 'LICENSE'),
        ('setup.py.j2', 'setup.py'),
        ('pyproject.toml.j2', 'pyproject.toml'),
        ('MANIFEST.in.j2', 'MANIFEST.in'),
        ('.gitignore.j2', '.gitignore'),

        # Package files
        ('__init__.py.j2', f'{package_name}/__init__.py'),
        ('server.py.j2', f'{package_name}/server.py'),
        ('cli.py.j2', f'{package_name}/cli.py'),
        ('generator.py.j2', f'{package_name}/generator.py'),

        # Tests
        ('tests/__init__.py.j2', f'{package_name}/tests/__init__.py'),
        ('tests/test_server.py.j2', f'{package_name}/tests/test_server.py'),
        ('tests/test_generator.py.j2', f'{package_name}/tests/test_generator.py'),
    ]

    files_created = []

    # Generate files
    for template_file, output_file in files_to_generate:
        try:
            template = env.get_template(template_file)
            content = template.render(**context)

            output_path = os.path.join(project_path, output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            files_created.append(output_file)
        except Exception as e:
            raise RuntimeError(f"Failed to generate {output_file}: {str(e)}")

    # Generate GitHub Actions workflow (required)
    try:
        from hitoshura25_pypi_workflow_generator import generate_workflows

        # Change to project directory
        original_dir = os.getcwd()
        os.chdir(project_path)

        try:
            workflow_result = generate_workflows(
                python_version=python_version,
                test_path=package_name,
            )

            # In 0.3.0+, generate_workflows creates 3 workflows and 1 script
            if workflow_result['success']:
                files_created.append('.github/workflows/_reusable-test-build.yml')
                files_created.append('.github/workflows/release.yml')
                files_created.append('.github/workflows/test-pr.yml')
                files_created.append('scripts/calculate_version.sh')
        finally:
            os.chdir(original_dir)

    except ImportError:
        raise ImportError(
            "pypi-workflow-generator is required but not installed. "
            "Install with: pip install pypi-workflow-generator"
        )

    return {
        'success': True,
        'project_path': project_path,
        'files_created': files_created,
        'message': f"Successfully generated MCP server project at {project_path}"
    }
