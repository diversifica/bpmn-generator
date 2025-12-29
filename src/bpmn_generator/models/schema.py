"""BPMN 2.0 Schema Models - ISO/IEC 19510 Compliant.

This module defines Pydantic models for BPMN elements following the ISO/IEC 19510
standard. All models use semantic typing (no generic Task nodes) and support
data architecture (DataObjects, DataAssociations).
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

# ============================================================================
# Event Nodes
# ============================================================================


class StartEventNode(BaseModel):
    """BPMN Start Event - marks the beginning of a process."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["StartEvent"] = "StartEvent"
    label: str = Field(default="Inicio", description="Event label")


class EndEventNode(BaseModel):
    """BPMN End Event - marks the end of a process."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["EndEvent"] = "EndEvent"
    label: str = Field(default="Fin", description="Event label")


class BoundaryEventNode(BaseModel):
    """BPMN Boundary Event - attached to an activity for error/timeout handling.

    ISO 19510: Boundary events are attached to the boundary of an activity and
    are triggered during the execution of that activity.
    """

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["BoundaryEvent"] = "BoundaryEvent"
    label: str = Field(description="Event label")
    attached_to_ref: str = Field(description="ID of the task/subprocess this event is attached to")
    event_type: Literal["error", "timer", "message"] = Field(description="Type of boundary event")
    cancel_activity: bool = Field(
        default=True, description="Whether this event interrupts the parent activity"
    )


# ============================================================================
# Task Nodes (ISO 19510 - Semantic Typing Mandatory)
# ============================================================================


class UserTaskNode(BaseModel):
    """BPMN User Task - requires human interaction."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["UserTask"] = "UserTask"
    label: str = Field(description="Task name")
    role: str | None = Field(default=None, description="Responsible role or actor")


class ServiceTaskNode(BaseModel):
    """BPMN Service Task - automated service/API call."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["ServiceTask"] = "ServiceTask"
    label: str = Field(description="Task name")
    implementation: str | None = Field(
        default=None, description="Implementation type (e.g., 'webService')"
    )


class ScriptTaskNode(BaseModel):
    """BPMN Script Task - executes a script."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["ScriptTask"] = "ScriptTask"
    label: str = Field(description="Task name")
    script_format: str | None = Field(default="python", description="Script language")


class SendTaskNode(BaseModel):
    """BPMN Send Task - sends a message."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["SendTask"] = "SendTask"
    label: str = Field(description="Task name")


class ReceiveTaskNode(BaseModel):
    """BPMN Receive Task - waits for a message."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["ReceiveTask"] = "ReceiveTask"
    label: str = Field(description="Task name")


# ============================================================================
# Control Flow Nodes
# ============================================================================

GatewayType = Literal["Exclusive", "Parallel", "Inclusive"]


class GatewayNode(BaseModel):
    """BPMN Gateway - decision or convergence point.

    ISO 19510: Gateways control the divergence and convergence of sequence flows.
    """

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["Gateway"] = "Gateway"
    label: str = Field(description="Decision question or condition")
    gateway_type: GatewayType = Field(description="Type of gateway")
    default_flow: str | None = Field(
        default=None,
        description="ID of the default sequence flow (happy path for Exclusive gateways)",
    )


class SubProcessNode(BaseModel):
    """BPMN SubProcess - encapsulates complex or iterative logic.

    ISO 19510: A subprocess is an activity whose internal details are defined
    as a flow of other activities.
    """

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["SubProcess"] = "SubProcess"
    label: str = Field(description="Subprocess name")
    is_expanded: bool = Field(
        default=True, description="Whether to show subprocess content in diagram"
    )
    loop_characteristics: Literal["sequential", "parallel"] | None = Field(
        default=None, description="Multi-instance loop type for batch processing"
    )


# ============================================================================
# Data Architecture (ISO 19510 Section 10.3)
# ============================================================================


class DataObjectNode(BaseModel):
    """BPMN Data Object - represents information created/manipulated in the process.

    ISO 19510: Data objects represent information flowing through the process,
    such as business documents, emails, or letters.
    """

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["DataObject"] = "DataObject"
    label: str = Field(description="Data name (e.g., 'Invoice', 'PDF File', 'Report')")
    is_collection: bool = Field(default=False, description="Whether this represents multiple items")


