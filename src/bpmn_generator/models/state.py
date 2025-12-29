"""LangGraph State Models.

This module defines the state structure for the LangGraph workflow,
including AgentState (shared state) and structured outputs (ProcessUpdate,
ClarificationQuestion).
"""

from typing import Annotated, Literal, Optional, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from bpmn_generator.models.schema import (
    BPMNEdge,
    BPMNNode,
    DataAssociation,
    DataObjectNode,
    ProcessArtifact,
)

# ============================================================================
# LangGraph State (Shared Memory)
# ============================================================================


class AgentState(TypedDict):
    """Shared state passed between nodes in the LangGraph workflow.

    This TypedDict defines all the context that flows through the graph,
    including conversation history, the process artifact, and control flags.
    """

    # --- Conversational Memory ---
    # Using 'add_messages' so LangGraph handles append automatically
    messages: Annotated[list, add_messages]

    # --- Process State (Core) ---
    # The ProcessArtifact object defined in schema.py
    process_artifact: ProcessArtifact

    # --- Control Flow ---
    # Current logical phase
    current_phase: Literal["clarification", "validation", "generation", "completed"]

    # Counter to avoid infinite loops in auto-corrections
    revision_count: int

    # --- Routing Flags (Critical for Conditional Edges) ---
    # Whether the process meets minimum sufficiency criteria
    is_sufficient: bool

    # Whether the user has approved proceeding to generation
    user_approved: bool

    # List of missing information detected by critic_node
    missing_info: list[str]

    # --- Context for Chat Node ---
    # Last update made by analyzer_node (for user confirmation)
    last_update: Optional["ProcessUpdate"]

    # --- Future Scalability: RAG (Optional) ---
    # Context retrieved from knowledge base (ISO PDFs, BPMN guides)
    # Initially None. Will be populated if knowledge_retrieval_node is implemented
    knowledge_context: str | None

    # --- User Feedback ---
    # Last explicit instruction from user to guide the next node
    user_intent: (
        Literal["continue_interview", "approve_artifact", "modify_structure", "cancel"] | None
    )


# ============================================================================
# Structured Outputs (LLM Generates These)
# ============================================================================


class ProcessUpdate(BaseModel):
    """Structure that the LLM generates to modify the process.

    The analyzer_node outputs this to propose changes to the ProcessArtifact.
    """

    thoughts: str = Field(description="Analyst's reasoning about what changed")

    new_nodes: list[BPMNNode] = Field(default_factory=list)
    new_edges: list[BPMNEdge] = Field(default_factory=list)

    # Data architecture (ISO 19510)
    new_data_objects: list[DataObjectNode] = Field(
        default_factory=list, description="New data objects identified"
    )
    new_data_associations: list[DataAssociation] = Field(
        default_factory=list, description="New associations between tasks and data"
    )

    # Nodes to remove or modify
    nodes_to_remove: list[str] = Field(default_factory=list, description="IDs of nodes to delete")

    # Completeness state
    confidence_score: float = Field(
        description="0 to 1, how complete the analyst perceives the process to be"
    )
    missing_information: list[str] = Field(description="What's missing to close the flow")


class ClarificationQuestion(BaseModel):
    """Structure for asking the user clarifying questions.

    The chat_node outputs this when more information is needed.
    """

    question_text: str = Field(description="The question to ask the user")
    question_type: Literal["open", "choice", "confirmation"] = Field(description="Type of question")
    options: list[str] | None = Field(
        default=None, description="Options for 'choice' type questions"
    )
    context: str = Field(description="Why this question is being asked (for internal reasoning)")
