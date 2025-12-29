"""LangGraph workflow definition.

This module defines the StateGraph that orchestrates the BPMN generation process.
It connects the analyst, critic, chat, and generator agents.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from bpmn_generator.agents.analyst import analyzer_node
from bpmn_generator.agents.chat import chat_node
from bpmn_generator.agents.critic import critic_node
from bpmn_generator.agents.generator import xml_generator_node
from bpmn_generator.graph.routers import route_critic
from bpmn_generator.models.state import AgentState


def create_graph() -> CompiledStateGraph:
    """Create and compile the BPMN generator workflow graph.

    Returns:
        CompiledGraph: The compiled LangGraph application.
    """
    # Initialize graph with AgentState
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyst", analyzer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("generator", xml_generator_node)

    # Define edges
    # Entry point is the analyst
    workflow.set_entry_point("analyst")

    # Analyst always goes to Critic for validation
    workflow.add_edge("analyst", "critic")

    # Critic uses conditional logic based on sufficiency
    workflow.add_conditional_edges(
        "critic",
        route_critic,
        {
            "sufficient": "generator",
            "insufficient": "chat",
        },
    )

    # Chat goes back to Analyst (after user input)
    workflow.add_edge("chat", "analyst")

    # Generator is the final step
    workflow.add_edge("generator", END)

    # Compile with memory persistence (for testing/dev)
    # Interrupt before 'chat' to allow user input
    return workflow.compile(checkpointer=MemorySaver(), interrupt_before=["chat"])
