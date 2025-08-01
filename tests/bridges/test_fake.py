"""
Unit tests for bridges/fake_bridge.py.

Tests the fake bridge implementations to ensure they provide
realistic test data and behavior.
"""

import pytest

from macos_ui_automation.bridges.fake_bridge import (
    FakeApplicationBridge,
    FakeAXUIElement,
    FakeAXValue,
    FakeNSRunningApplication,
    FakePyObjCBridge,
    FakeWorkspaceBridge,
)
from macos_ui_automation.bridges.types import AXError, AXValueType

# Constants for magic values
AX_MOCK_TYPE_ID = 12345
AX_ELEMENT_TYPE_ID = 54321
TEST_PID_DEFAULT = 1234
TEST_PID_CUSTOM = 5555
TEST_PID_INCOMPLETE = 6666
TEST_PID_FRONTMOST = 8888
TEST_PID_ADD_CUSTOM = 9999
EXPECTED_CHILDREN_COUNT = 2


class TestFakeAXValue:
    """Test FakeAXValue class."""

    def test_string_representation_point(self):
        """Test string representation for CGPoint."""
        value = FakeAXValue(AXValueType.CGPOINT.value, {"x": 100, "y": 200})
        str_repr = str(value)

        assert "kAXValueCGPointType" in str_repr
        assert "x:100" in str_repr
        assert "y:200" in str_repr

    def test_string_representation_size(self):
        """Test string representation for CGSize."""
        value = FakeAXValue(AXValueType.CGSIZE.value, {"width": 150, "height": 50})
        str_repr = str(value)

        assert "kAXValueCGSizeType" in str_repr
        assert "w:150" in str_repr
        assert "h:50" in str_repr

    def test_string_representation_rect(self):
        """Test string representation for CGRect."""
        value = FakeAXValue(
            AXValueType.CGRECT.value, {"x": 10, "y": 20, "width": 100, "height": 50}
        )
        str_repr = str(value)

        assert "kAXValueCGRectType" in str_repr
        assert "x:10" in str_repr
        assert "y:20" in str_repr
        assert "w:100" in str_repr
        assert "h:50" in str_repr

    def test_cf_type_id(self):
        """Test _cf_type_id mock attribute."""
        value = FakeAXValue(AXValueType.CGPOINT.value, {"x": 0, "y": 0})
        assert hasattr(value, "_cf_type_id")
        assert value._cf_type_id() == AX_MOCK_TYPE_ID


class TestFakeAXUIElement:
    """Test FakeAXUIElement class."""

    def test_basic_creation(self):
        """Test creating basic element."""
        element = FakeAXUIElement(
            element_id="test",
            attributes={"kAXTitleAttribute": "Test Element"},
            actions=["AXPress"],
        )

        assert element.element_id == "test"
        assert element.attributes["kAXTitleAttribute"] == "Test Element"
        assert "AXPress" in element.actions

    def test_cf_type_id(self):
        """Test _cf_type_id mock attribute."""
        element = FakeAXUIElement("test")
        assert hasattr(element, "_cf_type_id")
        assert element._cf_type_id() == AX_ELEMENT_TYPE_ID

    def test_hierarchy(self):
        """Test element hierarchy."""
        child1 = FakeAXUIElement("child1")
        child2 = FakeAXUIElement("child2")
        parent = FakeAXUIElement("parent", children=[child1, child2])

        assert len(parent.children) == EXPECTED_CHILDREN_COUNT
        assert child1.parent == parent
        assert child2.parent == parent


class TestFakeNSRunningApplication:
    """Test FakeNSRunningApplication class."""

    def test_basic_properties(self):
        """Test basic application properties."""
        app = FakeNSRunningApplication(
            name="Test App",
            pid=1234,
            bundle_id="com.test.app",
            active=True,
            hidden=False,
        )

        assert app.name == "Test App"
        assert app.pid == TEST_PID_DEFAULT
        assert app.bundle_id == "com.test.app"
        assert app.active is True
        assert app.hidden is False


