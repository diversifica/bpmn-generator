"""Generator agent - generates BPMN 2.0 XML (deterministic, no LLM).

This module implements the xml_generator_node which converts a ProcessArtifact
into valid BPMN 2.0 XML with Diagram Interchange (DI) coordinates.
"""

from xml.etree import ElementTree as ET

from bpmn_generator.models.schema import BPMNEdge, BPMNNode, ProcessArtifact
from bpmn_generator.models.state import AgentState
from bpmn_generator.utils.bpmn_validator import validate_bpmn_structure, validate_bpmn_xml
from bpmn_generator.utils.layout import (
    calculate_node_positions,
    calculate_waypoints,
    generate_bpmn_di_bounds,
    get_node_size,
)


def xml_generator_node(state: AgentState) -> dict:
    """Generate BPMN 2.0 XML from ProcessArtifact (deterministic).

    This node:
    1. Calculates node positions using Manhattan Grid
    2. Generates BPMN XML structure
    3. Adds Diagram Interchange (DI) elements
    4. Validates the XML
    5. Returns the XML string

    Args:
        state: Current AgentState with process_artifact.

    Returns:
        Dictionary with 'bpmn_xml' key containing the XML string.

    Examples:
        >>> from bpmn_generator.models.schema import StartEventNode, EndEventNode, BPMNEdge
        >>> state = AgentState(
        ...     messages=[],
        ...     process_artifact=ProcessArtifact(
        ...         process_id="proc1",
        ...         process_name="Test Process",
        ...         nodes=[StartEventNode(id="start1"), EndEventNode(id="end1")],
        ...         edges=[BPMNEdge(source_id="start1", target_id="end1")],
        ...     ),
        ...     current_phase="generation",
        ...     revision_count=0,
        ...     is_sufficient=True,
        ...     user_approved=True,
        ...     missing_info=[],
        ...     last_update=None,
        ...     knowledge_context=None,
        ...     user_intent=None,
        ... )
        >>> result = xml_generator_node(state)
        >>> "definitions" in result["bpmn_xml"]
        True
    """
    artifact = state["process_artifact"]

    # Calculate positions
    positions = calculate_node_positions(artifact)

    # Create XML structure
    xml_string = _generate_bpmn_xml(artifact, positions)

    # Validate
    is_valid, errors = validate_bpmn_xml(xml_string)
    if not is_valid:
        raise ValueError(f"Generated invalid BPMN XML: {errors}")

    is_valid_structure, structure_errors = validate_bpmn_structure(xml_string)
    if not is_valid_structure:
        raise ValueError(f"Generated BPMN with structural errors: {structure_errors}")

    return {"bpmn_xml": xml_string}


def _generate_bpmn_xml(artifact: ProcessArtifact, positions: dict[str, tuple[int, int]]) -> str:
    """Generate BPMN 2.0 XML string.

    Args:
        artifact: ProcessArtifact to convert.
        positions: Dictionary of node positions.

    Returns:
        BPMN XML string.
    """
    # Namespaces
    ns_bpmn = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    ns_bpmndi = "http://www.omg.org/spec/BPMN/20100524/DI"
    ns_dc = "http://www.omg.org/spec/DD/20100524/DC"
    ns_di = "http://www.omg.org/spec/DD/20100524/DI"

    # Register namespaces for proper prefixes
    ET.register_namespace("", ns_bpmn)  # Default namespace
    ET.register_namespace("bpmndi", ns_bpmndi)
    ET.register_namespace("dc", ns_dc)
    ET.register_namespace("di", ns_di)

    # Root element (don't manually add xmlns, ET will do it)
    definitions = ET.Element(
        f"{{{ns_bpmn}}}definitions",
        {
            "id": "Definitions_1",
            "targetNamespace": "http://bpmn.io/schema/bpmn",
        },
    )

    # Process element
    process = ET.SubElement(
        definitions,
        f"{{{ns_bpmn}}}process",
        {"id": artifact.process_id, "name": artifact.process_name, "isExecutable": "false"},
    )

    # Add nodes
    for node in artifact.nodes:
        _add_node_to_process(process, node, ns_bpmn)

    # Add edges
    for edge in artifact.edges:
        _add_edge_to_process(process, edge, ns_bpmn)

    # Add BPMNDiagram (DI)
    diagram = ET.SubElement(definitions, f"{{{ns_bpmndi}}}BPMNDiagram", {"id": "BPMNDiagram_1"})
    plane = ET.SubElement(
        diagram,
        f"{{{ns_bpmndi}}}BPMNPlane",
        {"id": "BPMNPlane_1", "bpmnElement": artifact.process_id},
    )

    # Add shapes for nodes
    for node in artifact.nodes:
        _add_shape_to_plane(plane, node, positions, ns_bpmndi, ns_dc)

    # Add edges to plane
    for edge in artifact.edges:
        _add_edge_to_plane(plane, edge, positions, artifact, ns_bpmndi, ns_di, ns_dc)

    # Convert to string
    xml_string = ET.tostring(definitions, encoding="unicode", method="xml")

    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'


