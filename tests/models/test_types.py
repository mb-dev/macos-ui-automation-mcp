"""
Unit tests for models/types.py.

Tests the Pydantic models for data validation and serialization.
"""

import pytest
from pydantic import ValidationError

from macos_ui_automation.models.types import (
    MenuBarItem,
    Position,
    Size,
    UIElement,
    WindowState,
)


class TestPosition:
    """Test Position model."""

    def test_valid_position(self):
        """Test creating valid position."""
        pos = Position(x=100, y=200)
        assert pos.x == 100
        assert pos.y == 200

    def test_position_serialization(self):
        """Test position serialization."""
        pos = Position(x=50, y=75)
        data = pos.model_dump()

        assert data == {"x": 50, "y": 75}

    def test_position_from_dict(self):
        """Test creating position from dict."""
        data = {"x": 25, "y": 30}
        pos = Position(**data)

        assert pos.x == 25
        assert pos.y == 30

    def test_negative_coordinates(self):
        """Test that negative coordinates are allowed."""
        pos = Position(x=-10, y=-20)
        assert pos.x == -10
        assert pos.y == -20

    def test_float_conversion(self):
        """Test that floats are converted to integers."""
        pos = Position(x=10.7, y=20.3)
        assert pos.x == 10
        assert pos.y == 20


class TestSize:
    """Test Size model."""

    def test_valid_size(self):
        """Test creating valid size."""
        size = Size(width=800, height=600)
        assert size.width == 800
        assert size.height == 600

    def test_size_serialization(self):
        """Test size serialization."""
        size = Size(width=400, height=300)
        data = size.model_dump()

        assert data == {"width": 400, "height": 300}

    def test_zero_dimensions(self):
        """Test that zero dimensions are allowed."""
        size = Size(width=0, height=0)
        assert size.width == 0
        assert size.height == 0

    def test_large_dimensions(self):
        """Test large dimensions."""
        size = Size(width=999999, height=999999)
        assert size.width == 999999
        assert size.height == 999999


class TestUIElement:
    """Test UIElement model."""

    def test_minimal_element(self):
        """Test creating element with minimal required fields."""
        element = UIElement(role="AXButton", element_type="button")
        assert element.role == "AXButton"
        assert element.element_type == "button"
        assert element.title is None  # Optional field

    def test_full_element(self):
        """Test creating element with all fields."""
        element = UIElement(
            role="AXButton",
            element_type="button",
            title="Submit",
            ax_identifier="submit-btn",
            enabled=True,
            focused=False,
            position=Position(x=100, y=200),
            size=Size(width=80, height=30),
            value="Click me",
            actions=["AXPress"],
            children_count=0,
        )

        assert element.title == "Submit"
        assert element.ax_identifier == "submit-btn"
        assert element.enabled is True
        assert element.position.x == 100
        assert element.size.width == 80
        assert element.actions == ["AXPress"]

    def test_element_serialization(self):
        """Test element serialization."""
        element = UIElement(
            role="AXTextField",
            element_type="textfield",
            title="Username",
            position=Position(x=50, y=100),
            size=Size(width=200, height=25),
        )

        data = element.model_dump()

        assert data["role"] == "AXTextField"
        assert data["title"] == "Username"
        assert data["position"] == {"x": 50, "y": 100}
        assert data["size"] == {"width": 200, "height": 25}

    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError):
            UIElement()  # Missing required fields

    def test_invalid_field_types(self):
        """Test validation error for invalid field types."""
        with pytest.raises(ValidationError):
            UIElement(
                role="AXButton",
                element_type="button",
                enabled="not_a_boolean",  # Should be boolean
            )


class TestWindowState:
    """Test WindowState model."""

    def test_minimal_window(self):
        """Test creating window with minimal fields."""
        window = WindowState(title="Test Window", window_id=123)
        assert window.title == "Test Window"
        assert window.window_id == 123

    def test_full_window(self):
        """Test creating window with all fields."""
        window = WindowState(
            title="Main Window",
            window_id=456,
            position=Position(x=100, y=100),
            size=Size(width=800, height=600),
            minimized=False,
            children=[],
        )

        assert window.title == "Main Window"
        assert window.minimized is False
        assert window.children == []

    def test_window_with_elements(self):
        """Test window with UI elements."""
        element = UIElement(role="AXButton", element_type="button")
        window = WindowState(
            title="Window with Button", window_id=789, children=[element]
        )

        assert len(window.children) == 1
        assert window.children[0].role == "AXButton"


class TestMenuBarItem:
    """Test MenuBarItem model."""

    def test_basic_menu_item(self):
        """Test creating basic menu item."""
        item = MenuBarItem(title="File", enabled=True)
        assert item.title == "File"
        assert item.enabled is True

    def test_menu_item_with_submenu(self):
        """Test menu item with submenu."""
        submenu_item = MenuBarItem(title="Save As...", enabled=True)
        main_item = MenuBarItem(title="File", enabled=True, submenu=[submenu_item])

        assert len(main_item.submenu) == 1
        assert main_item.submenu[0].title == "Save As..."

    def test_nested_submenu(self):
        """Test deeply nested submenu structure."""
        deep_item = MenuBarItem(title="Deep Item", enabled=True)
        mid_item = MenuBarItem(title="Mid Item", enabled=True, submenu=[deep_item])
        top_item = MenuBarItem(title="Top Item", enabled=True, submenu=[mid_item])

        assert top_item.submenu[0].submenu[0].title == "Deep Item"

    def test_disabled_menu_item(self):
        """Test disabled menu item."""
        item = MenuBarItem(title="Disabled Item", enabled=False)
        assert item.enabled is False


class TestModelIntegration:
    """Test integration between different models."""

    def test_complex_ui_structure(self):
        """Test complex UI structure with nested models."""
        # Create a complex window with multiple elements
        button = UIElement(
            role="AXButton",
            element_type="button",
            title="Submit",
            position=Position(x=200, y=300),
            size=Size(width=100, height=30),
            enabled=True,
        )

        text_field = UIElement(
            role="AXTextField",
            element_type="textfield",
            position=Position(x=200, y=250),
            size=Size(width=200, height=25),
            value="Enter text here",
        )

        window = WindowState(
            title="Login Form",
            window_id=1001,
            position=Position(x=100, y=100),
            size=Size(width=400, height=300),
            children=[text_field, button],
        )

        # Test serialization of complex structure
        data = window.model_dump()

        assert data["title"] == "Login Form"
        assert len(data["children"]) == 2
        assert data["children"][0]["role"] == "AXTextField"
        assert data["children"][1]["title"] == "Submit"

    def test_model_reconstruction(self):
        """Test reconstructing models from serialized data."""
        # Create original models
        original_pos = Position(x=50, y=100)
        original_size = Size(width=200, height=150)

        # Serialize
        pos_data = original_pos.model_dump()
        size_data = original_size.model_dump()

        # Reconstruct
        reconstructed_pos = Position(**pos_data)
        reconstructed_size = Size(**size_data)

        # Verify
        assert reconstructed_pos.x == original_pos.x
        assert reconstructed_pos.y == original_pos.y
        assert reconstructed_size.width == original_size.width
        assert reconstructed_size.height == original_size.height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
