"""
Core MCP server generation logic.
"""

import os
import re
import keyword
from datetime import datetime
from pathlib import Path
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
    package_name = name.replace("-", "_")

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


def analyze_tool_security(tool_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a tool definition for potential security risks.

    Args:
        tool_definition: Tool definition to analyze

    Returns:
        dict with 'risk_level', 'warnings', and 'recommendations'
    """
    warnings = []
    recommendations = []
    risk_level = "low"

    name = tool_definition.get("name", "").lower()
    description = tool_definition.get("description", "").lower()
    combined = f"{name} {description}"

    # High-risk patterns - more specific to reduce false positives
    # Using word boundaries and specific combinations
    high_risk_patterns = [
        (r"\b(execute|exec)(_|-|command|cmd|shell|process)\b", "command execution"),
        (r"\bshell(_|-|exec|command|run)\b", "shell access"),
        (r"\brun(_|-|command|cmd|shell|process)\b", "command execution"),
        (r"\b(system|subprocess)(_|-|call|exec|run)\b", "system command"),
        (r"\beval(_|-|code|expression)\b", "code evaluation"),
        (r"\bcompile(_|-|code|source)\b", "code compilation"),
    ]

    # Medium-risk patterns - more specific combinations
    medium_risk_patterns = [
        (r"\b(write|create|save)(_|-|file|data)\b", "file write operations"),
        (r"\b(delete|remove|unlink)(_|-|file|data)\b", "file deletion"),
        (
            r"\b(sql|database|db)(_|-|query|execute|run|connect)\b",
            "database operations",
        ),
        (r"\b(fetch|request|download|get)(_|-|url|http|api|web)\b", "network requests"),
        (r"\bupload(_|-|file|data)\b", "file uploads"),
        (r"\b(auth|authenticate|login)(_|-|user)\b", "authentication"),
        (
            r"\b(credential|password|secret|token|key)(_|-|store|save|get|fetch)\b",
            "credential handling",
        ),
    ]

    # Check for high-risk patterns
    for pattern, risk_type in high_risk_patterns:
        if re.search(pattern, combined):
            risk_level = "high"
            warnings.append(
                f"⚠️ HIGH RISK: Tool involves {risk_type}. "
                "This could allow arbitrary code execution or system access."
            )
            recommendations.append(
                f"For {risk_type}: Use strict whitelisting, input validation, "
                "and never use shell=True for subprocess calls. "
                "See SECURITY.md for secure implementation patterns."
            )

    # Check for medium-risk patterns
    if risk_level != "high":
        for pattern, risk_type in medium_risk_patterns:
            if re.search(pattern, combined):
                risk_level = "medium"
                warnings.append(
                    f"⚠️ MEDIUM RISK: Tool involves {risk_type}. "
                    "Requires careful security implementation."
                )
                recommendations.append(
                    f"For {risk_type}: Implement input validation, path traversal "
                    "protection, rate limiting, and audit logging. "
                    "See SECURITY.md for details."
                )
                break  # Only flag once for medium risk

    return {
        "risk_level": risk_level,
        "warnings": warnings,
        "recommendations": recommendations,
    }


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
        "string": "string",
        "str": "string",
        "number": "number",
        "int": "number",
        "integer": "number",
        "float": "number",
        "boolean": "boolean",
        "bool": "boolean",
        "array": "array",
        "list": "array",
        "object": "object",
        "dict": "object",
    }

    schema = {
        "name": tool_definition["name"],
        "description": tool_definition.get("description", ""),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    }

    for param in tool_definition.get("parameters", []):
        param_type = TYPE_MAPPING.get(param["type"].lower(), "string")

        schema["inputSchema"]["properties"][param["name"]] = {
            "type": param_type,
            "description": param.get("description", ""),
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
    return text.replace("{", "{{").replace("}", "}}")


def merge_gitignore(existing_path: str, template_content: str) -> Dict[str, Any]:
    """
    Merge .gitignore files by appending unique entries.

    Args:
        existing_path: Path to existing .gitignore
        template_content: Content from template

    Returns:
        dict with 'added', 'skipped', 'total' counts
    """
    try:
        existing_content = Path(existing_path).read_text()
    except UnicodeDecodeError:
        # Try different encoding
        try:
            existing_content = Path(existing_path).read_text(encoding="latin-1")
        except Exception:
            print(f"Warning: Could not read {existing_path}, treating as empty")
            existing_content = ""
    except Exception as e:
        print(f"Warning: Error reading {existing_path}: {e}")
        existing_content = ""

    # Read existing file
    existing_lines = set(line.strip() for line in existing_content.splitlines())

    # Parse template
    template_lines = [line.strip() for line in template_content.splitlines()]

    # Find new unique entries
    new_entries = []
    for line in template_lines:
        stripped = line.strip()
        # Always add comments and empty lines for structure
        if not stripped or stripped.startswith("#"):
            new_entries.append(line)
        # Only add patterns if not already present
        elif stripped not in existing_lines:
            new_entries.append(line)
            existing_lines.add(stripped)

    if new_entries:
        # Append with clear delimiter
        merged_content = existing_content.rstrip("\n") + "\n\n"
        merged_content += (
            f"# Added by MCP Generator on {datetime.now().strftime('%Y-%m-%d')}\n"
        )
        merged_content += "\n".join(new_entries) + "\n"

        Path(existing_path).write_text(merged_content)

    return {
        "added": len(
            [e for e in new_entries if e.strip() and not e.strip().startswith("#")]
        ),
        "skipped": len(template_lines) - len(new_entries),
        "total": len(template_lines),
    }


def merge_manifest(existing_path: str, template_content: str) -> Dict[str, Any]:
    """
    Merge MANIFEST.in files by appending unique include patterns.

    Args:
        existing_path: Path to existing MANIFEST.in
        template_content: Content from template

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
        if not stripped or stripped.startswith("#"):
            new_entries.append(line)
        # Only add if not present
        elif stripped not in existing_lines:
            new_entries.append(line)
            existing_lines.add(stripped)

    if new_entries:
        merged_content = existing_content.rstrip("\n") + "\n\n"
        merged_content += (
            f"# Added by MCP Generator on {datetime.now().strftime('%Y-%m-%d')}\n"
        )
        merged_content += "\n".join(new_entries) + "\n"

        Path(existing_path).write_text(merged_content)

    return {
        "added": len(
            [e for e in new_entries if e.strip() and not e.strip().startswith("#")]
        ),
        "skipped": len(template_lines) - len(new_entries),
    }


def append_to_readme(
    existing_path: str, template_content: str, project_name: str
) -> Dict[str, Any]:
    """
    Append generated README content to existing file with clear delimiter.

    Args:
        existing_path: Path to existing README.md
        template_content: Content from template
        project_name: Project name for marker

    Returns:
        dict with 'appended' status and line number
    """
    existing_content = Path(existing_path).read_text()

    # Check if already appended (avoid duplicates)
    marker = f"<!-- MCP-GENERATOR-CONTENT-START:{project_name} -->"
    if marker in existing_content:
        return {"appended": False, "reason": "Already contains generated content"}

    # Check file size
    file_size = os.path.getsize(existing_path)
    if file_size > 1_000_000:  # 1MB
        return {
            "appended": False,
            "reason": f"File too large ({file_size / 1024:.1f}KB), skipping to avoid unwieldy file",
        }

    # Append with clear delimiters
    delimiter_start = f"\n\n---\n\n{marker}\n"
    delimiter_end = f"\n<!-- MCP-GENERATOR-CONTENT-END:{project_name} -->\n"

    note = (
        f"> **Note:** The following content was generated by MCP Generator on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}.\n"
        f"> You can edit, move, or remove this section as needed.\n\n"
    )

    appended_content = delimiter_start + note + template_content + delimiter_end

    merged_content = existing_content.rstrip("\n") + appended_content

    # Calculate line number where content was added
    line_number = len(existing_content.splitlines()) + 1

    Path(existing_path).write_text(merged_content)

    return {
        "appended": True,
        "line_number": line_number,
        "bytes_added": len(appended_content),
    }


def append_to_mcp_usage(
    existing_path: str, template_content: str, project_name: str
) -> Dict[str, Any]:
    """
    Append to MCP-USAGE.md with clear delimiters.

    Args:
        existing_path: Path to existing MCP-USAGE.md
        template_content: Content from template
        project_name: Project name for marker

    Returns:
        dict with 'appended' status and line number
    """
    existing_content = Path(existing_path).read_text()

    # Check if already appended (avoid duplicates)
    marker = f"<!-- MCP-GENERATOR-USAGE-START:{project_name} -->"
    if marker in existing_content:
        return {"appended": False, "reason": "Already contains generated content"}

    # Check file size
    file_size = os.path.getsize(existing_path)
    if file_size > 1_000_000:  # 1MB
        return {
            "appended": False,
            "reason": f"File too large ({file_size / 1024:.1f}KB), skipping to avoid unwieldy file",
        }

    # Append with clear delimiters
    delimiter_start = f"\n\n---\n\n{marker}\n"
    delimiter_end = f"\n<!-- MCP-GENERATOR-USAGE-END:{project_name} -->\n"

    note = (
        f"> **Note:** The following content was generated by MCP Generator on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}.\n"
        f"> You can edit, move, or remove this section as needed.\n\n"
    )

    appended_content = delimiter_start + note + template_content + delimiter_end

    merged_content = existing_content.rstrip("\n") + appended_content

    # Calculate line number where content was added
    line_number = len(existing_content.splitlines()) + 1

    Path(existing_path).write_text(merged_content)

    return {
        "appended": True,
        "line_number": line_number,
        "bytes_added": len(appended_content),
    }


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

    # Security analysis: Check for potentially dangerous tool patterns
    print("\n" + "=" * 60)
    print("SECURITY ANALYSIS")
    print("=" * 60)

    high_risk_tools = []
    medium_risk_tools = []

    for tool in tools:
        analysis = analyze_tool_security(tool)
        if analysis["risk_level"] == "high":
            high_risk_tools.append((tool["name"], analysis))
        elif analysis["risk_level"] == "medium":
            medium_risk_tools.append((tool["name"], analysis))

    if high_risk_tools:
        print("\n🚨 HIGH RISK TOOLS DETECTED:")
        for tool_name, analysis in high_risk_tools:
            print(f"\n  Tool: {tool_name}")
            for warning in analysis["warnings"]:
                print(f"    {warning}")
            for rec in analysis["recommendations"]:
                print(f"    💡 {rec}")

    if medium_risk_tools:
        print("\n⚠️  MEDIUM RISK TOOLS DETECTED:")
        for tool_name, analysis in medium_risk_tools:
            print(f"\n  Tool: {tool_name}")
            for warning in analysis["warnings"]:
                print(f"    {warning}")
            for rec in analysis["recommendations"]:
                print(f"    💡 {rec}")

    if high_risk_tools or medium_risk_tools:
        print("\n📚 SECURITY RESOURCES:")
        print(
            "    - See SECURITY.md in your generated project for comprehensive guidelines"
        )
        print("    - Use security_utils.py for built-in security functions")
        print("    - Review: https://www.anthropic.com/news/disrupting-AI-espionage")
        print("=" * 60 + "\n")

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
        # For in-place generation, check only for CRITICAL conflicting files
        # Other files (.gitignore, README.md, etc.) will be smartly merged
        critical_files = [
            "pyproject.toml",
            "setup.py",
        ]

        existing_critical = [
            f for f in critical_files if os.path.exists(os.path.join(project_path, f))
        ]

        # Also check if package directory already exists
        if os.path.exists(os.path.join(project_path, package_name)):
            existing_critical.append(f"{package_name}/ directory")

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

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "templates", "python")

    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Templates not found at {template_dir}")

    # Validate and enforce minimum Python version
    # MCP SDK requires Python 3.10+
    def parse_version(version_str: str) -> tuple:
        """Parse version string like '3.10' into tuple (3, 10)"""
        try:
            parts = version_str.split(".")
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
        "project_name": project_name,  # Full name with hyphens (e.g., "hitoshura25-my-tool")
        "package_name": package_name,  # Full name with underscores (e.g., "hitoshura25_my_tool")
        "import_name": import_name,  # Same as package_name (for clarity in entry points)
        "base_name": base_name,  # Original name without prefix (e.g., "my-tool")
        "description": sanitize_description(description),
        "author": author,
        "author_email": author_email,
        "python_version": validated_python_version,
        "license": license_type,
        "tools": tools,
        "tool_schemas": [generate_tool_schema(tool) for tool in tools],
        "year": "2025",
    }

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))

    # Files to generate
    files_to_generate = [
        # Root files
        ("README.md.j2", "README.md"),
        ("MCP-USAGE.md.j2", "MCP-USAGE.md"),
        ("SECURITY.md.j2", "SECURITY.md"),
        ("SECURITY_EXAMPLES.md.j2", "SECURITY_EXAMPLES.md"),
        ("LICENSE.j2", "LICENSE"),
        ("setup.py.j2", "setup.py"),
        ("pyproject.toml.j2", "pyproject.toml"),
        ("MANIFEST.in.j2", "MANIFEST.in"),
        (".gitignore.j2", ".gitignore"),
        # Package files
        ("__init__.py.j2", f"{package_name}/__init__.py"),
        ("server.py.j2", f"{package_name}/server.py"),
        ("cli.py.j2", f"{package_name}/cli.py"),
        ("generator.py.j2", f"{package_name}/generator.py"),
        ("security_utils.py.j2", f"{package_name}/security_utils.py"),
        # Tests
        ("tests/__init__.py.j2", f"{package_name}/tests/__init__.py"),
        ("tests/test_server.py.j2", f"{package_name}/tests/test_server.py"),
        ("tests/test_generator.py.j2", f"{package_name}/tests/test_generator.py"),
    ]

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
            if output_file == ".gitignore" and file_exists:
                result = merge_gitignore(output_path, content)
                if result["added"] > 0:
                    files_merged.append(f".gitignore ({result['added']} entries added)")
                else:
                    files_skipped.append(".gitignore (no new entries)")

            # Strategy 2: Smart merge for MANIFEST.in
            elif output_file == "MANIFEST.in" and file_exists:
                result = merge_manifest(output_path, content)
                if result["added"] > 0:
                    files_merged.append(
                        f"MANIFEST.in ({result['added']} patterns added)"
                    )
                else:
                    files_skipped.append("MANIFEST.in (no new patterns)")

            # Strategy 3: Append to README.md
            elif output_file == "README.md" and file_exists:
                result = append_to_readme(output_path, content, project_name)
                if result["appended"]:
                    files_appended.append(f"README.md (line {result['line_number']})")
                else:
                    files_skipped.append(f"README.md ({result['reason']})")

            # Strategy 4: Append to MCP-USAGE.md
            elif output_file == "MCP-USAGE.md" and file_exists:
                result = append_to_mcp_usage(output_path, content, project_name)
                if result["appended"]:
                    files_appended.append(
                        f"MCP-USAGE.md (line {result['line_number']})"
                    )
                else:
                    files_skipped.append(f"MCP-USAGE.md ({result['reason']})")

            # Strategy 5: Skip LICENSE if exists
            elif output_file == "LICENSE" and file_exists:
                files_skipped.append("LICENSE (preserving existing)")

            # Default: Create file normally
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                files_created.append(output_file)

        except Exception as e:
            raise RuntimeError(f"Failed to generate {output_file}: {str(e)}")

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

    print(f"\n{'=' * 60}")
    print(f"Generation Summary: {', '.join(summary_parts)}")
    print(f"{'=' * 60}")

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

    print(f"{'=' * 60}\n")

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
            if workflow_result["success"]:
                files_created.append(".github/workflows/_reusable-test-build.yml")
                files_created.append(".github/workflows/release.yml")
                files_created.append(".github/workflows/test-pr.yml")
                files_created.append("scripts/calculate_version.sh")
        finally:
            os.chdir(original_dir)

    except ImportError:
        raise ImportError(
            "pypi-workflow-generator is required but not installed. "
            "Install with: pip install pypi-workflow-generator"
        )

    return {
        "success": True,
        "project_path": project_path,
        "files_created": files_created,
        "files_merged": files_merged,
        "files_appended": files_appended,
        "files_skipped": files_skipped,
        "message": f"Successfully generated MCP server project at {project_path}",
    }
