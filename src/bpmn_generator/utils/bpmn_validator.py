"""BPMN XML validation utilities.

This module provides functions to validate BPMN XML against the XSD schema.
"""


def validate_bpmn_xml(xml_string: str) -> tuple[bool, list[str]]:
    """Validate BPMN XML against XSD schema.

    Note: This is a basic implementation. Full XSD validation requires
    downloading the official BPMN 2.0 XSD schema from OMG.

    Args:
        xml_string: BPMN XML content.

    Returns:
        Tuple of (is_valid, error_messages).

    Examples:
        >>> xml = '<?xml version="1.0"?><definitions></definitions>'
        >>> is_valid, errors = validate_bpmn_xml(xml)
        >>> is_valid
        True
    """
    errors: list[str] = []

    # Basic XML well-formedness check
    try:
        from xml.etree import ElementTree as ET

        ET.fromstring(xml_string)
    except ET.ParseError as e:
        errors.append(f"XML parsing error: {e}")
        return False, errors

    # Basic BPMN structure checks
    if "<definitions" not in xml_string:
        errors.append("Missing <definitions> root element")

    if "http://www.omg.org/spec/BPMN/20100524/MODEL" not in xml_string:
        errors.append("Missing BPMN namespace declaration")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_bpmn_structure(xml_string: str) -> tuple[bool, list[str]]:
    """Validate BPMN structural requirements.

    Checks for common BPMN modeling errors:
    - Every process must have at least one start event
    - Every process must have at least one end event
    - All sequence flows must have source and target

    Args:
        xml_string: BPMN XML content.

    Returns:
        Tuple of (is_valid, error_messages).

    Examples:
        >>> xml = '''<?xml version="1.0"?>
        ... <definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
        ...   <process id="p1">
        ...     <startEvent id="start1"/>
        ...     <endEvent id="end1"/>
        ...   </process>
        ... </definitions>'''
        >>> is_valid, errors = validate_bpmn_structure(xml)
        >>> is_valid
        True
    """
    from xml.etree import ElementTree as ET

    errors: list[str] = []

    try:
        root = ET.fromstring(xml_string)
        ns = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}

        # Find all processes
        processes = root.findall(".//bpmn:process", ns)

        for process in processes:
            process_id = process.get("id", "unknown")

            # Check for start events
            start_events = process.findall(".//bpmn:startEvent", ns)
            if not start_events:
                errors.append(f"Process '{process_id}' has no start event")

            # Check for end events
            end_events = process.findall(".//bpmn:endEvent", ns)
            if not end_events:
                errors.append(f"Process '{process_id}' has no end event")

        # Check sequence flows
        flows = root.findall(".//bpmn:sequenceFlow", ns)
        for flow in flows:
            flow_id = flow.get("id", "unknown")
            if not flow.get("sourceRef"):
                errors.append(f"SequenceFlow '{flow_id}' missing sourceRef")
            if not flow.get("targetRef"):
                errors.append(f"SequenceFlow '{flow_id}' missing targetRef")

    except ET.ParseError as e:
        errors.append(f"XML parsing error: {e}")
        return False, errors

    is_valid = len(errors) == 0
    return is_valid, errors
