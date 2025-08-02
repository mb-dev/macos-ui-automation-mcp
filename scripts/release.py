#!/usr/bin/env python3
"""
Release management script for macos-ui-automation-mcp.

This script helps manage package versions and creates releases.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    version_match = re.search(r'version = "([^"]+)"', content)
    if not version_match:
        raise ValueError("Could not find version in pyproject.toml")
    
    return version_match.group(1)


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    updated_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(updated_content)
    print(f"Updated version to {new_version}")


def run_command(cmd: list[str]) -> str:
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def bump_version(version: str, bump_type: str) -> str:
    """Bump version based on type (patch, minor, major)."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    
    major, minor, patch = map(int, parts)
    
    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def create_release(version: str, dry_run: bool = False) -> None:
    """Create a new release."""
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {version}")
    
    if dry_run:
        print("DRY RUN - No changes will be made")
        return
    
    # Update version
    update_version(version)
    
    # Update lockfile after version change
    print("Updating lockfile...")
    run_command(["uv", "lock"])
    
    # Build package to test
    print("Building package...")
    run_command(["uv", "build"])
    
    # Commit version change
    print("Committing version change...")
    run_command(["git", "add", "pyproject.toml", "uv.lock"])
    run_command(["git", "commit", "-m", f"chore: bump version to {version}"])
    
    # Create and push tag
    tag = f"v{version}"
    print(f"Creating tag {tag}...")
    
    # Delete existing tag if it exists
    try:
        run_command(["git", "tag", "-d", tag])
        print(f"Deleted existing local tag {tag}")
    except subprocess.CalledProcessError:
        pass  # Tag doesn't exist locally
    
    try:
        run_command(["git", "push", "origin", "--delete", tag])
        print(f"Deleted existing remote tag {tag}")
    except subprocess.CalledProcessError:
        pass  # Tag doesn't exist remotely
    
    run_command(["git", "tag", "-a", tag, "-m", f"Release {version}"])
    run_command(["git", "push", "origin", "main"])
    run_command(["git", "push", "origin", tag])
    
    # Create GitHub release
    print("Creating GitHub release...")
    run_command([
        "gh", "release", "create", tag,
        "--title", f"Release {version}",
        "--notes", f"Release version {version}",
        "--latest"
    ])
    
    print(f"✅ Release {version} created successfully!")
    print(f"🚀 PyPI publishing will start automatically via GitHub Actions")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Release management for macos-ui-automation-mcp")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show current version")
    
    # Bump command
    bump_parser = subparsers.add_parser("bump", help="Bump version and create release")
    bump_parser.add_argument("type", choices=["patch", "minor", "major"], help="Version bump type")
    bump_parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    # Release command
    release_parser = subparsers.add_parser("release", help="Create release with specific version")
    release_parser.add_argument("version", help="Version to release (e.g., 1.0.0)")
    release_parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    if args.command == "version":
        print(get_current_version())
    elif args.command == "bump":
        current_version = get_current_version()
        new_version = bump_version(current_version, args.type)
        create_release(new_version, args.dry_run)
    elif args.command == "release":
        create_release(args.version, args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()