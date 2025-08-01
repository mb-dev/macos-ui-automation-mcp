"""
JSONPath selector for querying macOS UI state.

This module provides a powerful way to select UI elements from the
system state using JSONPath expressions.
"""

import logging
from typing import Any

from jsonpath import findall

from macos_ui_automation.models.types import (
    ProcessState,
    SystemState,
    UIElement,
    WindowState,
)

logger = logging.getLogger(__name__)


class JSONPathSelector:
    """JSONPath-based selector for UI elements."""

    def __init__(self, system_state: SystemState):
        """Initialize selector with system state.

        Args:
            system_state: The system state to query
        """
        self.system_state = system_state
        self._state_dict = system_state.model_dump()

    def find(self, jsonpath: str) -> list[Any]:
        """Find elements using JSONPath expression.

        Args:
            jsonpath: JSONPath expression (e.g., "$.processes[?@.name=='Safari']")

        Returns:
            List of matching elements

        Example:
            # Find all Safari windows
            selector.find("$.processes[?@.name=='Safari'].windows[*]")

            # Find all clickable buttons
            selector.find("$.processes[*].windows[*]..children[?@.clickable==true]")

            # Find element by title
            selector.find("$.processes[*].windows[*]..children[?@.title=='Submit']")
        """
        results = findall(jsonpath, self._state_dict)
        logger.debug("JSONPath '%s' found %s results", jsonpath, len(results))
        return results

    def find_first(self, jsonpath: str) -> Any | None:
        """Find first element matching JSONPath expression.

        Args:
            jsonpath: JSONPath expression

        Returns:
            First matching element or None
        """
        results = self.find(jsonpath)
        return results[0] if results else None

    def find_elements(self, jsonpath: str) -> list[UIElement]:
        """Find UI elements and return as UIElement objects.

        Args:
            jsonpath: JSONPath expression

        Returns:
            List of UIElement objects
        """
        results = self.find(jsonpath)
        elements = []

        for result in results:
            # Convert dict result back to UIElement
            if isinstance(result, dict) and "role" in result:
                # Convert position and size dicts back to proper objects
                if result.get("position") and isinstance(result["position"], dict):
                    from macos_ui_automation.models.types import Position

                    result["position"] = Position(**result["position"])

                if result.get("size") and isinstance(result["size"], dict):
                    from macos_ui_automation.models.types import Size

                    result["size"] = Size(**result["size"])

                element = UIElement(**result)
                elements.append(element)

        return elements

    def find_processes(self, jsonpath: str) -> list[ProcessState]:
        """Find processes and return as ProcessState objects.

        Args:
            jsonpath: JSONPath expression

        Returns:
            List of ProcessState objects
        """
        results = self.find(jsonpath)
        processes = []

        for result in results:
            if isinstance(result, dict) and "name" in result and "pid" in result:
                process = ProcessState(**result)
                processes.append(process)

        return processes

    # Convenience methods for common queries

    def find_process_by_name(self, name: str) -> ProcessState | None:
        """Find process by exact name match."""
        result = self.find_first(f"$.processes[?@.name=='{name}']")
        if result:
            return ProcessState(**result)
        return None

    def find_windows_by_title(self, title: str) -> list[WindowState]:
        """Find windows by title."""
        results = self.find(f"$.processes[*].windows[?@.title=='{title}']")
        windows = []

        for result in results:
            window = WindowState(**result)
            windows.append(window)

        return windows

    def find_buttons_by_title(self, title: str) -> list[UIElement]:
        """Find buttons by title."""
        return self.find_elements(
            f"$.processes[*].windows[*]..children[?@.role=='AXButton' && @.title=='{title}']"
        )

    def find_clickable_elements(self) -> list[UIElement]:
        """Find all clickable elements."""
        return self.find_elements(
            "$.processes[*].windows[*]..children[?@.clickable==true]"
        )

    def find_text_fields(self) -> list[UIElement]:
        """Find all text fields."""
        return self.find_elements(
            "$.processes[*].windows[*]..children[?@.role=='AXTextField']"
        )

    def find_menu_items_by_title(self, title: str) -> list[UIElement]:
        """Find menu items by title."""
        return self.find_elements(
            f"$.processes[*].menu_bar[*]..children[?@.title=='{title}']"
        )

    def find_frontmost_app_windows(self) -> list[WindowState]:
        """Find windows of the frontmost application."""
        results = self.find("$.processes[?@.frontmost==true].windows[*]")
        windows = []

        for result in results:
            window = WindowState(**result)
            windows.append(window)

        return windows

    def find_by_identifier(self, identifier: str) -> list[UIElement]:
        """Find elements by AX identifier."""
        return self.find_elements(
            f"$.processes[*].windows[*]..children[?@.ax_identifier=='{identifier}']"
        )

    def find_by_role(self, role: str) -> list[UIElement]:
        """Find elements by accessibility role."""
        return self.find_elements(
            f"$.processes[*].windows[*]..children[?@.role=='{role}']"
        )

    def find_enabled_elements(self) -> list[UIElement]:
        """Find all enabled elements."""
        return self.find_elements(
            "$.processes[*].windows[*]..children[?@.enabled==true]"
        )

    def find_focused_elements(self) -> list[UIElement]:
        """Find all focused elements."""
        return self.find_elements(
            "$.processes[*].windows[*]..children[?@.focused==true]"
        )

    def find_elements_with_actions(self, action: str) -> list[UIElement]:
        """Find elements that support a specific action."""
        return self.find_elements(
            f"$.processes[*].windows[*]..children[?@.actions[*]=='{action}']"
        )

    def find_elements_by_position(
        self, min_x: int, min_y: int, max_x: int, max_y: int
    ) -> list[UIElement]:
        """Find elements within a position range."""
        return self.find_elements(
            f"$.processes[*].windows[*]..children[?"
            f"@.position.x>={min_x} && @.position.x<={max_x} && "
            f"@.position.y>={min_y} && @.position.y<={max_y}]"
        )

    def find_elements_by_size(self, min_width: int, min_height: int) -> list[UIElement]:
        """Find elements larger than specified size."""
        return self.find_elements(
            f"$.processes[*].windows[*]..children[?"
            f"@.size.width>={min_width} && @.size.height>={min_height}]"
        )

    def update_state(self, new_state: SystemState) -> None:
        """Update the system state for querying.

        Args:
            new_state: New system state
        """
        self.system_state = new_state
        self._state_dict = new_state.model_dump()
        logger.debug("System state updated for JSONPath selector")


# Convenience functions for common patterns


def create_selector(system_state: SystemState) -> JSONPathSelector:
    """Create a JSONPath selector for the given system state."""
    return JSONPathSelector(system_state)


def find_interactive_elements(system_state: SystemState) -> list[UIElement]:
    """Find all interactive elements in the system state."""
    selector = JSONPathSelector(system_state)
    return selector.find_elements(
        "$.processes[*].windows[*]..children[?@.enabled==true && (@.clickable==true || @.editable==true)]"
    )


def find_process_elements(
    system_state: SystemState, process_name: str
) -> list[UIElement]:
    """Find all UI elements for a specific process."""
    selector = JSONPathSelector(system_state)
    return selector.find_elements(
        f"$.processes[?@.name=='{process_name}'].windows[*]..children[*]"
    )


def find_main_window_elements(
    system_state: SystemState, process_name: str
) -> list[UIElement]:
    """Find elements in the main window of a specific process."""
    selector = JSONPathSelector(system_state)
    return selector.find_elements(
        f"$.processes[?@.name=='{process_name}'].windows[?@.main_window==true]..children[*]"
    )
