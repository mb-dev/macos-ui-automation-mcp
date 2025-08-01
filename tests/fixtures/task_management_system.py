"""
TaskManagement fake system fixtures based on real app structure.

This module provides realistic fake UI hierarchies matching the actual
TaskManagement Swift application for comprehensive testing.
"""

from macos_ui_automation.bridges.fake_bridge import (
    FakeAXUIElement,
    FakeAXValue,
    FakeNSRunningApplication,
)
from macos_ui_automation.bridges.types import AXValueType


def create_task_management_system():
    """Create a realistic TaskManagement fake system based on actual app structure."""

    # Create the main TaskManagement application
    task_mgmt_app = create_task_management_app()

    # Create running applications list
    running_apps = [
        FakeNSRunningApplication(
            "Task Management", 84054, "com.example.taskmanagement", True, False
        ),
        FakeNSRunningApplication("Finder", 1671, "com.apple.finder", False, False),
        FakeNSRunningApplication("Safari", 2345, "com.apple.safari", False, False),
    ]

    # Applications dict for PyObjC bridge
    applications = {
        84054: task_mgmt_app,
    }

    return applications, running_apps


def create_task_management_app():
    """Create the TaskManagement application with realistic UI hierarchy."""

    # Main window
    main_window = create_main_window()

    # Application element
    app = FakeAXUIElement(
        element_id="task_mgmt_app",
        attributes={
            "kAXTitleAttribute": "Task Management",
            "kAXRoleAttribute": "AXApplication",
            "kAXEnabledAttribute": True,
        },
        actions=["AXRaise"],
        children=[main_window],
    )

    # Set window attributes
    app.attributes["kAXWindowsAttribute"] = [main_window]
    app.attributes["kAXMainWindowAttribute"] = main_window

    return app


def create_main_window():
    """Create the main TaskManagement window with all child elements."""

    # Create the 7 direct children we discovered
    content_group = create_content_group()
    toolbar = create_toolbar()
    close_button = create_button("close_btn", None, {"x": 253, "y": 161})
    menu_button = create_button("menu_btn", None, {"x": 293, "y": 161}, has_child=True)
    settings_button = create_button("settings_btn", None, {"x": 273, "y": 161})
    status_text = create_static_text("Status: Ready", {"x": 494, "y": 143})
    dialog_sheet = create_dialog_sheet()

    return FakeAXUIElement(
        element_id="task_mgmt_window",
        attributes={
            "kAXTitleAttribute": "Task Management",
            "kAXRoleAttribute": "AXWindow",
            "kAXPositionAttribute": FakeAXValue(
                AXValueType.CGPOINT.value, {"x": 235, "y": 143}
            ),
            "kAXSizeAttribute": FakeAXValue(
                AXValueType.CGSIZE.value, {"width": 1000, "height": 652}
            ),
            "kAXMinimizedAttribute": False,
        },
        actions=["AXRaise", "AXPress"],
        children=[
            content_group,
            toolbar,
            close_button,
            menu_button,
            settings_button,
            status_text,
            dialog_sheet,
        ],
    )


def create_content_group():
    """Create the main content group with split view."""

    # Create the split group with accessibility ID (this is the complex nested structure)
    split_group = FakeAXUIElement(
        element_id="split_group",
        attributes={
            "kAXTitleAttribute": None,
            "kAXRoleAttribute": "AXSplitGroup",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "SwiftUI.ModifiedContent<SwiftUI.ModifiedContent<TaskManagementUI.ContentView, SwiftUI._EnvironmentKeyWritingModifier<Swift.Optional<TaskManagementJIRA.TaskManagementEngine>>>, SwiftUI._TaskModifier>-1-AppWindow-1, SidebarNavigationSplitView",
        },
        actions=[],
        children=create_split_group_children(),
    )

    return FakeAXUIElement(
        element_id="content_group",
        attributes={
            "kAXTitleAttribute": None,
            "kAXRoleAttribute": "AXGroup",
            "kAXEnabledAttribute": True,
        },
        actions=[],
        children=[split_group],
    )


