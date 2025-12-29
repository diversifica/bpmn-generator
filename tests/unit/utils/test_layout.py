"""Unit tests for layout utilities."""

from bpmn_generator.models.schema import (
    BoundaryEventNode,
    DataAssociation,
    DataObjectNode,
    EndEventNode,
    GatewayNode,
    ProcessArtifact,
    StartEventNode,
    UserTaskNode,
)
from bpmn_generator.utils.layout import (
    GRID_START_X,
    GRID_START_Y,
    HORIZONTAL_STEP,
    calculate_node_positions,
    calculate_waypoints,
    generate_bpmn_di_bounds,
    get_node_size,
)


def test_calculate_node_positions_simple() -> None:
    """Test calculating positions for a simple sequential process."""
    artifact = ProcessArtifact(
        process_id="p1",
        process_name="Test",
        nodes=[
            StartEventNode(id="start_1"),
            UserTaskNode(id="task_1", label="Task 1"),
            EndEventNode(id="end_1"),
        ],
    )

    positions = calculate_node_positions(artifact)

    assert positions["start_1"] == (GRID_START_X, GRID_START_Y)
    assert positions["task_1"] == (GRID_START_X + HORIZONTAL_STEP, GRID_START_Y)
    assert positions["end_1"] == (GRID_START_X + 2 * HORIZONTAL_STEP, GRID_START_Y)


def test_calculate_node_positions_boundary_event() -> None:
    """Test positioning BoundaryEvent relative to parent task."""
    artifact = ProcessArtifact(
        process_id="p1",
        process_name="Test",
        nodes=[
            UserTaskNode(id="task_1", label="Task"),
            BoundaryEventNode(
                id="error_1",
                label="Error",
                attached_to_ref="task_1",
                event_type="error",
            ),
        ],
    )

    positions = calculate_node_positions(artifact)

    task_pos = positions["task_1"]
    error_pos = positions["error_1"]

    # BoundaryEvent should be offset from task
    assert error_pos[0] > task_pos[0]
    assert error_pos[1] > task_pos[1]


def test_calculate_node_positions_data_objects() -> None:
    """Test positioning DataObjects above associated tasks."""
    artifact = ProcessArtifact(
        process_id="p1",
        process_name="Test",
        nodes=[UserTaskNode(id="task_1", label="Process Invoice")],
        data_objects=[DataObjectNode(id="data_1", label="Invoice")],
        data_associations=[
            DataAssociation(
                id="assoc_1",
                source_ref="data_1",
                target_ref="task_1",
                association_type="input",
            )
        ],
    )

    positions = calculate_node_positions(artifact)

    task_pos = positions["task_1"]
    data_pos = positions["data_1"]

    # DataObject should be above task (lower Y value)
    assert data_pos[0] == task_pos[0]  # Same X
    assert data_pos[1] < task_pos[1]  # Above (lower Y)


def test_calculate_waypoints_horizontal() -> None:
    """Test waypoints for horizontal connection."""
    source_pos = (200, 200)
    target_pos = (380, 200)

    waypoints = calculate_waypoints(source_pos, target_pos)

    assert len(waypoints) == 2  # No elbow needed for horizontal
    assert waypoints[0][1] == waypoints[1][1]  # Same Y (horizontal)


def test_calculate_waypoints_with_vertical_offset() -> None:
    """Test waypoints with vertical offset (requires elbow)."""
    source_pos = (200, 200)
    target_pos = (380, 350)  # 150 pixels down

    waypoints = calculate_waypoints(source_pos, target_pos)

    assert len(waypoints) == 3  # Source, elbow, target
    # Middle waypoint should have source X and target Y
    assert waypoints[1][0] == waypoints[0][0]  # Same X as source
    assert waypoints[1][1] == waypoints[2][1]  # Same Y as target


def test_get_node_size_start_event() -> None:
    """Test getting size for StartEvent."""
    node = StartEventNode(id="start_1")
    size = get_node_size(node)
    assert size == (36, 36)


def test_get_node_size_task() -> None:
    """Test getting size for UserTask."""
    node = UserTaskNode(id="task_1", label="Task")
    size = get_node_size(node)
    assert size == (100, 80)


def test_get_node_size_gateway() -> None:
    """Test getting size for Gateway."""
    node = GatewayNode(id="gw_1", label="Decision", gateway_type="Exclusive")
    size = get_node_size(node)
    assert size == (50, 50)


def test_generate_bpmn_di_bounds() -> None:
    """Test generating BPMN DI Bounds."""
    node = UserTaskNode(id="task_1", label="Task")
    positions = {"task_1": (300, 250)}

    bounds = generate_bpmn_di_bounds("task_1", positions, node)

    assert bounds["x"] == 300
    assert bounds["y"] == 250
    assert bounds["width"] == 100
    assert bounds["height"] == 80


def test_generate_bpmn_di_bounds_missing_position() -> None:
    """Test generating bounds for node without position (uses default)."""
    node = StartEventNode(id="start_1")
    positions = {}  # Empty

    bounds = generate_bpmn_di_bounds("start_1", positions, node)

    # Should use default GRID_START position
    assert bounds["x"] == GRID_START_X
    assert bounds["y"] == GRID_START_Y
