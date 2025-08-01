"""
Unit tests for bridges/factory.py.

Tests the bridge factory functions for dependency injection.
"""

import pytest

from macos_ui_automation.bridges.factory import (
    create_pyobjc_bridge,
    get_application_bridge,
    get_pyobjc_bridge,
    get_workspace_bridge,
    reset_bridges,
    set_bridge_instances,
)
from macos_ui_automation.bridges.fake_bridge import (
    FakeApplicationBridge,
    FakePyObjCBridge,
    FakeWorkspaceBridge,
)
from macos_ui_automation.bridges.interfaces import (
    ApplicationBridge,
    PyObjCBridge,
    WorkspaceBridge,
)
from macos_ui_automation.core.registry import reset_test_mode, set_test_mode


def setup_module():
    """Enable test mode for all tests in this module."""
    set_test_mode(True)


def teardown_module():
    """Disable test mode after all tests in this module."""
    reset_test_mode()


class TestBridgeFactory:
    """Test bridge factory functions."""

    def test_create_fake_bridge(self):
        """Test creating fake bridges explicitly."""
        pyobjc_bridge, workspace_bridge, app_bridge = create_pyobjc_bridge(
            force_fake=True
        )

        assert isinstance(pyobjc_bridge, FakePyObjCBridge)
        assert isinstance(workspace_bridge, FakeWorkspaceBridge)
        assert isinstance(app_bridge, FakeApplicationBridge)

    def test_create_bridge_with_test_mode(self):
        """Test creating bridges with test mode enabled."""
        # Test mode is already enabled in setup_module
        pyobjc_bridge, workspace_bridge, app_bridge = create_pyobjc_bridge()

        assert isinstance(pyobjc_bridge, FakePyObjCBridge)
        assert isinstance(workspace_bridge, FakeWorkspaceBridge)
        assert isinstance(app_bridge, FakeApplicationBridge)

    def test_create_real_bridge_fallback(self):
        """Test that real bridge creation falls back to fake if PyObjC unavailable."""
        # This will likely fall back to fake since PyObjC may not be available in test environment
        pyobjc_bridge, workspace_bridge, app_bridge = create_pyobjc_bridge(
            force_fake=False
        )

        # Just verify we get valid bridge instances
        assert isinstance(pyobjc_bridge, PyObjCBridge)
        assert isinstance(workspace_bridge, WorkspaceBridge)
        assert isinstance(app_bridge, ApplicationBridge)

    def test_get_bridge_functions(self):
        """Test individual bridge getter functions."""
        # Test mode is already enabled in setup_module
        pyobjc_bridge = get_pyobjc_bridge()
        workspace_bridge = get_workspace_bridge()
        app_bridge = get_application_bridge()

        assert isinstance(pyobjc_bridge, FakePyObjCBridge)
        assert isinstance(workspace_bridge, FakeWorkspaceBridge)
        assert isinstance(app_bridge, FakeApplicationBridge)

    def test_bridge_caching(self):
        """Test that bridges are cached properly."""
        # Test mode is already enabled in setup_module
        # Get bridges twice
        bridge1 = get_pyobjc_bridge()
        bridge2 = get_pyobjc_bridge()

        # Should be the same instance
        assert bridge1 is bridge2

    def test_reset_bridges(self):
        """Test resetting bridge instances."""
        # Test mode is already enabled in setup_module
        # Get initial bridge
        bridge1 = get_pyobjc_bridge()

        # Reset bridges
        reset_bridges()

        # Get new bridge
        bridge2 = get_pyobjc_bridge()

        # Should be different instances
        assert bridge1 is not bridge2

    def test_set_bridge_instances(self):
        """Test setting custom bridge instances."""
        # Create custom fake bridges
        custom_pyobjc = FakePyObjCBridge()
        custom_workspace = FakeWorkspaceBridge()
        custom_app = FakeApplicationBridge()

        # Set custom instances
        set_bridge_instances(custom_pyobjc, custom_workspace, custom_app)

        # Verify they're used
        assert get_pyobjc_bridge() is custom_pyobjc
        assert get_workspace_bridge() is custom_workspace
        assert get_application_bridge() is custom_app

    def test_force_fake_parameter(self):
        """Test force_fake parameter overrides."""
        # Even without test mode, force_fake should work
        reset_test_mode()
        try:
            pyobjc_bridge, workspace_bridge, app_bridge = create_pyobjc_bridge(
                force_fake=True
            )

            assert isinstance(pyobjc_bridge, FakePyObjCBridge)
            assert isinstance(workspace_bridge, FakeWorkspaceBridge)
            assert isinstance(app_bridge, FakeApplicationBridge)
        finally:
            set_test_mode(True)  # Restore test mode

    def test_bridge_interfaces(self):
        """Test that bridges implement expected interfaces."""
        pyobjc_bridge, workspace_bridge, app_bridge = create_pyobjc_bridge(
            force_fake=True
        )

        # Test PyObjCBridge interface
        assert hasattr(pyobjc_bridge, "is_process_trusted")
        assert hasattr(pyobjc_bridge, "create_application")
        assert hasattr(pyobjc_bridge, "copy_attribute_value")
        assert hasattr(pyobjc_bridge, "copy_attribute_names")
        assert hasattr(pyobjc_bridge, "perform_action")

        # Test WorkspaceBridge interface
        assert hasattr(workspace_bridge, "get_running_applications")
        assert hasattr(workspace_bridge, "get_frontmost_application")

        # Test ApplicationBridge interface
        assert hasattr(app_bridge, "get_localized_name")
        assert hasattr(app_bridge, "get_process_identifier")
        assert hasattr(app_bridge, "get_bundle_identifier")
        assert hasattr(app_bridge, "is_active")
        assert hasattr(app_bridge, "is_hidden")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