def create_split_group_children():
    """Create the 5 children of the split group (sidebar, main content, etc)."""
    children = []

    # Sidebar
    sidebar = FakeAXUIElement(
        element_id="sidebar",
        attributes={
            "kAXTitleAttribute": "Sidebar",
            "kAXRoleAttribute": "AXOutline",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "sidebarOutline",
        },
        actions=["AXPress"],
        children=create_sidebar_items(),
    )
    children.append(sidebar)

    # Main content area
    main_content = FakeAXUIElement(
        element_id="main_content",
        attributes={
            "kAXTitleAttribute": "Task List",
            "kAXRoleAttribute": "AXTable",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "taskTable",
        },
        actions=["AXPress"],
        children=create_task_list_rows(),
    )
    children.append(main_content)

    # Detail panel
    detail_panel = FakeAXUIElement(
        element_id="detail_panel",
        attributes={
            "kAXTitleAttribute": "Task Details",
            "kAXRoleAttribute": "AXGroup",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "detailPanel",
        },
        actions=[],
        children=create_detail_panel_elements(),
    )
    children.append(detail_panel)

    # Add two more structural elements
    children.extend(
        [
            create_button(
                f"structure_elem_{i}", f"Element {i}", {"x": 100 + i * 50, "y": 200}
            )
            for i in range(2)
        ]
    )

    return children


def create_toolbar():
    """Create the toolbar with sync and screenshot buttons."""

    # Toolbar buttons with accessibility IDs
    sync_button = create_button(
        "sync_btn",
        "Sync",
        {"x": 120, "y": 60},
        ax_id="syncButton",
        actions=["AXPress"],
        has_child=True,
    )
    screenshot_button = create_button(
        "screenshot_btn",
        "Screenshot",
        {"x": 180, "y": 60},
        ax_id="screenshotButton",
        actions=["AXPress"],
        has_child=True,
    )
    menu_tool_button = create_button(
        "menu_tool_btn", None, {"x": 240, "y": 60}, has_child=True
    )

    # Add Epic button (matching the real app's addEpicButton)
    add_epic_button = create_button(
        "add_epic_btn",
        None,
        {"x": 448, "y": 214},
        ax_id="addEpicButton",
        actions=["AXPress"],
    )

    return FakeAXUIElement(
        element_id="toolbar",
        attributes={
            "kAXTitleAttribute": None,
            "kAXRoleAttribute": "AXToolbar",
            "kAXEnabledAttribute": True,
        },
        actions=[],
        children=[sync_button, screenshot_button, menu_tool_button, add_epic_button],
    )


def create_dialog_sheet():
    """Create the dialog sheet (this might be the dialog you mentioned)."""

    # Dialog content
    dialog_content = FakeAXUIElement(
        element_id="dialog_content",
        attributes={
            "kAXTitleAttribute": "Task Creation Dialog",
            "kAXRoleAttribute": "AXGroup",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "taskCreationDialog",
        },
        actions=[],
        children=create_dialog_elements(),
    )

    return FakeAXUIElement(
        element_id="dialog_sheet",
        attributes={
            "kAXTitleAttribute": None,
            "kAXRoleAttribute": "AXSheet",
            "kAXEnabledAttribute": True,
        },
        actions=[],
        children=[dialog_content],
    )


def create_dialog_elements():
    """Create elements within the dialog."""
    elements = []

    # Task title field
    title_field = FakeAXUIElement(
        element_id="task_title_field",
        attributes={
            "kAXTitleAttribute": "Task Title",
            "kAXRoleAttribute": "AXTextField",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "taskTitleField",
            "kAXValueAttribute": "",
        },
        actions=["AXConfirm", "AXSetValue"],
    )
    elements.append(title_field)

    # Priority popup
    priority_popup = FakeAXUIElement(
        element_id="priority_popup",
        attributes={
            "kAXTitleAttribute": "Priority",
            "kAXRoleAttribute": "AXPopUpButton",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "priorityPopup",
            "kAXValueAttribute": "Medium",
        },
        actions=["AXPress", "AXShowMenu"],
    )
    elements.append(priority_popup)

    # Create and Cancel buttons
    create_btn = create_button(
        "create_btn",
        "Create Task",
        {"x": 400, "y": 300},
        ax_id="createTaskButton",
        actions=["AXPress"],
    )
    cancel_btn = create_button(
        "cancel_btn",
        "Cancel",
        {"x": 320, "y": 300},
        ax_id="cancelTaskButton",
        actions=["AXPress"],
    )

    elements.extend([create_btn, cancel_btn])

    return elements


def create_sidebar_items():
    """Create sidebar items with accessibility IDs."""
    items = []

    sidebar_items = [
        ("All Tasks", "allTasksItem"),
        ("In Progress", "inProgressItem"),
        ("Completed", "completedItem"),
        ("High Priority", "highPriorityItem"),
    ]

    for i, (title, ax_id) in enumerate(sidebar_items):
        item = FakeAXUIElement(
            element_id=f"sidebar_item_{i}",
            attributes={
                "kAXTitleAttribute": title,
                "kAXRoleAttribute": "AXStaticText",
                "kAXEnabledAttribute": True,
                "kAXIdentifierAttribute": ax_id,
            },
            actions=["AXPress"],
        )
        items.append(item)

    return items


