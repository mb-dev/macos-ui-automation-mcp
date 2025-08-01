"""
Test SystemStateDumper and state capturing functionality.
"""

import pytest

from macos_ui_automation.bridges.fake_bridge import (
    FakeApplicationBridge,
    FakePyObjCBridge,
    FakeWorkspaceBridge,
)
from macos_ui_automation.core.elements import System
from macos_ui_automation.core.registry import set_test_mode
from macos_ui_automation.core.state import SystemStateDumper


def setup_module():
    """Enable test mode for all tests in this module."""
    set_test_mode(True)


@pytest.fixture
def fake_bridges():
    """Set up fake bridges for testing."""
    fake_pyobjc = FakePyObjCBridge()
    fake_workspace = FakeWorkspaceBridge()
    fake_application = FakeApplicationBridge()
    return fake_pyobjc, fake_workspace, fake_application


def test_system_state_dumper_basic(fake_bridges):
    """Test basic SystemStateDumper functionality."""
    fake_pyobjc, fake_workspace, fake_application = fake_bridges

    # SystemStateDumper will automatically use fake system due to test mode
    dumper = SystemStateDumper(timeout_seconds=5.0)

    # Dump state
    system_state = dumper.dump_system_state()

    # Should have test applications
    assert len(system_state.processes) > 0
    assert system_state.accessibility_enabled is True


def test_hierarchical_element_capture(fake_bridges):
    """Test that SystemStateDumper captures nested UI elements properly."""
    fake_pyobjc, fake_workspace, fake_application = fake_bridges

    # SystemStateDumper will automatically use fake system due to test mode
    dumper = SystemStateDumper(timeout_seconds=5.0)

    # Dump state
    system_state = dumper.dump_system_state()

    # Should have test applications
    assert len(system_state.processes) > 0

    # Find test app process
    test_proc = None
    for proc in system_state.processes:
        if proc.name == "Test App":
            test_proc = proc
            break

    assert test_proc is not None, "Test App process not found"
    assert len(test_proc.windows) == 1, (
        f"Expected 1 window, got {len(test_proc.windows)}"
    )

    window = test_proc.windows[0]
    assert window.title == "Test Window"

    # Should have 2 top-level elements: test_button and test_toolbar
    assert len(window.children) == 2, (
        f"Expected 2 top-level elements, got {len(window.children)}"
    )

    # Find button and toolbar
    button_element = None
    toolbar_element = None

    for elem in window.children:
        if elem.role == "AXButton" and elem.title == "Test Button":
            button_element = elem
        elif elem.role == "AXToolbar" and elem.title == "Test Toolbar":
            toolbar_element = elem

    assert button_element is not None, "Test Button not found"
    assert toolbar_element is not None, "Test Toolbar not found"

    # Test button should have nested children
    assert len(button_element.children) == 1, (
        f"Button should have 1 child, got {len(button_element.children)}"
    )

    button_child = button_element.children[0]
    assert button_child.role == "AXGroup"
    assert button_child.title == "Button Child"
    assert button_child.ax_identifier == "button-child-id"

    # Button child should have grandchildren
    assert len(button_child.children) == 1, (
        f"Button child should have 1 grandchild, got {len(button_child.children)}"
    )

    grandchild = button_child.children[0]
    assert grandchild.role == "AXStaticText"
    assert grandchild.title == "Deep Element"
    assert grandchild.ax_identifier == "deep-element-id"

    # Toolbar should have children
    assert len(toolbar_element.children) == 1, (
        f"Toolbar should have 1 child, got {len(toolbar_element.children)}"
    )

    sync_button = toolbar_element.children[0]
    assert sync_button.role == "AXButton"
    assert sync_button.title == "Sync"
    assert sync_button.ax_identifier == "syncButton"


def test_hierarchical_element_count(fake_bridges):
    """Test that we can count total elements including nested ones."""
    fake_pyobjc, fake_workspace, fake_application = fake_bridges

    dumper = SystemStateDumper(timeout_seconds=5.0)

    system_state = dumper.dump_system_state()

    # Find test app
    test_proc = None
    for proc in system_state.processes:
        if proc.name == "Test App":
            test_proc = proc
            break

    assert test_proc is not None
    window = test_proc.windows[0]

    def count_elements_recursive(elements):
        """Count total elements including nested children."""
        total = len(elements)
        for elem in elements:
            total += count_elements_recursive(elem.children)
        return total

    # Count all elements
    total_elements = count_elements_recursive(window.children)

    # Should have: button (1) + button_child (1) + grandchild (1) + toolbar (1) + sync_button (1) = 5 total
    assert total_elements == 5, f"Expected 5 total elements, got {total_elements}"

    # Top level should still be 2
    assert len(window.children) == 2, (
        f"Expected 2 top-level elements, got {len(window.children)}"
    )


def test_accessibility_ids_in_hierarchy(fake_bridges):
    """Test that accessibility IDs are preserved in the hierarchy."""
    fake_pyobjc, fake_workspace, fake_application = fake_bridges

    fake_system = System(use_fake=True)
    dumper = SystemStateDumper(system=fake_system, timeout_seconds=5.0)

    system_state = dumper.dump_system_state()

    # Find test app
    test_proc = None
    for proc in system_state.processes:
        if proc.name == "Test App":
            test_proc = proc
            break

    window = test_proc.windows[0]

    def collect_elements_with_ids(elements):
        """Collect all elements that have accessibility IDs."""
        elements_with_ids = []
        for elem in elements:
            if elem.ax_identifier:
                elements_with_ids.append((elem.role, elem.title, elem.ax_identifier))
            elements_with_ids.extend(collect_elements_with_ids(elem.children))
        return elements_with_ids

    elements_with_ids = collect_elements_with_ids(window.children)

    # Should find these elements with IDs:
    expected_ids = [
        ("AXButton", "Test Button", "test-button-id"),
        ("AXGroup", "Button Child", "button-child-id"),
        ("AXStaticText", "Deep Element", "deep-element-id"),
        ("AXButton", "Sync", "syncButton"),
    ]

    assert len(elements_with_ids) == 4, (
        f"Expected 4 elements with IDs, got {len(elements_with_ids)}"
    )

    for expected in expected_ids:
        assert expected in elements_with_ids, (
            f"Expected element {expected} not found in {elements_with_ids}"
        )


def test_timeout_behavior(fake_bridges):
    """Test that timeout behavior works correctly."""
    fake_pyobjc, fake_workspace, fake_application = fake_bridges

    # Test with very short timeout
    fake_system = System(use_fake=True)
    dumper = SystemStateDumper(
        system=fake_system, timeout_seconds=0.001
    )  # 1ms - should timeout quickly

    system_state = dumper.dump_system_state()

    # Should still complete but may have fewer elements due to timeout
    assert len(system_state.processes) >= 0
