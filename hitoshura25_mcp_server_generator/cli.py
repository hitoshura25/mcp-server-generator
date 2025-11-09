#!/usr/bin/env python3
"""
CLI for MCP Server Generator.
"""

import argparse
import json
import sys
from pathlib import Path
from .generator import generate_mcp_server, validate_project_name


def load_tools_from_file(filepath: str):
    """Load tool definitions from JSON/YAML file."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(
            f"Tools file not found: {filepath}\n"
            f"Please check:\n"
            f"  1. The file path is correct\n"
            f"  2. The file exists in the current directory: {Path.cwd()}\n"
            f"  3. You have read permissions for the file"
        )

    with open(path) as f:
        if filepath.endswith('.json'):
            return json.load(f)
        elif filepath.endswith(('.yaml', '.yml')):
            import yaml
            return yaml.safe_load(f)
        else:
            raise ValueError(
                f"Tools file must have .json, .yaml, or .yml extension\n"
                f"Current file: {filepath}\n"
                f"Example: tools.json or tools.yaml"
            )


def interactive_mode():
    """Interactive project creation."""
    print("=== MCP Server Generator - Interactive Mode ===\n")

    # Project name
    while True:
        project_name = input("Project name (e.g., my-mcp-server): ").strip()
        if not project_name:
            print("Project name cannot be empty.")
            continue
        if not validate_project_name(project_name):
            print("Invalid project name. Use lowercase, alphanumeric, hyphens/underscores only.")
            print("Must be a valid Python identifier (no keywords).")
            continue
        break

    # Prefix mode
    print("\nPackage prefix options:")
    print("  AUTO  - Auto-detect from git config (recommended)")
    print("  NONE  - No prefix")
    print("  Other - Custom prefix (e.g., 'acme')")
    prefix = input("Prefix (default: AUTO): ").strip() or "AUTO"

    # Description
    description = input("Description: ").strip()
    while not description:
        print("Description cannot be empty.")
        description = input("Description: ").strip()

    # Author info
    author = input("Author name: ").strip()
    while not author:
        print("Author name cannot be empty.")
        author = input("Author name: ").strip()

    author_email = input("Author email: ").strip()
    while not author_email:
        print("Author email cannot be empty.")
        author_email = input("Author email: ").strip()

    # Python version
    python_version = input("Python version (default: 3.10): ").strip() or "3.10"

    # Tools
    print("\nDefine your tools (empty name to finish):")
    tools = []

    while True:
        tool_name = input(f"\nTool #{len(tools) + 1} name (or press Enter to finish): ").strip()
        if not tool_name:
            break

        tool_desc = input(f"  Description for {tool_name}: ").strip()

        print(f"  Parameters for {tool_name} (empty name to finish):")
        parameters = []

        while True:
            param_name = input(f"    Parameter name (or press Enter to finish): ").strip()
            if not param_name:
                break

            param_type = input(f"    Type for {param_name} (string/number/boolean): ").strip()
            param_desc = input(f"    Description for {param_name}: ").strip()
            param_required = input(f"    Required? (y/n): ").strip().lower() == 'y'

            parameters.append({
                "name": param_name,
                "type": param_type,
                "description": param_desc,
                "required": param_required
            })

        tools.append({
            "name": tool_name,
            "description": tool_desc,
            "parameters": parameters
        })

    if not tools:
        print("\nError: At least one tool must be defined.")
        return 1

    print(f"\nGenerating MCP server '{project_name}' with {len(tools)} tool(s)...")

    try:
        result = generate_mcp_server(
            project_name=project_name,
            description=description,
            author=author,
            author_email=author_email,
            tools=tools,
            python_version=python_version,
            prefix=prefix
        )

        print(f"\n✅ {result['message']}")
        print(f"\nFiles created:")
        for file in result['files_created']:
            print(f"  - {file}")

        print(f"\nNext steps:")
        print(f"  1. cd {project_name}")
        print(f"  2. python3 -m venv venv")
        print(f"  3. source venv/bin/activate  # or: venv\\Scripts\\activate on Windows")
        print(f"  4. pip install -r requirements.txt")
        print(f"  5. pytest")
        print(f"  6. Implement tool logic in {project_name.replace('-', '_')}/generator.py")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate MCP servers with dual-mode architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  %(prog)s --interactive

  # From tools file
  %(prog)s --project-name my-tool --description "My tool" \\
    --author "Your Name" --email "you@example.com" \\
    --tools-file tools.json

  # With custom prefix
  %(prog)s --project-name my-tool --description "My tool" \\
    --author "Your Name" --email "you@example.com" \\
    --tools-file tools.json --prefix acme

  # With custom Python version
  %(prog)s -i --python-version 3.11
        """
    )

    parser.add_argument('--project-name', help='Project name (e.g., my-mcp-server)')
    parser.add_argument('--description', help='Project description')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--email', help='Author email')
    parser.add_argument('--tools-file', help='JSON/YAML file with tool definitions')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--output-dir', help='Output directory. Use "." to generate in current directory (in-place), or specify a path to create a subdirectory (default: current directory)')
    parser.add_argument('--python-version', default='3.10', help='Python version (default: 3.10)')
    parser.add_argument('--prefix', default='AUTO', help='Package prefix: AUTO (detect from git), NONE, or custom string (default: AUTO)')

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        return interactive_mode()

    # Validate required arguments for non-interactive mode
    if not all([args.project_name, args.description, args.author, args.email, args.tools_file]):
        parser.error(
            "The following arguments are required: "
            "--project-name, --description, --author, --email, --tools-file "
            "(or use --interactive)"
        )

    try:
        # Load tools
        tools_data = load_tools_from_file(args.tools_file)
        tools = tools_data if isinstance(tools_data, list) else tools_data.get('tools', [])

        if not tools:
            print("Error: No tools found in file", file=sys.stderr)
            return 1

        # Generate server
        result = generate_mcp_server(
            project_name=args.project_name,
            description=args.description,
            author=args.author,
            author_email=args.email,
            tools=tools,
            output_dir=args.output_dir,
            python_version=args.python_version,
            prefix=args.prefix
        )

        print(result['message'])
        print(f"\nFiles created:")
        for file in result['files_created']:
            print(f"  - {file}")

        print(f"\nNext steps:")
        print(f"  1. cd {args.project_name}")
        print(f"  2. python3 -m venv venv && source venv/bin/activate")
        print(f"  3. pip install -r requirements.txt")
        print(f"  4. pytest")
        print(f"  5. Implement tool logic in {args.project_name.replace('-', '_')}/generator.py")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
