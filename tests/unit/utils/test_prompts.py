"""Unit tests for prompt utilities."""

import pytest

from bpmn_generator.models.schema import ProcessArtifact, UserTaskNode
from bpmn_generator.utils.prompts import (
    format_prompt,
    inject_artifact_json,
    load_and_inject_artifact,
    load_prompt,
)


def test_load_prompt_analyst_rules() -> None:
    """Test loading analyst_rules.txt prompt."""
    prompt = load_prompt("analyst_rules")
    assert "BPMN 2.0" in prompt
    assert "TIPADO SEMÁNTICO" in prompt
    assert "UserTask" in prompt


def test_load_prompt_not_found() -> None:
    """Test loading non-existent prompt raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_prompt("non_existent_prompt")
    assert "Prompt file not found" in str(exc_info.value)


def test_inject_artifact_json() -> None:
    """Test injecting ProcessArtifact JSON into template."""
    artifact = ProcessArtifact(
        process_id="test_proc",
        process_name="Test Process",
        nodes=[UserTaskNode(id="task_1", label="Test Task", role="Manager")],
    )

    template = "Current state:\n{current_artifact_json}\nEnd of state."
    result = inject_artifact_json(template, artifact)

    assert "test_proc" in result
    assert "Test Process" in result
    assert "task_1" in result
    assert "Manager" in result
    assert "{current_artifact_json}" not in result


def test_inject_artifact_json_indent() -> None:
    """Test JSON indentation in inject_artifact_json."""
    artifact = ProcessArtifact(process_id="p1", process_name="Test")
    template = "{current_artifact_json}"

    result = inject_artifact_json(template, artifact, indent=4)
    # Check that JSON is indented (has newlines and spaces)
    assert "\n" in result
    assert "    " in result  # 4-space indent


def test_format_prompt() -> None:
    """Test formatting prompt with variables."""
    template = "Hello {name}, you have {count} messages."
    result = format_prompt(template, name="Alice", count=5)
    assert result == "Hello Alice, you have 5 messages."


def test_format_prompt_multiple_variables() -> None:
    """Test formatting with multiple variables."""
    template = "Process: {process_name}\nPhase: {phase}\nCount: {count}"
    result = format_prompt(template, process_name="Invoice Approval", phase="validation", count=3)
    assert "Invoice Approval" in result
    assert "validation" in result
    assert "3" in result


def test_load_and_inject_artifact() -> None:
    """Test convenience function load_and_inject_artifact."""
    artifact = ProcessArtifact(
        process_id="test_id",
        process_name="Test",
        nodes=[UserTaskNode(id="task_1", label="Task")],
    )

    # Note: analyst_rules.txt doesn't have {current_artifact_json} placeholder
    # so this just loads the prompt without injection
    result = load_and_inject_artifact("analyst_rules", artifact)

    # Should contain prompt content
    assert "BPMN 2.0" in result  # From prompt
    # Artifact won't be injected since there's no placeholder
    assert "{current_artifact_json}" not in result
