"""
Unit tests for core/elements.py using fake bridge system.

Tests Element, Application, Workspace, System classes without mocks,
demonstrating the power of the bridge architecture.
"""

import pytest

from macos_ui_automation.bridges.fake_bridge import (
    FakeApplicationBridge,
    FakeAXUIElement,
    FakeNSRunningApplication,
    FakePyObjCBridge,
    FakeWorkspaceBridge,
)
from macos_ui_automation.core.elements import (
    Application,
    AttributeConstants,
    Element,
    System,
    Workspace,
)


class TestElement:
    """Test Element class with fake bridge."""

    def setup_method(self):
        """Set up test with fake bridge."""
        self.bridge = FakePyObjCBridge()

        # Create test element
        self.test_element_ref = FakeAXUIElement(
            element_id="test_element",
            attributes={
                "kAXTitleAttribute": "Test Button",
                "kAXRoleAttribute": "AXButton",
                "kAXEnabledAttribute": True,
                "kAXFocusedAttribute": False,
            },
            actions=["AXPress"],
        )

        self.element = Element(self.test_element_ref, self.bridge)

    def test_simple_attributes(self):
        """Test getting simple string and boolean attributes."""
        assert self.element.get_attribute_value("title") == "Test Button"
        assert self.element.get_attribute_value("role") == "AXButton"
        assert self.element.get_attribute_value("enabled") is True
        assert self.element.get_attribute_value("focused") is False

    def test_missing_attribute(self):
        """Test getting attribute that doesn't exist."""
        result = self.element.get_attribute_value("nonexistent")
        assert result is None

    def test_attribute_constants(self):
        """Test using AttributeConstants enum."""
        title = self.element.get_attribute_value(AttributeConstants.TITLE.value)
        assert title == "Test Button"

        role = self.element.get_attribute_value(AttributeConstants.ROLE.value)
        assert role == "AXButton"

    def test_get_attribute_names(self):
        """Test getting all attribute names."""
        names = self.element.get_attribute_names()
        assert isinstance(names, list)
        assert "kAXTitleAttribute" in names
        assert "kAXRoleAttribute" in names

    def test_get_actions(self):
        """Test getting available actions."""
        actions = self.element.get_actions()
        assert isinstance(actions, list)
        assert "AXPress" in actions

    def test_perform_action(self):
        """Test performing an action."""
        # Should succeed for valid action
        result = self.element.perform_action("AXPress")
        assert result is True

        # Should fail for invalid action
        result = self.element.perform_action("NonexistentAction")
        assert result is False

    def test_set_attribute_value(self):
        """Test setting attribute values."""
        # Test setting a simple value
        result = self.element.set_attribute_value("title", "New Title")
        assert result is True

        # Verify it was set
        assert self.element.get_attribute_value("title") == "New Title"

    def test_element_wrapping_single(self):
        """Test wrapping single child elements."""
        child_element = FakeAXUIElement(
            element_id="child",
            attributes={
                "kAXTitleAttribute": "Child Element",
                "kAXRoleAttribute": "AXTextField",
            },
        )

        self.test_element_ref.attributes["kAXMainWindowAttribute"] = child_element

        main_window = self.element.get_attribute_value("main_window")
        assert isinstance(main_window, Element)
        assert main_window.get_attribute_value("title") == "Child Element"

    def test_element_wrapping_list(self):
        """Test wrapping lists of child elements."""
        child1 = FakeAXUIElement("child1", attributes={"kAXTitleAttribute": "Button 1"})
        child2 = FakeAXUIElement("child2", attributes={"kAXTitleAttribute": "Button 2"})

        # Set children directly on the element (the fake bridge uses this)
        self.test_element_ref.children = [child1, child2]

        children = self.element.get_attribute_value("children")
        assert isinstance(children, list)
        assert len(children) == 2
        assert all(isinstance(child, Element) for child in children)
        assert children[0].get_attribute_value("title") == "Button 1"
        assert children[1].get_attribute_value("title") == "Button 2"


