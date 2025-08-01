"""
Core data models for macOS UI automation using Pydantic.

Provides type-safe data models for UI elements, windows, applications,
and system state with JSON serialization support.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UIRole(str, Enum):
    """Common accessibility roles for UI elements."""

    BUTTON = "AXButton"
    TEXT_FIELD = "AXTextField"
    STATIC_TEXT = "AXStaticText"
    MENU_BAR = "AXMenuBar"
    MENU_ITEM = "AXMenuItem"
    WINDOW = "AXWindow"
    APPLICATION = "AXApplication"
    SCROLL_AREA = "AXScrollArea"
    TABLE = "AXTable"
    ROW = "AXRow"
    CELL = "AXCell"
    POPUP_BUTTON = "AXPopUpButton"
    UNKNOWN = "AXUnknown"


class UIAction(str, Enum):
    """Common accessibility actions."""

    PRESS = "AXPress"
    SET_VALUE = "AXSetValue"
    SHOW_MENU = "AXShowMenu"
    PICK = "AXPick"
    SCROLL_TO_VISIBLE = "AXScrollToVisible"
    CONFIRM = "AXConfirm"
    CANCEL = "AXCancel"


class Position(BaseModel):
    """2D position coordinates."""

    x: int = Field(description="X coordinate")
    y: int = Field(description="Y coordinate")

    @field_validator("x", "y", mode="before")
    @classmethod
    def convert_float_to_int(cls, v: float) -> int:
        """Convert float values to integers."""
        if isinstance(v, float):
            return int(v)
        return v


class Size(BaseModel):
    """2D size dimensions."""

    width: int = Field(description="Width in pixels")
    height: int = Field(description="Height in pixels")


class UIElement(BaseModel):
    """Base model for any UI element with accessibility information."""

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields for unknown accessibility attributes
        use_enum_values=True,
    )

    # Core accessibility attributes
    role: str = Field(description="AX role of the element")
    title: str | None = Field(None, description="Title or label of the element")
    value: str | int | float | bool | None = Field(None, description="Current value")
    description: str | None = Field(None, description="Accessibility description")

    # Positional information
    position: Position | None = Field(None, description="Element position")
    size: Size | None = Field(None, description="Element size")

    # Interaction capabilities
    actions: list[str] = Field(default_factory=list, description="Available actions")
    enabled: bool = Field(default=True, description="Whether element is enabled")
    focused: bool = Field(default=False, description="Whether element has focus")

    # Hierarchy
    children: list[UIElement] = Field(
        default_factory=list, description="Child elements"
    )

    # Metadata
    element_id: str | None = Field(None, description="Unique identifier")
    ax_identifier: str | None = Field(None, description="AX identifier")

    @property
    def clickable(self) -> bool:
        """Check if element can be clicked."""
        return UIAction.PRESS in self.actions or "AXPress" in self.actions

    @property
    def editable(self) -> bool:
        """Check if element can be edited."""
        # Check for various text editing actions
        text_actions = ["AXSetValue", "AXConfirm", "AXShowMenu"]
        has_text_action = any(action in self.actions for action in text_actions)

        # Text fields are typically editable if they have certain roles
        is_text_role = self.role in ["AXTextField", "AXTextArea", "AXComboBox"]

        return (
            UIAction.SET_VALUE in self.actions
            or "AXSetValue" in self.actions
            or (is_text_role and has_text_action)
            or (is_text_role and self.enabled)
        )


class MenuBarItem(UIElement):
    """Menu bar item with menu content."""

    # Override role with default for menu items
    role: str = Field(default="AXMenuItem", description="Accessibility role")
    element_type: str = Field(default="menuitem", description="Simplified element type")

    menu_items: list[UIElement] = Field(
        default_factory=list, description="Menu items when expanded"
    )
    expanded: bool = Field(
        default=False, description="Whether menu is currently expanded"
    )


class WindowState(UIElement):
    """Window with additional window-specific attributes."""

    # Override role with default for windows
    role: str = Field(default="AXWindow", description="Accessibility role")
    element_type: str = Field(default="window", description="Simplified element type")

    window_id: int | None = Field(None, description="Window ID")
    minimized: bool = Field(default=False, description="Whether window is minimized")
    maximized: bool = Field(default=False, description="Whether window is maximized")
    fullscreen: bool = Field(default=False, description="Whether window is fullscreen")
    main_window: bool = Field(
        default=False, description="Whether this is the main window"
    )


class ProcessState(BaseModel):
    """Complete state of a single process/application."""

    model_config = ConfigDict(use_enum_values=True)

    # Process information
    name: str = Field(description="Process name")
    pid: int = Field(description="Process ID")
    bundle_id: str | None = Field(None, description="Bundle identifier")

    # UI state
    windows: list[WindowState] = Field(default_factory=list, description="All windows")
    menu_bar: list[MenuBarItem] = Field(
        default_factory=list, description="Menu bar items"
    )

    # Process state
    frontmost: bool = Field(default=False, description="Whether process is frontmost")
    hidden: bool = Field(default=False, description="Whether process is hidden")

    # Timestamps
    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update time"
    )


class SystemState(BaseModel):
    """Complete macOS system UI state."""

    model_config = ConfigDict(use_enum_values=True)

    # System information
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Capture timestamp"
    )
    accessibility_enabled: bool = Field(description="Whether accessibility is enabled")

    # Process states
    processes: list[ProcessState] = Field(
        default_factory=list, description="All processes"
    )

    # System-level UI elements
    dock_items: list[UIElement] = Field(default_factory=list, description="Dock items")
    menu_bar_extras: list[UIElement] = Field(
        default_factory=list, description="Menu bar extras"
    )

    # Metadata
    capture_method: str = Field(
        "accessibility", description="How this state was captured"
    )
    version: str = Field("1.0", description="Schema version")


class ApplicationInfo(BaseModel):
    """Basic application information for MCP responses."""

    name: str = Field(description="Application name")
    pid: int = Field(description="Process ID")
    bundle_id: str | None = Field(None, description="Bundle identifier")
    active: bool = Field(description="Whether application is currently active")
    hidden: bool = Field(description="Whether application is hidden")


class AppOverview(BaseModel):
    """Overview information for an application with basic UI structure."""

    name: str = Field(description="Application name")
    pid: int = Field(description="Process ID")
    bundle_id: str | None = Field(None, description="Bundle identifier")
    frontmost: bool = Field(description="Whether application is frontmost")
    hidden: bool = Field(description="Whether application is hidden")
    window_count: int = Field(description="Number of windows")
    has_menu_bar: bool = Field(description="Whether application has menu bar items")
    windows: list[dict[str, Any]] = Field(
        default_factory=list, description="Basic window information"
    )


class SearchResult(BaseModel):
    """Result from UI element search operations."""

    role: str = Field(description="AX role of the element")
    title: str | None = Field(None, description="Title or label of the element")
    value: str | int | float | bool | None = Field(None, description="Current value")
    enabled: bool = Field(description="Whether element is enabled")
    focused: bool = Field(description="Whether element has focus")
    position: dict[str, int] | None = Field(None, description="Element position {x, y}")
    size: dict[str, int] | None = Field(
        None, description="Element size {width, height}"
    )
    description: str | None = Field(None, description="Accessibility description")
    ax_identifier: str | None = Field(None, description="AX identifier")
    actions: list[str] = Field(default_factory=list, description="Available actions")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchResult:
        """Create SearchResult from dictionary data."""
        return cls(
            role=data.get("role", "AXUnknown"),
            title=data.get("title"),
            value=data.get("value"),
            enabled=data.get("enabled", False),
            focused=data.get("focused", False),
            position=data.get("position"),
            size=data.get("size"),
            description=data.get("description"),
            ax_identifier=data.get("ax_identifier"),
            actions=data.get("actions", []),
        )


class ErrorResponse(BaseModel):
    """Error response for MCP operations."""

    error: str = Field(description="Error message")
    timeout: bool = Field(default=False, description="Whether error was due to timeout")


class AccessibilityStatus(BaseModel):
    """Status of accessibility permissions."""

    accessibility_trusted: bool = Field(description="Whether accessibility is trusted")
    message: str = Field(description="Status message")
    guidance: str | None = Field(None, description="Guidance for fixing issues")


# Update forward references
UIElement.model_rebuild()
