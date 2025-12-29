"""Critic agent - validates ProcessArtifact sufficiency.

This module implements the critic_node which validates whether the ProcessArtifact
meets the minimum sufficiency criteria defined in Doc 00 Section 6.4.1.
"""

from bpmn_generator.models.state import AgentState


def critic_node(state: AgentState) -> dict:
    """Validate ProcessArtifact sufficiency using algorithmic criteria.

    This node checks if the artifact meets minimum requirements:
    1. Has at least one StartEvent
    2. Has at least one EndEvent
    3. All nodes are connected (no isolated nodes except data objects)
    4. No missing information identified by analyst

    Args:
        state: Current AgentState with process_artifact and last_update.

    Returns:
        Dictionary with 'is_sufficient' and 'missing_info' keys.

    Examples:
        >>> from bpmn_generator.models.schema import ProcessArtifact, StartEventNode, EndEventNode
        >>> state = AgentState(
        ...     messages=[],
        ...     process_artifact=ProcessArtifact(
        ...         process_id="p1",
        ...         process_name="Test",
        ...         nodes=[StartEventNode(id="start"), EndEventNode(id="end")],
        ...     ),
        ...     current_phase="validation",
        ...     revision_count=0,
        ...     is_sufficient=False,
        ...     user_approved=False,
        ...     missing_info=[],
        ...     last_update=None,
        ...     knowledge_context=None,
        ...     user_intent=None,
        ... )
        >>> result = critic_node(state)
        >>> result["is_sufficient"]
        False
    """
    artifact = state["process_artifact"]
    missing_info = []

    # Criterion 1: Has at least one StartEvent
    has_start = any(hasattr(node, "type") and node.type == "StartEvent" for node in artifact.nodes)
    if not has_start:
        missing_info.append("Falta evento de inicio (StartEvent)")

    # Criterion 2: Has at least one EndEvent
    has_end = any(hasattr(node, "type") and node.type == "EndEvent" for node in artifact.nodes)
    if not has_end:
        missing_info.append("Falta evento de fin (EndEvent)")

    # Criterion 3: All nodes should be connected (basic check)
    if len(artifact.nodes) > 0 and len(artifact.edges) == 0:
        missing_info.append("No hay conexiones entre nodos (sequence flows)")

    # Criterion 4: Check if analyst identified missing information
    last_update = state.get("last_update")
    if last_update is not None:
        analyst_missing = last_update.missing_information
        if analyst_missing:
            missing_info.extend(analyst_missing)

    # Criterion 5: Confidence score from analyst
    if last_update is not None:
        confidence = last_update.confidence_score
        if confidence < 0.7:
            missing_info.append(
                f"Confianza del analista baja ({confidence:.0%}). Revisar completitud del proceso."
            )

    # Determine sufficiency
    is_sufficient = len(missing_info) == 0

    return {"is_sufficient": is_sufficient, "missing_info": missing_info}
