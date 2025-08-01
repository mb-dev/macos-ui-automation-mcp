"""
Simplified MCP server for macOS UI automation without context dependencies.
This version works immediately with Claude Code.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from typing import Any

from mcp.server.fastmcp import FastMCP

from macos_ui_automation.bridges.factory import (
    get_application_bridge,
    get_pyobjc_bridge,
    get_workspace_bridge,
)
from macos_ui_automation.core.actions import UIActions
from macos_ui_automation.core.state import SystemStateDumper
from macos_ui_automation.models.types import (
    ApplicationInfo,
    ErrorResponse,
    SearchResult,
)
from macos_ui_automation.selectors.jsonpath import JSONPathSelector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SEARCH_TIMEOUT = 10.0
APP_SPECIFIC_TIMEOUT = 15.0
QUICK_OVERVIEW_TIMEOUT = 5.0
DEEP_SEARCH_TIMEOUT = 20.0
STATE_COLLECTION_TIMEOUT = 5.0
OVERVIEW_TIMEOUT = 5.0
PERMISSION_CHECK_TIMEOUT = 5.0
MAX_WINDOWS_IN_OVERVIEW = 3

# Create MCP server
mcp = FastMCP("macOS UI Automation Server")


# Resources - Data that can be retrieved
@mcp.resource("ui://state/current")
def get_current_ui_state() -> str:
    """Get current UI overview for all running applications (shallow depth)."""
    try:
        # Shallow depth for overview - just show apps, windows, main elements
        dumper = SystemStateDumper(
            timeout_seconds=DEFAULT_SEARCH_TIMEOUT, only_visible_children=True
        )
        state = dumper.dump_system_state()
        return state.model_dump_json(indent=2)
    except Exception as e:
        logger.exception("Failed to get UI state: %s")
        return json.dumps({"error": str(e), "state": "unavailable"})


@mcp.resource("ui://state/process/{process_name}")
def get_process_ui_state(process_name: str) -> str:
    """Get deep UI state for a specific process/application."""
    try:
        # Deep depth for specific app - capture all nested elements for searching
        dumper = SystemStateDumper(
            timeout_seconds=APP_SPECIFIC_TIMEOUT, only_visible_children=True
        )
        state = dumper.dump_system_state(include_processes=[process_name])

        if not state.processes:
            return json.dumps(
                {"error": f"Process '{process_name}' not found", "processes": []}
            )

        return state.model_dump_json(indent=2)
    except Exception as e:
        logger.exception("Failed to get process state for %s", process_name)
        return json.dumps({"error": str(e), "process": process_name})


# Tools - Actions that can be performed
@mcp.tool()
def click_element_by_selector(jsonpath_selector: str) -> str:
    """Click a UI element using accessibility actions (AXPress) via JSONPath selector.

    Args:
        jsonpath_selector: JSONPath expression to find the element
                          (e.g., "$..[?(@.ax_identifier=='addEpicButton')]")

    Returns:
        Success message or error description
    """
    try:
        logger.info("Attempting to click element: %s", jsonpath_selector)

        # Get current UI state with timeout for click operations
        dumper = SystemStateDumper(
            timeout_seconds=DEFAULT_SEARCH_TIMEOUT, only_visible_children=True
        )
        state = dumper.dump_system_state_with_timeout(STATE_COLLECTION_TIMEOUT)

        # Find element using selector - use the existing find_elements method
        selector = JSONPathSelector(state)
        logger.info("About to call find_elements with selector: %s", jsonpath_selector)
        elements = selector.find_elements(jsonpath_selector)
        logger.info("Successfully found %d elements", len(elements))

        if not elements:
            logger.warning("No elements found matching selector: %s", jsonpath_selector)
            return f"No elements found matching selector: {jsonpath_selector}"

        if len(elements) > 1:
            logger.warning(
                "Multiple elements found (%d), clicking first one", len(elements)
            )

        element = elements[0]

        # Use proper accessibility-based clicking via UIActions
        logger.info(
            "Using accessibility-based click for element: %s",
            element.ax_identifier or element.title or element.role,
        )

        ui_actions = UIActions(dumper)
        success = ui_actions.click_element(element)

        if success:
            logger.info(
                "Successfully clicked element: %s", element.title or element.role
            )
            return f"Successfully clicked element: {element.title or element.role}"
        logger.error("Failed to click element: %s", element.title or element.role)
        return f"Failed to click element: {element.title or element.role}"

    except Exception as e:
        logger.exception("Click failed: %s")
        return f"Error clicking element: {e!s}"


@mcp.tool()
def click_at_position(x: int, y: int) -> str:
    """Click at a specific screen position using coordinates.

    Args:
        x: X coordinate on screen
        y: Y coordinate on screen

    Returns:
        Success message or error description
    """
    try:
        logger.info("Attempting to click at position (%d, %d)", x, y)

        # Get a dumper instance for UIActions
        dumper = SystemStateDumper(
            timeout_seconds=STATE_COLLECTION_TIMEOUT, only_visible_children=True
        )
        ui_actions = UIActions(dumper)

        success = ui_actions.click_at_position(x, y)

        if success:
            logger.info("Successfully clicked at position (%d, %d)", x, y)
            return f"Successfully clicked at position ({x}, {y})"
        logger.error("Failed to click at position (%d, %d)", x, y)
        return f"Failed to click at position ({x}, {y})"

    except Exception as e:
        logger.exception("Error clicking at position")
        return f"Error clicking at position: {e}"


@mcp.tool()
def type_text_to_element_by_selector(jsonpath_selector: str, text: str) -> str:
    """Type text into a UI element using JSONPath selector.

    Args:
        jsonpath_selector: JSONPath expression to find the element
        text: Text to type into the element

    Returns:
        Success message or error description
    """
    try:
        logger.info("Attempting to type into element: %s", jsonpath_selector)

        # Get current UI state with timeout for type operations
        dumper = SystemStateDumper(
            timeout_seconds=DEFAULT_SEARCH_TIMEOUT, only_visible_children=True
        )
        state = dumper.dump_system_state_with_timeout(STATE_COLLECTION_TIMEOUT)

        # Find element using selector - use the existing find_elements method
        selector = JSONPathSelector(state)
        elements = selector.find_elements(jsonpath_selector)

        if not elements:
            logger.warning("No elements found matching selector: %s", jsonpath_selector)
            return f"No elements found matching selector: {jsonpath_selector}"

        if len(elements) > 1:
            logger.warning(
                "Multiple elements found (%d), typing into first one", len(elements)
            )

        element = elements[0]

        # Create UI actions instance and perform type action
        ui_actions = UIActions(dumper)
        success = ui_actions.set_element_value(element, text)

        if success:
            logger.info(
                "Successfully typed text into element: %s",
                element.title or element.role,
            )
            return (
                f"Successfully typed '{text}' into element: "
                f"{element.title or element.role}"
            )
        logger.error(
            "Failed to type text into element: %s", element.title or element.role
        )
        return f"Failed to type text into element: {element.title or element.role}"

    except Exception as e:
        logger.exception("Type text failed: %s")
        return f"Error typing text: {e!s}"


@mcp.tool()
def find_elements(
    jsonpath_selector: str, timeout_seconds: float = DEFAULT_SEARCH_TIMEOUT
) -> list[dict[str, Any]]:
    """Find UI elements matching a JSONPath selector.

    Args:
        jsonpath_selector: JSONPath expression to find elements
        timeout_seconds: Maximum time to spend searching (default: 10 seconds)

    Returns:
        List of matching elements with their properties
    """
    try:
        logger.info(
            "Finding elements with selector: %s (timeout: %.1fs)",
            jsonpath_selector,
            timeout_seconds,
        )
        start_time = time.time()

        # Get current UI state with time-aware dumper
        # Use longer timeout for app-specific searches since they need to
        # traverse deeper
        if any(
            pattern in jsonpath_selector.lower()
            for pattern in [".processes[", "name==", "bundle_id=="]
        ):
            # App-specific search - use longer timeout for deep traversal
            search_timeout = min(timeout_seconds - 1.0, DEEP_SEARCH_TIMEOUT)
            logger.info(
                "Using extended timeout (%.1fs) for app-specific selector",
                search_timeout,
            )
        else:
            # General search - use moderate timeout
            search_timeout = min(timeout_seconds - 1.0, DEFAULT_SEARCH_TIMEOUT)
            logger.info(
                "Using moderate timeout (%.1fs) for general selector", search_timeout
            )

        dumper = SystemStateDumper(
            timeout_seconds=search_timeout, only_visible_children=True
        )
        state = dumper.dump_system_state_with_timeout(
            search_timeout
        )  # Time already reserved above

        # Check if we've already exceeded timeout
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            logger.warning("Search timed out during state dump (%.2fs)", elapsed)
            error_response = ErrorResponse(
                error=(f"Search timed out during state collection ({elapsed:.2f}s)"),
                timeout=True,
            )
            return [error_response.model_dump()]

        # Find elements using selector - use raw find method for better results
        selector = JSONPathSelector(state)
        raw_results = selector.find(jsonpath_selector)

        elapsed = time.time() - start_time
        logger.info(
            "Found %d raw results matching selector in %.2fs", len(raw_results), elapsed
        )

        # Convert raw results to Pydantic models then to dicts
        result = []
        for raw_element in raw_results:
            # Check timeout during processing
            if time.time() - start_time >= timeout_seconds:
                logger.warning("Search timed out during result processing")
                error_response = ErrorResponse(
                    error="Search timed out, results may be incomplete", timeout=True
                )
                result.append(error_response.model_dump())
                break

            if isinstance(raw_element, dict):
                # Handle UI elements (have role) vs other objects
                # (processes, windows, etc.)
                if "role" in raw_element:
                    # This is a UI element, use SearchResult
                    search_result = SearchResult.from_dict(raw_element)
                    result.append(search_result.model_dump())
                else:
                    # This is a process, window, or other object - return as-is
                    result.append(raw_element)

        final_elapsed = time.time() - start_time
        logger.info(
            "Converted %d valid UI elements in total time %.2fs",
            len(result),
            final_elapsed,
        )
        return result

    except Exception as e:
        logger.exception("Find elements failed: %s")
        error_response = ErrorResponse(error=str(e), timeout=False)
        return [error_response.model_dump()]


@mcp.tool()
def get_element_details(jsonpath_selector: str) -> dict[str, Any]:
    """Get detailed information about a specific UI element.

    Args:
        jsonpath_selector: JSONPath expression to find the element

    Returns:
        Detailed element properties including children
    """
    try:
        logger.info("Getting element details for: %s", jsonpath_selector)

        # Get current UI state with timeout for detail operations
        dumper = SystemStateDumper(
            timeout_seconds=DEFAULT_SEARCH_TIMEOUT, only_visible_children=True
        )
        state = dumper.dump_system_state_with_timeout(STATE_COLLECTION_TIMEOUT)

        # Find element using selector - use the existing find_elements method
        selector = JSONPathSelector(state)
        elements = selector.find_elements(jsonpath_selector)

        if not elements:
            logger.warning("No elements found matching selector: %s", jsonpath_selector)
            return {
                "error": f"No elements found matching selector: {jsonpath_selector}"
            }

        if len(elements) > 1:
            logger.warning(
                "Multiple elements found (%d), returning first one", len(elements)
            )

        element = elements[0]

        # Return complete element data
        result = element.model_dump()
        logger.info("Retrieved details for element: %s", element.title or element.role)

        return result

    except Exception as e:
        logger.exception("Get element details failed: %s")
        return {"error": str(e)}


@mcp.tool()
def list_running_applications() -> list[dict[str, Any]]:
    """List all currently running applications with basic info.

    Returns:
        List of running applications with name, PID, and bundle ID
    """
    try:
        logger.info("Listing running applications")

        workspace_bridge = get_workspace_bridge()
        app_bridge = get_application_bridge()
        running_apps = workspace_bridge.get_running_applications()

        result = []
        for app in running_apps:
            app_info = ApplicationInfo(
                name=app_bridge.get_localized_name(app),
                pid=app_bridge.get_process_identifier(app),
                bundle_id=app_bridge.get_bundle_identifier(app),
                active=app_bridge.is_active(app),
                hidden=app_bridge.is_hidden(app),
            )
            result.append(app_info.model_dump())

        logger.info("Found %s running applications", len(result))
        return result

    except Exception as e:
        logger.exception("List applications failed: %s")
        error_response = ErrorResponse(error=str(e), timeout=False)
        return [error_response.model_dump()]


@mcp.tool()
def find_elements_in_app(
    app_name: str,
    jsonpath_selector: str = "$..[?(@.ax_identifier)]",
    timeout_seconds: float = APP_SPECIFIC_TIMEOUT,
) -> list[dict[str, Any]]:
    """Find UI elements within a specific application using deep search.

    Args:
        app_name: Name of the application to search within
        jsonpath_selector: JSONPath expression to find elements
            (default: all elements with identifiers)
        timeout_seconds: Maximum time to spend searching (default: 15 seconds)

    Returns:
        List of matching elements with their properties
    """
    try:
        logger.info(
            "Finding elements in app '%s' with selector: %s (timeout: %.1fs)",
            app_name,
            jsonpath_selector,
            timeout_seconds,
        )
        start_time = time.time()

        # Use extended timeout for deep app-specific searches
        search_timeout = min(timeout_seconds - 1.0, DEEP_SEARCH_TIMEOUT)
        logger.info(
            "Using extended timeout (%.1fs) for app-specific search", search_timeout
        )

        # Get current UI state with time-aware dumper, filtering to specific app
        dumper = SystemStateDumper(
            timeout_seconds=search_timeout, only_visible_children=True
        )
        state = dumper.dump_system_state_with_timeout(
            search_timeout,  # Time already reserved above
            include_processes=[app_name],
        )

        # Check if we've already exceeded timeout
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            logger.warning("Search timed out during state dump (%.2fs)", elapsed)
            return [
                {
                    "error": (
                        f"Search timed out during state collection ({elapsed:.2f}s)"
                    ),
                    "timeout": True,
                }
            ]

        # Find elements using selector
        selector = JSONPathSelector(state)
        raw_results = selector.find(jsonpath_selector)

        elapsed = time.time() - start_time
        logger.info(
            "Found %d raw results in app '%s' in %.2fs",
            len(raw_results),
            app_name,
            elapsed,
        )

        # Convert raw results to simplified dict format
        result = []
        for raw_element in raw_results:
            # Check timeout during processing
            if time.time() - start_time >= timeout_seconds:
                logger.warning("Search timed out during result processing")
                result.append(
                    {
                        "warning": "Search timed out, results may be incomplete",
                        "timeout": True,
                    }
                )
                break

            if isinstance(raw_element, dict) and "role" in raw_element:
                element_dict = {
                    "role": raw_element.get("role"),
                    "title": raw_element.get("title"),
                    "value": raw_element.get("value"),
                    "enabled": raw_element.get("enabled"),
                    "focused": raw_element.get("focused"),
                    "position": raw_element.get("position"),
                    "size": raw_element.get("size"),
                    "description": raw_element.get("description"),
                    "ax_identifier": raw_element.get("ax_identifier"),
                    "actions": raw_element.get("actions", []),
                }
                result.append(element_dict)

        final_elapsed = time.time() - start_time
        logger.info(
            "Converted %d valid UI elements from app '%s' in total time %.2fs",
            len(result),
            app_name,
            final_elapsed,
        )
        return result

    except Exception as e:
        logger.exception("Find elements in app failed: %s")
        return [{"error": str(e)}]


@mcp.tool()
def get_app_overview(
    timeout_seconds: float = QUICK_OVERVIEW_TIMEOUT,
) -> list[dict[str, Any]]:
    """Get a quick overview of all running applications with shallow UI inspection.

    Args:
        timeout_seconds: Maximum time to spend getting overview (default: 5 seconds)

    Returns:
        List of applications with basic window and UI information
    """
    try:
        logger.info("Getting app overview (timeout: %ss)", timeout_seconds)
        start_time = time.time()

        # Use short timeout for quick overview
        overview_timeout = min(timeout_seconds - 0.5, OVERVIEW_TIMEOUT)
        logger.info("Using short timeout (%ss) for app overview", overview_timeout)

        # Get current UI state with time-aware dumper
        dumper = SystemStateDumper(
            timeout_seconds=overview_timeout, only_visible_children=True
        )
        state = dumper.dump_system_state_with_timeout(
            overview_timeout
        )  # Time already reserved above

        # Check if we've already exceeded timeout
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            logger.warning("Overview timed out during state dump (%.2fs)", elapsed)
            return [
                {
                    "error": (
                        f"Overview timed out during state collection ({elapsed:.2f}s)"
                    ),
                    "timeout": True,
                }
            ]

        # Extract app overview information
        result = []
        for process in state.processes:
            app_info: dict[str, Any] = {
                "name": process.name,
                "pid": process.pid,
                "bundle_id": process.bundle_id,
                "frontmost": process.frontmost,
                "hidden": process.hidden,
                "window_count": len(process.windows),
                "has_menu_bar": len(process.menu_bar) > 0,
                "windows": [],
            }

            # Add basic window info
            for window in process.windows[:MAX_WINDOWS_IN_OVERVIEW]:
                window_info = {
                    "title": window.title,
                    "position": window.position,
                    "size": window.size,
                    "main_window": window.main_window,
                    "minimized": window.minimized,
                    "element_count": len(window.children) if window.children else 0,
                }
                app_info["windows"].append(window_info)

            result.append(app_info)

        final_elapsed = time.time() - start_time
        logger.info(
            "Generated overview for %d apps in %.2fs", len(result), final_elapsed
        )
        return result

    except Exception as e:
        logger.exception("Get app overview failed: %s")
        return [{"error": str(e)}]


@mcp.tool()
def check_accessibility_permissions() -> dict[str, Any]:
    """Check if accessibility permissions are properly configured.

    Returns:
        Status of accessibility permissions and guidance
    """
    try:
        pyobjc_bridge = get_pyobjc_bridge()
        is_trusted = pyobjc_bridge.is_process_trusted()

        result = {
            "accessibility_trusted": is_trusted,
            "status": "OK" if is_trusted else "PERMISSION_REQUIRED",
        }

        if not is_trusted:
            result["guidance"] = (
                "Accessibility permissions not granted. "
                "Please enable accessibility access in System Preferences > "
                "Security & Privacy > Privacy > Accessibility"
            )
            logger.warning("Accessibility permissions not granted")
            return result

        logger.info("Accessibility permissions are properly configured")
        return result

    except Exception as e:
        logger.exception("Permission check failed: %s")
        return {"error": str(e), "status": "ERROR"}


def main() -> None:
    """Entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="macOS UI Automation MCP Server")
    parser.add_argument(
        "--mcp-debug",
        action="store_true",
        help="Enable detailed MCP protocol debugging logs",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port for HTTP transport (default: 3000)",
    )

    args = parser.parse_args()

    if args.mcp_debug:
        # Enable debug logging for MCP and related modules
        logging.getLogger("mcp").setLevel(logging.DEBUG)
        logging.getLogger("anyio").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

        debug_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(funcName)s:%(lineno)d - %(message)s"
        )
        for handler in logging.getLogger().handlers:
            handler.setFormatter(debug_formatter)

    logger.info("Starting macOS UI Automation MCP Server (Simple)")
    logger.info("Transport: %s", args.transport)
    logger.info("MCP Debug mode: %s", args.mcp_debug)

    if args.mcp_debug:
        logger.debug("Debug logging enabled for MCP protocol interactions")

    # Run the server with specified transport
    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http")
    elif args.transport == "sse":
        mcp.run(transport="sse")


if __name__ == "__main__":
    main()
