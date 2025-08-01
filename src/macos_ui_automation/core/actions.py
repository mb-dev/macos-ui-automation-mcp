"""
UI Actions for macOS automation.

This module provides methods to perform actions on UI elements
identified through the JSONPath selector system.
"""

import logging
import time

from macos_ui_automation.bridges.factory import get_pyobjc_bridge
from macos_ui_automation.bridges.types import AXError
from macos_ui_automation.core.elements import Element
from macos_ui_automation.models.types import UIElement

from .state import SystemStateDumper

logger = logging.getLogger(__name__)


class UIActions:
    """Performs actions on UI elements using accessibility APIs."""

    def __init__(self, state_dumper: SystemStateDumper):
        """Initialize UI actions.

        Args:
            state_dumper: SystemStateDumper instance with element map for O(1) lookup
        """
        self.state_dumper = state_dumper
        self.pyobjc_bridge = get_pyobjc_bridge()

    def _resolve_ui_element_to_live_element(
        self, ui_element: UIElement
    ) -> Element | None:
        """Convert a serialized UIElement back to a live Element with AXUIElementRef.

        Args:
            ui_element: Serialized UI element from JSON/state dump

        Returns:
            Live Element instance or None if not found
        """
        if not ui_element.element_id:
            logger.error(
                "UIElement %s has no element_id for lookup",
                ui_element.title or ui_element.role,
            )
            return None

        # O(1) lookup using dumper's method
        live_element = self.state_dumper.get_element_by_id(ui_element.element_id)
        if not live_element:
            logger.error(
                "No live element found for element_id: %s", ui_element.element_id
            )

        return live_element

    # Direct element actions using accessibility APIs

    def click_element(self, element: UIElement) -> bool:
        """Click on a UI element using O(1) lookup to live element.

        Args:
            element: The UIElement from JSON/state dump

        Returns:
            True if successful, False otherwise
        """
        logger.info(
            "Clicking element '%s' (ID: %s)",
            element.title or element.role,
            element.element_id,
        )

        # Use accessibility API only - no fallback to coordinates
        if not element.clickable or "AXPress" not in element.actions:
            logger.error(
                "Element '%s' is not clickable or missing AXPress action (actions: %s)",
                element.title or element.role,
                element.actions,
            )
            return False

        logger.info("Using accessibility API click")

        # O(1) lookup to get live element
        live_element = self._resolve_ui_element_to_live_element(element)
        if not live_element:
            logger.error("Failed to resolve element to live element")
            return False

        # Use bridge to perform action on live element
        result = self.pyobjc_bridge.perform_action(
            live_element.ax_element_ref, "AXPress"
        )

        if result == AXError.SUCCESS:
            logger.info("Successfully clicked element via accessibility API")
            return True

        logger.error("Failed to click element via accessibility API: %s", result)
        return False

    def set_element_value(self, element: UIElement, value: str) -> bool:
        """Set value of a UI element (like text field).

        Args:
            element: The UI element to set value on
            value: The value to set

        Returns:
            True if successful, False otherwise
        """
        logger.info(
            "Setting value '%s' on element: %s",
            value,
            element.title or element.role,
        )

        # Check element capabilities upfront and choose strategy
        if element.element_id:
            # Strategy 1: Use accessibility API if we have element ID for lookup
            logger.info("Using accessibility API approach")
            live_element = self._resolve_ui_element_to_live_element(element)
            if not live_element:
                logger.error(
                    "Cannot set value: no live element found for accessibility API"
                )
                return False

            result = self.pyobjc_bridge.set_attribute_value(
                live_element.ax_element_ref, "AXValue", value
            )
            if result == AXError.SUCCESS:
                logger.info("Successfully set value via accessibility API")
                return True
            logger.error("Failed to set value via accessibility API: %s", result)
            return False

        if element.position and element.size:
            # Strategy 2: Use click + type approach if we have position data
            logger.info("Using click + type approach")
            return self._set_value_via_click_and_type(element, value)

        logger.error(
            "Cannot set value: element has neither element_id nor position data"
        )
        return False

    def _set_value_via_click_and_type(self, element: UIElement, value: str) -> bool:
        """Set value by clicking element and typing text."""
        # Click at element center to focus it
        if not element.position or not element.size:
            logger.error("Element missing position or size data for click + type")
            return False

        x = element.position.x + element.size.width // 2
        y = element.position.y + element.size.height // 2

        if not self.pyobjc_bridge.click_at_position(x, y):
            logger.error("Failed to click element for focus")
            return False

        # Small delay to ensure focus
        time.sleep(0.1)

        # Clear existing text first (Cmd+A, then type)
        # Cmd+A to select all (0x00 = 'a' key)
        if not self.pyobjc_bridge.send_key_combination(0x00, ["cmd"]):
            logger.warning("Failed to select all text")

        # Type the new value
        if not self.pyobjc_bridge.type_text(value):
            logger.error("Failed to type text")
            return False

        logger.info("Successfully set value using click + type approach")
        return True

    def get_element_value(self, element: UIElement) -> str | None:
        """Get value of a UI element.

        Args:
            element: The UI element to get value from

        Returns:
            Element value or None if failed
        """
        # Return cached value for now
        return str(element.value) if element.value is not None else None

    # Coordinate-based actions (delegated to bridge)

    def click_at_position(self, x: int, y: int) -> bool:
        """Click at specific screen coordinates (delegated to bridge)."""
        return self.pyobjc_bridge.click_at_position(x, y)

    def right_click_at_position(self, x: int, y: int) -> bool:
        """Right-click at specific screen coordinates (delegated to bridge)."""
        return self.pyobjc_bridge.right_click_at_position(x, y)

    def double_click_at_position(self, x: int, y: int) -> bool:
        """Double-click at specific screen coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful, False otherwise
        """
        # Click twice with small delay
        if self.click_at_position(x, y):
            time.sleep(0.1)
            return self.click_at_position(x, y)
        return False

    def drag_from_to(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """Drag from one position to another (delegated to bridge)."""
        return self.pyobjc_bridge.drag_between_positions(start_x, start_y, end_x, end_y)

    # Keyboard actions

    def type_text(self, text: str) -> bool:
        """Type text using keyboard events (delegated to bridge)."""
        return self.pyobjc_bridge.type_text(text)

    def send_key_combination(self, key_code: int, modifiers: list[str]) -> bool:
        """Send key combination with modifiers (delegated to bridge)."""
        return self.pyobjc_bridge.send_key_combination(key_code, modifiers)
