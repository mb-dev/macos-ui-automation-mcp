"""
Command-line interface for macOS UI Automation.

This CLI provides easy access to system state dumping, element selection,
and automation testing without needing manual test scripts.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from ApplicationServices import AXIsProcessTrusted

from macos_ui_automation import JSONPathSelector
from macos_ui_automation.core.actions import UIActions
from macos_ui_automation.core.state import SystemStateDumper
from macos_ui_automation.models.types import SystemState, UIElement

# Constants
DEFAULT_TIMEOUT_SECONDS = 30.0
MENU_BAR_TIMEOUT_DEFAULT = 2.0
QUICK_DUMP_TIMEOUT = 5.0
MAX_ACTIONS_PREVIEW = 3


def action_command(args: argparse.Namespace) -> None:
    """Perform an action on elements found by JSONPath."""
    print(f"🎯 Performing action: {args.action} on {args.jsonpath}")

    # Load system state
    if args.input:
        print(f"📄 Loading system state from: {args.input}")
        state_data = Path(args.input).read_text()
        system_state = SystemState.model_validate_json(state_data)
    else:
        print("📱 Capturing current system state...")
        dumper = SystemStateDumper(timeout_seconds=args.timeout_seconds)
        system_state = dumper.dump_system_state()

    # Create selector and find elements
    selector = JSONPathSelector(system_state)
    elements = selector.find_elements(args.jsonpath)

    if not elements:
        print(f"❌ No elements found for JSONPath: {args.jsonpath}")
        sys.exit(1)

    print(f"📋 Found {len(elements)} matching element(s)")

    # Create UI actions handler
    dumper = SystemStateDumper()
    actions = UIActions(dumper)

    # Perform the action
    success_count = 0
    for i, element in enumerate(elements, 1):
        print(f"\n--- Element {i}/{len(elements)} ---")
        print(f"Role: {element.role}")
        print(f"Title: {element.title or 'No title'}")
        if element.position:
            print(f"Position: ({element.position.x}, {element.position.y})")

        if args.action == "click":
            if element.clickable:
                print("🖱️ Clicking element...")
                success = actions.click_element(element)
                if success:
                    print("✅ Click successful!")
                    success_count += 1
                else:
                    print("❌ Click failed!")
            else:
                print("⚠️ Element is not clickable")
                actions_str = ", ".join(element.actions) if element.actions else "None"
                print(f"Available actions: {actions_str}")

        elif args.action == "set_value":
            if not args.value:
                print("❌ --value is required for set_value action")
                continue

            if element.editable:
                print(f"✏️ Setting value to: {args.value}")
                success = actions.set_element_value(element, args.value)
                if success:
                    print("✅ Value set successfully!")
                    success_count += 1
                else:
                    print("❌ Failed to set value!")
            else:
                print("⚠️ Element is not editable")

        elif args.action == "get_value":
            value = actions.get_element_value(element)
            print(f"📝 Value: {value}")
            success_count += 1

        elif args.action == "info":
            # Just display info (already shown above)
            success_count += 1

        else:
            print(f"❌ Unknown action: {args.action}")

    print(f"\n🏁 Action completed on {success_count}/{len(elements)} element(s)")


def dump_system_state(args: argparse.Namespace) -> None:
    """Dump the current system state to JSON."""
    print("🔍 Dumping system state...")

    dumper = SystemStateDumper(
        timeout_seconds=args.timeout_seconds,
        menu_bar_timeout=args.menu_bar_timeout,
        only_visible_children=not args.include_invisible_children,
    )

    # Handle process filtering
    include_processes = (
        args.include_processes.split(",") if args.include_processes else None
    )
    exclude_processes = (
        args.exclude_processes.split(",") if args.exclude_processes else None
    )

    system_state = dumper.dump_system_state(
        include_processes=include_processes,
        exclude_processes=exclude_processes,
        skip_menu_bar_extras=args.skip_menu_bar_extras,
    )

    # Prepare output
    output_data = system_state.model_dump_json(indent=2)

    if args.output:
        # Write to file
        output_path = Path(args.output)
        output_path.write_text(output_data)
        print(f"✅ System state dumped to: {output_path}")
        print(f"📊 Captured {len(system_state.processes)} processes")
    else:
        # Write to stdout
        print(output_data)


def query_elements(args: argparse.Namespace) -> None:
    """Query UI elements using JSONPath selectors."""
    print(f"🔎 Querying elements with JSONPath: {args.jsonpath}")

    # Load system state
    if args.input:
        state_data = Path(args.input).read_text()
        system_state = SystemState.model_validate_json(state_data)
    else:
        print("📱 Capturing current system state...")
        dumper = SystemStateDumper()
        system_state = dumper.dump_system_state()

    # Create selector and query
    selector = JSONPathSelector(system_state)
    results = selector.find(args.jsonpath)

    print(f"📋 Found {len(results)} matching elements:")

    if args.output:
        # Write results to file
        output_data = json.dumps(results, indent=2)
        Path(args.output).write_text(output_data)
        print(f"✅ Results saved to: {args.output}")
    else:
        # Print results to console
        for i, result in enumerate(results, 1):
            print(f"\n--- Element {i} ---")
            if isinstance(result, dict):
                print(f"Role: {result.get('role', 'Unknown')}")
                print(f"Title: {result.get('title', 'No title')}")
                print(f"Enabled: {result.get('enabled', 'Unknown')}")
                if result.get("position"):
                    pos = result["position"]
                    print(f"Position: ({pos.get('x', 0)}, {pos.get('y', 0)})")
            else:
                print(f"Value: {result}")


def find_elements(args: argparse.Namespace) -> None:
    """Find UI elements using convenience methods."""
    print(f"🎯 Finding elements: {args.element_type}")

    # Load system state
    if args.input:
        state_data = Path(args.input).read_text()
        system_state = SystemState.model_validate_json(state_data)
    else:
        print("📱 Capturing current system state...")
        dumper = SystemStateDumper()
        system_state = dumper.dump_system_state()

    # Create selector
    selector = JSONPathSelector(system_state)

    # Find elements based on type
    elements: list[UIElement] = []
    if args.element_type == "buttons":
        if args.title:
            elements = selector.find_buttons_by_title(args.title)
        else:
            elements = selector.find_by_role("AXButton")
    elif args.element_type == "text_fields":
        elements = selector.find_text_fields()
    elif args.element_type == "clickable":
        elements = selector.find_clickable_elements()
    elif args.element_type == "menu_items":
        if args.title:
            elements = selector.find_menu_items_by_title(args.title)
        else:
            elements = selector.find_by_role("AXMenuItem")
    elif args.element_type == "windows":
        if args.title:
            elements = selector.find_windows_by_title(args.title)  # type: ignore[assignment]
        else:
            elements = selector.find_frontmost_app_windows()  # type: ignore[assignment]
    else:
        print(f"❌ Unknown element type: {args.element_type}")
        sys.exit(1)

    print(f"📋 Found {len(elements)} {args.element_type}:")

    for i, element in enumerate(elements, 1):
        print(f"\n--- {args.element_type.title()} {i} ---")
        print(f"Role: {element.role}")
        print(f"Title: {element.title or 'No title'}")
        print(f"Enabled: {element.enabled}")
        if element.position:
            print(f"Position: ({element.position.x}, {element.position.y})")
        if element.actions:
            actions_preview = ", ".join(element.actions[:MAX_ACTIONS_PREVIEW])
            suffix = "..." if len(element.actions) > MAX_ACTIONS_PREVIEW else ""
            print(f"Actions: {actions_preview}{suffix}")


def info_command(args: argparse.Namespace) -> None:
    """Show information about the system state or loaded file."""
    if args.input:
        print(f"📄 Loading system state from: {args.input}")
        state_data = Path(args.input).read_text()
        system_state = SystemState.model_validate_json(state_data)
    else:
        print("📱 Capturing current system state...")
        dumper = SystemStateDumper()
        system_state = dumper.dump_system_state()

    print("\n📊 System State Summary")
    print(f"{'=' * 50}")
    print(f"Timestamp: {system_state.timestamp}")
    print(f"Accessibility Enabled: {system_state.accessibility_enabled}")
    print(f"Capture Method: {system_state.capture_method}")
    print(f"Total Processes: {len(system_state.processes)}")

    # Frontmost process info
    frontmost = next(
        (process for process in system_state.processes if process.frontmost), None
    )
    if frontmost:
        print(f"Frontmost App: {frontmost.name} (PID: {frontmost.pid})")
        print(f"Frontmost App Windows: {len(frontmost.windows)}")
        print(f"Frontmost App Menu Items: {len(frontmost.menu_bar)}")

    print("\n📱 Process Details")
    print(f"{'=' * 50}")
    for proc in system_state.processes:
        status = "🔵" if proc.frontmost else "⚪"
        windows_count = len(proc.windows)
        menu_count = len(proc.menu_bar)
        print(
            f"{status} {proc.name} (PID: {proc.pid}) - "
            f"{windows_count} windows, {menu_count} menu items"
        )


def test_accessibility(args: argparse.Namespace) -> None:
    """Test accessibility permissions and functionality."""
    print("🔐 Testing accessibility permissions...")
    if hasattr(args, "verbose") and args.verbose:
        print("🔍 Running in verbose mode...")

    if AXIsProcessTrusted():
        print("✅ Accessibility permissions are granted")
    else:
        print("❌ Accessibility permissions are NOT granted")
        print("💡 Please enable accessibility permissions in System Preferences")
        print(
            "   Go to: System Preferences > Security & Privacy > "
            "Privacy > Accessibility"
        )
        sys.exit(1)

    # Test basic dumping functionality
    print("🧪 Testing basic system state dumping...")
    dumper = SystemStateDumper(
        timeout_seconds=QUICK_DUMP_TIMEOUT
    )  # Quick dump for speed
    system_state = dumper.dump_system_state()

    print(f"✅ Successfully captured {len(system_state.processes)} processes")

    # Test JSON serialization
    print("🧪 Testing JSON serialization...")
    json_data = system_state.model_dump_json()
    SystemState.model_validate_json(json_data)
    print("✅ JSON serialization/deserialization works")

    # Test JSONPath selector
    print("🧪 Testing JSONPath selector...")
    selector = JSONPathSelector(system_state)
    processes = selector.find("$.processes[*].name")
    print(f"✅ JSONPath selector found {len(processes)} process names")

    print("\n🎉 All accessibility tests passed!")


def setup_logging(*, verbose: bool = False, debug: bool = False) -> None:
    """Setup logging configuration for the CLI."""
    if debug:
        level = logging.DEBUG
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif verbose:
        level = logging.INFO
        format_str = "%(levelname)s - %(name)s - %(message)s"
    else:
        level = logging.WARNING
        format_str = "%(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt="%H:%M:%S",
        stream=sys.stderr,  # Use stderr so it doesn't interfere with JSON output
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="macOS UI Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dump current system state with default 30s timeout
  python -m macos_ui_automation.cli dump --output state.json

  # Dump with custom timeout for deep UI hierarchies
  python -m macos_ui_automation.cli dump --timeout-seconds 60 --output state.json

  # Dump only specific processes
  python -m macos_ui_automation.cli dump --include-processes \\
    "Safari,Finder,TextEdit"

  # Query elements with JSONPath
  python -m macos_ui_automation.cli query "$.processes[*].windows[*].title"

  # Find all buttons
  python -m macos_ui_automation.cli find buttons

  # Find buttons with specific title
  python -m macos_ui_automation.cli find buttons --title "Submit"

  # Show system state info
  python -m macos_ui_automation.cli info

  # Test accessibility permissions
  python -m macos_ui_automation.cli test

  # Perform actions on elements using JSONPath
  python -m macos_ui_automation.cli action \\
    "$.processes[?@.name=='Safari'].menu_bar[*]" click --input state.json

  # Click on a specific menu item
  python -m macos_ui_automation.cli action \\
    "$.processes[?@.name=='Safari'].menu_bar[*].children[?@.title=='File']" \\
    click

  # Set value of a text field
  python -m macos_ui_automation.cli action \\
    "$.processes[*].windows[*]..children[?@.role=='AXTextField' && " \\
    "@.title=='Username']" set_value --value "john.doe"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Helper function to add common arguments to all subparsers
    def add_common_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Enable verbose logging (INFO level)",
        )
        subparser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            help="Enable debug logging (DEBUG level)",
        )

    # Dump command
    dump_parser = subparsers.add_parser("dump", help="Dump system state to JSON")
    dump_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    dump_parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum time to spend traversing UI hierarchy in seconds (default: 30)",
    )
    dump_parser.add_argument(
        "--menu-bar-timeout",
        type=float,
        default=MENU_BAR_TIMEOUT_DEFAULT,
        help="Maximum time for menu bar traversal in seconds "
        "(default: 2 to avoid triggering menus)",
    )
    dump_parser.add_argument(
        "--include-processes", help="Comma-separated list of process names to include"
    )
    dump_parser.add_argument(
        "--exclude-processes", help="Comma-separated list of process names to exclude"
    )
    dump_parser.add_argument(
        "--skip-menu-bar-extras",
        action="store_true",
        help="Skip AXExtrasMenuBar to completely avoid menu bar extras",
    )
    dump_parser.add_argument(
        "--include-invisible-children",
        action="store_true",
        help="Include children of invisible elements (may trigger UI side effects)",
    )
    add_common_args(dump_parser)
    dump_parser.set_defaults(func=dump_system_state)

    # Query command
    query_parser = subparsers.add_parser("query", help="Query elements with JSONPath")
    query_parser.add_argument("jsonpath", help="JSONPath expression")
    query_parser.add_argument(
        "--input", "-i", help="Input JSON file (default: capture current state)"
    )
    query_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    add_common_args(query_parser)
    query_parser.set_defaults(func=query_elements)

    # Find command
    find_parser = subparsers.add_parser(
        "find", help="Find UI elements using convenience methods"
    )
    find_parser.add_argument(
        "element_type",
        choices=["buttons", "text_fields", "clickable", "menu_items", "windows"],
        help="Type of elements to find",
    )
    find_parser.add_argument("--title", help="Element title to search for")
    find_parser.add_argument(
        "--input", "-i", help="Input JSON file (default: capture current state)"
    )
    add_common_args(find_parser)
    find_parser.set_defaults(func=find_elements)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show system state information")
    info_parser.add_argument(
        "--input", "-i", help="Input JSON file (default: capture current state)"
    )
    add_common_args(info_parser)
    info_parser.set_defaults(func=info_command)

    # Test command
    test_parser = subparsers.add_parser(
        "test", help="Test accessibility permissions and functionality"
    )
    add_common_args(test_parser)
    test_parser.set_defaults(func=test_accessibility)

    # Action command
    action_parser = subparsers.add_parser(
        "action", help="Perform an action on elements found by JSONPath"
    )
    action_parser.add_argument("jsonpath", help="JSONPath expression to find elements")
    action_parser.add_argument(
        "action",
        choices=["click", "set_value", "get_value", "info"],
        help="Action to perform on found elements",
    )
    action_parser.add_argument("--value", help="Value to set for set_value action")
    action_parser.add_argument(
        "--input", "-i", help="Input JSON file (default: capture current state)"
    )
    action_parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum time for live capture in seconds (default: 30)",
    )
    add_common_args(action_parser)
    action_parser.set_defaults(func=action_command)

    args = parser.parse_args()

    # Setup logging based on command line arguments (if they exist)
    verbose = getattr(args, "verbose", False)
    debug = getattr(args, "debug", False)
    setup_logging(verbose=verbose, debug=debug)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