class DataObjectReferenceNode(BaseModel):
    """BPMN Data Object Reference - reference to a reusable data object."""

    id: str = Field(description="Unique identifier (UUID)")
    type: Literal["DataObjectReference"] = "DataObjectReference"
    label: str = Field(description="Reference label")
    data_object_ref: str = Field(description="ID of the DataObject being referenced")


# ============================================================================
# Union Type (Discriminated)
# ============================================================================

BPMNNode = Annotated[
    StartEventNode
    | EndEventNode
    | BoundaryEventNode
    | UserTaskNode
    | ServiceTaskNode
    | ScriptTaskNode
    | SendTaskNode
    | ReceiveTaskNode
    | GatewayNode
    | SubProcessNode
    | DataObjectNode
    | DataObjectReferenceNode,
    Field(discriminator="type"),
]


# ============================================================================
# Edges and Associations
# ============================================================================


class BPMNEdge(BaseModel):
    """BPMN Sequence Flow - represents the flow between two nodes."""

    source_id: str = Field(description="ID of the source node")
    target_id: str = Field(description="ID of the target node")
    condition: str | None = Field(
        default=None, description="Condition for this flow (e.g., 'Yes', 'No')"
    )
    is_default: bool = Field(
        default=False, description="Whether this is the default flow from a gateway"
    )


class DataAssociation(BaseModel):
    """BPMN Data Association - connects tasks with data objects (dotted line).

    ISO 19510: Data associations show the relationship between data objects
    and activities (input/output).
    """

    id: str = Field(description="Unique identifier")
    source_ref: str = Field(description="ID of source element (Task or DataObject)")
    target_ref: str = Field(description="ID of target element (Task or DataObject)")
    association_type: Literal["input", "output"] = Field(description="Direction of data flow")


# ============================================================================
# Process Artifact (Main Container)
# ============================================================================


class ProcessArtifact(BaseModel):
    """Main container for the business process knowledge.

    This is the "source of truth" - an intermediate JSON representation that
    will be transformed into BPMN XML. It's independent of the visual representation.
    """

    process_id: str
    process_name: str
    description: str | None = None

    # Graph structure
    nodes: list[BPMNNode] = Field(default_factory=list)
    edges: list[BPMNEdge] = Field(default_factory=list)

    # Data architecture (ISO 19510)
    data_objects: list[DataObjectNode] = Field(
        default_factory=list, description="Data objects processed in the flow"
    )
    data_associations: list[DataAssociation] = Field(
        default_factory=list, description="Associations between tasks and data"
    )

    # Quality metadata
    is_valid: bool = Field(default=False, description="Internal validation flag")
    validation_errors: list[str] = Field(
        default_factory=list, description="List of current validation errors"
    )

    # Traceability
    decision_log: list[dict] = Field(
        default_factory=list,
        description="History of why each element was created (for traceability)",
    )

    @model_validator(mode="after")
    def validate_graph_integrity(self) -> "ProcessArtifact":
        """Validate graph integrity: all edges must reference existing nodes.

        Also validates:
        - BoundaryEvents reference existing tasks
        - DataAssociations reference existing elements
        """
        node_ids = {node.id for node in self.nodes}
        errors = []

        # Validate edges
        for edge in self.edges:
            if edge.source_id not in node_ids:
                errors.append(f"Edge references non-existent source node: {edge.source_id}")
            if edge.target_id not in node_ids:
                errors.append(f"Edge references non-existent target node: {edge.target_id}")

        # Validate BoundaryEvents
        for node in self.nodes:
            if hasattr(node, "attached_to_ref"):  # BoundaryEventNode
                if node.attached_to_ref not in node_ids:
                    errors.append(
                        f"BoundaryEvent '{node.id}' references non-existent task: {node.attached_to_ref}"
                    )

        # Validate DataAssociations
        all_element_ids = node_ids | {do.id for do in self.data_objects}
        for assoc in self.data_associations:
            if assoc.source_ref not in all_element_ids:
                errors.append(
                    f"DataAssociation '{assoc.id}' references non-existent source: {assoc.source_ref}"
                )
            if assoc.target_ref not in all_element_ids:
                errors.append(
                    f"DataAssociation '{assoc.id}' references non-existent target: {assoc.target_ref}"
                )

        # Update validation fields
        self.validation_errors = errors
        self.is_valid = len(errors) == 0
        return self
