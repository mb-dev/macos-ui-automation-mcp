"""
Real PyObjC bridge implementation.

This module provides the actual PyObjC implementation that calls real
macOS accessibility APIs through PyObjC bindings.
"""

import logging
from typing import Any

from .interfaces import ApplicationBridge, PyObjCBridge, WorkspaceBridge
from .types import AXError, AXUIElementRef, AXValueRef

logger = logging.getLogger(__name__)

# Constants for magic values
KEY_CODE_TIMEOUT = 0
COORDINATE_NONE = 0
EVENT_SOURCE_STATE = 0
AX_MOCK_TYPE_ID = 12345
VALUE_CREATION_SUCCESS = True
PYOBJC_IMPORT_ERROR_CODE = -1


class RealPyObjCBridge(PyObjCBridge):
    """Real implementation using actual PyObjC calls."""

    def __init__(self) -> None:
        # Import PyObjC modules only when real bridge is used
        try:
            from ApplicationServices import (
                AXIsProcessTrusted,
                AXUIElementCopyActionNames,
                AXUIElementCopyAttributeNames,
                AXUIElementCopyAttributeValue,
                AXUIElementCreateApplication,
                AXUIElementPerformAction,
                AXUIElementSetAttributeValue,
                AXValueCreate,
                AXValueGetType,
                AXValueGetValue,
                kAXValueCGPointType,
                kAXValueCGRectType,
                kAXValueCGSizeType,
            )
            from Quartz import (
                CGPointMake,
                CGRectMake,
                CGSizeMake,
            )

            self._ax_is_process_trusted = AXIsProcessTrusted
            self._ax_ui_element_create_application = AXUIElementCreateApplication
            self._ax_ui_element_copy_attribute_value = AXUIElementCopyAttributeValue
            self._ax_ui_element_copy_attribute_names = AXUIElementCopyAttributeNames
            self._ax_ui_element_copy_action_names = AXUIElementCopyActionNames
            self._ax_ui_element_set_attribute_value = AXUIElementSetAttributeValue
            self._ax_ui_element_perform_action = AXUIElementPerformAction
            self._ax_value_get_type = AXValueGetType
            self._ax_value_get_value = AXValueGetValue
            self._ax_value_create = AXValueCreate
            self._cg_point_make = CGPointMake
            self._cg_size_make = CGSizeMake
            self._cg_rect_make = CGRectMake
            self._value_types = {
                "point": kAXValueCGPointType,
                "size": kAXValueCGSizeType,
                "rect": kAXValueCGRectType,
            }

        except ImportError:
            logger.exception("Failed to import PyObjC modules: %s")
            raise

    def is_process_trusted(self) -> bool:
        """Check if accessibility permissions are granted."""
        return self._ax_is_process_trusted()

    def create_application(self, pid: int) -> AXUIElementRef:
        """Create an AXUIElement reference for an application."""
        element_ref = self._ax_ui_element_create_application(pid)
        return AXUIElementRef(element_ref)

    def copy_attribute_value(
        self, element: AXUIElementRef, attribute: str
    ) -> tuple[AXError, Any | None]:
        """Copy an attribute value from an element."""
        error_code, value = self._ax_ui_element_copy_attribute_value(
            element, attribute, None
        )
        ax_error = (
            AXError(error_code)
            if error_code in [e.value for e in AXError]
            else AXError.FAILURE
        )
        return ax_error, value

    def copy_attribute_names(
        self, element: AXUIElementRef
    ) -> tuple[AXError, list[str] | None]:
        """Copy all attribute names from an element."""
        error_code, attributes = self._ax_ui_element_copy_attribute_names(element, None)
        ax_error = (
            AXError(error_code)
            if error_code in [e.value for e in AXError]
            else AXError.FAILURE
        )
        if ax_error == AXError.SUCCESS and attributes:
            return ax_error, list(attributes)
        return ax_error, None

    def copy_action_names(
        self, element: AXUIElementRef
    ) -> tuple[AXError, list[str] | None]:
        """Copy all action names from an element."""
        error_code, actions = self._ax_ui_element_copy_action_names(element, None)
        ax_error = (
            AXError(error_code)
            if error_code in [e.value for e in AXError]
            else AXError.FAILURE
        )
        if ax_error == AXError.SUCCESS and actions:
            return ax_error, list(actions)
        return ax_error, None

    def set_attribute_value(
        self, element: AXUIElementRef, attribute: str, value: Any
    ) -> AXError:
        """Set an attribute value on an element."""
        error_code = self._ax_ui_element_set_attribute_value(element, attribute, value)
        return (
            AXError(error_code)
            if error_code in [e.value for e in AXError]
            else AXError.FAILURE
        )

    def perform_action(self, element: AXUIElementRef, action: str) -> AXError:
        """Perform an action on an element."""
        logger.info(
            "REAL_BRIDGE: Calling AXUIElementPerformAction with action: %s", action
        )
        logger.info("REAL_BRIDGE: Element ref: %s", element)
        error_code = self._ax_ui_element_perform_action(element, action)
        logger.info(
            "REAL_BRIDGE: AXUIElementPerformAction returned error code: %s", error_code
        )
        ax_error = (
            AXError(error_code)
            if error_code in [e.value for e in AXError]
            else AXError.FAILURE
        )
        logger.info("REAL_BRIDGE: Converted to AXError: %s", ax_error)
        return ax_error

    def get_value_type(self, value: AXValueRef) -> int | None:
        """Get the type of an AXValue."""
        return self._ax_value_get_type(value)

    def get_value(self, value: AXValueRef, value_type: int) -> Any | None:
        """Extract the actual value from an AXValue."""
        return self._ax_value_get_value(value, value_type, None)

    def create_ax_value(self, value_type: int, value: Any) -> AXValueRef | None:
        """Create an AXValue from a value and type."""
        ax_value = self._ax_value_create(value_type, value)
        return AXValueRef(ax_value) if ax_value else None

    # Coordinate-based input operations using Quartz

    def click_at_position(self, x: int, y: int) -> bool:
        """Click at specific screen coordinates."""
        try:
            from Quartz import (
                CGEventCreateMouseEvent,
                CGEventPost,
                CGEventSourceCreate,
                kCGEventLeftMouseDown,
                kCGEventLeftMouseUp,
                kCGEventSourceStateHIDSystemState,
                kCGHIDEventTap,
            )

            event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

            # Mouse down
            down_event = CGEventCreateMouseEvent(
                event_source, kCGEventLeftMouseDown, (x, y), COORDINATE_NONE
            )

            # Mouse up
            up_event = CGEventCreateMouseEvent(
                event_source, kCGEventLeftMouseUp, (x, y), COORDINATE_NONE
            )

            # Post events
            CGEventPost(kCGHIDEventTap, down_event)
            CGEventPost(kCGHIDEventTap, up_event)

            logger.debug("Clicked at position (%s, %s)", x, y)

        except Exception:
            logger.exception("Failed to click at position (%s, %s)", x, y)
            return False

        return True

    def right_click_at_position(self, x: int, y: int) -> bool:
        """Right-click at specific screen coordinates."""
        try:
            from Quartz import (
                CGEventCreateMouseEvent,
                CGEventPost,
                CGEventSourceCreate,
                kCGEventRightMouseDown,
                kCGEventRightMouseUp,
                kCGEventSourceStateHIDSystemState,
                kCGHIDEventTap,
            )

            event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

            # Right mouse down
            down_event = CGEventCreateMouseEvent(
                event_source, kCGEventRightMouseDown, (x, y), COORDINATE_NONE
            )

            # Right mouse up
            up_event = CGEventCreateMouseEvent(
                event_source, kCGEventRightMouseUp, (x, y), COORDINATE_NONE
            )

            # Post events
            CGEventPost(kCGHIDEventTap, down_event)
            CGEventPost(kCGHIDEventTap, up_event)

            logger.debug("Right-clicked at position (%s, %s)", x, y)

        except Exception:
            logger.exception("Failed to right-click at position (%s, %s)", x, y)
            return False

        return True

    def drag_between_positions(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> bool:
        """Drag from start coordinates to end coordinates."""
        try:
            from Quartz import (
                CGEventCreateMouseEvent,
                CGEventPost,
                CGEventSourceCreate,
                kCGEventLeftMouseDown,
                kCGEventLeftMouseUp,
                kCGEventMouseMoved,
                kCGEventSourceStateHIDSystemState,
                kCGHIDEventTap,
            )

            event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

            # Mouse down at start
            down_event = CGEventCreateMouseEvent(
                event_source,
                kCGEventLeftMouseDown,
                (start_x, start_y),
                COORDINATE_NONE,
            )
            CGEventPost(kCGHIDEventTap, down_event)

            # Mouse move to end
            move_event = CGEventCreateMouseEvent(
                event_source,
                kCGEventMouseMoved,
                (end_x, end_y),
                COORDINATE_NONE,
            )
            CGEventPost(kCGHIDEventTap, move_event)

            # Mouse up at end
            up_event = CGEventCreateMouseEvent(
                event_source,
                kCGEventLeftMouseUp,
                (end_x, end_y),
                COORDINATE_NONE,
            )
            CGEventPost(kCGHIDEventTap, up_event)

            logger.debug(
                "Dragged from (%s, %s) to (%s, %s)", start_x, start_y, end_x, end_y
            )

        except Exception:
            logger.exception(
                "Failed to drag from (%d, %d) to (%d, %d)",
                start_x,
                start_y,
                end_x,
                end_y,
            )
            return False

        return True

    def type_text(self, text: str) -> bool:
        """Type text using system input."""
        try:
            from Quartz import (
                CGEventCreateKeyboardEvent,
                CGEventKeyboardSetUnicodeString,
                CGEventPost,
                CGEventSourceCreate,
                kCGEventSourceStateHIDSystemState,
                kCGHIDEventTap,
            )

            event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

            # Use Unicode string posting which is more reliable for text input
            unicode_event = CGEventCreateKeyboardEvent(
                event_source, KEY_CODE_TIMEOUT, keyDown=True
            )

            # Post the string as Unicode
            CGEventKeyboardSetUnicodeString(unicode_event, len(text), text)
            CGEventPost(kCGHIDEventTap, unicode_event)

            logger.debug("Typed text: %s", text)

        except Exception:
            logger.exception("Failed to type text '%s'", text)
            return False

        return True

    def send_key_combination(self, key_code: int, modifiers: list[str]) -> bool:
        """Send key combination with modifiers."""
        try:
            from Quartz import (
                CGEventCreateKeyboardEvent,
                CGEventPost,
                CGEventSetFlags,
                CGEventSourceCreate,
                kCGEventFlagMaskAlternate,
                kCGEventFlagMaskCommand,
                kCGEventFlagMaskControl,
                kCGEventFlagMaskShift,
                kCGEventSourceStateHIDSystemState,
                kCGHIDEventTap,
            )

            event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

            # Convert modifiers to flags
            flags = 0
            for modifier in modifiers:
                if modifier.lower() in ["cmd", "command"]:
                    flags |= kCGEventFlagMaskCommand
                elif modifier.lower() == "shift":
                    flags |= kCGEventFlagMaskShift
                elif modifier.lower() in ["ctrl", "control"]:
                    flags |= kCGEventFlagMaskControl
                elif modifier.lower() in ["alt", "option"]:
                    flags |= kCGEventFlagMaskAlternate

            # Key down
            down_event = CGEventCreateKeyboardEvent(
                event_source, key_code, keyDown=True
            )
            CGEventSetFlags(down_event, flags)
            CGEventPost(kCGHIDEventTap, down_event)

            # Key up
            up_event = CGEventCreateKeyboardEvent(event_source, key_code, keyDown=False)
            CGEventSetFlags(up_event, flags)
            CGEventPost(kCGHIDEventTap, up_event)

            logger.debug("Sent key combination: %s + %s", modifiers, key_code)

        except Exception:
            logger.exception(
                "Failed to send key combination %s + %d", modifiers, key_code
            )
            return False

        return True


class RealWorkspaceBridge(WorkspaceBridge):
    """Real workspace implementation using NSWorkspace."""

    def __init__(self) -> None:
        try:
            from Cocoa import NSWorkspace

            self._workspace = NSWorkspace.sharedWorkspace()
        except ImportError:
            logger.exception("Failed to import NSWorkspace: %s")
            raise

    def get_running_applications(self) -> list[Any]:
        """Get all running applications."""
        return list(self._workspace.runningApplications())

    def get_frontmost_application(self) -> Any | None:
        """Get the frontmost application."""
        return self._workspace.frontmostApplication()


class RealApplicationBridge(ApplicationBridge):
    """Real application implementation using NSRunningApplication methods."""

    def get_localized_name(self, app: Any) -> str:
        """Get the localized name of an application."""
        return app.localizedName() or "Unknown"

    def get_process_identifier(self, app: Any) -> int:
        """Get the process identifier of an application."""
        return app.processIdentifier()

    def get_bundle_identifier(self, app: Any) -> str | None:
        """Get the bundle identifier of an application."""
        return app.bundleIdentifier()

    def is_active(self, app: Any) -> bool:
        """Check if an application is active."""
        return app.isActive()

    def is_hidden(self, app: Any) -> bool:
        """Check if an application is hidden."""
        return app.isHidden()
