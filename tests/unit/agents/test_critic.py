"""Unit tests for critic agent."""

from bpmn_generator.agents.critic import critic_node
from bpmn_generator.models.schema import (
    BPMNEdge,
    EndEventNode,
    ProcessArtifact,
    StartEventNode,
    UserTaskNode,
)
from bpmn_generator.models.state import AgentState, ProcessUpdate


def test_critic_node_valid_artifact() -> None:
    """Test critic with valid artifact (has start and end)."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="p1",
            process_name="Test",
            nodes=[
                StartEventNode(id="start1"),
                UserTaskNode(id="task1", label="Task"),
                EndEventNode(id="end1"),
            ],
            edges=[
                BPMNEdge(source_id="start1", target_id="task1"),
                BPMNEdge(source_id="task1", target_id="end1"),
            ],
        ),
        "current_phase": "validation",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": ProcessUpdate(thoughts="Test", confidence_score=0.9, missing_information=[]),
        "knowledge_context": None,
        "user_intent": None,
    }

    result = critic_node(state)

    assert result["is_sufficient"] is True
    assert len(result["missing_info"]) == 0


def test_critic_node_missing_start_event() -> None:
    """Test critic with artifact missing start event."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="p1",
            process_name="Test",
            nodes=[EndEventNode(id="end1")],
        ),
        "current_phase": "validation",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = critic_node(state)

    assert result["is_sufficient"] is False
    assert any("inicio" in info.lower() for info in result["missing_info"])


def test_critic_node_missing_end_event() -> None:
    """Test critic with artifact missing end event."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="p1",
            process_name="Test",
            nodes=[StartEventNode(id="start1")],
        ),
        "current_phase": "validation",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = critic_node(state)

    assert result["is_sufficient"] is False
    assert any("fin" in info.lower() for info in result["missing_info"])


def test_critic_node_no_edges() -> None:
    """Test critic with nodes but no edges."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="p1",
            process_name="Test",
            nodes=[StartEventNode(id="start1"), EndEventNode(id="end1")],
            edges=[],
        ),
        "current_phase": "validation",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": None,
        "knowledge_context": None,
        "user_intent": None,
    }

    result = critic_node(state)

    assert result["is_sufficient"] is False
    assert any("conexiones" in info.lower() for info in result["missing_info"])


def test_critic_node_low_confidence() -> None:
    """Test critic with low confidence from analyst."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="p1",
            process_name="Test",
            nodes=[StartEventNode(id="start1"), EndEventNode(id="end1")],
            edges=[BPMNEdge(source_id="start1", target_id="end1")],
        ),
        "current_phase": "validation",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": ProcessUpdate(thoughts="Test", confidence_score=0.5, missing_information=[]),
        "knowledge_context": None,
        "user_intent": None,
    }

    result = critic_node(state)

    assert result["is_sufficient"] is False
    assert any("confianza" in info.lower() for info in result["missing_info"])


def test_critic_node_analyst_missing_info() -> None:
    """Test critic with missing info from analyst."""
    state: AgentState = {
        "messages": [],
        "process_artifact": ProcessArtifact(
            process_id="p1",
            process_name="Test",
            nodes=[StartEventNode(id="start1"), EndEventNode(id="end1")],
            edges=[BPMNEdge(source_id="start1", target_id="end1")],
        ),
        "current_phase": "validation",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": ProcessUpdate(
            thoughts="Test",
            confidence_score=0.8,
            missing_information=["¿Qué pasa si se rechaza?"],
        ),
        "knowledge_context": None,
        "user_intent": None,
    }

    result = critic_node(state)

    assert result["is_sufficient"] is False
    assert "¿Qué pasa si se rechaza?" in result["missing_info"]
