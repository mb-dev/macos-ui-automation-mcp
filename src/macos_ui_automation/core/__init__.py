"""
Core UI automation functionality.

This package provides the main classes for UI automation:
- Element: Individual UI elements
- Application: Running applications
- Workspace: System-level workspace operations
- System: Main entry point for UI automation
"""

from .elements import (
    AccessibilityProvider,
    Application,
    AttributeConstants,
    Element,
    System,
    Workspace,
)

__all__ = [
    "AccessibilityProvider",
    "Application",
    "AttributeConstants",
    "Element",
    "System",
    "Workspace",
]
