# Playwright MCP for macOS 🎭

**Like Playwright, but for native macOS applications. Control any Mac app with natural language through Claude - perfect for developing and testing Mac applications with AI assistance.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What is this?

This is an MCP (Model Context Protocol) server that gives Claude the ability to see and interact with any macOS application - just like Playwright does for web browsers, but for native Mac apps.

**Perfect for:**
- 🧪 **Testing Mac applications** - "Test the login flow in my app"
- 🔍 **App development** - "Check if all buttons are properly labeled"
- 🤖 **UI automation** - "Fill out this form and submit it"
- 📱 **App exploration** - "Show me all the interactive elements in Finder"

## 🚀 Quick Start

### 1. Install
```bash
git clone https://github.com/mb-dev/macos-ui-automation-mcp.git
cd macos-ui-automation-mcp
uv sync
```

### 2. Set Up Accessibility Permissions
⚠️ **Critical**: Enable accessibility for your **parent application**:

- **If using Terminal**: Add Terminal to `System Settings → Privacy & Security → Accessibility`
- **If using VS Code**: Add VS Code to `System Settings → Privacy & Security → Accessibility`  
- **If using Claude Code**: Add Claude Code to `System Settings → Privacy & Security → Accessibility`

*The parent app needs permission because it's the one actually executing the MCP server.*

### 3. Configure Claude Code
Add to your Claude Code MCP settings:
```json
{
  "mcpServers": {
    "macos-ui-automation": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/macos-ui-automation-mcp",
        "run",
        "macos-ui-automation-mcp"
      ]
    }
  }
}
```

### 4. Start Automating!
Now you can ask Claude things like:
- *"Find all buttons in the Calculator app"*
- *"Click the submit button in my app"*
- *"Click the screenshot button to capture the current window"*  
- *"Test the login flow by filling in credentials and clicking submit"*

## 🛠 Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `find_elements` | Find UI elements using JSONPath | "Show me all text fields" |
| `find_elements_in_app` | Search within a specific app | "Find buttons in Safari" |
| `click_by_accessibility_id` | Click using accessibility actions | "Click the submit button" |
| `click_at_position` | Click at screen coordinates | "Click at position (100, 200)" |
| `type_text_to_element_by_selector` | Type text into elements | "Type 'hello' into the search field" |
| `get_app_overview` | Overview of running applications | "What apps are currently running?" |
| `list_running_applications` | List all running apps | "Show me all open applications" |
| `check_accessibility_permissions` | Verify setup is correct | "Is accessibility properly configured?" |

## 🔍 JSONPath Examples

Find elements using powerful JSONPath queries:

```bash
# All buttons in any app
$..[?(@.role=='AXButton')]

# Buttons with specific text
$..[?(@.title=='Submit')]

# All text fields that are enabled
$..[?(@.role=='AXTextField' && @.enabled==true)]

# Elements with accessibility identifiers
$..[?(@.ax_identifier=='loginButton')]

# Elements in a specific app
$.processes[?(@.name=='Calculator')]..[?(@.role=='AXButton')]
```

## 🧪 Perfect for App Testing

This tool shines when developing and testing Mac applications:

### Test Automation
```
"Test my login flow:
1. Find the username field and type 'testuser'  
2. Find the password field and type 'password123'
3. Click the login button
4. Verify a success message appears"
```

### UI Validation
```
"Check my settings window:
- Are all buttons properly labeled?
- Are there any text fields without accessibility identifiers?
- Click the screenshot button to capture the current state"
```

### Accessibility Auditing
```
"Audit my app for accessibility:
- Find all interactive elements without accessibility labels
- Check if keyboard navigation works properly
- Identify any elements that might be hard to use"
```

## 📸 Adding Screenshots to Your App

We don't provide built-in screenshot functionality, but you can easily add it to your Mac app! Check out our [complete Swift implementation example](examples/screenshot.swift) based on a real-world app.

**Key points:**
- Uses `ScreenCaptureKit` (macOS 14+) for high-quality captures
- Automatically finds your app window
- Saves timestamped screenshots to Documents/Screenshots
- Integrates perfectly with this MCP - just add an accessibility identifier!

**Usage with Playwright MCP:**
```
"Click the screenshot button to capture the current window"
```

The MCP will find your button by accessibility ID and trigger the screenshot!

## 📦 Development Setup

For contributors and advanced users:

```bash
# Clone and install
git clone https://github.com/mb-dev/macos-ui-automation-mcp.git
cd macos-ui-automation-mcp
uv sync --dev

# Run tests
uv run python -m pytest tests/ -v

# Check code quality  
uv run ruff check src/ tests/ mcp_server_wrapper.py
uv run ruff format

# Test the MCP server
uv run macos-ui-automation-mcp
```

## 🤝 Contributing & Bug Reports

I have limited time to fix issues, so here's the deal:

- 🐛 **Found a bug?** File an issue, but please include:
  - Your macOS version
  - Steps to reproduce
  - What you expected vs what happened
  
- 🛠 **Want it fixed faster?** The best way is to:
  1. Fork the repo
  2. Write a failing test that reproduces the bug
  3. Fix the bug
  4. Submit a PR

- ✨ **Want a feature?** Same deal - code it up and submit a PR!

I'm happy to review PRs and provide guidance, but I can't promise quick fixes for reported issues. The codebase is well-tested and documented, so dive in! 🚀

## 🔧 Architecture

Built with:
- **FastMCP** - MCP server framework
- **PyObjC** - macOS accessibility API bindings  
- **Pydantic** - Type-safe data models
- **JSONPath** - Powerful element querying
- **Comprehensive test suite** - Fake system for testing without real UI

## ⚠️ Important Notes

### Accessibility Permissions
- Must be granted to the **parent application** (Terminal, VS Code, etc.)
- Not to Python or the MCP server itself
- Required for any UI automation on macOS

### Screenshot Permissions
- If your app has screenshot functionality, it needs **Screen Recording** permission
- Add your app to `System Settings → Privacy & Security → Screen Recording`
- This is separate from accessibility permissions

### Performance Tips
- Use app-specific searches when possible (`find_elements_in_app`)
- Shallow searches are faster for overviews
- Deep searches are thorough but slower

### Limitations
- Requires accessibility API access (some apps restrict this)
- Works best with native macOS applications
- Some system-level elements may not be accessible

## 📄 License

MIT License - feel free to use this in your projects!

## 🎭 Why "Playwright for Mac"?

Just like Playwright revolutionized web testing by providing a simple API to control browsers, this tool does the same for native macOS applications. Instead of writing complex GUI automation scripts, just tell Claude what you want to test or automate in natural language.

Perfect for the age of AI-assisted development! 🤖

---

**Need help?** Check the [examples/](examples/) folder or [open an issue](https://github.com/mb-dev/macos-ui-automation-mcp/issues). Better yet, submit a PR! 😄