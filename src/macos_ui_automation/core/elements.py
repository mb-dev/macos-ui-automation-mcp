"""
Core UI automation elements using bridge abstraction.

This module provides clean element wrappers that use the bridge layer
for both real and fake implementations.
"""

import logging
import re
from enum import Enum
from typing import Any

from macos_ui_automation.bridges import (
    ApplicationBridge,
    AXError,
    PyObjCBridge,
    WorkspaceBridge,
    get_application_bridge,
    get_pyobjc_bridge,
    get_workspace_bridge,
)
from macos_ui_automation.models.types import Position, Size

logger = logging.getLogger(__name__)


class AttributeConstants(Enum):
    """Accessibility attribute constants."""

    TITLE = "title"
    ROLE = "role"
    VALUE = "value"
    DESCRIPTION = "description"
    POSITION = "position"
    SIZE = "size"
    ENABLED = "enabled"
    FOCUSED = "focused"
    CHILDREN = "children"
    WINDOWS = "windows"
    MAIN_WINDOW = "main_window"
    MINIMIZED = "minimized"
    IDENTIFIER = "identifier"
    MENU_BAR = "menu_bar"
    SELECTED = "selected"
    HELP = "help"
    URL = "url"
    TOP_LEVEL_UI_ELEMENT = "top_level_ui_element"
    PARENT = "parent"


