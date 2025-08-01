#!/usr/bin/env python3
"""
Basic macOS UI automation examples using the library directly.

This script demonstrates how to use the macos-ui-automation library
programmatically without the MCP interface.
"""

import json
import time
from pathlib import Path

from macos_ui_automation import JSONPathSelector, SystemStateDumper


def main():
    """Run basic automation examples."""
    print("🚀 macOS UI Automation - Basic Examples")
    print("=" * 50)

    # Example 1: Get system overview
    print("\n1️⃣ Getting System Overview")
    print("-" * 30)

    # Create system state dumper with shallow depth for overview
    dumper = SystemStateDumper(max_depth=3, only_visible_children=True)
    system_state = dumper.dump_system_state()

    print(f"📱 Captured system state at: {system_state.timestamp}")
    print(f"🔧 Accessibility enabled: {system_state.accessibility_enabled}")
    print(f"📦 Found {len(system_state.processes)} running applications")

    # Show running applications
    print("\n📋 Running Applications:")
    for process in system_state.processes[:10]:  # Show first 10
        status = "🟢 Active" if process.frontmost else "⚫ Background"
        print(f"  {status} {process.name} (PID: {process.pid})")

    # Example 2: Find UI elements with JSONPath
    print("\n\n2️⃣ Finding UI Elements")
    print("-" * 30)

    # Create JSONPath selector
    selector = JSONPathSelector(system_state)

    # Find all buttons in the system
    all_buttons = selector.find("$..[?(@.role=='AXButton')]")
    print(f"🔘 Found {len(all_buttons)} buttons across all applications")

    # Find buttons with titles
    titled_buttons = selector.find("$..[?(@.role=='AXButton' && @.title)]")
    print(f"🏷️  Found {len(titled_buttons)} buttons with titles")

    # Show some example button titles
    if titled_buttons:
        print("\n📝 Example button titles:")
        for button in titled_buttons[:5]:
            if isinstance(button, dict) and button.get("title"):
                print(f"  • {button['title']}")

    # Example 3: Application-specific search
    print("\n\n3️⃣ Application-Specific Search")
    print("-" * 30)

    # Find applications with windows
    apps_with_windows = [p for p in system_state.processes if p.windows]

    if apps_with_windows:
        target_app = apps_with_windows[0]
        print(f"🎯 Focusing on: {target_app.name}")

        # Search within specific application
        app_buttons = selector.find(
            f"$.processes[?(@.name=='{target_app.name}')]..[?(@.role=='AXButton')]"
        )
        print(f"🔍 Found {len(app_buttons)} buttons in {target_app.name}")

        # Find text fields in the app
        app_text_fields = selector.find(
            f"$.processes[?(@.name=='{target_app.name}')]..[?(@.role=='AXTextField')]"
        )
        print(f"📝 Found {len(app_text_fields)} text fields in {target_app.name}")

    # Example 4: Element details and properties
    print("\n\n4️⃣ Element Analysis")
    print("-" * 30)

    # Find elements with accessibility identifiers
    elements_with_id = selector.find("$..[?(@.ax_identifier)]")
    print(f"🆔 Found {len(elements_with_id)} elements with accessibility identifiers")

    # Show some examples
    if elements_with_id:
        print("\n🏷️  Example accessibility identifiers:")
        for element in elements_with_id[:5]:
            if isinstance(element, dict):
                identifier = element.get("ax_identifier", "Unknown")
                role = element.get("role", "Unknown")
                title = element.get("title", "No title")
                print(f"  • {identifier} ({role}) - {title}")

    # Example 5: Enabled vs disabled elements
    print("\n\n5️⃣ Element States")
    print("-" * 30)

    # Find enabled buttons
    enabled_buttons = selector.find("$..[?(@.role=='AXButton' && @.enabled==true)]")
    disabled_buttons = selector.find("$..[?(@.role=='AXButton' && @.enabled==false)]")

    print(f"✅ Enabled buttons: {len(enabled_buttons)}")
    print(f"❌ Disabled buttons: {len(disabled_buttons)}")

    # Find focused elements
    focused_elements = selector.find("$..[?(@.focused==true)]")
    print(f"🎯 Currently focused elements: {len(focused_elements)}")

    # Example 6: Save system state for later analysis
    print("\n\n6️⃣ Saving System State")
    print("-" * 30)

    # Save system state to JSON file
    output_file = Path("ui_state_snapshot.json")
    with output_file.open("w") as f:
        json.dump(system_state.model_dump(), f, indent=2, default=str)

    print(f"💾 System state saved to: {output_file.absolute()}")
    print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")

    # Example 7: Time-based search with timeout
    print("\n\n7️⃣ Time-Limited Deep Search")
    print("-" * 30)

    print("🔍 Performing deep search with timeout...")
    start_time = time.time()

    # Use deep search with timeout
    deep_dumper = SystemStateDumper(max_depth=10, only_visible_children=True)
    deep_state = deep_dumper.dump_system_state_with_timeout(timeout_seconds=8.0)

    elapsed = time.time() - start_time
    print(f"⏱️  Deep search completed in {elapsed:.2f} seconds")
    print(f"🔍 Deep search found {len(deep_state.processes)} processes")

    # Compare shallow vs deep results
    deep_selector = JSONPathSelector(deep_state)
    deep_buttons = deep_selector.find("$..[?(@.role=='AXButton')]")
    print(f"🆚 Shallow search: {len(all_buttons)} buttons")
    print(f"🆚 Deep search: {len(deep_buttons)} buttons")
    improvement = len(deep_buttons) - len(all_buttons)
    print(f"📈 Improvement: {improvement} additional buttons found")


def demo_ui_actions():
    """Demonstrate UI actions (commented out for safety)."""
    print("\n\n🎮 UI Actions Demo (Safe Mode)")
    print("-" * 30)
    print("ℹ️  UI actions are commented out for safety.")
    print("ℹ️  Uncomment and modify for your specific use case.")

    # SAFETY NOTE: These actions are commented out to prevent
    # accidental clicks during demonstration

    """
    # Create UI actions handler
    dumper = SystemStateDumper(max_depth=5)
    state = dumper.dump_system_state()
    selector = JSONPathSelector(state)
    actions = UIActions(selector)

    # Example: Find and click a specific button
    buttons = selector.find("$..[?(@.ax_identifier=='myButton')]")
    if buttons:
        print(f"Found button: {buttons[0].get('title', 'No title')}")
        # actions.click(buttons[0])  # Uncomment to actually click
        print("✅ Would click button (action disabled for safety)")

    # Example: Type into a text field
    text_fields = selector.find(
        "$..[?(@.role=='AXTextField' && @.enabled==true)]"
    )
    if text_fields:
        print(f"Found text field: {text_fields[0].get('title', 'No title')}")
        # actions.type_text(text_fields[0], "Hello, World!")
        # Uncomment to actually type
        print("✅ Would type text (action disabled for safety)")
    """


if __name__ == "__main__":
    try:
        main()
        demo_ui_actions()
        print("\n\n✨ Examples completed successfully!")
        print("🔧 Modify this script for your specific automation needs.")

    except PermissionError as e:
        print(f"\n❌ Permission Error: {e}")
        print("🔧 Please grant accessibility permissions in System Preferences")
        print("   System Preferences → Security & Privacy → Privacy → Accessibility")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("🐛 Check the error message above for troubleshooting guidance")
