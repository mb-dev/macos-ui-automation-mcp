"""
Pytest integration example for macOS UI automation testing.

This module shows how to integrate the macOS UI automation library
with pytest for automated UI testing workflows.
"""

import time
from typing import TYPE_CHECKING, Any

import pytest

from macos_ui_automation import JSONPathSelector, SystemStateDumper, UIActions

if TYPE_CHECKING:
    from macos_ui_automation.core.models import SystemState


# Constants for test thresholds
MIN_EXPECTED_PROCESSES = 5
MIN_CALCULATOR_BUTTONS = 10
MAX_STATE_CAPTURE_TIME = 5.0
MAX_SEARCH_TIME = 2.0
MAX_TIMEOUT_TOLERANCE = 4.0


class UITestFixture:
    """Test fixture for UI automation testing."""

    def __init__(self, app_name: str | None = None, max_depth: int = 8):
        """Initialize UI test fixture.

        Args:
            app_name: Specific application to focus on (optional)
            max_depth: Maximum depth for UI tree traversal
        """
        self.app_name = app_name
        self.max_depth = max_depth
        self.dumper = SystemStateDumper(max_depth=max_depth, only_visible_children=True)
        self.system_state: SystemState = None
        self.selector: JSONPathSelector = None
        self.actions: UIActions = None

    def setup(self) -> None:
        """Set up test environment."""
        # Capture current UI state
        if self.app_name:
            self.system_state = self.dumper.dump_system_state(
                include_processes=[self.app_name]
            )
        else:
            self.system_state = self.dumper.dump_system_state()

        # Initialize selector and actions
        self.selector = JSONPathSelector(self.system_state)
        self.actions = UIActions(self.selector)

    def teardown(self) -> None:
        """Clean up after test."""
        # Could add cleanup logic here

    def find_elements(self, jsonpath: str) -> list[dict[str, Any]]:
        """Find elements using JSONPath selector."""
        return self.selector.find(jsonpath)

    def assert_element_exists(
        self, jsonpath: str, message: str | None = None
    ) -> dict[str, Any]:
        """Assert that an element exists and return it."""
        elements = self.find_elements(jsonpath)
        if not elements:
            pytest.fail(message or f"Element not found: {jsonpath}")
        return elements[0]

    def assert_element_count(
        self, jsonpath: str, expected_count: int, message: str | None = None
    ) -> list[dict[str, Any]]:
        """Assert specific number of elements exist."""
        elements = self.find_elements(jsonpath)
        if len(elements) != expected_count:
            pytest.fail(
                message
                or (
                    f"Expected {expected_count} elements, "
                    f"found {len(elements)}: {jsonpath}"
                )
            )
        return elements

    def assert_element_enabled(
        self, jsonpath: str, message: str | None = None
    ) -> dict[str, Any]:
        """Assert that an element exists and is enabled."""
        element = self.assert_element_exists(jsonpath, message)
        if not element.get("enabled", False):
            pytest.fail(message or f"Element is not enabled: {jsonpath}")
        return element

    def wait_for_element(
        self, jsonpath: str, timeout: float = 10.0, message: str | None = None
    ) -> dict[str, Any]:
        """Wait for element to appear within timeout."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Refresh UI state
            self.setup()
            elements = self.find_elements(jsonpath)
            if elements:
                return elements[0]
            time.sleep(0.5)

        pytest.fail(message or f"Element not found within {timeout}s: {jsonpath}")


@pytest.fixture
def ui_fixture():
    """Pytest fixture for UI testing."""
    fixture = UITestFixture()
    fixture.setup()
    yield fixture
    fixture.teardown()


@pytest.fixture
def calculator_fixture():
    """Pytest fixture specifically for Calculator app testing."""
    fixture = UITestFixture(app_name="Calculator")
    fixture.setup()
    yield fixture
    fixture.teardown()


# Example test cases
class TestUIAutomation:
    """Test cases for UI automation functionality."""

    def test_system_accessibility(self, ui_fixture):
        """Test that accessibility is enabled and working."""
        assert ui_fixture.system_state.accessibility_enabled, (
            "Accessibility must be enabled"
        )
        assert len(ui_fixture.system_state.processes) > 0, (
            "Should find running processes"
        )

    def test_find_running_applications(self, ui_fixture):
        """Test finding running applications."""
        # Should have at least some applications running
        processes = ui_fixture.system_state.processes
        assert len(processes) >= MIN_EXPECTED_PROCESSES, (
            f"Expected at least {MIN_EXPECTED_PROCESSES} processes, "
            f"found {len(processes)}"
        )

        # Should have at least one frontmost application
        frontmost_apps = [p for p in processes if p.frontmost]
        assert len(frontmost_apps) >= 1, (
            "Should have at least one frontmost application"
        )

    def test_find_ui_elements(self, ui_fixture):
        """Test finding basic UI elements."""
        # Find all buttons
        buttons = ui_fixture.find_elements("$..[?(@.role=='AXButton')]")
        assert len(buttons) > 0, "Should find at least some buttons"

        # Find all text fields
        ui_fixture.find_elements("$..[?(@.role=='AXTextField')]")
        # Note: May be 0 if no text fields are visible

        # Find elements with accessibility identifiers
        ui_fixture.find_elements("$..[?(@.ax_identifier)]")
        # Note: May be 0 if no elements have identifiers

    def test_element_properties(self, ui_fixture):
        """Test element property validation."""
        # Find enabled buttons
        enabled_buttons = ui_fixture.find_elements(
            "$..[?(@.role=='AXButton' && @.enabled==true)]"
        )

        for button in enabled_buttons[:5]:  # Test first 5
            assert "role" in button, "Button should have role property"
            assert button["role"] == "AXButton", "Role should be AXButton"
            assert button.get("enabled"), "Button should be enabled"

            # Check position and size if available
            if button.get("position"):
                pos = button["position"]
                assert "x" in pos, "Position should have x coordinate"
                assert "y" in pos, "Position should have y coordinate"
                assert isinstance(pos["x"], int | float), (
                    "X coordinate should be numeric"
                )
                assert isinstance(pos["y"], int | float), (
                    "Y coordinate should be numeric"
                )

    def test_jsonpath_selectors(self, ui_fixture):
        """Test various JSONPath selector patterns."""
        # Test basic role selection
        buttons = ui_fixture.find_elements("$..[?(@.role=='AXButton')]")

        # Test combination selectors
        enabled_buttons = ui_fixture.find_elements(
            "$..[?(@.role=='AXButton' && @.enabled==true)]"
        )
        assert len(enabled_buttons) <= len(buttons), (
            "Enabled buttons should be subset of all buttons"
        )

        # Test existence checks
        ui_fixture.find_elements("$..[?(@.title)]")
        # Should find some elements with titles

        # Test application-specific selectors
        if ui_fixture.system_state.processes:
            first_app = ui_fixture.system_state.processes[0]
            ui_fixture.find_elements(
                f"$.processes[?(@.name=='{first_app.name}')]..[?(@.role)]"
            )
            # May be empty if app has no UI elements


class TestCalculatorApp:
    """Test cases specific to Calculator application."""

    def test_calculator_exists(self, calculator_fixture):
        """Test that Calculator app is running and accessible."""
        calc_processes = [
            p
            for p in calculator_fixture.system_state.processes
            if p.name == "Calculator"
        ]
        assert len(calc_processes) > 0, "Calculator app should be running"

    def test_calculator_buttons(self, calculator_fixture):
        """Test Calculator button detection."""
        # Find all buttons in Calculator
        calc_buttons = calculator_fixture.find_elements("$..[?(@.role=='AXButton')]")

        # Calculator should have number buttons (0-9) and operation buttons
        # Note: Actual count may vary by macOS version
        if calc_buttons:
            assert len(calc_buttons) >= MIN_CALCULATOR_BUTTONS, (
                f"Calculator should have at least {MIN_CALCULATOR_BUTTONS} buttons, "
                f"found {len(calc_buttons)}"
            )

            # Check that buttons have proper properties
            for button in calc_buttons[:5]:
                assert "role" in button
                assert button["role"] == "AXButton"

    def test_calculator_number_buttons(self, calculator_fixture):
        """Test finding specific number buttons."""
        # Try to find number buttons by title
        for number in ["0", "1", "2", "3", "4", "5"]:
            calculator_fixture.find_elements(
                f"$..[?(@.role=='AXButton' && @.title=='{number}')]"
            )
            # Note: May not find all numbers if Calculator UI is different

    @pytest.mark.skip(
        reason="Clicking disabled for safety - enable manually for testing"
    )
    def test_calculator_interaction(self, calculator_fixture):
        """Test Calculator interaction (disabled for safety)."""
        # This test is skipped by default to prevent accidental automation
        # Remove the skip decorator to enable actual clicking

        # Find the "1" button
        calculator_fixture.assert_element_exists(
            "$..[?(@.role=='AXButton' && @.title=='1')]"
        )

        # Note: Clicking disabled for safety - would use:
        # calculator_fixture.actions.click(one_button)

        # Find the "+" button
        calculator_fixture.assert_element_exists(
            "$..[?(@.role=='AXButton' && @.title=='+')]"
        )

        # Note: Clicking disabled for safety - would use:
        # calculator_fixture.actions.click(plus_button)

        # Verify result display updated
        # Note: Would need to check display element for actual result


class TestUITiming:
    """Test cases for timing and performance."""

    def test_state_capture_timing(self):
        """Test UI state capture performance."""
        start_time = time.time()

        # Shallow capture should be fast
        shallow_dumper = SystemStateDumper(max_depth=3, only_visible_children=True)
        shallow_state = shallow_dumper.dump_system_state()

        shallow_time = time.time() - start_time
        assert shallow_time < MAX_STATE_CAPTURE_TIME, (
            f"Shallow capture should be under {MAX_STATE_CAPTURE_TIME}s, "
            f"took {shallow_time:.2f}s"
        )
        assert len(shallow_state.processes) > 0, "Should capture some processes"

    def test_element_search_timing(self, ui_fixture):
        """Test element search performance."""
        start_time = time.time()

        # Simple search should be fast
        ui_fixture.find_elements("$..[?(@.role=='AXButton')]")

        search_time = time.time() - start_time
        assert search_time < MAX_SEARCH_TIME, (
            f"Button search should be under {MAX_SEARCH_TIME}s, took {search_time:.2f}s"
        )

    def test_timeout_handling(self):
        """Test timeout handling in deep searches."""
        # This would test timeout functionality
        deep_dumper = SystemStateDumper(max_depth=15, only_visible_children=True)

        start_time = time.time()
        # Test with timeout
        try:
            deep_dumper.dump_system_state_with_timeout(timeout_seconds=3.0)
            elapsed = time.time() - start_time
            assert elapsed <= MAX_TIMEOUT_TOLERANCE, (
                f"Should respect timeout, took {elapsed:.2f}s"
            )
        except TimeoutError:
            # Timeout exceptions are acceptable
            elapsed = time.time() - start_time
            assert elapsed <= MAX_TIMEOUT_TOLERANCE, (
                f"Should timeout gracefully, took {elapsed:.2f}s"
            )


# Custom pytest markers for different test categories
pytestmark = [pytest.mark.ui_automation, pytest.mark.macos_only]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "ui_automation: mark test as UI automation test")
    config.addinivalue_line("markers", "macos_only: mark test as macOS specific")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_app(app_name): mark test as requiring specific app"
    )


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
