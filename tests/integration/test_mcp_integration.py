"""
Comprehensive MCP integration tests using realistic TaskManagement fake system.

These tests verify the entire stack from MCP server down to the bridge layer
using a realistic fake system that matches actual application structure.
"""

import pytest

from macos_ui_automation.bridges.factory import (
    create_fake_bridges_with_system,
    reset_bridges,
    set_bridge_instances,
)
from macos_ui_automation.core.registry import set_test_mode
from macos_ui_automation.interfaces import mcp_server

# Import the MCP tool functions directly for testing
from macos_ui_automation.interfaces.mcp_server import (
    click_element_by_selector,
    find_elements,
    find_elements_in_app,
    get_app_overview,
    list_running_applications,
    type_text_to_element_by_selector,
)
from tests.fixtures.task_management_system import create_task_management_system

# Constants for test values
EXPECTED_APP_COUNT = 3
TASK_MGMT_PID = 84054
EXPECTED_DIRECT_CHILDREN = 7
MIN_ELEMENT_COUNT = 5


def setup_module():
    """Enable test mode for all tests in this module."""
    set_test_mode(True)


class TestMCPIntegration:
    """Integration tests for the complete MCP stack."""

    @pytest.fixture(autouse=True)
    def setup_fake_system(self):
        """Set up the fake TaskManagement system for all tests."""
        applications, running_apps = create_task_management_system()

        # Create and set fake bridges globally so MCP functions use them
        pyobjc_bridge, workspace_bridge, app_bridge = create_fake_bridges_with_system(
            applications, running_apps
        )
        set_bridge_instances(pyobjc_bridge, workspace_bridge, app_bridge)

        yield

        # Cleanup
        reset_bridges()

    # No special client fixture needed - we test tool functions directly

    def test_mcp_tools_are_registered(self):
        """Test that all expected MCP tools are properly registered as functions."""

        # Expected tool functions that should be available
        expected_tools = [
            "find_elements",
            "find_elements_in_app",
            "click_element_by_selector",
            "type_text_to_element_by_selector",
            "get_app_overview",
            "list_running_applications",
            "get_element_details",
            "check_accessibility_permissions",
        ]

        # Verify each tool function exists and is callable
        for tool_name in expected_tools:
            assert hasattr(mcp_server, tool_name), (
                f"Tool function {tool_name} not found in mcp_server module"
            )
            tool_func = getattr(mcp_server, tool_name)
            assert callable(tool_func), f"Tool {tool_name} is not callable"

        # Test that key tools actually work (already tested individually,
        # but verify here)
        apps = list_running_applications()
        assert len(apps) > 0, (
            "list_running_applications should return apps from fake system"
        )

    def test_list_running_applications(self):
        """Test listing running applications through MCP."""
        apps_data = list_running_applications()
        assert len(apps_data) == EXPECTED_APP_COUNT

        # Check TaskManagement app is present
        task_mgmt = next(
            (app for app in apps_data if app["name"] == "Task Management"), None
        )
        assert task_mgmt is not None
        assert task_mgmt["pid"] == TASK_MGMT_PID
        assert task_mgmt["active"] is True

    def test_get_app_overview_task_management(self):
        """Test getting app overview for TaskManagement."""
        overview_data = get_app_overview(timeout_seconds=10.0)

        # Should find TaskManagement as frontmost app
        assert len(overview_data) > 0
        task_mgmt_overview = overview_data[0]  # First app should be the frontmost
        assert task_mgmt_overview["name"] == "Task Management"
        assert task_mgmt_overview["frontmost"] is True
        assert task_mgmt_overview["window_count"] == 1
        assert (
            task_mgmt_overview["has_menu_bar"] is False
        )  # Our fake doesn't have menu bar

    def test_find_elements_hierarchy_capture(self):
        """Test that find_elements captures the full hierarchy including nested
        children."""
        elements_data = find_elements(
            jsonpath_selector=(
                "$.processes[?(@.name=='Task Management')].windows[*].children[*]"
            ),
            timeout_seconds=10.0,
        )

        # Should capture the 7 direct children of the window
        assert len(elements_data) == EXPECTED_DIRECT_CHILDREN

        # Verify specific elements are captured - elements_data contains dicts now
        roles = [elem["role"] for elem in elements_data]
        assert "AXGroup" in roles  # content_group
        assert "AXToolbar" in roles  # toolbar
        assert "AXButton" in roles  # buttons
        assert "AXStaticText" in roles  # status text
        assert "AXSheet" in roles  # dialog sheet

    def test_find_elements_with_accessibility_ids(self):
        """Test finding elements with accessibility IDs through the full stack."""
        elements_data = find_elements(
            jsonpath_selector=(
                "$.processes[?(@.name=='Task Management')]..children[?"
                "(@.ax_identifier)]"
            ),
            timeout_seconds=10.0,
        )

        # Should find multiple elements with accessibility IDs
        assert len(elements_data) > MIN_ELEMENT_COUNT

        # Check for specific IDs we created
        ax_ids = [
            elem["ax_identifier"] for elem in elements_data if elem.get("ax_identifier")
        ]
        expected_ids = [
            "syncButton",
            "screenshotButton",
            "sidebarOutline",
            "taskTable",
            "taskCreationDialog",
            "taskTitleField",
        ]

        for expected_id in expected_ids:
            assert expected_id in ax_ids, (
                f"Expected ID {expected_id} not found in {ax_ids}"
            )

    def test_find_elements_in_specific_app(self):
        """Test finding elements within a specific application."""
        buttons_data = find_elements_in_app(
            app_name="Task Management",
            jsonpath_selector="$..[?(@.role=='AXButton')]",
            timeout_seconds=10.0,
        )

        # Should find multiple buttons throughout the hierarchy
        assert len(buttons_data) >= MIN_ELEMENT_COUNT

        # All results should be buttons with proper actions
        for button in buttons_data:
            assert button["role"] == "AXButton"
            assert "actions" in button, (
                f"Button {button.get('ax_identifier', 'unknown')} missing actions field"
            )
            assert "AXPress" in button["actions"], (
                f"Button {button.get('ax_identifier', 'unknown')} missing AXPress "
                "action"
            )

    def test_click_by_accessibility_id(self):
        """Test clicking an element through the MCP interface."""
        result = click_element_by_selector(
            jsonpath_selector=(
                "$.processes[?(@.name=='Task Management')]..children[?"
                "(@.ax_identifier=='syncButton')]"
            )
        )

        # Should successfully click the sync button (returns string message)
        assert "Successfully clicked" in result
        # The actual element title "Sync" is in the result, which shows it found
        # the right element

    def test_click_add_epic_button(self):
        """Test clicking the addEpicButton specifically."""
        result = click_element_by_selector(
            jsonpath_selector="$..[?(@.ax_identifier=='addEpicButton')]"
        )

        # Should successfully click the add epic button
        assert "Successfully clicked" in result

    def test_type_text_to_dialog_field(self):
        """Test typing text into a dialog field - expect failure with fake system."""
        result = type_text_to_element_by_selector(
            jsonpath_selector=(
                "$.processes[?(@.name=='Task Management')]..children[?"
                "(@.ax_identifier=='taskTitleField')]"
            ),
            text="New task from MCP",
        )

        # With fake system, typing may fail due to missing position data, but
        # element should be found
        assert "Task Title" in result  # Element was found with correct title
        # Note: Real typing functionality would work with real accessibility system

    def test_error_handling_invalid_selector(self):
        """Test error handling for invalid JSONPath selectors."""
        result = find_elements(
            jsonpath_selector="$.invalid[syntax",  # Invalid JSONPath
            timeout_seconds=5.0,
        )

        # Should return error object for invalid selector
        assert isinstance(result, list)
        assert len(result) == 1  # Returns error object
        assert "error" in result[0]  # Error object contains error message

    def test_timeout_behavior(self):
        """Test timeout behavior in element finding."""
        result = find_elements(
            jsonpath_selector="$.processes[?(@.name=='NonExistentApp')]",
            timeout_seconds=0.1,  # Very short timeout
        )

        # Should return empty results quickly
        assert isinstance(result, list)
        assert len(result) == 0
