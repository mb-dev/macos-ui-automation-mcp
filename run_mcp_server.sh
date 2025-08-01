#!/bin/bash
# Wrapper script to run MCP server with editable package from any directory

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Run the MCP server with editable package
exec uv run python mcp_server_wrapper.py "$@"