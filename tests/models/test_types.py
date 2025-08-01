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

# Test constants to avoid magic values
SAMPLE_X = 100
SAMPLE_Y = 200
SMALL_X = 50
SMALL_Y = 75
TEST_X = 25
TEST_Y = 30
NEGATIVE_X = -10
NEGATIVE_Y = -20
FLOAT_X_RESULT = 10
FLOAT_Y_RESULT = 20
STANDARD_WIDTH = 800
STANDARD_HEIGHT = 600
SMALL_WIDTH = 400
SMALL_HEIGHT = 300
LARGE_DIMENSION = 999999
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 30
TEXT_FIELD_WIDTH = 200
TEXT_FIELD_HEIGHT = 25
WINDOW_ID = 123
ANOTHER_WINDOW_ID = 456
THIRD_WINDOW_ID = 789
FORM_WINDOW_ID = 1001
EXPECTED_CHILDREN_COUNT = 2


class TestPosition:
    """Test Position model."""

    def test_valid_position(self):
        """Test creating valid position."""
        pos = Position(x=SAMPLE_X, y=SAMPLE_Y)
        assert pos.x == SAMPLE_X
        assert pos.y == SAMPLE_Y

    def test_position_serialization(self):
        """Test position serialization."""
        pos = Position(x=SMALL_X, y=SMALL_Y)
        data = pos.model_dump()

        assert data == {"x": SMALL_X, "y": SMALL_Y}

    def test_position_from_dict(self):
        """Test creating position from dict."""
        data = {"x": TEST_X, "y": TEST_Y}
        pos = Position(**data)

        assert pos.x == TEST_X
        assert pos.y == TEST_Y

    def test_negative_coordinates(self):
        """Test that negative coordinates are allowed."""
        pos = Position(x=NEGATIVE_X, y=NEGATIVE_Y)
        assert pos.x == NEGATIVE_X
        assert pos.y == NEGATIVE_Y

    def test_float_conversion(self):
        """Test that floats are converted to integers."""
        pos = Position(x=10.7, y=20.3)
        assert pos.x == FLOAT_X_RESULT
        assert pos.y == FLOAT_Y_RESULT


class TestSize:
    """Test Size model."""

    def test_valid_size(self):
        """Test creating valid size."""
        size = Size(width=STANDARD_WIDTH, height=STANDARD_HEIGHT)
        assert size.width == STANDARD_WIDTH
        assert size.height == STANDARD_HEIGHT

    def test_size_serialization(self):
        """Test size serialization."""
        size = Size(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        data = size.model_dump()

        assert data == {"width": SMALL_WIDTH, "height": SMALL_HEIGHT}

    def test_zero_dimensions(self):
        """Test that zero dimensions are allowed."""
        size = Size(width=0, height=0)
        assert size.width == 0
        assert size.height == 0

    def test_large_dimensions(self):
        """Test large dimensions."""
        size = Size(width=LARGE_DIMENSION, height=LARGE_DIMENSION)
        assert size.width == LARGE_DIMENSION
        assert size.height == LARGE_DIMENSION


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
            position=Position(x=SAMPLE_X, y=SAMPLE_Y),
            size=Size(width=BUTTON_WIDTH, height=BUTTON_HEIGHT),
            value="Click me",
            actions=["AXPress"],
            children_count=0,
        )

        assert element.title == "Submit"
        assert element.ax_identifier == "submit-btn"
        assert element.enabled is True
        assert element.position.x == SAMPLE_X
        assert element.size.width == BUTTON_WIDTH
        assert element.actions == ["AXPress"]

    def test_element_serialization(self):
        """Test element serialization."""
        element = UIElement(
            role="AXTextField",
            element_type="textfield",
            title="Username",
            position=Position(x=SMALL_X, y=100),
            size=Size(width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT),
        )

        data = element.model_dump()

        assert data["role"] == "AXTextField"
        assert data["title"] == "Username"
        assert data["position"] == {"x": SMALL_X, "y": 100}
        assert data["size"] == {"width": TEXT_FIELD_WIDTH, "height": TEXT_FIELD_HEIGHT}

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
        window = WindowState(title="Test Window", window_id=WINDOW_ID)
        assert window.title == "Test Window"
        assert window.window_id == WINDOW_ID

    def test_full_window(self):
        """Test creating window with all fields."""
        window = WindowState(
            title="Main Window",
            window_id=ANOTHER_WINDOW_ID,
            position=Position(x=SAMPLE_X, y=SAMPLE_X),
            size=Size(width=STANDARD_WIDTH, height=STANDARD_HEIGHT),
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
            title="Window with Button", window_id=THIRD_WINDOW_ID, children=[element]
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
            position=Position(x=SAMPLE_Y, y=300),
            size=Size(width=SAMPLE_X, height=BUTTON_HEIGHT),
            enabled=True,
        )

        text_field = UIElement(
            role="AXTextField",
            element_type="textfield",
            position=Position(x=SAMPLE_Y, y=250),
            size=Size(width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT),
            value="Enter text here",
        )

        window = WindowState(
            title="Login Form",
            window_id=FORM_WINDOW_ID,
            position=Position(x=SAMPLE_X, y=SAMPLE_X),
            size=Size(width=SMALL_WIDTH, height=SMALL_HEIGHT),
            children=[text_field, button],
        )

        # Test serialization of complex structure
        data = window.model_dump()

        assert data["title"] == "Login Form"
        assert len(data["children"]) == EXPECTED_CHILDREN_COUNT
        assert data["children"][0]["role"] == "AXTextField"
        assert data["children"][1]["title"] == "Submit"

    def test_model_reconstruction(self):
        """Test reconstructing models from serialized data."""
        # Create original models
        original_pos = Position(x=SMALL_X, y=SAMPLE_X)
        original_size = Size(width=TEXT_FIELD_WIDTH, height=150)

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
