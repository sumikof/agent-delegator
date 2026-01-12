"""
Configuration validator using JSON Schema.

Provides validation against workflow-schema.yaml and agent-interface.yaml.
"""

from pathlib import Path
from typing import Any
import yaml
import jsonschema
from jsonschema import ValidationError, SchemaError

from orchestrator.utils.constants import (
    WORKFLOW_SCHEMA_PATH,
    AGENT_INTERFACE_SCHEMA_PATH,
)


class ConfigValidator:
    """Validates configurations against JSON schemas."""

    def __init__(self):
        """Initialize the validator."""
        self._workflow_schema_cache: dict | None = None
        self._agent_schema_cache: dict | None = None

    def validate_workflow(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate workflow configuration against workflow-schema.yaml.

        Args:
            config: Workflow configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        schema = self._load_workflow_schema()
        return self._validate_against_schema(config, schema)

    def validate_agent(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate agent configuration against agent-interface.yaml.

        Args:
            config: Agent configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        schema = self._load_agent_schema()
        return self._validate_against_schema(config, schema)

    def validate_against_schema(
        self,
        data: dict[str, Any],
        schema_path: str | Path
    ) -> tuple[bool, list[str]]:
        """
        Generic validation against a JSON Schema file.

        Args:
            data: Data to validate
            schema_path: Path to JSON Schema file (YAML format)

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            FileNotFoundError: If schema file doesn't exist
        """
        schema_path = Path(schema_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        # Load schema from YAML file
        with open(schema_path, 'r', encoding='utf-8') as f:
            docs = list(yaml.safe_load_all(f))

        # First document is the schema
        schema = docs[0] if docs else {}

        return self._validate_against_schema(data, schema)

    def _validate_against_schema(
        self,
        data: dict[str, Any],
        schema: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Validate data against a JSON schema.

        Args:
            data: Data to validate
            schema: JSON Schema

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        try:
            # Validate schema itself first
            jsonschema.Draft202012Validator.check_schema(schema)
        except SchemaError as e:
            return False, [f"Invalid schema: {e.message}"]

        try:
            # Validate data against schema
            validator = jsonschema.Draft202012Validator(schema)
            validation_errors = sorted(validator.iter_errors(data), key=str)

            if validation_errors:
                for error in validation_errors:
                    # Build a clear error message
                    path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                    message = f"[{path}] {error.message}"
                    errors.append(message)

                return False, errors

            return True, []

        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    def _load_workflow_schema(self) -> dict[str, Any]:
        """
        Load workflow schema from workflow-schema.yaml.

        Returns:
            JSON Schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
        """
        if self._workflow_schema_cache is not None:
            return self._workflow_schema_cache

        if not WORKFLOW_SCHEMA_PATH.exists():
            raise FileNotFoundError(
                f"Workflow schema not found: {WORKFLOW_SCHEMA_PATH}"
            )

        with open(WORKFLOW_SCHEMA_PATH, 'r', encoding='utf-8') as f:
            docs = list(yaml.safe_load_all(f))

        # First document is the schema
        self._workflow_schema_cache = docs[0] if docs else {}
        return self._workflow_schema_cache

    def _load_agent_schema(self) -> dict[str, Any]:
        """
        Load agent schema from agent-interface.yaml.

        Returns:
            JSON Schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
        """
        if self._agent_schema_cache is not None:
            return self._agent_schema_cache

        if not AGENT_INTERFACE_SCHEMA_PATH.exists():
            raise FileNotFoundError(
                f"Agent interface schema not found: {AGENT_INTERFACE_SCHEMA_PATH}"
            )

        with open(AGENT_INTERFACE_SCHEMA_PATH, 'r', encoding='utf-8') as f:
            docs = list(yaml.safe_load_all(f))

        # First document is the schema
        self._agent_schema_cache = docs[0] if docs else {}
        return self._agent_schema_cache


# Convenience functions

def validate_workflow(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Convenience function to validate workflow configuration.

    Args:
        config: Workflow configuration dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = ConfigValidator()
    return validator.validate_workflow(config)


def validate_agent(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Convenience function to validate agent configuration.

    Args:
        config: Agent configuration dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = ConfigValidator()
    return validator.validate_agent(config)
