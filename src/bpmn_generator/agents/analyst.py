"""Analyst agent - analyzes conversation and proposes changes to ProcessArtifact.

This module implements the analyzer_node which is the core of the system.
It reads the conversation history and the current ProcessArtifact, then proposes
changes following ISO 19510 BPMN modeling rules.
"""

from langchain_core.messages import SystemMessage

from bpmn_generator.models.state import AgentState, ProcessUpdate
from bpmn_generator.utils.llm_provider import get_default_llm
from bpmn_generator.utils.prompts import inject_artifact_json, load_prompt


def analyzer_node(state: AgentState) -> dict:
    """Analyze conversation and propose changes to the ProcessArtifact.

    This node:
    1. Loads the analyst prompt with ISO 19510 rules
    2. Injects the current ProcessArtifact JSON
    3. Invokes the LLM with structured output (ProcessUpdate)
    4. Returns the proposed update

    Args:
        state: Current AgentState with messages and process_artifact.

    Returns:
        Dictionary with 'last_update' key containing ProcessUpdate.

    Examples:
        >>> state = AgentState(
        ...     messages=[],
        ...     process_artifact=ProcessArtifact(process_id="p1", process_name="Test"),
        ...     current_phase="clarification",
        ...     revision_count=0,
        ...     is_sufficient=False,
        ...     user_approved=False,
        ...     missing_info=[],
        ...     last_update=None,
        ...     knowledge_context=None,
        ...     user_intent=None,
        ... )
        >>> result = analyzer_node(state)
        >>> isinstance(result["last_update"], ProcessUpdate)
        True
    """
    # Get LLM instance (respects LLM_PROVIDER env var)
    llm = get_default_llm()

    # Load analyst rules prompt
    analyst_rules = load_prompt("analyst_rules")

    # Create system message with rules and current artifact
    system_prompt = f"""Eres un analista experto en modelado de procesos BPMN 2.0 (ISO/IEC 19510).

Tu tarea es analizar la conversación con el usuario y proponer cambios al ProcessArtifact actual.

{analyst_rules}

ARTEFACTO ACTUAL:
{{current_artifact_json}}

INSTRUCCIONES:
1. Lee la conversación completa
2. Identifica QUÉ cambios proponer al artefacto
3. Genera un ProcessUpdate estructurado con:
   - thoughts: Tu razonamiento interno
   - new_nodes: Nodos a añadir
   - new_edges: Conexiones a añadir
   - new_data_objects: Datos a añadir
   - new_data_associations: Asociaciones de datos
   - nodes_to_remove: IDs de nodos a eliminar
   - confidence_score: 0-1, qué tan completo está el proceso
   - missing_information: Lista de lo que falta para cerrar el flujo

IMPORTANTE:
- NO inventes información
- Si no sabes algo, ponlo en missing_information
- Sigue ESTRICTAMENTE las reglas ISO 19510
- NO generes texto conversacional, solo datos estructurados
"""

    # Inject current artifact JSON
    system_prompt_with_artifact = inject_artifact_json(system_prompt, state["process_artifact"])

    # Prepare messages
    messages = [SystemMessage(content=system_prompt_with_artifact)] + state["messages"]

    # Invoke LLM with structured output
    llm_with_structure = llm.with_structured_output(ProcessUpdate)
    update = llm_with_structure.invoke(messages)

    return {"last_update": update}
