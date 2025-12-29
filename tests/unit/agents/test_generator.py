"""Unit tests for generator agent."""

from bpmn_generator.agents.generator import xml_generator_node
from bpmn_generator.models.schema import (
    BPMNEdge,
    EndEventNode,
    GatewayNode,
    ProcessArtifact,
    StartEventNode,
    UserTaskNode,
)
from bpmn_generator.models.state import AgentState


def test_xml_generator_node_simple_process() -> None:
    """Test generating XML for simple process."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="proc1",
            process_name="Simple Process",
            nodes=[
                StartEventNode(id="start1"),
                UserTaskNode(id="task1", label="Review", role="Manager"),
                EndEventNode(id="end1"),
            ],
            edges=[
                BPMNEdge(source_id="start1", target_id="task1"),
                BPMNEdge(source_id="task1", target_id="end1"),
            ],
        ),
        "current_phase": "generation",
        "revision_count": 0,
        "is_sufficient": True,
        "user_approved": True,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = xml_generator_node(state)

    xml = result["bpmn_xml"]
    assert "<?xml version" in xml
    assert "definitions" in xml
    assert "proc1" in xml
    assert "Simple Process" in xml
    assert "startEvent" in xml
    assert "endEvent" in xml
    assert "userTask" in xml
    assert "sequenceFlow" in xml
    assert "BPMNDiagram" in xml


def test_xml_generator_node_with_gateway() -> None:
    """Test generating XML with gateway."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="proc1",
            process_name="Process with Gateway",
            nodes=[
                StartEventNode(id="start1"),
                GatewayNode(id="gw1", label="Approved?", gateway_type="Exclusive"),
                EndEventNode(id="end1"),
            ],
            edges=[
                BPMNEdge(source_id="start1", target_id="gw1"),
                BPMNEdge(source_id="gw1", target_id="end1", condition="Yes"),
            ],
        ),
        "current_phase": "generation",
        "revision_count": 0,
        "is_sufficient": True,
        "user_approved": True,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = xml_generator_node(state)

    xml = result["bpmn_xml"]
    assert "exclusiveGateway" in xml
    assert "Approved?" in xml


def test_xml_generator_node_validates_output() -> None:
    """Test that generator validates its output."""
    # This should pass validation
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="proc1",
            process_name="Valid Process",
            nodes=[StartEventNode(id="start1"), EndEventNode(id="end1")],
            edges=[BPMNEdge(source_id="start1", target_id="end1")],
        ),
        "current_phase": "generation",
        "revision_count": 0,
        "is_sufficient": True,
        "user_approved": True,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = xml_generator_node(state)
    assert "bpmn_xml" in result
    assert len(result["bpmn_xml"]) > 0


def test_xml_generator_node_includes_di_coordinates() -> None:
    """Test that generated XML includes DI coordinates."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="proc1",
            process_name="Test",
            nodes=[StartEventNode(id="start1"), EndEventNode(id="end1")],
            edges=[BPMNEdge(source_id="start1", target_id="end1")],
        ),
        "current_phase": "generation",
        "revision_count": 0,
        "is_sufficient": True,
        "user_approved": True,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = xml_generator_node(state)

    xml = result["bpmn_xml"]
    assert "BPMNShape" in xml
    assert "BPMNEdge" in xml
    assert "Bounds" in xml
    assert "waypoint" in xml
