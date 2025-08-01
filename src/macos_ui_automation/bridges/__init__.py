"""
Bridge abstraction layer for UI automation.

This package provides the lowest-level abstraction over platform APIs,
enabling dependency injection for testing.
"""

from .factory import (
    create_pyobjc_bridge,
    get_application_bridge,
    get_pyobjc_bridge,
    get_workspace_bridge,
)
from .interfaces import ApplicationBridge, PyObjCBridge, WorkspaceBridge
from .types import AXError, AXUIElementRef, AXValueRef, AXValueType

__all__ = [
    "AXError",
    "AXUIElementRef",
    "AXValueRef",
    "AXValueType",
    "ApplicationBridge",
    "PyObjCBridge",
    "WorkspaceBridge",
    "create_pyobjc_bridge",
    "get_application_bridge",
    "get_pyobjc_bridge",
    "get_workspace_bridge",
]
