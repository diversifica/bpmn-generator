"""Integration tests for the LangGraph workflow."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from bpmn_generator.graph.workflow import create_graph
from bpmn_generator.models.schema import ProcessArtifact
from bpmn_generator.models.state import ProcessUpdate


@patch("bpmn_generator.graph.workflow.analyzer_node")
@patch("bpmn_generator.graph.workflow.critic_node")
@patch("bpmn_generator.graph.workflow.chat_node")
@patch("bpmn_generator.graph.workflow.xml_generator_node")
def test_workflow_insufficient_artifact_routing(
    mock_generator, mock_chat, mock_critic, mock_analyst
):
    """Test routing when artifact is insufficient: Analyst -> Critic -> Chat."""
    # Setup mocks
    # Analyst returns an update
    mock_analyst.return_value = {
        "last_update": ProcessUpdate(
            thoughts="Thinking...",
            confidence_score=0.6,
            missing_information=["Missing start event"],
            bpmn_changes=[],
        )
    }
    
    # Critic says insufficient
    mock_critic.return_value = {
        "is_sufficient": False,
        "missing_info": ["Missing start event"]
    }
    
    # Chat generates a question
    mock_chat.return_value = {
        "messages": [HumanMessage(content="What is the start trigger?")]
    }

    # Initialize graph
    app = create_graph()
    
    # Initial state
    initial_artifact = ProcessArtifact(process_id="p1", process_name="Test")
    state = {
        "messages": [HumanMessage(content="My process")],
        "process_artifact": initial_artifact,
        "current_phase": "planning",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": None,
    }
    
    config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # Run the graph
    # It should stop before 'chat' because of interrupt_before=["chat"]
    # So the sequence executed should be: Start -> Analyst -> Critic -> (Stop before Chat)
    # Wait, if route_critic returns "insufficient", it goes to "chat".
    # With interrupt_before=["chat"], it should execute Analyst, Critic, and then STOP.
    
    events = list(app.stream(state, config=config))
    
    # Verify nodes called
    assert mock_analyst.called
    assert mock_critic.called
    assert not mock_chat.called  # Should be interrupted before chat
    assert not mock_generator.called
    
    # Verify we stopped
    snapshot = app.get_state(config)
    assert snapshot.next == ("chat",)


@patch("bpmn_generator.graph.workflow.analyzer_node")
@patch("bpmn_generator.graph.workflow.critic_node")
@patch("bpmn_generator.graph.workflow.chat_node")
@patch("bpmn_generator.graph.workflow.xml_generator_node")
def test_workflow_sufficient_artifact_routing(
    mock_generator, mock_chat, mock_critic, mock_analyst
):
    """Test routing when artifact is sufficient: Analyst -> Critic -> Generator -> End."""
    # Setup mocks
    # Analyst returns good update
    mock_analyst.return_value = {
        "last_update": ProcessUpdate(
            thoughts="Good",
            confidence_score=0.9,
            missing_information=[],
            bpmn_changes=[],
        )
    }
    
    # Critic says sufficient
    mock_critic.return_value = {
        "is_sufficient": True,
        "missing_info": []
    }
    
    # Generator creates XML
    mock_generator.return_value = {"bpmn_xml": "<xml>..."}

    # Initialize graph
    app = create_graph()
    
    # Initial state
    initial_artifact = ProcessArtifact(process_id="p1", process_name="Test")
    state = {
        "messages": [HumanMessage(content="My process")],
        "process_artifact": initial_artifact,
        "current_phase": "planning",
        "revision_count": 0,
        "is_sufficient": False,
        "user_approved": False,
        "missing_info": [],
        "last_update": None,
    }
    
    config = {"configurable": {"thread_id": "test_thread_2"}}
    
    # Run the graph
    events = list(app.stream(state, config=config))
    
    # Verify nodes called
    assert mock_analyst.called
    assert mock_critic.called
    assert not mock_chat.called
    assert mock_generator.called
    
    # Verify flow reached the end
    snapshot = app.get_state(config)
    assert len(snapshot.next) == 0  # No next step means END
