#!/bin/bash
# Claude Code hook to check code quality (tests and linting)
# This hook runs on Stop/SubagentStop events and fails with non-zero exit if quality checks don't pass

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

echo "🔍 Running code quality checks..."
echo

# Function to print section headers
print_section() {
    echo -e "${YELLOW}=== $1 ===${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "pyproject.toml not found. Are we in the project root?"
    exit 1
fi

# Run tests
print_section "Running Tests"
if uv run python -m pytest tests/ -x --tb=short -q; then
    print_success "All tests passed"
else
    print_error "Tests failed"
    OVERALL_STATUS=1
fi

echo

# Run linting (focus on main source code, not examples)
print_section "Running Linter (ruff check)"
LINT_OUTPUT=$(uv run ruff check src/ tests/ mcp_server_wrapper.py 2>&1 || true)
LINT_EXIT_CODE=$?

if [[ $LINT_EXIT_CODE -eq 0 ]]; then
    print_success "No lint errors found in main source code"
else
    print_error "Lint errors found in main source code:"
    echo
    echo "$LINT_OUTPUT" | head -30  # Show first 30 lines of lint output
    
    # Extract total error count from the "Found X errors" line
    TOTAL_ERRORS=$(echo "$LINT_OUTPUT" | grep "Found [0-9]* error" | grep -o "[0-9]*" | tail -1)
    if [[ -n "$TOTAL_ERRORS" ]]; then
        echo
        echo -e "${RED}Total lint errors: $TOTAL_ERRORS${NC}"
        if [[ $(echo "$LINT_OUTPUT" | wc -l) -gt 30 ]]; then
            echo -e "${YELLOW}(showing first 30 lines - run 'uv run ruff check src/ tests/ mcp_server_wrapper.py' for full output)${NC}"
        fi
    fi
    
    OVERALL_STATUS=1
fi

echo

# Summary
print_section "Quality Check Summary"
if [[ $OVERALL_STATUS -eq 0 ]]; then
    print_success "All quality checks passed! 🎉"
else
    print_error "Quality checks failed"
    echo
    echo -e "${YELLOW}To fix issues:${NC}"
    echo "• Run tests: uv run python -m pytest tests/ -v"
    echo "• Check linting: uv run ruff check src/ tests/ mcp_server_wrapper.py"
    echo "• Auto-fix lint: uv run ruff check --fix src/ tests/ mcp_server_wrapper.py"
    echo
fi

exit $OVERALL_STATUS