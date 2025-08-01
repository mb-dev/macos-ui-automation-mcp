"""
Fake PyObjC bridge implementation for testing.

This module provides fake implementations that return test data
without requiring actual PyObjC or macOS accessibility permissions.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from .interfaces import ApplicationBridge, PyObjCBridge, WorkspaceBridge
from .types import AXError, AXUIElementRef, AXValueRef, AXValueType

logger = logging.getLogger(__name__)


@dataclass
class FakeAXValue:
    """Fake AXValue for testing position, size, and rect data."""

    value_type: int
    data: Any

    def __str__(self) -> str:
        """String representation that mimics real AXValue output."""
        if self.value_type == AXValueType.CGPOINT.value:
            return (
                f"<AXValue 0x123456789 [kAXValueCGPointType] "
                f"x:{self.data['x']} y:{self.data['y']}>"
            )
        if self.value_type == AXValueType.CGSIZE.value:
            return (
                f"<AXValue 0x123456789 [kAXValueCGSizeType] "
                f"w:{self.data['width']} h:{self.data['height']}>"
            )
        if self.value_type == AXValueType.CGRECT.value:
            return (
                f"<AXValue 0x123456789 [kAXValueCGRectType] "
                f"x:{self.data['x']} y:{self.data['y']} "
                f"w:{self.data['width']} h:{self.data['height']}>"
            )
        return f"<AXValue 0x123456789 [unknown] {self.data}>"

    def _cf_type_id(self) -> int:
        """Mock _cfTypeID attribute for AXValue detection."""
        return 12345


@dataclass
class FakeAXUIElement:
    """Fake AXUIElement for testing."""

    element_id: str
    attributes: dict[str, Any] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)
    children: list["FakeAXUIElement"] = field(default_factory=list)
    parent: Optional["FakeAXUIElement"] = None

    def __post_init__(self) -> None:
        """Set parent for children."""
        for child in self.children:
            child.parent = self

    def _cf_type_id(self) -> int:
        """Mock _cfTypeID attribute for AXUIElement detection."""
        return 54321


@dataclass
class FakeNSRunningApplication:
    """Fake NSRunningApplication for testing."""

    name: str
    pid: int
    bundle_id: str | None = None
    active: bool = False
    hidden: bool = False


class FakePyObjCBridge(PyObjCBridge):
    """Fake PyObjC implementation for testing."""

    def __init__(self, applications: dict[int, FakeAXUIElement] | None = None) -> None:
        self._process_trusted = True
        self._elements: dict[str, FakeAXUIElement] = {}
        self._applications: dict[int, FakeAXUIElement] = applications or {}

        if not self._applications:
            self._setup_default_test_data()
        else:
            self._register_elements_from_applications()

    def _register_elements_from_applications(self) -> None:
        """Register all elements from the provided applications for lookup."""
        for pid, app in self._applications.items():
            self._elements[f"app_{pid}"] = app
            self._register_element_hierarchy(app)

    def _register_element_hierarchy(self, element: FakeAXUIElement) -> None:
        """Recursively register all elements in the hierarchy."""
        if element.element_id:
            self._elements[element.element_id] = element

        for child in element.children:
            self._register_element_hierarchy(child)

    def _setup_default_test_data(self) -> None:
        """Set up default test data."""
        # Create test application
        test_app = FakeAXUIElement(
            element_id="app_1",
            attributes={
                "kAXTitleAttribute": "Test App",
                "kAXRoleAttribute": "AXApplication",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 0, "y": 0}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 800, "height": 600}
                ),
                "kAXEnabledAttribute": True,
                "kAXFocusedAttribute": False,
            },
            actions=["AXPress", "AXRaise"],
        )

        # Create test window
        test_window = FakeAXUIElement(
            element_id="window_1",
            attributes={
                "kAXTitleAttribute": "Test Window",
                "kAXRoleAttribute": "AXWindow",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 100, "y": 100}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 600, "height": 400}
                ),
                "kAXMinimizedAttribute": False,
            },
            actions=["AXRaise", "AXPress"],
        )

        # Create test button with nested children
        test_button = FakeAXUIElement(
            element_id="button_1",
            attributes={
                "kAXTitleAttribute": "Test Button",
                "kAXRoleAttribute": "AXButton",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 200, "y": 200}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 100, "height": 30}
                ),
                "kAXEnabledAttribute": True,
                "kAXIdentifierAttribute": "test-button-id",
            },
            actions=["AXPress"],
        )

        # Create nested child elements (like TaskManagement has)
        button_child = FakeAXUIElement(
            element_id="button_1_child",
            attributes={
                "kAXTitleAttribute": "Button Child",
                "kAXRoleAttribute": "AXGroup",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 205, "y": 205}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 90, "height": 20}
                ),
                "kAXEnabledAttribute": True,
                "kAXIdentifierAttribute": "button-child-id",
            },
            actions=[],
        )

        # Create grandchild element
        button_grandchild = FakeAXUIElement(
            element_id="button_1_grandchild",
            attributes={
                "kAXTitleAttribute": "Deep Element",
                "kAXRoleAttribute": "AXStaticText",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 210, "y": 210}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 80, "height": 15}
                ),
                "kAXEnabledAttribute": True,
                "kAXIdentifierAttribute": "deep-element-id",
            },
            actions=[],
        )

        # Create toolbar similar to TaskManagement
        test_toolbar = FakeAXUIElement(
            element_id="toolbar_1",
            attributes={
                "kAXTitleAttribute": "Test Toolbar",
                "kAXRoleAttribute": "AXToolbar",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 100, "y": 50}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 400, "height": 40}
                ),
                "kAXEnabledAttribute": True,
            },
            actions=[],
        )

        sync_button = FakeAXUIElement(
            element_id="sync_button",
            attributes={
                "kAXTitleAttribute": "Sync",
                "kAXRoleAttribute": "AXButton",
                "kAXPositionAttribute": FakeAXValue(
                    AXValueType.CGPOINT.value, {"x": 120, "y": 60}
                ),
                "kAXSizeAttribute": FakeAXValue(
                    AXValueType.CGSIZE.value, {"width": 60, "height": 25}
                ),
                "kAXEnabledAttribute": True,
                "kAXIdentifierAttribute": "syncButton",
            },
            actions=["AXPress"],
        )

        # Set up the complete hierarchy
        button_child.children = [button_grandchild]
        test_button.children = [button_child]
        test_toolbar.children = [sync_button]
        test_window.children = [test_button, test_toolbar]
        test_app.children = [test_window]
        test_app.attributes["kAXWindowsAttribute"] = [test_window]
        test_app.attributes["kAXMainWindowAttribute"] = test_window

        # Store references
        self._applications[1234] = test_app
        self._elements["app_1"] = test_app
        self._elements["window_1"] = test_window
        self._elements["button_1"] = test_button
        self._elements["button_1_child"] = button_child
        self._elements["button_1_grandchild"] = button_grandchild
        self._elements["toolbar_1"] = test_toolbar
        self._elements["sync_button"] = sync_button

    def is_process_trusted(self) -> bool:
        """Check if accessibility permissions are granted."""
        return self._process_trusted

    def create_application(self, pid: int) -> AXUIElementRef:
        """Create an AXUIElement reference for an application."""
        if pid in self._applications:
            return AXUIElementRef(self._applications[pid])
        # Create new application if not exists
        app = FakeAXUIElement(
            element_id=f"app_{pid}",
            attributes={
                "kAXTitleAttribute": f"App {pid}",
                "kAXRoleAttribute": "AXApplication",
                "kAXEnabledAttribute": True,
            },
            actions=["AXRaise"],
        )
        self._applications[pid] = app
        return AXUIElementRef(app)

    def copy_attribute_value(
        self, element: AXUIElementRef, attribute: str
    ) -> tuple[AXError, Any | None]:
        """Copy an attribute value from an element."""
        fake_element: FakeAXUIElement = element  # type: ignore[assignment]  # element is already a FakeAXUIElement

        # Handle special cases first (they may not be in attributes dict)
        if attribute in {"AXChildren", "kAXChildrenAttribute"}:
            return AXError.SUCCESS, fake_element.children

        # Map new attribute names to old ones for backwards compatibility
        attribute_mapping = {
            "AXWindows": "kAXWindowsAttribute",
            "AXMainWindow": "kAXMainWindowAttribute",
            "AXMenuBar": "kAXMenuBarAttribute",
            "AXTitle": "kAXTitleAttribute",
            "AXRole": "kAXRoleAttribute",
            "AXValue": "kAXValueAttribute",
            "AXPosition": "kAXPositionAttribute",
            "AXSize": "kAXSizeAttribute",
            "AXEnabled": "kAXEnabledAttribute",
            "AXFocused": "kAXFocusedAttribute",
            "AXIdentifier": "kAXIdentifierAttribute",
            "AXMinimized": "kAXMinimizedAttribute",
        }

        # Try the new attribute name first, then fall back to mapped old name
        search_attribute = attribute
        if attribute in attribute_mapping:
            search_attribute = attribute_mapping[attribute]

        # Check if attribute exists in attributes dict
        if (
            hasattr(fake_element, "attributes")
            and search_attribute in fake_element.attributes
        ):
            value = fake_element.attributes[search_attribute]

            # Handle special cases for attributes that are in the dict
            if (
                search_attribute == "kAXWindowsAttribute" and isinstance(value, list)
            ) or (
                search_attribute in ["kAXMainWindowAttribute", "kAXMenuBarAttribute"]
                and value
            ):
                return AXError.SUCCESS, value

            return AXError.SUCCESS, value
        return AXError.ATTRIBUTE_UNSUPPORTED, None

    def copy_attribute_names(
        self, element: AXUIElementRef
    ) -> tuple[AXError, list[str] | None]:
        """Copy all attribute names from an element."""
        fake_element = element
        if hasattr(fake_element, "attributes"):
            return AXError.SUCCESS, list(fake_element.attributes.keys())
        return AXError.FAILURE, None

    def copy_action_names(
        self, element: AXUIElementRef
    ) -> tuple[AXError, list[str] | None]:
        """Copy all action names from an element."""
        fake_element = element
        if hasattr(fake_element, "actions"):
            return AXError.SUCCESS, fake_element.actions.copy()
        return AXError.FAILURE, None

    def set_attribute_value(
        self, element: AXUIElementRef, attribute: str, value: Any
    ) -> AXError:
        """Set an attribute value on an element."""
        fake_element = element
        if hasattr(fake_element, "attributes"):
            # Map new attribute names to old ones for backwards compatibility
            attribute_mapping = {
                "AXWindows": "kAXWindowsAttribute",
                "AXMainWindow": "kAXMainWindowAttribute",
                "AXMenuBar": "kAXMenuBarAttribute",
                "AXTitle": "kAXTitleAttribute",
                "AXRole": "kAXRoleAttribute",
                "AXValue": "kAXValueAttribute",
                "AXPosition": "kAXPositionAttribute",
                "AXSize": "kAXSizeAttribute",
                "AXEnabled": "kAXEnabledAttribute",
                "AXFocused": "kAXFocusedAttribute",
                "AXIdentifier": "kAXIdentifierAttribute",
                "AXMinimized": "kAXMinimizedAttribute",
            }

            # Use mapped attribute name if available
            target_attribute = attribute_mapping.get(attribute, attribute)
            fake_element.attributes[target_attribute] = value
            return AXError.SUCCESS
        return AXError.FAILURE

    def perform_action(self, element: AXUIElementRef, action: str) -> AXError:
        """Perform an action on an element."""
        fake_element: FakeAXUIElement = element  # type: ignore[assignment]  # element is already a FakeAXUIElement
        if hasattr(fake_element, "actions") and action in fake_element.actions:
            # Simulate action side effects
            if action == "AXPress":
                logger.debug(
                    "Simulated press action on element %s", fake_element.element_id
                )
            return AXError.SUCCESS
        return AXError.ACTION_UNSUPPORTED

    def get_value_type(self, value: AXValueRef) -> int | None:
        """Get the type of an AXValue."""
        fake_value = value
        if isinstance(fake_value, FakeAXValue):
            return fake_value.value_type
        return None

    def get_value(self, value: AXValueRef, value_type: int) -> Any | None:
        """Extract the actual value from an AXValue."""
        fake_value = value
        # Constants for value type validation
        valid_value_types = {1, 2, 3}  # Basic type validation
        if value_type not in valid_value_types:
            return None
        if isinstance(fake_value, FakeAXValue):
            return fake_value.data
        return None

    def create_ax_value(self, value_type: int, value: Any) -> AXValueRef | None:
        """Create an AXValue from a value and type."""
        fake_value = FakeAXValue(value_type, value)
        return AXValueRef(fake_value)

    # Coordinate-based input operations (noop for testing)

    def click_at_position(self, x: int, y: int) -> bool:
        """Simulate click at specific screen coordinates."""
        logger.debug("Fake click at position (%s, %s)", x, y)
        return True

    def right_click_at_position(self, x: int, y: int) -> bool:
        """Simulate right-click at specific screen coordinates."""
        logger.debug("Fake right-click at position (%s, %s)", x, y)
        return True

    def drag_between_positions(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> bool:
        """Simulate drag from start coordinates to end coordinates."""
        logger.debug(
            "Fake drag from (%s, %s) to (%s, %s)", start_x, start_y, end_x, end_y
        )
        return True

    def type_text(self, text: str) -> bool:
        """Simulate typing text."""
        logger.debug("Fake type text: '%s'", text)
        return True

    def send_key_combination(self, key_code: int, modifiers: list[str]) -> bool:
        """Simulate key combination with modifiers."""
        logger.debug("Fake key combination: %s + %s", modifiers, key_code)
        return True

    def add_test_element(self, element: FakeAXUIElement) -> None:
        """Add a test element for testing purposes."""
        self._elements[element.element_id] = element

    def set_process_trusted(self, *, trusted: bool) -> None:
        """Set process trust status for testing."""
        self._process_trusted = trusted


class FakeWorkspaceBridge(WorkspaceBridge):
    """Fake workspace implementation for testing."""

    def __init__(
        self, running_applications: list[FakeNSRunningApplication] | None = None
    ) -> None:
        if running_applications:
            self._running_applications = running_applications
            # Set frontmost app
            self._frontmost_app = None
            for app in self._running_applications:
                if app.active:
                    self._frontmost_app = app
                    break
            if not self._frontmost_app and self._running_applications:
                self._frontmost_app = self._running_applications[0]
        else:
            self._setup_default_apps()

    def _setup_default_apps(self) -> None:
        """Set up default running applications."""
        self._running_applications = [
            FakeNSRunningApplication(
                name="Test App",
                pid=1234,
                bundle_id="com.test.app",
                active=True,
                hidden=False,
            ),
            FakeNSRunningApplication(
                name="Another App",
                pid=5678,
                bundle_id="com.another.app",
                active=False,
                hidden=False,
            ),
            FakeNSRunningApplication(
                name="Hidden App",
                pid=9999,
                bundle_id="com.hidden.app",
                active=False,
                hidden=True,
            ),
        ]
        self._frontmost_app = self._running_applications[0]

    def get_running_applications(self) -> list[Any]:
        """Get all running applications."""
        return self._running_applications.copy()

    def get_frontmost_application(self) -> Any | None:
        """Get the frontmost application."""
        return self._frontmost_app

    def add_application(self, app: FakeNSRunningApplication) -> None:
        """Add an application for testing."""
        self._running_applications.append(app)

    def set_frontmost_application(self, app: FakeNSRunningApplication) -> None:
        """Set the frontmost application for testing."""
        self._frontmost_app = app


class FakeApplicationBridge(ApplicationBridge):
    """Fake application implementation for testing."""

    def get_localized_name(self, app: Any) -> str:
        """Get the localized name of an application."""
        return getattr(app, "name", "Unknown")

    def get_process_identifier(self, app: Any) -> int:
        """Get the process identifier of an application."""
        return getattr(app, "pid", -1)

    def get_bundle_identifier(self, app: Any) -> str | None:
        """Get the bundle identifier of an application."""
        return getattr(app, "bundle_id", None)

    def is_active(self, app: Any) -> bool:
        """Check if an application is active."""
        return getattr(app, "active", False)

    def is_hidden(self, app: Any) -> bool:
        """Check if an application is hidden."""
        return getattr(app, "hidden", False)
