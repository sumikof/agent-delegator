#!/usr/bin/env python3
"""
Schema validation script for OpenHands Agent Delegation workflows.

This script validates workflow configuration files against the defined schemas.
"""

import json
import sys
import yaml
from pathlib import Path
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError


def load_yaml_file(file_path: str) -> dict:
    """Load YAML file and return as dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}")
        sys.exit(1)


def validate_workflow_config(config_data: dict, schema_data: dict) -> bool:
    """Validate workflow configuration against schema."""
    try:
        validate(instance=config_data, schema=schema_data)
        print("✅ Workflow configuration is valid!")
        return True
    except ValidationError as e:
        print(f"❌ Validation error: {e.message}")
        print(f"   Path: {' -> '.join(str(p) for p in e.path)}")
        if e.context:
            print(f"   Context: {e.context}")
        return False
    except SchemaError as e:
        print(f"❌ Schema error: {e.message}")
        return False


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python validate_schema.py <workflow-config-file>")
        print("Example: python validate_schema.py examples/simple-web-app/workflow.yaml")
        sys.exit(1)

    config_file = sys.argv[1]

    # Load schema
    schema_path = Path("schemas/workflow-schema.yaml")
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        sys.exit(1)

    schema_data = load_yaml_file(schema_path)

    # Load config
    config_data = load_yaml_file(config_file)

    print(f"Validating workflow configuration: {config_file}")
    print(f"Using schema: {schema_path}")
    print("-" * 50)

    # Validate
    is_valid = validate_workflow_config(config_data, schema_data)

    if not is_valid:
        sys.exit(1)

    print("\nValidation completed successfully!")


if __name__ == "__main__":
    main()
