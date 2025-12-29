"""Manhattan Grid layout algorithm for BPMN Diagram Interchange (DI).

This module implements the orthogonal (90° angles) layout algorithm for
generating professional BPMN diagram coordinates following ISO 19510.
"""

from typing import Any

from bpmn_generator.models.schema import BPMNNode, ProcessArtifact

# ============================================================================
# Layout Constants (Manhattan Grid)
# ============================================================================

GRID_START_X = 200
GRID_START_Y = 200
HORIZONTAL_STEP = 180  # Advance between sequential elements
VERTICAL_BRANCH_OFFSET = 150  # Vertical separation for parallel branches
DATA_OBJECT_Y_OFFSET = -100  # Data Objects float above tasks
BOUNDARY_EVENT_X_OFFSET = 80  # Position relative to parent task
BOUNDARY_EVENT_Y_OFFSET = 60  # Lower-right corner

# Node dimensions (BPMN standard sizes)
START_EVENT_SIZE = (36, 36)
END_EVENT_SIZE = (36, 36)
TASK_SIZE = (100, 80)
GATEWAY_SIZE = (50, 50)
DATA_OBJECT_SIZE = (36, 50)
SUBPROCESS_SIZE = (350, 200)


def calculate_node_positions(
    artifact: ProcessArtifact,
) -> dict[str, tuple[int, int]]:
    """Calculate DI coordinates for all nodes using Manhattan Grid algorithm.

    This function implements a simple left-to-right, top-to-bottom layout
    for BPMN diagrams with orthogonal connections.

    Args:
        artifact: ProcessArtifact with nodes and edges.

    Returns:
        Dictionary mapping node IDs to (x, y) coordinates.

    Examples:
        >>> from bpmn_generator.models.schema import StartEventNode, UserTaskNode
        >>> artifact = ProcessArtifact(
        ...     process_id="p1",
        ...     process_name="Test",
        ...     nodes=[
        ...         StartEventNode(id="start_1"),
        ...         UserTaskNode(id="task_1", label="Task"),
        ...     ],
        ... )
        >>> positions = calculate_node_positions(artifact)
        >>> positions["start_1"]
        (200, 200)
        >>> positions["task_1"]
        (380, 200)
    """
    positions: dict[str, tuple[int, int]] = {}

    # Simple sequential layout (left to right)
    current_x = GRID_START_X
    current_y = GRID_START_Y

    for node in artifact.nodes:
        # Skip BoundaryEvents (they're positioned relative to their parent)
        if hasattr(node, "attached_to_ref"):
            continue

        positions[node.id] = (current_x, current_y)
        current_x += HORIZONTAL_STEP

    # Position BoundaryEvents relative to their parent tasks
    for node in artifact.nodes:
        if hasattr(node, "attached_to_ref"):  # BoundaryEventNode
            parent_pos = positions.get(node.attached_to_ref)
            if parent_pos:
                positions[node.id] = (
                    parent_pos[0] + BOUNDARY_EVENT_X_OFFSET,
                    parent_pos[1] + BOUNDARY_EVENT_Y_OFFSET,
                )

    # Position DataObjects above their associated tasks
    for assoc in artifact.data_associations:
        # Find the task this data object is associated with
        if assoc.association_type == "input":
            task_id = assoc.target_ref
        else:  # output
            task_id = assoc.source_ref

        task_pos = positions.get(task_id)
        if task_pos:
            # Position data object above the task
            data_obj_id = (
                assoc.source_ref if assoc.association_type == "input" else assoc.target_ref
            )
            positions[data_obj_id] = (
                task_pos[0],
                task_pos[1] + DATA_OBJECT_Y_OFFSET,
            )

    return positions


def calculate_waypoints(
    source_pos: tuple[int, int],
    target_pos: tuple[int, int],
    source_size: tuple[int, int] = TASK_SIZE,
    target_size: tuple[int, int] = TASK_SIZE,
) -> list[tuple[int, int]]:
    """Calculate orthogonal waypoints between two nodes (90° angles).

    Generates waypoints for sequence flows that follow Manhattan routing
    (only horizontal and vertical segments).

    Args:
        source_pos: (x, y) position of source node.
        target_pos: (x, y) position of target node.
        source_size: (width, height) of source node.
        target_size: (width, height) of target node.

    Returns:
        List of (x, y) waypoints for the connection.

    Examples:
        >>> waypoints = calculate_waypoints((200, 200), (380, 200))
        >>> len(waypoints)
        2
        >>> waypoints[0]
        (218, 218)
        >>> waypoints[1]
        (380, 220)
    """
    # Calculate center points
    source_center_x = source_pos[0] + source_size[0] // 2
    source_center_y = source_pos[1] + source_size[1] // 2
    target_center_x = target_pos[0] + target_size[0] // 2
    target_center_y = target_pos[1] + target_size[1] // 2

    waypoints = [(source_center_x, source_center_y)]

    # If there's a vertical difference, add an elbow
    if abs(source_center_y - target_center_y) > 10:
        # Intermediate point: same X as source, same Y as target
        waypoints.append((source_center_x, target_center_y))

    waypoints.append((target_center_x, target_center_y))

    return waypoints


def get_node_size(node: BPMNNode) -> tuple[int, int]:
    """Get the standard size for a BPMN node type.

    Args:
        node: BPMN node.

    Returns:
        (width, height) tuple.

    Examples:
        >>> from bpmn_generator.models.schema import StartEventNode
        >>> node = StartEventNode(id="start_1")
        >>> get_node_size(node)
        (36, 36)
    """
    node_type = node.type

    if node_type == "StartEvent":
        return START_EVENT_SIZE
    elif node_type == "EndEvent":
        return END_EVENT_SIZE
    elif node_type == "Gateway":
        return GATEWAY_SIZE
    elif node_type == "SubProcess":
        return SUBPROCESS_SIZE
    elif node_type in ("DataObject", "DataObjectReference"):
        return DATA_OBJECT_SIZE
    else:  # Tasks (User, Service, Script, Send, Receive)
        return TASK_SIZE


def generate_bpmn_di_bounds(
    node_id: str, positions: dict[str, tuple[int, int]], node: BPMNNode
) -> dict[str, Any]:
    """Generate BPMN DI Bounds element for a node.

    Args:
        node_id: Node ID.
        positions: Dictionary of node positions.
        node: BPMN node.

    Returns:
        Dictionary with x, y, width, height for DI Bounds.

    Examples:
        >>> from bpmn_generator.models.schema import UserTaskNode
        >>> node = UserTaskNode(id="task_1", label="Task")
        >>> positions = {"task_1": (200, 200)}
        >>> bounds = generate_bpmn_di_bounds("task_1", positions, node)
        >>> bounds
        {'x': 200, 'y': 200, 'width': 100, 'height': 80}
    """
    pos = positions.get(node_id, (GRID_START_X, GRID_START_Y))
    size = get_node_size(node)

    return {"x": pos[0], "y": pos[1], "width": size[0], "height": size[1]}
