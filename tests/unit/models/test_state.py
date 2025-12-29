"""Unit tests for state models."""

from bpmn_generator.models.schema import (
    BPMNEdge,
    DataAssociation,
    DataObjectNode,
    UserTaskNode,
)
from bpmn_generator.models.state import ClarificationQuestion, ProcessUpdate

# ============================================================================
# ProcessUpdate Tests
# ============================================================================


def test_process_update_creation() -> None:
    """Test creating a ProcessUpdate."""
    update = ProcessUpdate(
        thoughts="User described a simple approval flow",
        new_nodes=[UserTaskNode(id="task_1", label="Approve Request", role="Manager")],
        new_edges=[BPMNEdge(source_id="start_1", target_id="task_1")],
        confidence_score=0.7,
        missing_information=["What happens if rejected?"],
    )
    assert update.thoughts == "User described a simple approval flow"
    assert len(update.new_nodes) == 1
    assert len(update.new_edges) == 1
    assert update.confidence_score == 0.7
    assert len(update.missing_information) == 1


def test_process_update_with_data_objects() -> None:
    """Test ProcessUpdate with data objects and associations."""
    update = ProcessUpdate(
        thoughts="Identified data flow",
        new_data_objects=[DataObjectNode(id="data_1", label="Invoice")],
        new_data_associations=[
            DataAssociation(
                id="assoc_1",
                source_ref="data_1",
                target_ref="task_1",
                association_type="input",
            )
        ],
        confidence_score=0.8,
        missing_information=[],
    )
    assert len(update.new_data_objects) == 1
    assert len(update.new_data_associations) == 1
    assert update.new_data_objects[0].label == "Invoice"


def test_process_update_with_removals() -> None:
    """Test ProcessUpdate with nodes to remove."""
    update = ProcessUpdate(
        thoughts="Removing redundant task",
        nodes_to_remove=["task_old"],
        confidence_score=0.9,
        missing_information=[],
    )
    assert "task_old" in update.nodes_to_remove


# ============================================================================
# ClarificationQuestion Tests
# ============================================================================


def test_clarification_question_open() -> None:
    """Test creating an open-ended ClarificationQuestion."""
    question = ClarificationQuestion(
        question_text="What happens after the approval?",
        question_type="open",
        context="Need to understand the next step in the flow",
    )
    assert question.question_text == "What happens after the approval?"
    assert question.question_type == "open"
    assert question.options is None


def test_clarification_question_choice() -> None:
    """Test creating a choice ClarificationQuestion."""
    question = ClarificationQuestion(
        question_text="Who approves the request?",
        question_type="choice",
        options=["Manager", "Director", "Both"],
        context="Need to identify the responsible role",
    )
    assert question.question_type == "choice"
    assert len(question.options) == 3
    assert "Manager" in question.options


def test_clarification_question_confirmation() -> None:
    """Test creating a confirmation ClarificationQuestion."""
    question = ClarificationQuestion(
        question_text="Is this process complete?",
        question_type="confirmation",
        context="Checking if user is satisfied with the current model",
    )
    assert question.question_type == "confirmation"


# ============================================================================
# AgentState Integration Tests
# ============================================================================


def test_agent_state_structure() -> None:
    """Test that AgentState has all required fields.

    Note: AgentState is a TypedDict, so we can't instantiate it directly in tests.
    This test verifies the structure is correct by checking annotations.
    """
    from bpmn_generator.models.state import AgentState

    # Verify all required fields exist in annotations
    required_fields = {
        "messages",
        "process_artifact",
        "current_phase",
        "revision_count",
        "is_sufficient",
        "user_approved",
        "missing_info",
        "last_update",
        "knowledge_context",
        "user_intent",
    }

    assert required_fields.issubset(set(AgentState.__annotations__.keys()))


def test_agent_state_field_types() -> None:
    """Test that AgentState fields have correct types."""
    from bpmn_generator.models.state import AgentState

    # Check specific field types
    assert "ProcessArtifact" in str(AgentState.__annotations__["process_artifact"])
    assert "Literal" in str(AgentState.__annotations__["current_phase"])
    assert "bool" in str(AgentState.__annotations__["is_sufficient"])
