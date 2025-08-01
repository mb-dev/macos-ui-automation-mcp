"""
Factory for creating PyObjC bridge implementations.

This module provides factory functions to create the appropriate bridge
implementation based on the environment and testing requirements.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# Import moved inside function to avoid circular imports

if TYPE_CHECKING:
    from .fake_bridge import FakeAXUIElement, FakeNSRunningApplication
    from .interfaces import ApplicationBridge, PyObjCBridge, WorkspaceBridge

# Import bridge classes at module level to avoid PLC0415
try:
    from .fake_bridge import (
        FakeApplicationBridge,
        FakePyObjCBridge,
        FakeWorkspaceBridge,
    )
except ImportError:
    FakeApplicationBridge = None
    FakePyObjCBridge = None
    FakeWorkspaceBridge = None

try:
    from .real_bridge import (
        RealApplicationBridge,
        RealPyObjCBridge,
        RealWorkspaceBridge,
    )
except ImportError:
    RealApplicationBridge = None
    RealPyObjCBridge = None
    RealWorkspaceBridge = None

logger = logging.getLogger(__name__)

# Global bridge instances
_pyobjc_bridge: PyObjCBridge | None = None
_workspace_bridge: WorkspaceBridge | None = None
_application_bridge: ApplicationBridge | None = None


def create_fake_bridges_with_system(
    applications: dict[int, FakeAXUIElement],
    running_apps: list[FakeNSRunningApplication],
) -> tuple[PyObjCBridge, WorkspaceBridge, ApplicationBridge]:
    """
    Create fake bridges with specific fake objects.

    Args:
        applications: Dict of PID -> FakeAXUIElement for applications
        running_apps: List of FakeNSRunningApplication objects

    Returns:
        Tuple of (FakePyObjCBridge, FakeWorkspaceBridge, FakeApplicationBridge)
    """
    if not all([FakePyObjCBridge, FakeWorkspaceBridge, FakeApplicationBridge]):
        msg = "Fake bridge classes not available"
        raise ImportError(msg)

    return (
        FakePyObjCBridge(applications),
        FakeWorkspaceBridge(running_apps),
        FakeApplicationBridge(),
    )


def create_pyobjc_bridge(
    *,
    force_fake: bool = False,
) -> tuple[PyObjCBridge, WorkspaceBridge, ApplicationBridge]:
    """
    Create PyObjC bridge implementations.

    Args:
        force_fake: If True, always use fake implementations

    Returns:
        Tuple of (PyObjCBridge, WorkspaceBridge, ApplicationBridge)
    """
    # Use explicit force_fake parameter or check if we're in test mode
    # Import here to avoid circular imports
    from macos_ui_automation.core.registry import is_test_mode

    use_fake = force_fake or is_test_mode()

    # If in test mode and bridges are already set globally, use those
    if (
        use_fake
        and _pyobjc_bridge is not None
        and _workspace_bridge is not None
        and _application_bridge is not None
    ):
        return _pyobjc_bridge, _workspace_bridge, _application_bridge

    if use_fake:
        logger.info("Using fake PyObjC bridge for testing")
        if not all([FakePyObjCBridge, FakeWorkspaceBridge, FakeApplicationBridge]):
            msg = "Fake bridge classes not available"
            raise ImportError(msg)

        return (
            FakePyObjCBridge(),
            FakeWorkspaceBridge(),
            FakeApplicationBridge(),
        )

    if all([RealPyObjCBridge, RealWorkspaceBridge, RealApplicationBridge]):
        logger.info("Using real PyObjC bridge")
        return (
            RealPyObjCBridge(),
            RealWorkspaceBridge(),
            RealApplicationBridge(),
        )

    logger.warning("Real PyObjC bridge not available, falling back to fake")
    logger.info("Falling back to fake PyObjC bridge")
    if not all([FakePyObjCBridge, FakeWorkspaceBridge, FakeApplicationBridge]):
        msg = "Neither real nor fake bridge classes are available"
        raise ImportError(msg)

    return (
        FakePyObjCBridge(),
        FakeWorkspaceBridge(),
        FakeApplicationBridge(),
    )


def get_pyobjc_bridge() -> PyObjCBridge:
    """
    Get the current PyObjC bridge instance.

    Returns:
        PyObjCBridge implementation
    """
    global _pyobjc_bridge, _workspace_bridge, _application_bridge

    if (
        _pyobjc_bridge is None
        or _workspace_bridge is None
        or _application_bridge is None
    ):
        _pyobjc_bridge, _workspace_bridge, _application_bridge = create_pyobjc_bridge()

    return _pyobjc_bridge


def get_workspace_bridge() -> WorkspaceBridge:
    """
    Get the current workspace bridge instance.

    Returns:
        WorkspaceBridge implementation
    """
    global _pyobjc_bridge, _workspace_bridge, _application_bridge

    if (
        _pyobjc_bridge is None
        or _workspace_bridge is None
        or _application_bridge is None
    ):
        _pyobjc_bridge, _workspace_bridge, _application_bridge = create_pyobjc_bridge()

    return _workspace_bridge


def get_application_bridge() -> ApplicationBridge:
    """
    Get the current application bridge instance.

    Returns:
        ApplicationBridge implementation
    """
    global _pyobjc_bridge, _workspace_bridge, _application_bridge

    if (
        _pyobjc_bridge is None
        or _workspace_bridge is None
        or _application_bridge is None
    ):
        _pyobjc_bridge, _workspace_bridge, _application_bridge = create_pyobjc_bridge()

    return _application_bridge


def reset_bridges() -> None:
    """
    Reset bridge instances.

    Useful for testing when you want to switch between real and fake implementations.
    """
    global _pyobjc_bridge, _workspace_bridge, _application_bridge
    _pyobjc_bridge = None
    _workspace_bridge = None
    _application_bridge = None


def set_bridge_instances(
    pyobjc_bridge: PyObjCBridge,
    workspace_bridge: WorkspaceBridge,
    application_bridge: ApplicationBridge,
) -> None:
    """
    Set specific bridge instances.

    Useful for dependency injection in tests.

    Args:
        pyobjc_bridge: PyObjC bridge implementation
        workspace_bridge: Workspace bridge implementation
        application_bridge: Application bridge implementation
    """
    global _pyobjc_bridge, _workspace_bridge, _application_bridge
    _pyobjc_bridge = pyobjc_bridge
    _workspace_bridge = workspace_bridge
    _application_bridge = application_bridge
