# Contributing to macOS UI Automation MCP

Thank you for your interest in contributing to this project! This guide will help you get started with contributing code, documentation, or ideas.

## 🚀 Quick Start

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/mb-dev/macos-ui-automation-mcp.git
   cd macos-ui-automation-mcp
   ```

2. **Set up development environment**
   ```bash
   # Install uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync --dev
   
   # Install pre-commit hooks
   uv run pre-commit install
   ```

3. **Verify setup**
   ```bash
   # Run tests
   uv run pytest
   
   # Run linting
   uv run ruff check
   
   # Test MCP server
   uv run macos-ui-automation-mcp
   ```

### Accessibility Permissions

⚠️ **Important**: Grant accessibility permissions for development:
- **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
- Add your terminal application and Python

## 🎯 Ways to Contribute

### 1. Code Contributions
- **Bug fixes** - Fix issues in existing functionality
- **New features** - Add MCP tools, CLI commands, or library functions
- **Performance improvements** - Optimize UI state capture or search algorithms
- **Platform compatibility** - Improve macOS version support

### 2. Documentation
- **API documentation** - Improve docstrings and type hints
- **Usage examples** - Add examples for MCP, library, or CLI usage
- **Tutorials** - Create guides for specific automation workflows
- **README improvements** - Clarify setup or usage instructions

### 3. Testing
- **Unit tests** - Add tests for core functionality
- **Integration tests** - Test MCP server integration
- **UI tests** - Add automated UI testing examples
- **Performance tests** - Benchmark and optimize performance

### 4. Community
- **Issue reports** - Report bugs or suggest features
- **Issue triage** - Help categorize and respond to issues
- **Code review** - Review pull requests from other contributors
- **Discussions** - Participate in project discussions

## 📋 Development Guidelines

### Code Style

We use **Ruff** for code formatting and linting:

```bash
# Format code
uv run ruff format

# Check linting
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix
```

**Key style guidelines:**
- Line length: 88 characters
- Use type hints for all public functions
- Follow PEP 8 naming conventions
- Add docstrings to all public functions and classes

### Code Quality

#### Type Checking
```bash
# Run type checking
uv run mypy src/
```

#### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=macos_ui_automation

# Run specific test file
uv run pytest tests/test_models.py
```

#### Pre-commit Hooks
Pre-commit hooks run automatically before each commit:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Test execution (pytest)

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add timeout support to find_elements MCP tool"
git commit -m "Fix JSONPath selector handling of special characters"
git commit -m "Update README with Claude Desktop setup instructions"

# Bad examples
git commit -m "fix bug"
git commit -m "update code"
git commit -m "changes"
```

**Format:**
- Start with verb in imperative mood (Add, Fix, Update, Remove)
- Keep first line under 72 characters
- Add detailed description if needed

## 🔧 Project Architecture

### Directory Structure
```
src/macos_ui_automation/
├── __init__.py              # Public API exports
├── cli.py                   # Command-line interface
├── mcp_server_simple.py     # MCP server implementation
├── core/                    # Core functionality
│   ├── models.py           # Pydantic data models
│   └── state_dumper.py     # System state capture
├── accessibility/          # macOS accessibility APIs
│   ├── interfaces.py       # Abstract interfaces
│   ├── macos_implementation.py  # macOS-specific implementation
│   └── ax_utils.py         # Utility functions
├── actions/                # UI action implementations
│   └── ui_actions.py       # Click, type, etc.
└── element_selectors/      # Element selection and querying
    ├── jsonpath_selector.py # JSONPath implementation
    └── element_registry.py  # Element management
```

### Key Components

#### 1. **Core Models** (`core/models.py`)
- Pydantic models for type safety
- System state representation
- UI element structures

#### 2. **State Dumper** (`core/state_dumper.py`)
- Captures complete macOS UI state
- Configurable depth and timeout
- Performance optimizations

#### 3. **MCP Server** (`mcp_server_simple.py`)
- FastMCP-based server implementation
- Tools for Claude Desktop/Code integration
- Error handling and validation

#### 4. **Accessibility Layer** (`accessibility/`)
- Abstract interfaces for cross-platform support
- macOS-specific PyObjC implementations
- Utility functions for common operations

#### 5. **Element Selectors** (`element_selectors/`)
- JSONPath querying implementation
- Element filtering and matching
- Performance optimizations

## 📝 Adding New Features

### Adding a New MCP Tool

1. **Define the tool in `mcp_server_simple.py`:**
   ```python
   @mcp.tool()
   def my_new_tool(param1: str, param2: int = 10) -> list[dict[str, Any]]:
       """Description of what this tool does.
       
       Args:
           param1: Description of parameter
           param2: Description with default value
           
       Returns:
           List of results or error information
       """
       try:
           # Implementation here
           result = do_something(param1, param2)
           return [result.model_dump() for result in results]
       except Exception as e:
           logger.error(f"Tool failed: {str(e)}")
           error_response = ErrorResponse(error=str(e))
           return [error_response.model_dump()]
   ```

2. **Add corresponding tests:**
   ```python
   def test_my_new_tool():
       """Test the new MCP tool."""
       result = my_new_tool("test_param", 5)
       assert len(result) > 0
       assert "error" not in result[0]
   ```

3. **Update documentation:**
   - Add tool to README.md tool table
   - Add usage examples
   - Update CLAUDE.md if relevant

### Adding a New CLI Command

1. **Add command to `cli.py`:**
   ```python
   def my_command(args):
       """Implementation of new command."""
       # Command logic here
       
   # Add to argument parser
   subparser = subparsers.add_parser('mycommand', help='Description')
   subparser.add_argument('--param', help='Parameter description')
   subparser.set_defaults(func=my_command)
   ```

2. **Add tests and documentation**

### Adding New Pydantic Models

1. **Define in `core/models.py`:**
   ```python
   class MyNewModel(BaseModel):
       """Description of the model."""
       
       field1: str = Field(description="Field description")
       field2: int | None = Field(None, description="Optional field")
       
       @classmethod
       def from_dict(cls, data: dict) -> 'MyNewModel':
           """Create from dictionary data."""
           return cls(
               field1=data.get("field1", ""),
               field2=data.get("field2")
           )
   ```

2. **Export in `__init__.py`** if part of public API

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test MCP server integration
3. **UI Tests** - Test actual UI automation (careful!)
4. **Performance Tests** - Benchmark critical paths

### Writing Tests

```python
import pytest
from macos_ui_automation import SystemStateDumper

