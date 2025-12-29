"""Chat agent - interacts with user for clarifications.

This module implements the chat_node which generates clarification questions
when the ProcessArtifact is insufficient.
"""

from langchain_core.messages import AIMessage, SystemMessage

from bpmn_generator.models.state import AgentState, ClarificationQuestion
from bpmn_generator.utils.llm_provider import get_default_llm


def chat_node(state: AgentState) -> dict:
    """Generate clarification questions for the user.

    This node:
    1. Analyzes missing_info from critic
    2. Generates a ClarificationQuestion
    3. Returns it as an AI message

    Args:
        state: Current AgentState with missing_info.

    Returns:
        Dictionary with 'messages' key containing new AI message.

    Examples:
        >>> state = AgentState(
        ...     messages=[],
        ...     process_artifact=ProcessArtifact(process_id="p1", process_name="Test"),
        ...     current_phase="clarification",
        ...     revision_count=0,
        ...     is_sufficient=False,
        ...     user_approved=False,
        ...     missing_info=["Falta evento de inicio"],
        ...     last_update=None,
        ...     knowledge_context=None,
        ...     user_intent=None,
        ... )
        >>> result = chat_node(state)
        >>> len(result["messages"])
        1
    """
    missing_info = state.get("missing_info", [])

    # Get LLM instance
    llm = get_default_llm()

    # Create system prompt
    system_prompt = """Eres un asistente experto en BPMN que ayuda a usuarios a describir sus procesos.

Tu tarea es generar UNA pregunta de clarificación basada en la información faltante.

REGLAS:
1. Haz UNA pregunta a la vez (la más importante)
2. Sé específico y claro
3. Usa lenguaje natural y amigable
4. Si hay múltiples cosas faltantes, prioriza lo más crítico

INFORMACIÓN FALTANTE:
{missing_info}

Genera una ClarificationQuestion estructurada."""

    # Format missing info
    missing_info_text = "\n".join(f"- {info}" for info in missing_info)
    system_prompt = system_prompt.format(missing_info=missing_info_text)

    # Prepare messages
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    # Invoke LLM with structured output
    llm_with_structure = llm.with_structured_output(ClarificationQuestion)
    question = llm_with_structure.invoke(messages)

    # Create AI message with the question
    # Handle both ClarificationQuestion object and dict
    if hasattr(question, "question_text"):
        question_text = question.question_text
    elif isinstance(question, dict):
        question_text = question.get("question_text", "¿Puedes darme más detalles?")
    else:
        question_text = "¿Puedes darme más detalles?"

    ai_message = AIMessage(content=question_text)

    return {"messages": [ai_message]}