class TestApplication:
    """Test Application class with fake bridge."""

    def setup_method(self):
        """Set up test with fake application bridge."""
        self.app_bridge = FakeApplicationBridge()
        self.fake_ns_app = FakeNSRunningApplication(
            name="Test App",
            pid=1234,
            bundle_id="com.test.app",
            active=True,
            hidden=False,
        )
        self.app = Application(self.fake_ns_app, self.app_bridge)

    def test_get_name(self):
        """Test getting application name."""
        assert self.app.get_name() == "Test App"

    def test_get_pid(self):
        """Test getting process ID."""
        assert self.app.get_pid() == 1234

    def test_get_bundle_id(self):
        """Test getting bundle identifier."""
        assert self.app.get_bundle_id() == "com.test.app"

    def test_is_active(self):
        """Test checking if application is active."""
        assert self.app.is_active() is True

    def test_is_hidden(self):
        """Test checking if application is hidden."""
        assert self.app.is_hidden() is False


class TestWorkspace:
    """Test Workspace class with fake bridges."""

    def setup_method(self):
        """Set up test with fake workspace and application bridges."""
        self.workspace_bridge = FakeWorkspaceBridge()
        self.app_bridge = FakeApplicationBridge()
        self.workspace = Workspace(self.workspace_bridge, self.app_bridge)

    def test_get_running_applications(self):
        """Test getting list of running applications."""
        apps = self.workspace.get_running_applications()

        assert isinstance(apps, list)
        assert len(apps) > 0  # Fake bridge has some test apps

        # Test first app
        first_app = apps[0]
        assert isinstance(first_app, Application)
        assert isinstance(first_app.get_name(), str)
        assert isinstance(first_app.get_pid(), int)

    def test_is_accessibility_trusted(self):
        """Test checking accessibility permissions."""
        # Fake bridge defaults to trusted
        assert self.workspace.is_accessibility_trusted() is True


class TestSystem:
    """Test System class - the main entry point."""

    def test_real_system_creation(self):
        """Test creating system with real bridges (will fallback to fake if PyObjC unavailable)."""
        system = System(use_fake=False)

        workspace = system.get_workspace()
        accessibility = system.get_accessibility()

        assert workspace is not None
        assert accessibility is not None
        assert system.is_available() is True

    def test_fake_system_creation(self):
        """Test creating system with explicit fake bridges."""
        system = System(use_fake=True)

        workspace = system.get_workspace()
        accessibility = system.get_accessibility()

        assert workspace is not None
        assert accessibility is not None
        assert system.is_available() is True

    def test_fake_system_functionality(self):
        """Test full workflow with fake system."""
        system = System(use_fake=True)

        # Get workspace and applications
        workspace = system.get_workspace()
        apps = workspace.get_running_applications()
        assert len(apps) > 0

        # Get accessibility provider
        accessibility = system.get_accessibility()

        # Create application element for first app
        first_app = apps[0]
        app_element = accessibility.create_application_element(first_app.get_pid())
        assert app_element is not None
        assert isinstance(app_element, Element)


class TestAttributeConstants:
    """Test AttributeConstants enum."""

    def test_all_constants_exist(self):
        """Test that all expected constants are defined."""
        expected_constants = [
            "TITLE",
            "ROLE",
            "VALUE",
            "DESCRIPTION",
            "POSITION",
            "SIZE",
            "ENABLED",
            "FOCUSED",
            "CHILDREN",
            "WINDOWS",
            "MAIN_WINDOW",
            "MINIMIZED",
            "IDENTIFIER",
            "MENU_BAR",
            "SELECTED",
            "HELP",
            "URL",
            "TOP_LEVEL_UI_ELEMENT",
            "PARENT",
        ]

        for constant in expected_constants:
            assert hasattr(AttributeConstants, constant)
            assert isinstance(getattr(AttributeConstants, constant).value, str)

    def test_constants_have_meaningful_values(self):
        """Test that constants have the expected string values."""
        assert AttributeConstants.TITLE.value == "title"
        assert AttributeConstants.ROLE.value == "role"
        assert AttributeConstants.ENABLED.value == "enabled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
