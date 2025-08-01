"""
System state dumper for capturing complete macOS UI state.

This module provides functionality to capture and serialize the complete
state of macOS UI elements, including processes, windows, and menu bars
using the new bridge-based architecture.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone

from macos_ui_automation.models.types import (
    MenuBarItem,
    ProcessState,
    SystemState,
    UIElement,
    WindowState,
)

from .elements import (
    AccessibilityProvider,
    Application,
    AttributeConstants,
    Element,
    System,
)

logger = logging.getLogger(__name__)


class SystemStateDumper:
    """Dumps complete macOS system UI state using bridge-based architecture."""

    def __init__(
        self,
        system: System | None = None,
        timeout_seconds: float = 30.0,
        menu_bar_timeout: float = 2.0,
        only_visible_children: bool = True,
    ) -> None:
        """Initialize the state dumper.

        Args:
            system: System instance to use (default: creates new real System)
            timeout_seconds: Maximum time to spend traversing UI hierarchy
                (default 30 seconds)
            menu_bar_timeout: Maximum time to spend on menu bar traversal
                (default 2 seconds to avoid triggering menus)
            only_visible_children: Only traverse children of visible elements
                (default True to avoid side effects)
        """
        self.timeout_seconds = timeout_seconds
        self.menu_bar_timeout = menu_bar_timeout
        self.only_visible_children = only_visible_children
        self.system = system or self._create_system()
        self._check_accessibility()

        # Element mapping for O(1) lookup during actions
        self.element_map: dict[str, Element] = {}  # element_id -> live Element

    def _create_system(self) -> System:
        """Create a System instance checking test mode registry."""
        from .registry import is_test_mode

        return System(use_fake=is_test_mode())

    def _check_accessibility(self) -> None:
        """Check if accessibility is enabled."""
        workspace = self.system.get_workspace()
        if not workspace.is_accessibility_trusted():
            msg = (
                "Accessibility permissions not granted. "
                "Please enable accessibility access in System Preferences."
            )
            raise PermissionError(msg)

    def dump_system_state(
        self,
        include_processes: list[str] | None = None,
        exclude_processes: list[str] | None = None,
        skip_menu_bar_extras: bool = False,
    ) -> SystemState:
        """Dump complete system state.

        Args:
            include_processes: Only include these processes (by name)
            exclude_processes: Exclude these processes (by name)
            skip_menu_bar_extras: Skip AXExtrasMenuBar to avoid triggering menu opening

        Returns:
            Complete system state as Pydantic model
        """
        return self.dump_system_state_with_timeout(
            timeout_seconds=None,
            include_processes=include_processes,
            exclude_processes=exclude_processes,
            skip_menu_bar_extras=skip_menu_bar_extras,
        )

    def dump_system_state_with_timeout(
        self,
        timeout_seconds: float | None = None,
        include_processes: list[str] | None = None,
        exclude_processes: list[str] | None = None,
        skip_menu_bar_extras: bool = False,
    ) -> SystemState:
        """Dump complete system state with timeout.

        Args:
            timeout_seconds: Maximum time to spend dumping state (None for no limit)
            include_processes: Only include these processes (by name)
            exclude_processes: Exclude these processes (by name)
            skip_menu_bar_extras: Skip AXExtrasMenuBar to avoid triggering menu opening

        Returns:
            Complete system state as Pydantic model
        """
        start_time = time.time() if timeout_seconds else None

        timeout_msg = f" with {timeout_seconds}s timeout" if timeout_seconds else ""
        logger.info("Starting system state dump%s", timeout_msg)
        if skip_menu_bar_extras:
            logger.info("Skipping AXExtrasMenuBar to avoid triggering menu opening")

        # Get running applications
        workspace = self.system.get_workspace()
        applications = workspace.get_running_applications()

        # Filter applications
        if include_processes:
            applications = [
                app for app in applications if app.get_name() in include_processes
            ]
        if exclude_processes:
            applications = [
                app for app in applications if app.get_name() not in exclude_processes
            ]

        processes = []
        accessibility = self.system.get_accessibility()

        for app in applications:
            # Check timeout
            if start_time and timeout_seconds:
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    logger.warning(
                        "Timeout reached (%.1fs), stopping app processing",
                        timeout_seconds,
                    )
                    break

            process_state = self._dump_application_state(
                app,
                accessibility,
                start_time,
                timeout_seconds,
                skip_menu_bar_extras,
            )
            if process_state:
                processes.append(process_state)

        return SystemState(
            timestamp=datetime.now(timezone.utc),
            processes=processes,
            accessibility_enabled=True,
            capture_method="accessibility",
            version="1.0",
        )

    def _dump_application_state(
        self,
        app: Application,
        accessibility: AccessibilityProvider,
        start_time: float | None,
        timeout_seconds: float | None,
        skip_menu_bar_extras: bool,
    ) -> ProcessState | None:
        """Dump state for a single application."""
        # Create application element
        app_element = accessibility.create_application_element(app.get_pid())
        if not app_element:
            return None

        # Get basic app info
        name = app.get_name()
        pid = app.get_pid()
        bundle_id = app.get_bundle_id()

        logger.debug("Processing application: %s (PID: %s)", name, pid)

        # Get windows
        windows = []
        windows_elements = app_element.get_attribute_value(
            AttributeConstants.WINDOWS.value
        )
        if windows_elements:
            for i, window_element in enumerate(windows_elements):
                # Check timeout
                if start_time and timeout_seconds:
                    elapsed = time.time() - start_time
                    if elapsed > timeout_seconds:
                        logger.warning(
                            "Timeout reached during window processing for %s", name
                        )
                        break

                window_state = self._dump_window_state(
                    window_element, i, start_time, timeout_seconds
                )
                if window_state:
                    windows.append(window_state)

        # Get menu bar (limited by time to avoid triggering menus)
        menu_bar_items = []
        if not skip_menu_bar_extras:
            menu_bar_element = app_element.get_attribute_value(
                AttributeConstants.MENU_BAR.value
            )
            if menu_bar_element:
                menu_bar_start_time = start_time or time.time()
                menu_bar_items = self._dump_menu_bar_with_timeout(
                    menu_bar_element, menu_bar_start_time
                )

        return ProcessState(
            name=name,
            pid=pid,
            bundle_id=bundle_id,
            frontmost=app.is_active(),
            hidden=app.is_hidden(),
            windows=windows,
            menu_bar=menu_bar_items,
        )

    def _dump_window_state(
        self,
        window_element: Element,
        window_index: int,
        start_time: float | None = None,
        timeout_seconds: float | None = None,
    ) -> WindowState | None:
        """Dump state for a single window."""
        title = (
            window_element.get_attribute_value(AttributeConstants.TITLE.value)
            or f"Window {window_index}"
        )
        position = window_element.get_attribute_value(AttributeConstants.POSITION.value)
        size = window_element.get_attribute_value(AttributeConstants.SIZE.value)
        minimized = (
            window_element.get_attribute_value(AttributeConstants.MINIMIZED.value)
            or False
        )

        # Get window elements (limited by time)
        window_start_time = start_time or time.time()
        window_timeout = timeout_seconds or self.timeout_seconds
        elements = self._dump_ui_elements_with_timeout(
            window_element, window_start_time, window_timeout
        )

        return WindowState(
            title=title,
            window_id=window_index,
            role="AXWindow",
            position=position,
            size=size,
            minimized=minimized,
            maximized=False,
            fullscreen=False,
            main_window=False,
            children=elements,
            value=None,
            description=None,
            enabled=True,
            focused=False,
            element_id=str(uuid.uuid4()),
            ax_identifier=None,
        )

    def _dump_ui_elements_with_timeout(
        self, element: Element, start_time: float, timeout_seconds: float
    ) -> list[UIElement]:
        """Recursively dump UI elements with hierarchical structure and time-based
        limits."""
        return self._dump_element_hierarchy(element, start_time, timeout_seconds)

    def _dump_element_hierarchy(
        self,
        element: Element,
        start_time: float,
        timeout_seconds: float,
        depth: int = 0,
    ) -> list[UIElement]:
        """Recursively dump element hierarchy preserving parent-child relationships."""
        elements: list[UIElement] = []

        children = element.get_attribute_value(AttributeConstants.CHILDREN.value)
        if not children:
            return elements

        for child in children:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.warning(
                    "Timeout reached (%.1fs) during UI element traversal at depth %d",
                    timeout_seconds,
                    depth,
                )
                break

            # Get basic element info
            role = child.get_attribute_value(AttributeConstants.ROLE.value)
            title = child.get_attribute_value(AttributeConstants.TITLE.value)
            identifier = child.get_attribute_value(AttributeConstants.IDENTIFIER.value)
            enabled = child.get_attribute_value(AttributeConstants.ENABLED.value)
            focused = child.get_attribute_value(AttributeConstants.FOCUSED.value)
            position = child.get_attribute_value(AttributeConstants.POSITION.value)
            size = child.get_attribute_value(AttributeConstants.SIZE.value)
            value = child.get_attribute_value(AttributeConstants.VALUE.value)
            actions = child.get_actions()

            # Handle None values for Pydantic validation
            enabled = enabled if enabled is not None else False
            focused = focused if focused is not None else False

            # Handle value field - convert complex objects to None since UIElement
            # expects basic types
            if hasattr(value, "__class__") and (
                "Element" in str(type(value))
                or "Position" in str(type(value))
                or "Size" in str(type(value))
            ):
                value = None

            # Skip elements without roles (usually not useful)
            if not role:
                continue

            # Recursively get child elements if this element has children and is visible
            child_elements = child.get_attribute_value(
                AttributeConstants.CHILDREN.value
            )
            children_count = len(child_elements) if child_elements else 0

            nested_children = []
            if children_count > 0 and (
                not self.only_visible_children or self._is_element_visible(child)
            ):
                nested_children = self._dump_element_hierarchy(
                    child, start_time, timeout_seconds, depth + 1
                )

            # Generate unique element ID for O(1) lookup during actions
            element_id = str(uuid.uuid4())

            ui_element = UIElement(
                role=role,
                title=title,
                ax_identifier=identifier,
                enabled=enabled,
                focused=focused,
                position=position,
                size=size,
                value=value,
                description=None,  # Add required description field
                actions=actions,
                children=nested_children,  # Store actual nested children
                element_id=element_id,  # Add unique ID for action lookup
            )

            # Store mapping from element_id to live Element for O(1) action lookup
            self.element_map[element_id] = child

            elements.append(ui_element)

        return elements

    def get_element_map(self) -> dict[str, Element]:
        """Get the element ID to live Element mapping for O(1) action lookup."""
        return self.element_map

    def get_element_by_id(self, element_id: str) -> Element | None:
        """Get live Element by element_id with O(1) lookup.

        Args:
            element_id: Unique element identifier from UIElement

        Returns:
            Live Element instance or None if not found
        """
        return self.element_map.get(element_id)

    def _dump_menu_bar_with_timeout(
        self, menu_element: Element, start_time: float
    ) -> list[MenuBarItem]:
        """Dump menu bar items with time-based limits to avoid triggering menus."""
        items: list[MenuBarItem] = []

        children = menu_element.get_attribute_value(AttributeConstants.CHILDREN.value)
        if not children:
            return items

        for child in children:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.menu_bar_timeout:
                logger.warning(
                    "Menu bar timeout reached (%.1fs)", self.menu_bar_timeout
                )
                break

            title = child.get_attribute_value(AttributeConstants.TITLE.value)
            enabled = child.get_attribute_value(AttributeConstants.ENABLED.value)

            if not title:
                continue

            # For menu items, we avoid going deeper to prevent triggering menu opening
            # This is safer than depth-based limiting for menu bars
            item = MenuBarItem(
                title=title,
                enabled=enabled if enabled is not None else True,
                role="AXMenuItem",
                value=None,
                description=None,
                position=None,
                size=None,
                focused=False,
                element_id=str(uuid.uuid4()),
                ax_identifier=None,
                expanded=False,
            )
            items.append(item)

        return items

    def _is_element_visible(self, element: Element) -> bool:
        """Check if element is visible (simple heuristic)."""
        # Check if element has size and position
        size = element.get_attribute_value(AttributeConstants.SIZE.value)
        element.get_attribute_value(AttributeConstants.POSITION.value)

        if size and hasattr(size, "width") and hasattr(size, "height"):
            return bool(size.width > 0 and size.height > 0)

        return True  # Default to visible if we can't determine

    def _role_to_element_type(self, role: str) -> str:
        """Convert AX role to simplified element type."""
        role_mapping = {
            "AXButton": "button",
            "AXTextField": "textfield",
            "AXStaticText": "text",
            "AXWindow": "window",
            "AXMenuItem": "menuitem",
            "AXMenuBar": "menubar",
            "AXPopUpButton": "popup",
            "AXTable": "table",
            "AXRow": "row",
            "AXCell": "cell",
            "AXScrollArea": "scroll",
        }
        return role_mapping.get(role, "unknown")
