"""Additional unit tests to improve coverage."""


from bpmn_generator.models.schema import (
    DataObjectReferenceNode,
    ProcessArtifact,
    StartEventNode,
    UserTaskNode,
)


def test_start_event_default_label() -> None:
    """Test StartEventNode with default label."""
    node = StartEventNode(id="start_1")
    assert node.label == "Inicio"


def test_data_object_reference_node() -> None:
    """Test DataObjectReferenceNode creation."""
    node = DataObjectReferenceNode(
        id="ref_1", label="Invoice Ref", data_object_ref="data_1"
    )
    assert node.id == "ref_1"
    assert node.type == "DataObjectReference"
    assert node.data_object_ref == "data_1"


def test_process_artifact_empty() -> None:
    """Test creating an empty ProcessArtifact."""
    artifact = ProcessArtifact(process_id="proc_1", process_name="Empty Process")
    assert artifact.is_valid is True
    assert len(artifact.nodes) == 0
    assert len(artifact.edges) == 0


def test_process_artifact_with_description() -> None:
    """Test ProcessArtifact with description."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test",
        description="A test process for validation",
    )
    assert artifact.description == "A test process for validation"


def test_process_artifact_decision_log() -> None:
    """Test ProcessArtifact with decision log."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Test",
        decision_log=[
            {"node_id": "task_1", "reason": "User mentioned approval step"}
        ],
    )
    assert len(artifact.decision_log) == 1
    assert artifact.decision_log[0]["node_id"] == "task_1"


def test_gateway_without_default_flow() -> None:
    """Test Gateway without default flow."""
    from bpmn_generator.models.schema import GatewayNode

    node = GatewayNode(id="gw_1", label="Decision", gateway_type="Parallel")
    assert node.default_flow is None


def test_subprocess_not_expanded() -> None:
    """Test SubProcess with is_expanded=False."""
    from bpmn_generator.models.schema import SubProcessNode

    node = SubProcessNode(id="sub_1", label="Hidden Process", is_expanded=False)
    assert node.is_expanded is False


def test_subprocess_without_loop() -> None:
    """Test SubProcess without loop characteristics."""
    from bpmn_generator.models.schema import SubProcessNode

    node = SubProcessNode(id="sub_1", label="Simple Subprocess")
    assert node.loop_characteristics is None


def test_user_task_without_role() -> None:
    """Test UserTask without role assigned."""
    node = UserTaskNode(id="task_1", label="Unassigned Task")
    assert node.role is None


def test_service_task_without_implementation() -> None:
    """Test ServiceTask without implementation specified."""
    from bpmn_generator.models.schema import ServiceTaskNode

    node = ServiceTaskNode(id="task_1", label="Generic Service")
    assert node.implementation is None


def test_boundary_event_non_interrupting() -> None:
    """Test BoundaryEvent with cancel_activity=False."""
    from bpmn_generator.models.schema import BoundaryEventNode

    node = BoundaryEventNode(
        id="timer_1",
        label="Reminder",
        attached_to_ref="task_1",
        event_type="timer",
        cancel_activity=False,
    )
    assert node.cancel_activity is False


def test_edge_without_condition() -> None:
    """Test BPMNEdge without condition."""
    from bpmn_generator.models.schema import BPMNEdge

    edge = BPMNEdge(source_id="task_1", target_id="task_2")
    assert edge.condition is None


def test_process_artifact_multiple_validation_errors() -> None:
    """Test ProcessArtifact with multiple validation errors."""
    artifact = ProcessArtifact(
        process_id="proc_1",
        process_name="Invalid Process",
        nodes=[UserTaskNode(id="task_1", label="Task")],
        edges=[
            {"source_id": "invalid_1", "target_id": "task_1"},
            {"source_id": "task_1", "target_id": "invalid_2"},
        ],
    )
    assert artifact.is_valid is False
    assert len(artifact.validation_errors) == 2
