"""
Formatters for displaying workflow configurations.

Provides human-readable formatting of WorkflowConfig objects.
"""

from orchestrator.config.models import (
    WorkflowConfig,
    ProjectConfig,
    StageConfig,
    ErrorHandling,
)


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    RED = "\033[91m"


class WorkflowFormatter:
    """Formats workflow configurations for display."""

    def __init__(self, use_colors: bool = True):
        """
        Initialize the formatter.

        Args:
            use_colors: Whether to use ANSI colors in output
        """
        self.use_colors = use_colors

    def format_workflow_summary(self, config: WorkflowConfig) -> str:
        """
        Format complete workflow configuration.

        Args:
            config: WorkflowConfig to format

        Returns:
            Formatted string
        """
        sections = []

        # Header
        sections.append(self._format_header(config.project.name))

        # Project info
        sections.append(self.format_project_info(config.project))

        # Agent templates
        if config.agents and config.agents.include_templates:
            sections.append(self._format_agent_templates(config.agents.include_templates))

        # Workflow stages
        sections.append(self.format_stages(config.workflow.stages))

        # Error handling
        if config.workflow.error_handling:
            sections.append(self.format_error_handling(config.workflow.error_handling))

        # Global timeout
        timeout_hours = config.workflow.global_timeout_ms / 3600000
        timeout_str = (
            f"{timeout_hours:.1f} hours"
            if timeout_hours >= 1
            else f"{config.workflow.global_timeout_ms / 60000:.0f} minutes"
        )
        sections.append(f"\n{self._bold('Global Timeout:')} {timeout_str}")

        return "\n".join(sections)

    def format_project_info(self, project: ProjectConfig) -> str:
        """
        Format project information.

        Args:
            project: ProjectConfig to format

        Returns:
            Formatted string
        """
        lines = [
            self._section_header("Project Details"),
            f"  {self._label('Name:')} {project.name}",
            f"  {self._label('Type:')} {project.type.value}",
        ]

        if project.description:
            lines.append(f"  {self._label('Description:')} {project.description}")

        if project.language_policy:
            lp = project.language_policy
            lines.append(
                f"  {self._label('Language Policy:')} Customer-facing ({lp.customer_facing}), Development ({lp.development})"
            )

        return "\n".join(lines)

    def format_stages(self, stages: list[StageConfig]) -> str:
        """
        Format workflow stages.

        Args:
            stages: List of StageConfig to format

        Returns:
            Formatted string
        """
        lines = [self._section_header(f"Workflow Stages ({len(stages)})")]

        for idx, stage in enumerate(stages, 1):
            lines.append(f"  {self._bold(f'{idx}. {stage.name}')} [{stage.execution_mode.value}]")

            # Agents
            if len(stage.agents) == 1:
                lines.append(f"     {self._gray('→')} {stage.agents[0]}")
            else:
                lines.append(f"     {self._gray('→')} {', '.join(stage.agents)}")

            # Gate configuration
            if stage.gate:
                gate_info = []
                gate_info.append(f"Required status = {stage.gate.required_status.value}")
                if stage.gate.allow_warnings:
                    gate_info.append("Allow warnings")
                if stage.gate.max_errors > 0:
                    gate_info.append(f"Max errors = {stage.gate.max_errors}")
                lines.append(f"     {self._gray('Gate:')} {', '.join(gate_info)}")

            # Timeout
            if stage.timeout_ms:
                timeout_min = stage.timeout_ms / 60000
                lines.append(f"     {self._gray('Timeout:')} {timeout_min:.0f}m")

            # On failure
            if stage.on_failure:
                lines.append(f"     {self._gray('On failure:')} {stage.on_failure.value}")

            # Add blank line between stages
            if idx < len(stages):
                lines.append("")

        return "\n".join(lines)

    def format_error_handling(self, error_handling: ErrorHandling) -> str:
        """
        Format error handling configuration.

        Args:
            error_handling: ErrorHandling to format

        Returns:
            Formatted string
        """
        lines = [self._section_header("Error Handling")]

        # Retry policy
        if error_handling.retry_policy:
            rp = error_handling.retry_policy
            initial_s = rp.initial_delay_ms / 1000
            max_s = rp.max_delay_ms / 1000
            lines.append(
                f"  {self._label('Retry:')} {rp.max_attempts} attempts, "
                f"{rp.backoff_type.value} backoff ({initial_s:.1f}s → {max_s:.0f}s)"
            )

        # Circuit breaker
        if error_handling.circuit_breaker and error_handling.circuit_breaker.enabled:
            cb = error_handling.circuit_breaker
            recovery_s = cb.recovery_timeout_ms / 1000
            lines.append(
                f"  {self._label('Circuit Breaker:')} {cb.failure_threshold} failures → open, "
                f"{recovery_s:.0f}s recovery"
            )

        # Fallback strategies
        if error_handling.fallback_strategies:
            fallback_strs = [
                f"{fb.condition.value} → {fb.action.value}"
                for fb in error_handling.fallback_strategies
            ]
            lines.append(f"  {self._label('Fallback:')} {' / '.join(fallback_strs)}")

        return "\n".join(lines)

    def _format_header(self, title: str) -> str:
        """Format section header."""
        separator = "=" * 60
        return f"\n{self._bold(f'Workflow Configuration: {title}')}\n{self._gray(separator)}"

    def _format_agent_templates(self, templates: list[str]) -> str:
        """Format agent templates list."""
        lines = [self._section_header("Agent Templates")]
        for template in templates:
            lines.append(f"  {self._green('✓')} {template}")
        return "\n".join(lines)

    def _section_header(self, title: str) -> str:
        """Format a section header."""
        return f"\n{self._cyan(title)}:"

    def _label(self, text: str) -> str:
        """Format a label."""
        return self._blue(text)

    def _bold(self, text: str) -> str:
        """Make text bold."""
        if not self.use_colors:
            return text
        return f"{Colors.BOLD}{text}{Colors.RESET}"

    def _green(self, text: str) -> str:
        """Make text green."""
        if not self.use_colors:
            return text
        return f"{Colors.GREEN}{text}{Colors.RESET}"

    def _yellow(self, text: str) -> str:
        """Make text yellow."""
        if not self.use_colors:
            return text
        return f"{Colors.YELLOW}{text}{Colors.RESET}"

    def _blue(self, text: str) -> str:
        """Make text blue."""
        if not self.use_colors:
            return text
        return f"{Colors.BLUE}{text}{Colors.RESET}"

    def _cyan(self, text: str) -> str:
        """Make text cyan."""
        if not self.use_colors:
            return text
        return f"{Colors.CYAN}{text}{Colors.RESET}"

    def _gray(self, text: str) -> str:
        """Make text gray."""
        if not self.use_colors:
            return text
        return f"{Colors.GRAY}{text}{Colors.RESET}"

    def _red(self, text: str) -> str:
        """Make text red."""
        if not self.use_colors:
            return text
        return f"{Colors.RED}{text}{Colors.RESET}"


# Convenience functions


def format_workflow(config: WorkflowConfig, use_colors: bool = True) -> str:
    """
    Convenience function to format a workflow configuration.

    Args:
        config: WorkflowConfig to format
        use_colors: Whether to use ANSI colors

    Returns:
        Formatted string
    """
    formatter = WorkflowFormatter(use_colors=use_colors)
    return formatter.format_workflow_summary(config)