class Element:
    """UI element wrapper using bridge abstraction."""

    def __init__(self, ax_element_ref: Any, bridge: PyObjCBridge | None = None):
        self.ax_element_ref = ax_element_ref
        self._bridge = bridge if bridge is not None else get_pyobjc_bridge()
        self._attribute_map = self._build_attribute_map()

    def _build_attribute_map(self) -> dict[str, str]:
        """Build mapping from our constants to system constants."""
        return {
            AttributeConstants.TITLE.value: "AXTitle",
            AttributeConstants.ROLE.value: "AXRole",
            AttributeConstants.VALUE.value: "AXValue",
            AttributeConstants.DESCRIPTION.value: "AXDescription",
            AttributeConstants.POSITION.value: "AXPosition",
            AttributeConstants.SIZE.value: "AXSize",
            AttributeConstants.ENABLED.value: "AXEnabled",
            AttributeConstants.FOCUSED.value: "AXFocused",
            AttributeConstants.CHILDREN.value: "AXChildren",
            AttributeConstants.WINDOWS.value: "AXWindows",
            AttributeConstants.MAIN_WINDOW.value: "AXMainWindow",
            AttributeConstants.MINIMIZED.value: "AXMinimized",
            AttributeConstants.IDENTIFIER.value: "AXIdentifier",
            AttributeConstants.MENU_BAR.value: "AXMenuBar",
            AttributeConstants.SELECTED.value: "AXSelected",
            AttributeConstants.HELP.value: "AXHelp",
            AttributeConstants.URL.value: "AXURL",
            AttributeConstants.TOP_LEVEL_UI_ELEMENT.value: "AXTopLevelUIElement",
            AttributeConstants.PARENT.value: "AXParent",
            # Add AXExtrasMenuBar mapping
            "AXExtrasMenuBar": "AXExtrasMenuBar",
        }

    def _is_ax_value_object(self, value: Any) -> bool:
        """Check if value is an AXValue object."""
        return (
            value is not None
            and hasattr(value, "__class__")
            and "AXValue" in str(type(value))
        )

    def _is_ax_ui_element(self, value: Any) -> bool:
        """Check if value is an AXUIElement object."""
        return (
            value is not None
            and hasattr(value, "__class__")
            and "AXUIElement" in str(type(value))
        )

    def get_attribute_value(self, attribute: str) -> Any:
        """Get an attribute value from the element."""
        # Convert our attribute constant to system constant
        system_attribute = self._attribute_map.get(attribute, attribute)
        error, value = self._bridge.copy_attribute_value(
            self.ax_element_ref, system_attribute
        )

        if error == AXError.SUCCESS:
            # Handle AXValue objects (position, size, frame)
            if self._is_ax_value_object(value):
                value_str = str(value)
                if "AXValue" in value_str:
                    # Extract position (x, y)
                    if "kAXValueCGPointType" in value_str:
                        # Pattern for format: {value = x:652.000000 y:-77.000000
                        # type = kAXValueCGPointType}
                        match = re.search(r"x:(-?\d+\.?\d*) y:(-?\d+\.?\d*)", value_str)
                        if match:
                            x, y = map(float, match.groups())
                            # Return a dict that matches Pydantic Position model
                            return Position(x=int(x), y=int(y))

                    # Extract size (width, height)
                    elif "kAXValueCGSizeType" in value_str:
                        # Pattern for format similar to position
                        match = re.search(r"w:(-?\d+\.?\d*) h:(-?\d+\.?\d*)", value_str)
                        if match:
                            w, h = map(float, match.groups())
                            # Return a dict that matches Pydantic Size model
                            return Size(width=int(w), height=int(h))

                    # Extract rect (x, y, width, height)
                    elif "kAXValueCGRectType" in value_str:
                        match = re.search(
                            r"x:(-?\d+\.?\d*) y:(-?\d+\.?\d*) w:(-?\d+\.?\d*) "
                            r"h:(-?\d+\.?\d*)",
                            value_str,
                        )
                        if match:
                            x, y, w, h = map(float, match.groups())
                            # Return a dict that matches Pydantic models
                            return {
                                "origin": Position(x=int(x), y=int(y)),
                                "size": Size(width=int(w), height=int(h)),
                            }

            # Handle AXUIElement objects
            if self._is_ax_ui_element(value):
                return Element(value, self._bridge)
            if (
                value
                and hasattr(value, "__iter__")
                and hasattr(value, "__len__")
                and len(value) > 0
            ):
                # Check if it's a list/array of AXUIElementRefs
                # (handles both Python lists and NSArray)
                first_elem = value[0]
                if self._is_ax_ui_element(first_elem):
                    return [Element(elem, self._bridge) for elem in value]
            return value
        return None

    def get_attribute_names(self) -> list[str]:
        """Get all available attribute names."""
        error, attributes = self._bridge.copy_attribute_names(self.ax_element_ref)
        if error == AXError.SUCCESS and attributes:
            return attributes
        return []

    def get_actions(self) -> list[str]:
        """Get available actions for the element."""
        error, actions = self._bridge.copy_action_names(self.ax_element_ref)
        if error == AXError.SUCCESS and actions:
            return actions
        return []

    def set_attribute_value(self, attribute: str, value: Any) -> bool:
        """Set an attribute value on the element."""
        try:
            # Convert our attribute constant to system constant
            system_attribute = self._attribute_map.get(attribute, attribute)

            # Special handling for setting text values
            if system_attribute == "kAXValueAttribute" and isinstance(value, str):
                logger.debug("Setting text value: '%s' on element", value)

                # First try to set the value directly
                error = self._bridge.set_attribute_value(
                    self.ax_element_ref, system_attribute, value
                )

                # Check if the operation was successful
                if error != AXError.SUCCESS:
                    logger.warning("set_attribute_value returned error: %s", error)
                    return False

                # For text fields, we may also need to perform an AXConfirm action
                # to ensure the change is recognized by the application
                # Get available actions
                error, actions = self._bridge.copy_action_names(self.ax_element_ref)
                if error == AXError.SUCCESS and actions and "AXConfirm" in actions:
                    logger.debug("Performing AXConfirm action to finalize text input")
                    self._bridge.perform_action(self.ax_element_ref, "AXConfirm")

                return True
            # For non-text attributes, use the standard approach
            error = self._bridge.set_attribute_value(
                self.ax_element_ref, system_attribute, value
            )
            if error != AXError.SUCCESS:
                logger.error("set_attribute_value failed with error: %s", error)
                return False
            return True

        except Exception:
            logger.exception("Failed to set attribute %s", attribute)
            return False

    def perform_action(self, action: str) -> bool:
        """Perform an action on the element."""
        try:
            error = self._bridge.perform_action(self.ax_element_ref, action)
            if error != AXError.SUCCESS:
                logger.error("perform_action failed with error: %s", error)
                return False
            return True
        except Exception:
            logger.exception("Failed to perform action %s", action)
            return False


