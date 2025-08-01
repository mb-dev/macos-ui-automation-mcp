# Claude Code Integration Guide

This guide specifically covers integrating the macOS UI Automation MCP Server with **Claude Code**, Anthropic's AI-powered coding assistant.

## 🚀 Quick Setup for Claude Code

### 1. Install the MCP Server

```bash
# Navigate to your projects directory
cd ~/projects

# Clone or download the repository
git clone https://github.com/mb-dev/macos-ui-automation-mcp.git
cd macos-ui-automation-mcp

# Install dependencies
uv sync

# Test the installation
uv run macos-ui-automation-mcp --help
```

### 2. Configure Claude Code

Claude Code uses a configuration file to manage MCP servers. Add this server to your Claude Code MCP settings:

#### Location of Configuration
The configuration file location varies by platform:
- **macOS**: `~/.claude/claude_code_config.json`
- **Linux**: `~/.config/claude/claude_code_config.json`
- **Windows**: `%APPDATA%\Claude\claude_code_config.json`

#### Configuration Content
Add this to your `claude_code_config.json`:

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
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/macos-ui-automation-mcp/src"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/macos-ui-automation-mcp` with the actual path where you cloned the repository.

### 3. Enable Accessibility Permissions

⚠️ **Critical Step**: macOS requires explicit permission for accessibility access.

1. Open **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Click the lock icon and enter your password
3. Add **Claude Code** to the list of allowed applications
4. If Claude Code is already listed, remove it and add it again to refresh permissions

### 4. Restart Claude Code

After configuration:
1. Completely quit Claude Code
2. Restart Claude Code
3. The MCP server should now be available

## 🎯 Using the MCP Server in Claude Code

### Natural Language Commands

Once configured, you can use natural language to interact with macOS UI:

**Example Commands:**
- *"Find all buttons in the current window"*
- *"Click the submit button in Safari"*
- *"Show me all text fields that are currently visible"*
- *"Take a screenshot of the login form"*
- *"Find elements with the identifier 'loginButton'"*

### Manual Tool Usage

You can also directly invoke the MCP tools:

#### 1. **find_elements** - Search for UI elements
```
Tool: find_elements
Parameters:
- jsonpath_selector: $..[?(@.role=='AXButton')]
- timeout_seconds: 10
```

#### 2. **find_elements_in_app** - Search within specific application
```
Tool: find_elements_in_app  
Parameters:
- app_name: Safari
- jsonpath_selector: $..[?(@.ax_identifier=='submitButton')]
- timeout_seconds: 15
```

#### 3. **click_element_by_selector** - Click an element
```
Tool: click_element_by_selector
Parameters:
- jsonpath_selector: $..[?(@.title=='Login')]
```

#### 4. **type_text_to_element_by_selector** - Type into element
```
Tool: type_text_to_element_by_selector
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='usernameField')]
- text: myusername
```

#### 5. **get_app_overview** - Quick app overview
```
Tool: get_app_overview
Parameters:
- timeout_seconds: 5
```

#### 6. **list_running_applications** - List all apps
```
Tool: list_running_applications
Parameters: (none)
```

## 🔍 JSONPath Selector Reference

### Common Patterns for Claude Code Users

#### Find Elements by Role
```bash
# All buttons
$..[?(@.role=='AXButton')]

# All text fields  
$..[?(@.role=='AXTextField')]

# All clickable elements
$..[?(@.role=='AXButton' || @.role=='AXMenuItem')]
```

#### Find Elements by Properties
```bash
# Elements with specific identifier
$..[?(@.ax_identifier=='submitButton')]

# Elements by title/text
$..[?(@.title=='Submit')]

# Enabled elements only
$..[?(@.enabled==true)]

# Focused elements
$..[?(@.focused==true)]
```

#### Application-Specific Searches
```bash
# All buttons in Safari
$.processes[?(@.name=='Safari')]..[?(@.role=='AXButton')]

# Text fields in current frontmost app
$.processes[?(@.frontmost==true)]..[?(@.role=='AXTextField')]

# Elements in specific window
$.processes[?(@.name=='MyApp')].windows[0]..[?(@.role=='AXButton')]
```

#### Advanced Filtering
```bash
# Multiple conditions
$..[?(@.role=='AXButton' && @.enabled==true && @.title)]

# Pattern matching (case insensitive)
$..[?(@.title && @.title =~ /(?i).*submit.*/)]

# Position-based selection
$..[?(@.position && @.position.x > 100)]
```

## 🛠 Troubleshooting

### Common Issues and Solutions

#### 1. **MCP Server Not Found**
```
Error: Could not start MCP server 'macos-ui-automation'
```

**Solutions:**
- Verify the absolute path in your configuration is correct
- Ensure `uv` is installed and in your PATH
- Test manually: `uv --directory /path/to/project run macos-ui-automation-mcp`

