"""Unit tests for BPMN validator."""

from bpmn_generator.utils.bpmn_validator import (
    validate_bpmn_structure,
    validate_bpmn_xml,
)


def test_validate_bpmn_xml_valid() -> None:
    """Test validating valid BPMN XML."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="proc1"/>
</definitions>"""

    is_valid, errors = validate_bpmn_xml(xml)
    assert is_valid
    assert len(errors) == 0


def test_validate_bpmn_xml_malformed() -> None:
    """Test validating malformed XML."""
    xml = "<definitions><unclosed>"

    is_valid, errors = validate_bpmn_xml(xml)
    assert not is_valid
    assert len(errors) > 0
    assert "parsing error" in errors[0].lower()


def test_validate_bpmn_xml_missing_definitions() -> None:
    """Test validating XML without definitions element."""
    xml = '<?xml version="1.0"?><root/>'

    is_valid, errors = validate_bpmn_xml(xml)
    assert not is_valid
    assert any("definitions" in err.lower() for err in errors)


def test_validate_bpmn_xml_missing_namespace() -> None:
    """Test validating XML without BPMN namespace."""
    xml = '<?xml version="1.0"?><definitions/>'

    is_valid, errors = validate_bpmn_xml(xml)
    assert not is_valid
    assert any("namespace" in err.lower() for err in errors)


def test_validate_bpmn_structure_valid() -> None:
    """Test validating BPMN with correct structure."""
    xml = """<?xml version="1.0"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="p1">
    <startEvent id="start1"/>
    <endEvent id="end1"/>
    <sequenceFlow id="flow1" sourceRef="start1" targetRef="end1"/>
  </process>
</definitions>"""

    is_valid, errors = validate_bpmn_structure(xml)
    assert is_valid
    assert len(errors) == 0


def test_validate_bpmn_structure_missing_start_event() -> None:
    """Test validating BPMN without start event."""
    xml = """<?xml version="1.0"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="p1">
    <endEvent id="end1"/>
  </process>
</definitions>"""

    is_valid, errors = validate_bpmn_structure(xml)
    assert not is_valid
    assert any("start event" in err.lower() for err in errors)


def test_validate_bpmn_structure_missing_end_event() -> None:
    """Test validating BPMN without end event."""
    xml = """<?xml version="1.0"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="p1">
    <startEvent id="start1"/>
  </process>
</definitions>"""

    is_valid, errors = validate_bpmn_structure(xml)
    assert not is_valid
    assert any("end event" in err.lower() for err in errors)


def test_validate_bpmn_structure_missing_source_ref() -> None:
    """Test validating sequence flow without sourceRef."""
    xml = """<?xml version="1.0"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="p1">
    <startEvent id="start1"/>
    <endEvent id="end1"/>
    <sequenceFlow id="flow1" targetRef="end1"/>
  </process>
</definitions>"""

    is_valid, errors = validate_bpmn_structure(xml)
    assert not is_valid
    assert any("sourceref" in err.lower() for err in errors)


def test_validate_bpmn_structure_missing_target_ref() -> None:
    """Test validating sequence flow without targetRef."""
    xml = """<?xml version="1.0"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="p1">
    <startEvent id="start1"/>
    <endEvent id="end1"/>
    <sequenceFlow id="flow1" sourceRef="start1"/>
  </process>
</definitions>"""

    is_valid, errors = validate_bpmn_structure(xml)
    assert not is_valid
    assert any("targetref" in err.lower() for err in errors)