class TestFakePyObjCBridge:
    """Test FakePyObjCBridge class."""

    def setup_method(self):
        """Set up test bridge."""
        self.bridge = FakePyObjCBridge()

    def test_is_process_trusted(self):
        """Test accessibility trust check."""
        assert self.bridge.is_process_trusted() is True

        # Test setting trust status
        self.bridge.set_process_trusted(trusted=False)
        assert self.bridge.is_process_trusted() is False

    def test_create_application(self):
        """Test creating application element."""
        element_ref = self.bridge.create_application(1234)
        assert element_ref is not None

        # Should be a FakeAXUIElement
        assert hasattr(element_ref, "element_id")
        assert hasattr(element_ref, "attributes")

    def test_copy_attribute_value_success(self):
        """Test copying attribute value successfully."""
        # Use pre-existing test element from setup
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error, value = self.bridge.copy_attribute_value(test_app, "kAXTitleAttribute")
        assert error == AXError.SUCCESS
        assert value == "Test App"

    def test_copy_attribute_value_unsupported(self):
        """Test copying unsupported attribute."""
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error, value = self.bridge.copy_attribute_value(
            test_app, "kAXNonexistentAttribute"
        )
        assert error == AXError.ATTRIBUTE_UNSUPPORTED
        assert value is None

    def test_copy_attribute_names(self):
        """Test getting attribute names."""
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error, attributes = self.bridge.copy_attribute_names(test_app)
        assert error == AXError.SUCCESS
        assert isinstance(attributes, list)
        assert len(attributes) > 0

    def test_copy_action_names(self):
        """Test getting action names."""
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error, actions = self.bridge.copy_action_names(test_app)
        assert error == AXError.SUCCESS
        assert isinstance(actions, list)

    def test_set_attribute_value(self):
        """Test setting attribute value."""
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error = self.bridge.set_attribute_value(
            test_app, "kAXTitleAttribute", "New Title"
        )
        assert error == AXError.SUCCESS

        # Verify it was set
        error, value = self.bridge.copy_attribute_value(test_app, "kAXTitleAttribute")
        assert error == AXError.SUCCESS
        assert value == "New Title"

    def test_perform_action_success(self):
        """Test performing valid action."""
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error = self.bridge.perform_action(test_app, "AXPress")
        assert error == AXError.SUCCESS

    def test_perform_action_unsupported(self):
        """Test performing unsupported action."""
        test_app = self.bridge._applications[TEST_PID_DEFAULT]

        error = self.bridge.perform_action(test_app, "NonexistentAction")
        assert error == AXError.ACTION_UNSUPPORTED

    def test_ax_value_operations(self):
        """Test AXValue get/create operations."""
        # Create AXValue
        fake_value = FakeAXValue(AXValueType.CGPOINT.value, {"x": 100, "y": 200})

        # Test getting value type
        value_type = self.bridge.get_value_type(fake_value)
        assert value_type == AXValueType.CGPOINT.value

        # Test getting value data
        data = self.bridge.get_value(fake_value, AXValueType.CGPOINT.value)
        assert data == {"x": 100, "y": 200}

        # Test creating AXValue
        new_value = self.bridge.create_ax_value(
            AXValueType.CGSIZE.value, {"width": 50, "height": 25}
        )
        assert isinstance(new_value, FakeAXValue)

    def test_add_test_element(self):
        """Test adding custom test elements."""
        custom_element = FakeAXUIElement(
            "custom", attributes={"kAXTitleAttribute": "Custom Element"}
        )

        self.bridge.add_test_element(custom_element)
        assert custom_element in self.bridge._elements.values()


class TestFakeWorkspaceBridge:
    """Test FakeWorkspaceBridge class."""

    def setup_method(self):
        """Set up test workspace bridge."""
        self.bridge = FakeWorkspaceBridge()

    def test_get_running_applications(self):
        """Test getting running applications."""
        apps = self.bridge.get_running_applications()

        assert isinstance(apps, list)
        assert len(apps) > 0

        # Check first app
        first_app = apps[0]
        assert hasattr(first_app, "name")
        assert hasattr(first_app, "pid")

    def test_get_frontmost_application(self):
        """Test getting frontmost application."""
        app = self.bridge.get_frontmost_application()
        assert app is not None
        assert hasattr(app, "name")

    def test_add_application(self):
        """Test adding custom application."""
        custom_app = FakeNSRunningApplication(
            "Custom App", TEST_PID_ADD_CUSTOM, "com.custom.app"
        )

        initial_count = len(self.bridge.get_running_applications())
        self.bridge.add_application(custom_app)
        new_count = len(self.bridge.get_running_applications())

        assert new_count == initial_count + 1

    def test_set_frontmost_application(self):
        """Test setting frontmost application."""
        custom_app = FakeNSRunningApplication(
            "Frontmost App", TEST_PID_FRONTMOST, "com.frontmost.app"
        )

        self.bridge.set_frontmost_application(custom_app)
        frontmost = self.bridge.get_frontmost_application()

        assert frontmost == custom_app


class TestFakeApplicationBridge:
    """Test FakeApplicationBridge class."""

    def setup_method(self):
        """Set up test application bridge."""
        self.bridge = FakeApplicationBridge()
        self.test_app = FakeNSRunningApplication(
            name="Test App",
            pid=TEST_PID_CUSTOM,
            bundle_id="com.test.app",
            active=True,
            hidden=False,
        )

    def test_get_localized_name(self):
        """Test getting localized name."""
        name = self.bridge.get_localized_name(self.test_app)
        assert name == "Test App"

    def test_get_process_identifier(self):
        """Test getting process identifier."""
        pid = self.bridge.get_process_identifier(self.test_app)
        assert pid == TEST_PID_CUSTOM

    def test_get_bundle_identifier(self):
        """Test getting bundle identifier."""
        bundle_id = self.bridge.get_bundle_identifier(self.test_app)
        assert bundle_id == "com.test.app"

    def test_is_active(self):
        """Test checking if application is active."""
        assert self.bridge.is_active(self.test_app) is True

    def test_is_hidden(self):
        """Test checking if application is hidden."""
        assert self.bridge.is_hidden(self.test_app) is False

    def test_missing_attributes(self):
        """Test handling missing attributes gracefully."""
        incomplete_app = FakeNSRunningApplication("Incomplete", TEST_PID_INCOMPLETE)
        # bundle_id is None by default

        name = self.bridge.get_localized_name(incomplete_app)
        assert name == "Incomplete"

        bundle_id = self.bridge.get_bundle_identifier(incomplete_app)
        assert bundle_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
