#!/usr/bin/env python3
"""
Wrapper script for MCP server with enhanced logging for Claude Code debugging.
"""

import importlib
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


def log_debug(message):
    """Log debug information to stderr for Claude Code to capture."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] WRAPPER DEBUG: {message}", file=sys.stderr, flush=True)


def main():
    try:
        log_debug("=== MCP Server Wrapper Starting ===")
        log_debug(f"Python executable: {sys.executable}")
        log_debug(f"Python version: {sys.version}")
        log_debug(f"Working directory: {Path.cwd()}")
        log_debug(f"Python path: {sys.path[:3]}...")  # First 3 entries
        log_debug(f"Environment PATH: {os.environ.get('PATH', '')[:100]}...")

        # Determine the correct project directory
        # The wrapper should be in /Users/moshechen/workspace/macos-ui-automation-mcp/
        script_dir = Path(__file__).parent.resolve()
        log_debug(f"Script directory: {script_dir}")

        # Change to the project directory first
        os.chdir(script_dir)
        log_debug(f"Changed working directory to: {script_dir}")

        # Add the src directory to Python path
        src_dir = script_dir / "src"
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
            log_debug(f"Added src directory to path: {src_dir}")

        # Verify the src directory exists
        if not src_dir.exists():
            log_debug(f"ERROR: src directory does not exist: {src_dir}")
            sys.exit(1)

        # Verify the MCP server module exists
        mcp_server_path = src_dir / "macos_ui_automation" / "mcp_server.py"
        if not mcp_server_path.exists():
            log_debug(f"ERROR: MCP server module does not exist: {mcp_server_path}")
            sys.exit(1)

        log_debug(f"MCP server module found: {mcp_server_path}")

        # Import and run the server
        log_debug("Importing MCP server...")
        mcp_module = importlib.import_module(
            "macos_ui_automation.interfaces.mcp_server"
        )
        server_main = mcp_module.main

        log_debug("Starting MCP server...")
        server_main()

    except ImportError as e:
        log_debug(f"Import error: {e}")
        log_debug(f"Current sys.path: {sys.path}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        log_debug(f"Unexpected error: {e}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
