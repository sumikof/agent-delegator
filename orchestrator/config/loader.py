"""
Configuration loader for YAML workflow files.

Handles loading workflow configurations, template resolution, and multi-document YAML files.
"""

from pathlib import Path
from typing import Union
import yaml

from orchestrator.config.models import WorkflowConfig, AgentConfig
from orchestrator.utils.constants import (
    TEMPLATES_DIR,
    AGENT_INTERFACE_SCHEMA_PATH,
    AgentTemplateCategory,
)


class ConfigLoader:
    """Loads and parses workflow configuration files."""

    def __init__(self):
        """Initialize the configuration loader."""
        self._agent_templates_cache: dict[str, dict[str, AgentConfig]] | None = None

    def load_workflow(self, path: str | Path) -> WorkflowConfig:
        """
        Load workflow configuration from a YAML file.

        Args:
            path: Path to the workflow YAML file

        Returns:
            Validated WorkflowConfig instance

        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is invalid
            ValidationError: If the configuration doesn't match the schema
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")

        # Load YAML file (may have multiple documents)
        docs = self._load_yaml_file(path)

        # First document is the workflow definition
        workflow_dict = docs[0] if isinstance(docs, list) else docs

        # Second document (if exists) contains agent configurations
        agents_config = {}
        if isinstance(docs, list) and len(docs) > 1:
            agents_config = docs[1].get('agents_config', {})

        # Resolve agent templates if needed
        if 'agents' in workflow_dict and 'include_templates' in workflow_dict['agents']:
            template_names = workflow_dict['agents']['include_templates']
            resolved_agents = self._resolve_agent_templates(
                template_names,
                agents_config
            )
            # Store resolved agents for potential use
            # (Note: in full implementation, these would be registered)

        # Parse into Pydantic model (validates structure)
        config = WorkflowConfig(**workflow_dict)
        return config

    def load_template(self, template_name: str) -> WorkflowConfig:
        """
        Load a built-in workflow template.

        Args:
            template_name: Name of the template (e.g., 'web-fullstack')

        Returns:
            Validated WorkflowConfig instance

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_path = TEMPLATES_DIR / f"{template_name}.yaml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        return self.load_workflow(template_path)

    def list_templates(self) -> list[str]:
        """
        List all available templates.

        Returns:
            List of template names (without .yaml extension)
        """
        if not TEMPLATES_DIR.exists():
            return []

        templates = []
        for template_file in TEMPLATES_DIR.glob("*.yaml"):
            templates.append(template_file.stem)

        return sorted(templates)

    def _load_yaml_file(self, path: Path) -> Union[dict, list[dict]]:
        """
        Load YAML file, handling multi-document files.

        Args:
            path: Path to YAML file

        Returns:
            Single dict for single-document files, list of dicts for multi-document files

        Raises:
            yaml.YAMLError: If YAML is invalid
        """
        with open(path, 'r', encoding='utf-8') as f:
            docs = list(yaml.safe_load_all(f))

        # Filter out None documents (trailing --- can create empty documents)
        docs = [doc for doc in docs if doc is not None]

        if len(docs) == 0:
            raise ValueError(f"Empty YAML file: {path}")
        elif len(docs) == 1:
            return docs[0]
        else:
            return docs

    def _resolve_agent_templates(
        self,
        template_names: list[str],
        agents_config: dict[str, dict]
    ) -> dict[str, AgentConfig]:
        """
        Resolve agent template names to agent configurations.

        Args:
            template_names: List of template names (e.g., ['core', 'quality'])
            agents_config: Agent configurations from workflow file

        Returns:
            Dictionary mapping agent IDs to AgentConfig instances

        Raises:
            FileNotFoundError: If agent-interface.yaml doesn't exist
            ValueError: If template name is invalid
        """
        # Load template mappings from agent-interface.yaml
        template_mappings = self._load_agent_template_mappings()

        # Collect all agent IDs from templates
        agent_ids = set()
        for template_name in template_names:
            if template_name not in template_mappings:
                raise ValueError(f"Unknown agent template: {template_name}")
            agent_ids.update(template_mappings[template_name])

        # Build AgentConfig instances from agents_config
        resolved_agents = {}
        for agent_id in agent_ids:
            if agent_id not in agents_config:
                # Agent defined in template but not in config - skip with warning
                # (In production, we might want to load from a central registry)
                continue

            agent_dict = agents_config[agent_id]
            # Ensure 'id' field is set
            if 'id' not in agent_dict:
                agent_dict['id'] = agent_id

            try:
                resolved_agents[agent_id] = AgentConfig(**agent_dict)
            except Exception as e:
                raise ValueError(f"Invalid agent configuration for '{agent_id}': {e}")

        return resolved_agents

    def _load_agent_template_mappings(self) -> dict[str, list[str]]:
        """
        Load agent template to agent ID mappings from agent-interface.yaml.

        Returns:
            Dictionary mapping template names to lists of agent IDs

        Raises:
            FileNotFoundError: If agent-interface.yaml doesn't exist
        """
        if not AGENT_INTERFACE_SCHEMA_PATH.exists():
            raise FileNotFoundError(
                f"Agent interface schema not found: {AGENT_INTERFACE_SCHEMA_PATH}"
            )

        docs = self._load_yaml_file(AGENT_INTERFACE_SCHEMA_PATH)

        # agent-interface.yaml has multiple documents, templates are in the last one
        if isinstance(docs, list):
            # Find the document with 'templates' key
            for doc in docs:
                if 'templates' in doc:
                    templates = doc['templates']
                    break
            else:
                raise ValueError(
                    "No 'templates' section found in agent-interface.yaml"
                )
        else:
            if 'templates' not in docs:
                raise ValueError(
                    "No 'templates' section found in agent-interface.yaml"
                )
            templates = docs['templates']

        # Extract agent IDs from each template
        mappings = {}
        for template_name, template_config in templates.items():
            if 'agents' in template_config:
                mappings[template_name] = template_config['agents']

        return mappings

    def _merge_agent_configs(
        self,
        template_agents: dict[str, AgentConfig],
        custom_agents: list[dict],
        exclude: list[str]
    ) -> dict[str, AgentConfig]:
        """
        Merge template agents with custom agents, applying exclusions.

        Args:
            template_agents: Agents from templates
            custom_agents: Custom agent definitions
            exclude: Agent IDs to exclude

        Returns:
            Merged agent configurations

        Raises:
            ValueError: If custom agent configuration is invalid
        """
        # Start with template agents
        merged = dict(template_agents)

        # Remove excluded agents
        for agent_id in exclude:
            merged.pop(agent_id, None)

        # Add custom agents (may override template agents)
        for custom_agent_dict in custom_agents:
            agent_id = custom_agent_dict.get('id')
            if not agent_id:
                raise ValueError("Custom agent missing 'id' field")

            try:
                merged[agent_id] = AgentConfig(**custom_agent_dict)
            except Exception as e:
                raise ValueError(
                    f"Invalid custom agent configuration for '{agent_id}': {e}"
                )

        return merged


# Convenience functions

def load_workflow(path: str | Path) -> WorkflowConfig:
    """
    Convenience function to load a workflow configuration.

    Args:
        path: Path to workflow YAML file

    Returns:
        Validated WorkflowConfig instance
    """
    loader = ConfigLoader()
    return loader.load_workflow(path)


def load_template(template_name: str) -> WorkflowConfig:
    """
    Convenience function to load a workflow template.

    Args:
        template_name: Template name (e.g., 'web-fullstack')

    Returns:
        Validated WorkflowConfig instance
    """
    loader = ConfigLoader()
    return loader.load_template(template_name)


def list_templates() -> list[str]:
    """
    Convenience function to list available templates.

    Returns:
        List of template names
    """
    loader = ConfigLoader()
    return loader.list_templates()
