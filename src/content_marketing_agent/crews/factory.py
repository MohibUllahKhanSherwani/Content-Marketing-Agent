from typing import Any

from crewai import Task


def task_from_config(config: Any) -> Task:
    """Build a CrewAI task from YAML config.

    CrewAI supports `Task(config=...)` at runtime, but its current type hints
    still require explicit `description` and `expected_output`.
    """

    return Task(config=config)  # type: ignore[call-arg]

