"""
Type definitions for PyObjC bridge.

This module defines types that represent PyObjC objects and constants
without importing the actual PyObjC modules, enabling better testing
and type safety.
"""

from enum import Enum
from typing import NewType

# Type aliases for PyObjC object references
AXUIElementRef = NewType("AXUIElementRef", object)
AXValueRef = NewType("AXValueRef", object)


class AXError(Enum):
    """Accessibility API error codes."""

    SUCCESS = 0
    FAILURE = -25200
    ILLEGAL_ARGUMENT = -25201
    INVALID_UI_ELEMENT = -25202
    INVALID_UI_ELEMENT_OBSERVER = -25203
    CANNOT_COMPLETE = -25204
    ATTRIBUTE_UNSUPPORTED = -25205
    ACTION_UNSUPPORTED = -25206
    NOTIFICATION_UNSUPPORTED = -25207
    NOT_IMPLEMENTED = -25208
    NOTIFICATION_ALREADY_REGISTERED = -25209
    NOTIFICATION_NOT_REGISTERED = -25210
    API_DISABLED = -25211
    NO_VALUE = -25212
    PARAMETER_NOT_SUPPORTED = -25213
    NOT_ENOUGH_PRECISION = -25214


class AXValueType(Enum):
    """AXValue type constants."""

    CGPOINT = 1
    CGSIZE = 2
    CGRECT = 3
    CFRANGE = 4
    AXERROR = 5
    ILLEGAL = 0


class AXAttribute:
    """Accessibility attribute constants."""

    # Core attributes
    TITLE = "kAXTitleAttribute"
    ROLE = "kAXRoleAttribute"
    VALUE = "kAXValueAttribute"
    DESCRIPTION = "kAXDescriptionAttribute"
    HELP = "kAXHelpAttribute"

    # Position and size
    POSITION = "kAXPositionAttribute"
    SIZE = "kAXSizeAttribute"

    # State attributes
    ENABLED = "kAXEnabledAttribute"
    FOCUSED = "kAXFocusedAttribute"
    SELECTED = "kAXSelectedAttribute"
    MINIMIZED = "kAXMinimizedAttribute"

    # Hierarchy attributes
    CHILDREN = "kAXChildrenAttribute"
    PARENT = "kAXParentAttribute"

    # Window attributes
    WINDOWS = "kAXWindowsAttribute"
    MAIN_WINDOW = "kAXMainWindowAttribute"

    # Application attributes
    MENU_BAR = "kAXMenuBarAttribute"
    TOP_LEVEL_UI_ELEMENT = "kAXTopLevelUIElementAttribute"

    # Identifier attributes
    IDENTIFIER = "kAXIdentifierAttribute"
    URL = "kAXURLAttribute"


class AXAction:
    """Accessibility action constants."""

    PRESS = "AXPress"
    CONFIRM = "AXConfirm"
    CANCEL = "AXCancel"
    DECREMENT = "AXDecrement"
    INCREMENT = "AXIncrement"
    PICK = "AXPick"
    RAISE = "AXRaise"
    SHOW_MENU = "AXShowMenu"
