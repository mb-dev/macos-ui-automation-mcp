#!/bin/bash

# Start MCP server in development mode with auto-reload
# This uses uv and installs the package in editable mode for live changes

set -e

echo "🔧 Setting up MCP development environment with uv..."

# Install dependencies with uv
echo "📦 Installing dependencies..."
uv sync --dev

# Install this package in editable mode
echo "🔗 Installing package in editable mode..."
uv pip install -e .

# Start MCP inspector in development mode
echo "🚀 Starting MCP development server..."
echo "   📝 Any changes to the code will be reflected immediately"
echo "   🌐 Opening MCP Inspector in browser..."

# Use uv to run the MCP dev command with auto-reload
uv run mcp dev src/macos_ui_automation/mcp_server.py --with-editable .