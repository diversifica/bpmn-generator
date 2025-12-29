"""Prompt loading and templating utilities.

This module provides functions to load prompts from files and inject
dynamic content (like ProcessArtifact JSON) into prompt templates.
"""

from pathlib import Path
from typing import Any

from bpmn_generator.models.schema import ProcessArtifact


def load_prompt(prompt_name: str, base_dir: str = "prompts/base") -> str:
    """Load a prompt template from file.

    Args:
        prompt_name: Name of the prompt file (without .txt extension).
        base_dir: Base directory for prompts (relative to project root).

    Returns:
        Prompt content as string.

    Raises:
        FileNotFoundError: If prompt file doesn't exist.

    Examples:
        >>> prompt = load_prompt("analyst_rules")
        >>> "ISO 19510" in prompt
        True
    """
    # Get project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent
    prompt_path = project_root / base_dir / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}\nExpected location: {base_dir}/{prompt_name}.txt"
        )

    return prompt_path.read_text(encoding="utf-8")


def inject_artifact_json(prompt_template: str, artifact: ProcessArtifact, indent: int = 2) -> str:
    """Inject ProcessArtifact JSON into a prompt template.

    Replaces the placeholder {current_artifact_json} in the template
    with the JSON representation of the artifact.

    Args:
        prompt_template: Prompt template with {current_artifact_json} placeholder.
        artifact: ProcessArtifact to serialize.
        indent: JSON indentation level (default: 2).

    Returns:
        Prompt with artifact JSON injected.

    Examples:
        >>> artifact = ProcessArtifact(process_id="p1", process_name="Test")
        >>> template = "Current state: {current_artifact_json}"
        >>> result = inject_artifact_json(template, artifact)
        >>> "process_id" in result
        True
    """
    # Serialize artifact to JSON
    artifact_json = artifact.model_dump_json(indent=indent, exclude_none=True)

    # Replace placeholder
    return prompt_template.replace("{current_artifact_json}", artifact_json)


def format_prompt(prompt_template: str, **kwargs: Any) -> str:
    """Format a prompt template with arbitrary variables.

    Args:
        prompt_template: Template string with {variable} placeholders.
        **kwargs: Variables to inject into template.

    Returns:
        Formatted prompt.

    Examples:
        >>> template = "Hello {name}, you have {count} messages."
        >>> format_prompt(template, name="Alice", count=5)
        'Hello Alice, you have 5 messages.'
    """
    return prompt_template.format(**kwargs)


def load_and_inject_artifact(
    prompt_name: str, artifact: ProcessArtifact, base_dir: str = "prompts/base"
) -> str:
    """Load prompt and inject artifact JSON in one step.

    Convenience function combining load_prompt() and inject_artifact_json().

    Args:
        prompt_name: Name of the prompt file.
        artifact: ProcessArtifact to inject.
        base_dir: Base directory for prompts.

    Returns:
        Prompt with artifact JSON injected.

    Examples:
        >>> artifact = ProcessArtifact(process_id="p1", process_name="Test")
        >>> prompt = load_and_inject_artifact("analyst_base", artifact)
        >>> "process_id" in prompt
        True
    """
    template = load_prompt(prompt_name, base_dir)
    return inject_artifact_json(template, artifact)