def _add_node_to_process(process: ET.Element, node: "BPMNNode", ns: str) -> None:
    """Add a BPMN node to the process element."""
    node_type = node.type

    if node_type == "StartEvent":
        ET.SubElement(process, f"{{{ns}}}startEvent", {"id": node.id, "name": node.label})
    elif node_type == "EndEvent":
        ET.SubElement(process, f"{{{ns}}}endEvent", {"id": node.id, "name": node.label})
    elif node_type == "UserTask":
        task = ET.SubElement(process, f"{{{ns}}}userTask", {"id": node.id, "name": node.label})
        if hasattr(node, "role") and node.role:
            task.set("performer", node.role)
    elif node_type == "ServiceTask":
        ET.SubElement(process, f"{{{ns}}}serviceTask", {"id": node.id, "name": node.label})
    elif node_type == "ScriptTask":
        ET.SubElement(process, f"{{{ns}}}scriptTask", {"id": node.id, "name": node.label})
    elif node_type == "SendTask":
        ET.SubElement(process, f"{{{ns}}}sendTask", {"id": node.id, "name": node.label})
    elif node_type == "ReceiveTask":
        ET.SubElement(process, f"{{{ns}}}receiveTask", {"id": node.id, "name": node.label})
    elif node_type == "Gateway":
        if hasattr(node, "gateway_type"):
            gateway_type = node.gateway_type.lower() + "Gateway"
            ET.SubElement(process, f"{{{ns}}}{gateway_type}", {"id": node.id, "name": node.label})
    elif node_type == "SubProcess":
        ET.SubElement(process, f"{{{ns}}}subProcess", {"id": node.id, "name": node.label})


def _add_edge_to_process(process: ET.Element, edge: "BPMNEdge", ns: str) -> None:
    """Add a sequence flow to the process element."""
    attrs = {
        "id": f"Flow_{edge.source_id}_to_{edge.target_id}",
        "sourceRef": edge.source_id,
        "targetRef": edge.target_id,
    }
    if edge.condition:
        attrs["name"] = edge.condition
    ET.SubElement(process, f"{{{ns}}}sequenceFlow", attrs)


def _add_shape_to_plane(
    plane: ET.Element, node: "BPMNNode", positions: dict[str, tuple[int, int]], ns_bpmndi: str, ns_dc: str
) -> None:
    """Add a BPMNShape to the diagram plane."""
    bounds = generate_bpmn_di_bounds(node.id, positions, node)

    shape = ET.SubElement(
        plane, f"{{{ns_bpmndi}}}BPMNShape", {"id": f"{node.id}_di", "bpmnElement": node.id}
    )
    ET.SubElement(
        shape,
        f"{{{ns_dc}}}Bounds",
        {
            "x": str(bounds["x"]),
            "y": str(bounds["y"]),
            "width": str(bounds["width"]),
            "height": str(bounds["height"]),
        },
    )


def _add_edge_to_plane(
    plane: ET.Element,
    edge: "BPMNEdge",
    positions: dict[str, tuple[int, int]],
    artifact: ProcessArtifact,
    ns_bpmndi: str,
    ns_di: str,
    ns_dc: str,
) -> None:
    """Add a BPMNEdge to the diagram plane."""
    edge_id = f"Flow_{edge.source_id}_to_{edge.target_id}"

    bpmn_edge = ET.SubElement(
        plane, f"{{{ns_bpmndi}}}BPMNEdge", {"id": f"{edge_id}_di", "bpmnElement": edge_id}
    )

    # Get source and target nodes
    source_node = next((n for n in artifact.nodes if n.id == edge.source_id), None)
    target_node = next((n for n in artifact.nodes if n.id == edge.target_id), None)

    if source_node and target_node:
        source_pos = positions.get(edge.source_id, (200, 200))
        target_pos = positions.get(edge.target_id, (380, 200))
        source_size = get_node_size(source_node)
        target_size = get_node_size(target_node)

        waypoints = calculate_waypoints(source_pos, target_pos, source_size, target_size)

        for wp in waypoints:
            ET.SubElement(bpmn_edge, f"{{{ns_di}}}waypoint", {"x": str(wp[0]), "y": str(wp[1])})
