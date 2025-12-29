"""Router logic for the BPMN generator graph.

This module contains the conditional routing logic used by the StateGraph
to determine the next step in the workflow based on the current state.
"""

from typing import Literal

from bpmn_generator.models.state import AgentState


def route_critic(state: AgentState) -> Literal["sufficient", "insufficient"]:
    """Determine the next node after the critic.

    If the artifact is deemed sufficient by the critic, route to the generator.
    Otherwise, route to the chat node to ask for clarification.

    Args:
        state: Current AgentState.

    Returns:
        "sufficient" or "insufficient".
    """
    if state["is_sufficient"]:
        return "sufficient"
    return "insufficient"