def create_task_list_rows():
    """Create task list rows with realistic task data."""
    rows = []

    tasks = [
        ("Fix login bug", "HIGH", "In Progress", "fixLoginBugRow"),
        ("Update documentation", "MEDIUM", "To Do", "updateDocsRow"),
        ("Code review PR #123", "LOW", "Completed", "reviewPR123Row"),
    ]

    for i, (title, priority, status, ax_id) in enumerate(tasks):
        row = FakeAXUIElement(
            element_id=f"task_row_{i}",
            attributes={
                "kAXTitleAttribute": title,
                "kAXRoleAttribute": "AXRow",
                "kAXEnabledAttribute": True,
                "kAXIdentifierAttribute": ax_id,
            },
            actions=["AXPress"],
            children=create_task_row_cells(title, priority, status),
        )
        rows.append(row)

    return rows


def create_task_row_cells(title, priority, status):
    """Create cells within a task row."""
    cells = []

    # Title cell
    title_cell = FakeAXUIElement(
        element_id=f"title_cell_{title}",
        attributes={
            "kAXTitleAttribute": title,
            "kAXRoleAttribute": "AXCell",
            "kAXEnabledAttribute": True,
            "kAXValueAttribute": title,
        },
        actions=["AXPress"],
    )
    cells.append(title_cell)

    # Priority cell
    priority_cell = FakeAXUIElement(
        element_id=f"priority_cell_{priority}",
        attributes={
            "kAXTitleAttribute": priority,
            "kAXRoleAttribute": "AXCell",
            "kAXEnabledAttribute": True,
            "kAXValueAttribute": priority,
        },
        actions=["AXPress"],
    )
    cells.append(priority_cell)

    # Status cell
    status_cell = FakeAXUIElement(
        element_id=f"status_cell_{status}",
        attributes={
            "kAXTitleAttribute": status,
            "kAXRoleAttribute": "AXCell",
            "kAXEnabledAttribute": True,
            "kAXValueAttribute": status,
        },
        actions=["AXPress"],
    )
    cells.append(status_cell)

    return cells


def create_detail_panel_elements():
    """Create elements in the detail panel."""
    elements = []

    # Task description
    description = FakeAXUIElement(
        element_id="task_description",
        attributes={
            "kAXTitleAttribute": "Description",
            "kAXRoleAttribute": "AXTextArea",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "taskDescription",
            "kAXValueAttribute": "This is a detailed task description...",
        },
        actions=["AXSetValue", "AXConfirm"],
    )
    elements.append(description)

    # Due date field
    due_date = FakeAXUIElement(
        element_id="due_date",
        attributes={
            "kAXTitleAttribute": "Due Date",
            "kAXRoleAttribute": "AXDateField",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "taskDueDate",
            "kAXValueAttribute": "2025-07-25",
        },
        actions=["AXSetValue", "AXConfirm"],
    )
    elements.append(due_date)

    # Assignee popup
    assignee = FakeAXUIElement(
        element_id="assignee",
        attributes={
            "kAXTitleAttribute": "Assignee",
            "kAXRoleAttribute": "AXPopUpButton",
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": "taskAssignee",
            "kAXValueAttribute": "John Doe",
        },
        actions=["AXPress", "AXShowMenu"],
    )
    elements.append(assignee)

    return elements


def create_button(
    element_id, title, position, ax_id=None, actions=None, has_child=False
):
    """Helper to create button elements."""

    button = FakeAXUIElement(
        element_id=element_id,
        attributes={
            "kAXTitleAttribute": title,
            "kAXRoleAttribute": "AXButton",
            "kAXPositionAttribute": FakeAXValue(AXValueType.CGPOINT.value, position),
            "kAXSizeAttribute": FakeAXValue(
                AXValueType.CGSIZE.value, {"width": 80, "height": 25}
            ),
            "kAXEnabledAttribute": True,
            "kAXIdentifierAttribute": ax_id,
        },
        actions=actions or ["AXPress"],
    )

    # Add a child element if specified (like real TaskManagement buttons have)
    if has_child:
        child = FakeAXUIElement(
            element_id=f"{element_id}_child",
            attributes={
                "kAXTitleAttribute": f"{title} Child" if title else "Button Child",
                "kAXRoleAttribute": "AXGroup",
                "kAXEnabledAttribute": True,
            },
            actions=[],
        )
        button.children = [child]

    return button


def create_static_text(text, position):
    """Helper to create static text elements."""

    return FakeAXUIElement(
        element_id="static_text",
        attributes={
            "kAXTitleAttribute": text,
            "kAXRoleAttribute": "AXStaticText",
            "kAXPositionAttribute": FakeAXValue(AXValueType.CGPOINT.value, position),
            "kAXEnabledAttribute": True,
        },
        actions=[],
    )
