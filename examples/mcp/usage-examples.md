# MCP Usage Examples

This guide shows how to use the macOS UI Automation MCP server with Claude Desktop and Claude Code through natural language and direct tool usage.

## 🗣 Natural Language Examples

Once the MCP server is configured, you can use these natural language commands with Claude:

### Web Browser Automation
```
"Open Safari and find all the input fields on the current page"

"Click the login button in my browser"

"Find all links on this webpage and show me their titles"

"Fill out the search box with 'macOS automation' and submit the form"
```

### Desktop Application Control
```
"Show me all the buttons in the Calculator app"

"Click the number 5, then plus, then 3, then equals in Calculator"

"Find all menu items in the currently focused application"

"Take a screenshot of the current window and describe what you see"
```

### Development Workflow
```
"In my code editor, find all open tabs and tell me which files are open"

"Click the run button in Xcode"

"Find all text that contains 'TODO' in the current window"

"Show me all error messages currently visible on screen"
```

### System Navigation
```
"List all applications currently running on my system"

"Find the minimize button in the current window and click it"

"Show me all notification badges in the menu bar"

"Find all text fields that are currently focused"
```

## 🛠 Direct Tool Usage Examples

### 1. Basic Element Search

**Find all buttons:**
```
Tool: find_elements
Parameters:
- jsonpath_selector: $..[?(@.role=='AXButton')]
- timeout_seconds: 10
```

**Find elements with specific identifier:**
```
Tool: find_elements
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='submitButton')]
- timeout_seconds: 5
```

### 2. Application-Specific Searches

**Search within Safari:**
```
Tool: find_elements_in_app
Parameters:
- app_name: Safari
- jsonpath_selector: $..[?(@.role=='AXTextField')]
- timeout_seconds: 15
```

**Find buttons in current frontmost app:**
```
Tool: find_elements
Parameters:
- jsonpath_selector: $.processes[?(@.frontmost==true)]..[?(@.role=='AXButton')]
- timeout_seconds: 10
```

### 3. UI Actions

**Click a login button:**
```
Tool: click_element_by_selector
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='loginButton')]
```

**Type into username field:**
```
Tool: type_text_to_element_by_selector
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='usernameField')]
- text: john@example.com
```

### 4. System Overview

**Get running applications:**
```
Tool: list_running_applications
Parameters: (none)
```

**Quick app overview:**
```
Tool: get_app_overview
Parameters:
- timeout_seconds: 5
```

## 🎯 Practical Workflow Examples

### Example 1: Login Automation
```
1. "First, show me all running applications"
   (Use list_running_applications)

2. "Find the login form in Safari"
   (Use find_elements_in_app with Safari and text field selectors)

3. "Fill in the username field with 'user@example.com'"
   (Use type_text_to_element_by_selector)

4. "Fill in the password field"
   (Use type_text_to_element_by_selector)

5. "Click the login button"
   (Use click_element_by_selector)
```

### Example 2: UI Testing
```
1. "Get an overview of the current app"
   (Use get_app_overview)

2. "Find all form elements"
   (Use find_elements with form-related selectors)

3. "Check if all required fields are present"
   (Analyze the results for required elements)

4. "Verify all buttons are enabled"
   (Use find_elements with enabled filter)
```

### Example 3: Data Extraction
```
1. "Find all menu items in the current application"
   (Use find_elements with menu item selectors)

2. "Extract all visible text from the current window"
   (Use find_elements with static text selectors)

3. "Get details about each element found"
   (Use get_element_details for each element)
```

## 🔍 Advanced JSONPath Patterns

### Complex Filtering
```
# Buttons that are enabled and have titles
$..[?(@.role=='AXButton' && @.enabled==true && @.title)]

# Text fields that are not empty
$..[?(@.role=='AXTextField' && @.value && @.value != '')]

# Elements in specific position range
$..[?(@.position && @.position.x > 100 && @.position.x < 500)]
```

### Application Context
```
# All elements in frontmost application
$.processes[?(@.frontmost==true)]..[?(@.role)]

# Elements in specific window of an app
$.processes[?(@.name=='MyApp')].windows[?(@.main_window==true)]..[?(@.role=='AXButton')]

# Menu items in application menu bar
$.processes[?(@.name=='Safari')].menu_bar[*]..[?(@.role=='AXMenuItem')]
```

### Pattern Matching
```
# Case-insensitive title matching
$..[?(@.title && @.title =~ /(?i).*submit.*/)]

# Multiple role types
$..[?(@.role=='AXButton' || @.role=='AXMenuItem' || @.role=='AXPopUpButton')]

# Elements with specific action capabilities
$..[?(@.actions && @.actions[*] == 'AXPress')]
```

## ⚠️ Best Practices

### 1. Start Broad, Then Narrow
```
# First: Get overview
Tool: get_app_overview

# Then: Search within specific app
Tool: find_elements_in_app
Parameters:
- app_name: [discovered from overview]
- jsonpath_selector: $..[?(@.role=='AXButton')]
```

### 2. Use Timeouts Appropriately
- **Simple searches**: 5-10 seconds
- **Complex applications**: 15-20 seconds  
- **Deep hierarchies**: 20+ seconds

### 3. Verify Before Acting
```
# First: Find the element
Tool: find_elements
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='loginButton')]

# Then: Verify it's clickable before clicking
Tool: get_element_details
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='loginButton')]

# Finally: Perform the action
Tool: click_element_by_selector
Parameters:
- jsonpath_selector: $..[?(@.ax_identifier=='loginButton')]
```

### 4. Handle Multiple Results
When multiple elements match, be specific:
```
# Too broad (might return many results)
$..[?(@.title=='Button')]

# More specific (likely single result)
$.processes[?(@.name=='MyApp')].windows[0]..[?(@.ax_identifier=='submitButton')]
```

## 🐛 Troubleshooting Common Issues

### No Elements Found
```
# Try broader selector first
$..[?(@.role)]

# Check if app is in foreground
$.processes[?(@.frontmost==true)]

# Increase timeout
(Set timeout_seconds to 15-20)
```

### Element Not Clickable
```
# Verify element is enabled
$..[?(@.enabled==true)]

# Check for click actions
$..[?(@.actions[*]=='AXPress')]
```

### App Not Found
```
# List all running apps first
Tool: list_running_applications

# Use exact app name from the list
Tool: find_elements_in_app
Parameters:
- app_name: [exact name from list]
```

## 🚀 Progressive Automation

Start simple and build complexity:

### Level 1: Basic Discovery
- List applications
- Find basic elements (buttons, text fields)
- Get element details

### Level 2: Simple Actions  
- Click buttons
- Type into fields
- Navigate basic UI

### Level 3: Complex Workflows
- Multi-step form filling
- Application switching
- Conditional logic based on UI state

### Level 4: Advanced Integration
- Combine with file operations
- Data extraction and processing
- Automated testing workflows

## 💡 Tips for Effective Usage

1. **Always start with discovery** - understand what's available before acting
2. **Use specific identifiers** when possible - more reliable than titles
3. **Test selectors incrementally** - start broad, then add conditions
4. **Combine tools strategically** - overview → search → details → action
5. **Handle edge cases** - verify elements exist and are actionable

Ready to automate your macOS workflows? Start with simple discovery commands and build up to complex automation patterns!