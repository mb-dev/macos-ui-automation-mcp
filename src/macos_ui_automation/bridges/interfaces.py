"""
Abstract interfaces for PyObjC bridge operations.

This module defines the contract that both real and fake PyObjC implementations
must follow, enabling dependency injection and comprehensive testing.
"""

from abc import ABC, abstractmethod
from typing import Any

from .types import AXError, AXUIElementRef, AXValueRef


class PyObjCBridge(ABC):
    """
    Abstract interface for PyObjC accessibility operations.

    This interface wraps the low-level PyObjC accessibility functions,
    allowing for both real implementations (that call actual PyObjC)
    and fake implementations (for testing).
    """

    @abstractmethod
    def is_process_trusted(self) -> bool:
        """Check if accessibility permissions are granted."""

    @abstractmethod
    def create_application(self, pid: int) -> AXUIElementRef:
        """Create an AXUIElement reference for an application."""

    @abstractmethod
    def copy_attribute_value(
        self, element: AXUIElementRef, attribute: str
    ) -> tuple[AXError, Any | None]:
        """Copy an attribute value from an element."""

    @abstractmethod
    def copy_attribute_names(
        self, element: AXUIElementRef
    ) -> tuple[AXError, list[str] | None]:
        """Copy all attribute names from an element."""

    @abstractmethod
    def copy_action_names(
        self, element: AXUIElementRef
    ) -> tuple[AXError, list[str] | None]:
        """Copy all action names from an element."""

    @abstractmethod
    def set_attribute_value(
        self, element: AXUIElementRef, attribute: str, value: Any
    ) -> AXError:
        """Set an attribute value on an element."""

    @abstractmethod
    def perform_action(self, element: AXUIElementRef, action: str) -> AXError:
        """Perform an action on an element."""

    @abstractmethod
    def get_value_type(self, value: AXValueRef) -> int | None:
        """Get the type of an AXValue."""

    @abstractmethod
    def get_value(self, value: AXValueRef, value_type: int) -> Any | None:
        """Extract the actual value from an AXValue."""

    @abstractmethod
    def create_ax_value(self, value_type: int, value: Any) -> AXValueRef | None:
        """Create an AXValue from a value and type."""

    # Coordinate-based input operations

    @abstractmethod
    def click_at_position(self, x: int, y: int) -> bool:
        """Click at specific screen coordinates."""

    @abstractmethod
    def right_click_at_position(self, x: int, y: int) -> bool:
        """Right-click at specific screen coordinates."""

    @abstractmethod
    def drag_between_positions(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> bool:
        """Drag from start coordinates to end coordinates."""

    @abstractmethod
    def type_text(self, text: str) -> bool:
        """Type text using system input."""

    @abstractmethod
    def send_key_combination(self, key_code: int, modifiers: list[str]) -> bool:
        """Send key combination with modifiers."""


class WorkspaceBridge(ABC):
    """
    Abstract interface for NSWorkspace operations.

    Provides workspace-level functionality like listing running applications.
    """

    @abstractmethod
    def get_running_applications(self) -> list[Any]:
        """Get all running applications."""

    @abstractmethod
    def get_frontmost_application(self) -> Any | None:
        """Get the frontmost application."""


class ApplicationBridge(ABC):
    """
    Abstract interface for NSRunningApplication operations.

    Provides application-specific functionality.
    """

    @abstractmethod
    def get_localized_name(self, app: Any) -> str:
        """Get the localized name of an application."""

    @abstractmethod
    def get_process_identifier(self, app: Any) -> int:
        """Get the process identifier of an application."""

    @abstractmethod
    def get_bundle_identifier(self, app: Any) -> str | None:
        """Get the bundle identifier of an application."""

    @abstractmethod
    def is_active(self, app: Any) -> bool:
        """Check if an application is active."""

    @abstractmethod
    def is_hidden(self, app: Any) -> bool:
        """Check if an application is hidden."""