def test_system_dumper_basic():
    """Test basic system dumper functionality."""
    dumper = SystemStateDumper(max_depth=3)
    state = dumper.dump_system_state()
    
    assert state.accessibility_enabled
    assert len(state.processes) > 0
    assert state.timestamp is not None

@pytest.mark.slow
def test_deep_system_dump():
    """Test deep system dump (marked as slow)."""
    dumper = SystemStateDumper(max_depth=10)
    state = dumper.dump_system_state_with_timeout(15.0)
    assert len(state.processes) > 0
```

### Test Safety

⚠️ **Important**: UI automation tests can affect the system:
- Use `@pytest.mark.skip` for tests that perform actions
- Test on non-production systems
- Use timeouts to prevent hanging
- Mock external dependencies when possible

## 📖 Documentation Standards

### Docstring Format

Use Google-style docstrings:

```python
def find_elements(self, jsonpath: str, timeout: float = 10.0) -> list[SearchResult]:
    """Find UI elements matching JSONPath selector.
    
    This function searches the current UI state for elements matching
    the provided JSONPath expression with intelligent depth selection.
    
    Args:
        jsonpath: JSONPath expression to match elements
        timeout: Maximum time to spend searching in seconds
        
    Returns:
        List of SearchResult objects matching the selector
        
    Raises:
        TimeoutError: If search exceeds timeout
        ValueError: If JSONPath expression is invalid
        
    Example:
        >>> finder = ElementFinder()
        >>> buttons = finder.find_elements("$..[?(@.role=='AXButton')]")
        >>> print(f"Found {len(buttons)} buttons")
    """
```

### README Updates

When adding features:
1. Update the tool table in README.md
2. Add usage examples
3. Update installation instructions if needed
4. Add troubleshooting information

## 🐛 Bug Reports

### Good Bug Reports Include:

1. **Environment information:**
   - macOS version
   - Python version
   - Package version

2. **Steps to reproduce:**
   ```
   1. Install package with `uv add macos-ui-automation-mcp`
   2. Run `macos-ui-automation find "$..[?(@.role=='AXButton')]"`
   3. Error occurs: [paste error message]
   ```

3. **Expected vs actual behavior**

4. **Relevant logs or error messages**

5. **Minimal reproduction case**

### Security Issues

For security vulnerabilities:
- **Don't** open public issues
- Email maintainers directly
- Provide detailed information
- Allow time for fix before disclosure

## 🎨 Feature Requests

### Good Feature Requests Include:

1. **Clear description** of the problem or opportunity
2. **Specific use case** or example scenario
3. **Proposed solution** or implementation approach
4. **Alternatives considered**
5. **Willingness to contribute** implementation

### Feature Request Template:

```markdown
## Problem/Opportunity
[Describe what you're trying to accomplish]

## Proposed Solution
[Describe your proposed approach]

## Use Case
[Provide specific example of how this would be used]

## Implementation Notes
[Any technical considerations or constraints]

## Alternatives
[Other approaches you've considered]
```

## 📦 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backwards compatible
- **Patch** (0.0.1): Bug fixes, backwards compatible

### Release Checklist

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Publish to PyPI

## 🤝 Code Review

### As a Reviewer

- Be constructive and specific
- Focus on code quality, not personal preferences
- Suggest improvements with examples
- Test the changes locally if possible
- Approve when ready, request changes when needed

### As an Author

- Write clear PR descriptions
- Include tests for new features
- Update documentation
- Respond to feedback constructively
- Keep PRs focused and reasonably sized

## 🆘 Getting Help

### Stuck? Here's how to get help:

1. **Check existing issues** - your question might be answered
2. **Review documentation** - README, examples, docstrings
3. **Ask in discussions** - for questions and ideas
4. **Create an issue** - for bugs or feature requests
5. **Join community** - participate in project discussions

### Communication Guidelines

- Be respectful and inclusive
- Provide context and details
- Use clear, descriptive titles
- Search before posting duplicates
- Follow up on your issues/PRs

## 📜 Legal

### Contributor License Agreement

By contributing to this project, you agree that:
- Your contributions will be licensed under the MIT License
- You have the right to submit the contributions
- You understand this is an open source project

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please read and follow it.

---

**Thank you for contributing!** Your efforts help make macOS automation more accessible to everyone. 🎉