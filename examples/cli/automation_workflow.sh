#!/bin/bash

# macOS UI Automation CLI Workflow Examples
# 
# This script demonstrates how to use the macos-ui-automation CLI tool
# for common automation workflows and system analysis.

set -e  # Exit on any error

echo "🚀 macOS UI Automation CLI Examples"
echo "===================================="

# Check if the CLI tool is available
if ! command -v macos-ui-automation &> /dev/null; then
    echo "❌ macos-ui-automation CLI not found"
    echo "💡 Install with: uv add macos-ui-automation-mcp"
    echo "💡 Or run with: uv run macos-ui-automation"
    exit 1
fi

# Create output directory for results
OUTPUT_DIR="./automation_results"
mkdir -p "$OUTPUT_DIR"
echo "📁 Results will be saved to: $OUTPUT_DIR"

echo ""
echo "1️⃣ System Overview"
echo "=================="

# Dump current system state with shallow depth for overview
echo "📱 Capturing system state overview..."
macos-ui-automation dump \
    --max-depth 3 \
    --output "$OUTPUT_DIR/system_overview.json"

echo "✅ System overview saved to system_overview.json"

# Get basic statistics from the dump
if command -v jq &> /dev/null; then
    echo "📊 System Statistics:"
    PROCESS_COUNT=$(jq '.processes | length' "$OUTPUT_DIR/system_overview.json")
    echo "   • Running applications: $PROCESS_COUNT"
    
    FRONTMOST_APP=$(jq -r '.processes[] | select(.frontmost==true) | .name' "$OUTPUT_DIR/system_overview.json")
    echo "   • Frontmost application: $FRONTMOST_APP"
else
    echo "💡 Install 'jq' for enhanced JSON processing: brew install jq"
fi

echo ""
echo "2️⃣ Finding UI Elements"
echo "====================="

# Find all buttons in the system
echo "🔘 Finding all buttons..."
macos-ui-automation find \
    '$..[?(@.role=="AXButton")]' \
    --output "$OUTPUT_DIR/all_buttons.json"

# Count the results
if command -v jq &> /dev/null; then
    BUTTON_COUNT=$(jq '. | length' "$OUTPUT_DIR/all_buttons.json")
    echo "✅ Found $BUTTON_COUNT buttons"
else
    echo "✅ Button search completed"
fi

# Find elements with accessibility identifiers
echo "🆔 Finding elements with accessibility identifiers..."
macos-ui-automation find \
    '$..[?(@.ax_identifier)]' \
    --output "$OUTPUT_DIR/elements_with_ids.json"

if command -v jq &> /dev/null; then
    ID_COUNT=$(jq '. | length' "$OUTPUT_DIR/elements_with_ids.json")
    echo "✅ Found $ID_COUNT elements with identifiers"
fi

echo ""
echo "3️⃣ Application-Specific Searches"
echo "================================"

# Find the frontmost application and search within it
if command -v jq &> /dev/null && [ -f "$OUTPUT_DIR/system_overview.json" ]; then
    FRONTMOST_APP=$(jq -r '.processes[] | select(.frontmost==true) | .name' "$OUTPUT_DIR/system_overview.json")
    
    if [ "$FRONTMOST_APP" != "null" ] && [ "$FRONTMOST_APP" != "" ]; then
        echo "🎯 Searching within frontmost app: $FRONTMOST_APP"
        
        # Find buttons in the frontmost application
        macos-ui-automation find \
            "$.processes[?(@.name==\"$FRONTMOST_APP\")]..[?(@.role==\"AXButton\")]" \
            --output "$OUTPUT_DIR/frontmost_app_buttons.json"
        
        FRONTMOST_BUTTONS=$(jq '. | length' "$OUTPUT_DIR/frontmost_app_buttons.json")
        echo "✅ Found $FRONTMOST_BUTTONS buttons in $FRONTMOST_APP"
        
        # Find text fields in the frontmost application
        macos-ui-automation find \
            "$.processes[?(@.name==\"$FRONTMOST_APP\")]..[?(@.role==\"AXTextField\")]" \
            --output "$OUTPUT_DIR/frontmost_app_textfields.json"
        
        FRONTMOST_TEXTFIELDS=$(jq '. | length' "$OUTPUT_DIR/frontmost_app_textfields.json")
        echo "✅ Found $FRONTMOST_TEXTFIELDS text fields in $FRONTMOST_APP"
    fi
fi

echo ""
echo "4️⃣ Element State Analysis"
echo "========================="

# Find enabled vs disabled buttons
echo "🔍 Analyzing button states..."

macos-ui-automation find \
    '$..[?(@.role=="AXButton" && @.enabled==true)]' \
    --output "$OUTPUT_DIR/enabled_buttons.json"

macos-ui-automation find \
    '$..[?(@.role=="AXButton" && @.enabled==false)]' \
    --output "$OUTPUT_DIR/disabled_buttons.json"

if command -v jq &> /dev/null; then
    ENABLED_COUNT=$(jq '. | length' "$OUTPUT_DIR/enabled_buttons.json")
    DISABLED_COUNT=$(jq '. | length' "$OUTPUT_DIR/disabled_buttons.json")
    echo "✅ Button Analysis:"
    echo "   • Enabled: $ENABLED_COUNT"
    echo "   • Disabled: $DISABLED_COUNT"