class Application:
    """Application wrapper using bridge abstraction."""

    def __init__(self, ns_app: Any, bridge: ApplicationBridge | None = None):
        self.ns_app = ns_app
        self._bridge = bridge if bridge is not None else get_application_bridge()

    def get_name(self) -> str:
        return self._bridge.get_localized_name(self.ns_app)

    def get_pid(self) -> int:
        return self._bridge.get_process_identifier(self.ns_app)

    def get_bundle_id(self) -> str | None:
        return self._bridge.get_bundle_identifier(self.ns_app)

    def is_active(self) -> bool:
        return self._bridge.is_active(self.ns_app)

    def is_hidden(self) -> bool:
        return self._bridge.is_hidden(self.ns_app)


class Workspace:
    """Workspace provider using bridge abstraction."""

    def __init__(
        self,
        workspace_bridge: WorkspaceBridge | None = None,
        application_bridge: ApplicationBridge | None = None,
    ):
        self._workspace_bridge = (
            workspace_bridge if workspace_bridge is not None else get_workspace_bridge()
        )
        self._application_bridge = (
            application_bridge
            if application_bridge is not None
            else get_application_bridge()
        )
        self._pyobjc_bridge = get_pyobjc_bridge()

    def get_running_applications(self) -> list[Application]:
        """Get all running applications."""
        try:
            ns_apps = self._workspace_bridge.get_running_applications()
            return [Application(app, self._application_bridge) for app in ns_apps]
        except Exception:
            logger.exception("Failed to get running applications")
            return []

    def is_accessibility_trusted(self) -> bool:
        """Check if accessibility permissions are granted."""
        try:
            return self._pyobjc_bridge.is_process_trusted()
        except Exception:
            logger.exception("Failed to check accessibility trust")
            return False


class AccessibilityProvider:
    """Accessibility provider using bridge abstraction."""

    def __init__(self, bridge: PyObjCBridge | None = None):
        self._bridge = bridge if bridge is not None else get_pyobjc_bridge()

    def create_application_element(self, pid: int) -> Element | None:
        """Create accessibility element for application."""
        try:
            ax_element_ref = self._bridge.create_application(pid)
            return Element(ax_element_ref, self._bridge)
        except Exception:
            logger.exception("Failed to create application element for PID %s", pid)
            return None

    def get_attribute_value(self, element: Element, attribute: str) -> Any:
        """Get attribute value from element."""
        return element.get_attribute_value(attribute)

    def get_attribute_names(self, element: Element) -> list[str]:
        """Get all attribute names for element."""
        return element.get_attribute_names()

    def get_actions(self, element: Element) -> list[str]:
        """Get available actions for element."""
        return element.get_actions()

    def set_attribute_value(self, element: Element, attribute: str, value: Any) -> bool:
        """Set attribute value on element."""
        return element.set_attribute_value(attribute, value)

    def perform_action(self, element: Element, action: str) -> bool:
        """Perform action on element."""
        return element.perform_action(action)


class System:
    """Main system class for UI automation."""

    def __init__(self, *, use_fake: bool = False) -> None:
        # Get bridge instances
        if use_fake:
            # Import here to avoid circular imports
            from macos_ui_automation.bridges.factory import create_pyobjc_bridge

            pyobjc_bridge, workspace_bridge, application_bridge = create_pyobjc_bridge(
                force_fake=True
            )
            self._workspace = Workspace(workspace_bridge, application_bridge)
            self._accessibility = AccessibilityProvider(pyobjc_bridge)
        else:
            # Use default bridges from factory
            self._workspace = Workspace()
            self._accessibility = AccessibilityProvider()

    def get_workspace(self) -> Workspace:
        """Get workspace provider."""
        return self._workspace

    def get_accessibility(self) -> AccessibilityProvider:
        """Get accessibility provider."""
        return self._accessibility

    def is_available(self) -> bool:
        """Check if the accessibility system is available."""
        return True  # If we can create the system, we're available
