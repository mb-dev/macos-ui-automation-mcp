"""
Data models for UI automation.

This package provides Pydantic models for type-safe data structures.
"""

from .types import MenuBarItem, Position, Size, UIElement, WindowState

__all__ = [
    "MenuBarItem",
    "Position",
    "Size",
    "UIElement",
    "WindowState",
]