fi

# Find currently focused elements
echo "🎯 Finding focused elements..."
macos-ui-automation find \
    '$..[?(@.focused==true)]' \
    --output "$OUTPUT_DIR/focused_elements.json"

if command -v jq &> /dev/null; then
    FOCUSED_COUNT=$(jq '. | length' "$OUTPUT_DIR/focused_elements.json")
    echo "✅ Found $FOCUSED_COUNT focused elements"
fi

echo ""
echo "5️⃣ Deep System Analysis"
echo "======================"

echo "🔍 Performing deep system analysis (this may take longer)..."
macos-ui-automation dump \
    --max-depth 8 \
    --output "$OUTPUT_DIR/deep_system_state.json"

echo "✅ Deep analysis complete"

# Compare shallow vs deep results
if command -v jq &> /dev/null; then
    echo "📊 Comparison Analysis:"
    
    SHALLOW_ELEMENTS=$(jq '[.. | objects | select(has("role"))] | length' "$OUTPUT_DIR/system_overview.json")
    DEEP_ELEMENTS=$(jq '[.. | objects | select(has("role"))] | length' "$OUTPUT_DIR/deep_system_state.json")
    
    echo "   • Shallow scan (depth 3): $SHALLOW_ELEMENTS elements"
    echo "   • Deep scan (depth 8): $DEEP_ELEMENTS elements"
    echo "   • Additional elements found: $((DEEP_ELEMENTS - SHALLOW_ELEMENTS))"
fi

echo ""
echo "6️⃣ Safe Action Examples"
echo "======================"

echo "ℹ️  Action examples (read-only for safety):"
echo ""

# Note: These are read-only examples. Uncomment and modify for actual automation.

echo "# Example: Click a specific button (DISABLED FOR SAFETY)"
echo "# macos-ui-automation action click '\$..[?(@.ax_identifier==\"submitButton\")]'"
echo ""

echo "# Example: Type into a text field (DISABLED FOR SAFETY)"  
echo "# macos-ui-automation action type '\$..[?(@.ax_identifier==\"usernameField\")]' --text 'myusername'"
echo ""

echo "# Example: Click first enabled button (DISABLED FOR SAFETY)"
echo "# macos-ui-automation action click '\$..[?(@.role==\"AXButton\" && @.enabled==true)]' --max-results 1"

echo ""
echo "7️⃣ Report Generation"
echo "==================="

# Generate a summary report
REPORT_FILE="$OUTPUT_DIR/automation_report.txt"
echo "📄 Generating automation report..."

cat > "$REPORT_FILE" << EOF
macOS UI Automation Analysis Report
Generated: $(date)

SYSTEM OVERVIEW:
EOF

if command -v jq &> /dev/null; then
    cat >> "$REPORT_FILE" << EOF
- Running Applications: $(jq '.processes | length' "$OUTPUT_DIR/system_overview.json")
- Frontmost Application: $(jq -r '.processes[] | select(.frontmost==true) | .name' "$OUTPUT_DIR/system_overview.json")

ELEMENT ANALYSIS:
- Total Buttons: $(jq '. | length' "$OUTPUT_DIR/all_buttons.json")
- Enabled Buttons: $(jq '. | length' "$OUTPUT_DIR/enabled_buttons.json")
- Disabled Buttons: $(jq '. | length' "$OUTPUT_DIR/disabled_buttons.json")
- Elements with IDs: $(jq '. | length' "$OUTPUT_DIR/elements_with_ids.json")
- Focused Elements: $(jq '. | length' "$OUTPUT_DIR/focused_elements.json")

DEPTH COMPARISON:
- Shallow Scan Elements: $(jq '[.. | objects | select(has("role"))] | length' "$OUTPUT_DIR/system_overview.json")
- Deep Scan Elements: $(jq '[.. | objects | select(has("role"))] | length' "$OUTPUT_DIR/deep_system_state.json")

FILES GENERATED:
EOF
    ls -la "$OUTPUT_DIR"/*.json | while read line; do
        echo "- $line" >> "$REPORT_FILE"
    done
else
    cat >> "$REPORT_FILE" << EOF
- Install 'jq' for detailed statistics: brew install jq

FILES GENERATED:
EOF
    ls -la "$OUTPUT_DIR"/ >> "$REPORT_FILE"
fi

echo "✅ Report saved to: $REPORT_FILE"

echo ""
echo "🎉 CLI Workflow Examples Complete!"
echo "=================================="
echo ""
echo "📁 All results saved to: $OUTPUT_DIR/"
echo "📄 Summary report: $REPORT_FILE"
echo ""
echo "💡 Next Steps:"
echo "   • Review the generated JSON files"
echo "   • Modify selectors for your specific needs"
echo "   • Uncomment action examples for automation (be careful!)"
echo "   • Integrate into your own scripts and workflows"
echo ""
echo "⚠️  Safety Reminder:"
echo "   • Always test selectors before running actions"
echo "   • Use --max-results 1 to limit action scope"
echo "   • Backup important data before automation"