#### 2. **Accessibility Permission Denied**
```
Error: Accessibility permissions not granted
```

**Solutions:**
- Add Claude Code to Accessibility permissions in System Preferences
- Restart Claude Code after granting permissions
- Test with: `uv run python -c "from macos_ui_automation.accessibility import get_ax_utils; print(get_ax_utils().is_accessibility_trusted())"`

#### 3. **No Elements Found**
```
Result: []
```

**Solutions:**
- Try a broader selector: `$..[?(@.role)]`
- Increase timeout: `timeout_seconds: 15`
- Check if target app is in foreground
- Use `get_app_overview` to see available applications

#### 4. **Timeout Errors**
```
Error: Search timed out during state collection
```

**Solutions:**
- Increase `timeout_seconds` parameter
- Use app-specific searches: `find_elements_in_app`
- Try shallow search first: reduce complexity of selector

#### 5. **Element Not Clickable**
```
Error: Element is not clickable
```

**Solutions:**
- Verify element is enabled: `$..[?(@.enabled==true)]`
- Check element has click action: `$..[?(@.actions[*]=='AXPress')]`
- Try clicking parent element
- Ensure window is in foreground

### Debug Mode

Enable detailed logging for debugging:

```json
{
  "mcpServers": {
    "macos-ui-automation": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/macos-ui-automation-mcp", 
        "run",
        "macos-ui-automation-mcp"
      ],
      "env": {
        "PYTHONPATH": "/path/to/macos-ui-automation-mcp/src",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Testing Outside Claude Code

Test the MCP server independently:

```bash
# Test basic functionality
uv run python -c "
from macos_ui_automation.mcp_server_simple import list_running_applications
apps = list_running_applications()
print(f'Found {len(apps)} applications')
for app in apps[:3]:
    print(f'- {app[\"name\"]} (PID: {app[\"pid\"]})')
"

# Test element finding
uv run python -c "
from macos_ui_automation.mcp_server_simple import find_elements
elements = find_elements('$..[?(@.role==\"AXButton\")]', timeout_seconds=5)
print(f'Found {len(elements)} buttons')
"
```

## 🚀 Advanced Usage Patterns

### 1. **Web Automation in Claude Code**
```
"Find the login form in Safari and fill it out:
- Username field: john@example.com  
- Password field: mypassword
- Click the login button"
```

### 2. **Desktop App Automation**
```
"In the Calculator app:
- Click the number 5
- Click the plus button  
- Click the number 3
- Click equals
- Tell me the result"
```

### 3. **Development Workflow Automation**
```
"In my code editor:
- Find all open tabs
- Click on the tab containing 'main.py'
- Find the run button and click it"
```

### 4. **UI Testing and Validation**
```
"Check if the login form has all required fields:
- Username/email field
- Password field  
- Submit button
- Remember me checkbox"
```

## 🔗 Integration with Other Tools

### Combine with File Operations
```
"Take a screenshot of the current window, then save the current UI state to a JSON file for later analysis"
```

### Data Extraction Workflows
```
"Extract all menu items from the current application and save them to a CSV file for documentation"
```

### Automated Testing
```
"Run through this login workflow and verify each step works:
1. Open Safari
2. Navigate to login page  
3. Fill in credentials
4. Submit form
5. Verify success page appears"
```

## 📖 Best Practices

### 1. **Start with Overview**
Always begin with `get_app_overview` or `list_running_applications` to understand the current state.

### 2. **Use Specific Selectors**
Prefer specific identifiers over generic searches:
- ✅ `$..[?(@.ax_identifier=='loginButton')]`
- ❌ `$..[?(@.title=='Button')]`

### 3. **Handle Timeouts Gracefully**
Set appropriate timeouts based on UI complexity:
- Simple searches: 5-10 seconds
- Complex apps: 15-20 seconds
- Deep hierarchies: 20+ seconds

### 4. **Test Interactively**
Use Claude Code's interactive mode to refine selectors before automation.

### 5. **Verify Before Acting**
Always check if elements exist and are enabled before performing actions.

## 🤝 Contributing to Integration

Found an issue with Claude Code integration? Please:

1. Check this guide first
2. Test the MCP server independently
3. Create an issue with:
   - Claude Code version
   - macOS version  
   - Configuration used
   - Error messages
   - Steps to reproduce

## 📞 Support

- **General Issues**: [GitHub Issues](https://github.com/mb-dev/macos-ui-automation-mcp/issues)
- **Claude Code Specific**: Include "Claude Code" in issue title
- **Quick Help**: Check the [troubleshooting section](examples/troubleshooting.md)

---

**Ready to automate macOS with Claude Code?** Follow the setup steps above and start with simple commands like *"Show me all running applications"* to get familiar with the interface.