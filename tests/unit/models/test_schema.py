"""Unit tests for BPMN schema models."""

from bpmn_generator.models.schema import (
    BoundaryEventNode,
    BPMNEdge,
    DataAssociation,
    DataObjectNode,
    EndEventNode,
    GatewayNode,
    ProcessArtifact,
    ReceiveTaskNode,
    ScriptTaskNode,
    SendTaskNode,
    ServiceTaskNode,
    StartEventNode,
    SubProcessNode,
    UserTaskNode,
)

# ============================================================================
# Event Nodes Tests
# ============================================================================


def test_start_event_node_creation() -> None:
    """Test creating a StartEventNode."""
    node = StartEventNode(id="start_1", label="Process Start")
    assert node.id == "start_1"
    assert node.type == "StartEvent"
    assert node.label == "Process Start"


def test_end_event_node_creation() -> None:
    """Test creating an EndEventNode."""
    node = EndEventNode(id="end_1", label="Process End")
    assert node.id == "end_1"
    assert node.type == "EndEvent"
    assert node.label == "Process End"


def test_boundary_event_node_creation() -> None:
    """Test creating a BoundaryEventNode."""
    node = BoundaryEventNode(
        id="error_1",
        label="Handle Error",
        attached_to_ref="task_1",
        event_type="error",
        cancel_activity=True,
    )
    assert node.id == "error_1"
    assert node.type == "BoundaryEvent"
    assert node.attached_to_ref == "task_1"
    assert node.event_type == "error"
    assert node.cancel_activity is True


# ============================================================================
# Task Nodes Tests
# ============================================================================


def test_user_task_node_creation() -> None:
    """Test creating a UserTaskNode."""
    node = UserTaskNode(id="task_1", label="Review Document", role="Manager")
    assert node.id == "task_1"
    assert node.type == "UserTask"
    assert node.label == "Review Document"
    assert node.role == "Manager"


def test_service_task_node_creation() -> None:
    """Test creating a ServiceTaskNode."""
    node = ServiceTaskNode(id="task_2", label="Send Email", implementation="webService")
    assert node.id == "task_2"
    assert node.type == "ServiceTask"
    assert node.implementation == "webService"


def test_script_task_node_creation() -> None:
    """Test creating a ScriptTaskNode."""
    node = ScriptTaskNode(id="task_3", label="Calculate Total", script_format="python")
    assert node.id == "task_3"
    assert node.type == "ScriptTask"
    assert node.script_format == "python"


def test_send_task_node_creation() -> None:
    """Test creating a SendTaskNode."""
    node = SendTaskNode(id="task_4", label="Send Notification")
    assert node.id == "task_4"
    assert node.type == "SendTask"


def test_receive_task_node_creation() -> None:
    """Test creating a ReceiveTaskNode."""
    node = ReceiveTaskNode(id="task_5", label="Wait for Response")
    assert node.id == "task_5"
    assert node.type == "ReceiveTask"


# ============================================================================
# Control Flow Tests
# ============================================================================


def test_gateway_node_creation() -> None:
    """Test creating a GatewayNode."""
    node = GatewayNode(
        id="gw_1",
        label="Is Valid?",
        gateway_type="Exclusive",
        default_flow="flow_yes",
    )
    assert node.id == "gw_1"
    assert node.type == "Gateway"
    assert node.gateway_type == "Exclusive"
    assert node.default_flow == "flow_yes"


def test_subprocess_node_creation() -> None:
    """Test creating a SubProcessNode."""
    node = SubProcessNode(
        id="sub_1",
        label="Process Files",
        is_expanded=True,
        loop_characteristics="sequential",
    )
    assert node.id == "sub_1"
    assert node.type == "SubProcess"
    assert node.loop_characteristics == "sequential"


# ============================================================================
# Data Architecture Tests
# ============================================================================


def test_data_object_node_creation() -> None:
    """Test creating a DataObjectNode."""
    node = DataObjectNode(id="data_1", label="Invoice", is_collection=False)
    assert node.id == "data_1"
    assert node.type == "DataObject"
    assert node.is_collection is False


def test_data_object_collection() -> None:
    """Test creating a DataObjectNode representing multiple items."""
    node = DataObjectNode(id="data_2", label="PDF Files", is_collection=True)
    assert node.is_collection is True


