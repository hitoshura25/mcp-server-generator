"""
Git username detection and prefix application utilities.

This module provides utilities for detecting GitHub usernames from git
configuration and applying prefixes to package names to avoid PyPI namespace
conflicts.
"""

from __future__ import annotations

import subprocess
from typing import Optional
import re


def get_github_username() -> Optional[str]:
    """
    Detect GitHub username from git configuration.

    Tries multiple detection methods in priority order:
    1. git config --get github.user (most specific)
    2. Username from remote URL (e.g., git@github.com:username/repo.git)
    3. git config --get user.name (sanitized to package-friendly format)

    Returns:
        GitHub username string, or None if detection fails

    Examples:
        >>> get_github_username()
        'hitoshura25'
    """
    # Priority 1: github.user config (most specific)
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
    # Gracefully handle missing git configuration - try next method
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
    # Gracefully handle missing git remote or configuration - try next method
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Priority 3: user.name (sanitized to package-friendly format)
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
    # Gracefully handle missing git configuration - all methods exhausted
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def sanitize_username(name: str) -> str:
    """
    Sanitize username for use as package prefix.

    Converts to lowercase, replaces spaces with hyphens, and removes
    invalid characters to create a PyPI-compatible package prefix.

    Args:
        name: Raw username string (e.g., "John Smith", "john@example.com")

    Returns:
        Sanitized username suitable for package prefix

    Examples:
        >>> sanitize_username("John Smith")
        'john-smith'
        >>> sanitize_username("John Q. Public")
        'john-q-public'
        >>> sanitize_username("user@example.com")
        'userexamplecom'
    """
    # Convert to lowercase
    name = name.lower()

    # Replace spaces and dots with hyphens
    name = name.replace(' ', '-').replace('.', '-')

    # Keep only alphanumeric characters and hyphens
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
        prefix: Prefix mode:
                - "AUTO": Auto-detect from git config (default)
                - Custom string (e.g., "acme"): Use specified prefix
                - "NONE": No prefix

    Returns:
        Tuple of (package_name, import_name)
        - package_name: For PyPI, uses hyphens (e.g., "acme-my-tool")
        - import_name: For Python imports, uses underscores (e.g., "acme_my_tool")

    Examples:
        >>> apply_prefix("my-tool", "AUTO")  # Assuming git user is "jsmith"
        ("jsmith-my-tool", "jsmith_my_tool")

        >>> apply_prefix("my-tool", "acme")
        ("acme-my-tool", "acme_my_tool")

        >>> apply_prefix("my-tool", "NONE")
        ("my-tool", "my_tool")
    """
    if prefix == "NONE":
        # No prefix requested
        package_name = base_name
    elif prefix == "AUTO":
        # Auto-detect from git
        detected = get_github_username()
        if detected:
            package_name = f"{detected}-{base_name}"
        else:
            # Fallback to no prefix if detection fails
            package_name = base_name
    else:
        # Custom prefix provided - sanitize it first
        sanitized_prefix = sanitize_username(prefix)
        package_name = f"{sanitized_prefix}-{base_name}"

    # Convert package name to import name (hyphens to underscores)
    import_name = package_name.replace('-', '_')

    return package_name, import_name
