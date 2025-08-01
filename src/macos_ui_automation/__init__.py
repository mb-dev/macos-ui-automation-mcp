"""
macOS UI Automation Framework

A Python-based framework for automating macOS applications using
accessibility APIs, with clean architecture and testing support.

Key Features:
- Clean element abstraction with Element, Application, Workspace
- Bridge-based architecture for testing (real vs fake implementations)
- Powerful JSONPath selectors for element targeting
- Type-safe Pydantic models for UI state representation
- MCP server for LLM integration
- CLI for command-line usage

Quick Start:
    from macos_ui_automation import System, JSONPathSelector
    from macos_ui_automation.core import SystemStateDumper

    # Create system (use use_fake=True for testing)
    system = System()

    # Dump current UI state
    dumper = SystemStateDumper()
    ui_state = dumper.dump_system_state()

    # Select elements using JSONPath
    selector = JSONPathSelector(ui_state)
    buttons = selector.find("$..[?(@.role=='AXButton')]")

    # Get applications
    workspace = system.get_workspace()
    apps = workspace.get_running_applications()
"""

__version__ = "0.1.0"

# Core exports - main classes users will interact with
# Bridges (for advanced users/testing)
from .bridges import create_pyobjc_bridge, get_pyobjc_bridge
from .core import Application, AttributeConstants, Element, System, Workspace

# Models
from .models import MenuBarItem, Position, Size, UIElement, WindowState

# Selectors
from .selectors import JSONPathSelector

__all__ = [
    "Application",
    "AttributeConstants",
    "Element",
    # Selectors
    "JSONPathSelector",
    "MenuBarItem",
    # Models
    "Position",
    "Size",
    # Core classes
    "System",
    "UIElement",
    "WindowState",
    "Workspace",
    "create_pyobjc_bridge",
    # Bridge utilities
    "get_pyobjc_bridge",
]