# ============================================================================
# Edge and Association Tests
# ============================================================================


def test_bpmn_edge_creation() -> None:
    """Test creating a BPMNEdge."""
    edge = BPMNEdge(source_id="task_1", target_id="task_2", condition="Yes")
    assert edge.source_id == "task_1"
    assert edge.target_id == "task_2"
    assert edge.condition == "Yes"
    assert edge.is_default is False


def test_bpmn_edge_default() -> None:
    """Test creating a default BPMNEdge."""
    edge = BPMNEdge(source_id="gw_1", target_id="task_1", is_default=True)
    assert edge.is_default is True


def test_data_association_creation() -> None:
    """Test creating a DataAssociation."""
    assoc = DataAssociation(
        id="assoc_1",
        source_ref="data_1",
        target_ref="task_1",
        association_type="input",
    )
    assert assoc.source_ref == "data_1"
    assert assoc.target_ref == "task_1"
    assert assoc.association_type == "input"


# ============================================================================
# ProcessArtifact Tests
# ============================================================================


def test_process_artifact_creation() -> None:
    """Test creating a valid ProcessArtifact."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test Process",
        nodes=[
            StartEventNode(id="start_1"),
            UserTaskNode(id="task_1", label="Task 1"),
            EndEventNode(id="end_1"),
        ],
        edges=[
            BPMNEdge(source_id="start_1", target_id="task_1"),
            BPMNEdge(source_id="task_1", target_id="end_1"),
        ],
    )
    assert artifact.is_valid is True
    assert len(artifact.validation_errors) == 0


def test_process_artifact_invalid_edge_source() -> None:
    """Test ProcessArtifact with edge referencing non-existent source."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test Process",
        nodes=[UserTaskNode(id="task_1", label="Task 1")],
        edges=[BPMNEdge(source_id="invalid_id", target_id="task_1")],
    )
    assert artifact.is_valid is False
    assert any("non-existent source node" in err for err in artifact.validation_errors)


def test_process_artifact_invalid_edge_target() -> None:
    """Test ProcessArtifact with edge referencing non-existent target."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test Process",
        nodes=[UserTaskNode(id="task_1", label="Task 1")],
        edges=[BPMNEdge(source_id="task_1", target_id="invalid_id")],
    )
    assert artifact.is_valid is False
    assert any("non-existent target node" in err for err in artifact.validation_errors)


def test_process_artifact_invalid_boundary_event() -> None:
    """Test ProcessArtifact with BoundaryEvent referencing non-existent task."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test Process",
        nodes=[
            BoundaryEventNode(
                id="error_1",
                label="Error",
                attached_to_ref="non_existent_task",
                event_type="error",
            )
        ],
    )
    assert artifact.is_valid is False
    assert any(
        "BoundaryEvent" in err and "non-existent task" in err for err in artifact.validation_errors
    )


def test_process_artifact_invalid_data_association() -> None:
    """Test ProcessArtifact with DataAssociation referencing non-existent element."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test Process",
        nodes=[UserTaskNode(id="task_1", label="Task 1")],
        data_associations=[
            DataAssociation(
                id="assoc_1",
                source_ref="non_existent_data",
                target_ref="task_1",
                association_type="input",
            )
        ],
    )
    assert artifact.is_valid is False
    assert any(
        "DataAssociation" in err and "non-existent source" in err
        for err in artifact.validation_errors
    )


def test_process_artifact_with_data_objects() -> None:
    """Test ProcessArtifact with data objects and associations."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test Process",
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
    assert artifact.is_valid is True
    assert len(artifact.data_objects) == 1
    assert len(artifact.data_associations) == 1


# ============================================================================
# Discriminated Union Tests
# ============================================================================


def test_bpmn_node_discriminator() -> None:
    """Test that BPMNNode discriminated union works correctly."""
    # This should work - Pydantic will use the 'type' field to determine the correct model
    nodes: list = [
        StartEventNode(id="start_1"),
        UserTaskNode(id="task_1", label="Task"),
        GatewayNode(id="gw_1", label="Decision", gateway_type="Exclusive"),
    ]

    # Verify types are preserved
    assert nodes[0].type == "StartEvent"
    assert nodes[1].type == "UserTask"
    assert nodes[2].type == "Gateway"
