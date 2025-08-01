#!/bin/bash
set -e

echo "🧹 Running linting tools..."

echo "📝 Running ruff check..."
uv run ruff check .

echo "🎨 Running ruff format..."
uv run ruff format .

echo "🔍 Running mypy..."
uv run mypy src/

echo "✅ All linting tools completed!"