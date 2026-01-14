"""
Command-line interface for agent-delegate orchestration system.

Provides commands for validating, displaying, and managing workflow configurations.
"""

import sys
import json
from pathlib import Path
import click
from pydantic import ValidationError

from orchestrator import __version__
from orchestrator.config.loader import ConfigLoader
from orchestrator.config.validator import ConfigValidator
from orchestrator.display.formatter import WorkflowFormatter
from orchestrator.main import run as run_workflow


@click.group()
@click.version_option(version=__version__, prog_name="agent-delegate")
@click.pass_context
def main(ctx):
    """
    Agent-Delegate Orchestration System

    Multi-agent orchestration using OpenHands SDK for virtual development organizations.
    """
    ctx.ensure_object(dict)


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed validation output")
def validate(workflow_file: str, verbose: bool):
    """
    Validate a workflow configuration file.

    WORKFLOW_FILE: Path to the workflow YAML file
    """
    try:
        loader = ConfigLoader()
        validator = ConfigValidator()

        # Load YAML
        if verbose:
            click.echo(f"Loading workflow file: {workflow_file}")

        workflow_path = Path(workflow_file)
        docs = loader._load_yaml_file(workflow_path)
        workflow_dict = docs[0] if isinstance(docs, list) else docs

        # JSON Schema validation
        if verbose:
            click.echo("Validating against JSON Schema...")

        is_valid, errors = validator.validate_workflow(workflow_dict)

        if not is_valid:
            click.secho("✗ JSON Schema validation failed:", fg="red", bold=True)
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        if verbose:
            click.secho("✓ JSON Schema validation passed", fg="green")

        # Pydantic model validation
        if verbose:
            click.echo("Validating with Pydantic models...")

        try:
            config = loader.load_workflow(workflow_path)
        except ValidationError as e:
            click.secho("✗ Pydantic validation failed:", fg="red", bold=True)
            if verbose:
                click.echo(str(e))
            else:
                for error in e.errors():
                    loc = " -> ".join(str(loc_part) for loc_part in error["loc"])
                    click.echo(f"  - [{loc}] {error['msg']}")
            sys.exit(1)
        except Exception as e:
            click.secho(f"✗ Validation failed: {e}", fg="red", bold=True)
            if verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

        # Success
        click.secho("✓ Configuration is valid", fg="green", bold=True)

        if verbose:
            click.echo(f"\nWorkflow: {config.project.name}")
            click.echo(f"Type: {config.project.type.value}")
            click.echo(f"Stages: {len(config.workflow.stages)}")

    except FileNotFoundError as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e}", fg="red", bold=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
)
@click.option("--no-color", is_flag=True, help="Disable colored output")
def show(workflow_file: str, format: str, no_color: bool):
    """
    Display workflow configuration details.

    WORKFLOW_FILE: Path to the workflow YAML file
    """
    try:
        loader = ConfigLoader()
        config = loader.load_workflow(workflow_file)

        if format == "json":
            # Output as JSON
            output = config.model_dump(mode="json")
            click.echo(json.dumps(output, indent=2))
        else:
            # Output as formatted text
            formatter = WorkflowFormatter(use_colors=not no_color)
            output = formatter.format_workflow_summary(config)
            click.echo(output)

    except FileNotFoundError as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)
    except ValidationError as e:
        click.secho("✗ Invalid configuration:", fg="red", bold=True)
        for error in e.errors():
            loc = " -> ".join(str(loc_part) for loc_part in error["loc"])
            click.echo(f"  - [{loc}] {error['msg']}")
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)


@main.command(name="list-templates")
def list_templates():
    """
    List all available workflow templates.
    """
    try:
        loader = ConfigLoader()
        templates = loader.list_templates()

        if not templates:
            click.echo("No templates found.")
            return

        click.secho(f"Available Templates ({len(templates)}):", bold=True)
        click.echo()

        for template_name in templates:
            try:
                # Load template to get description
                config = loader.load_template(template_name)
                description = config.project.description or "No description"
                type_str = config.project.type.value

                click.secho(f"  {template_name}", fg="cyan", bold=True)
                click.echo(f"    Type: {type_str}")
                click.echo(f"    Description: {description}")
                click.echo(f"    Stages: {len(config.workflow.stages)}")
                click.echo()

            except Exception as e:
                click.secho(f"  {template_name}", fg="cyan", bold=True)
                click.secho(f"    Error loading template: {e}", fg="red")
                click.echo()

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)


@main.command()
@click.argument("template_name")
@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
)
@click.option("--no-color", is_flag=True, help="Disable colored output")
def info(template_name: str, format: str, no_color: bool):
    """
    Show detailed information about a template.

    TEMPLATE_NAME: Name of the template (e.g., 'web-fullstack')
    """
    try:
        loader = ConfigLoader()
        config = loader.load_template(template_name)

        if format == "json":
            # Output as JSON
            output = config.model_dump(mode="json")
            click.echo(json.dumps(output, indent=2))
        else:
            # Output as formatted text
            formatter = WorkflowFormatter(use_colors=not no_color)
            output = formatter.format_workflow_summary(config)
            click.echo(output)

    except FileNotFoundError:
        click.secho(f"✗ Template not found: {template_name}", fg="red", bold=True)
        click.echo("\nAvailable templates:")
        loader = ConfigLoader()
        templates = loader.list_templates()
        for t in templates:
            click.echo(f"  - {t}")
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--parallel", "-p", is_flag=True, help="Execute workflow using parallel processing")
@click.option("--feedback-loop", "-f", is_flag=True, help="Enable feedback loop with quality reviews")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed execution output")
def run(workflow_file: str, parallel: bool, feedback_loop: bool, verbose: bool):
    """
    Execute a workflow configuration.

    WORKFLOW_FILE: Path to the workflow YAML file
    """
    try:
        if verbose:
            click.echo(f"Starting workflow execution: {workflow_file}")
            click.echo(f"Parallel mode: {'enabled' if parallel else 'disabled'}")
            click.echo(f"Feedback loop: {'enabled' if feedback_loop else 'disabled'}")
        
        # Execute workflow
        result = run_workflow(workflow_file, use_parallel=parallel, use_feedback_loop=feedback_loop)
        
        # Output results
        if verbose:
            click.echo("\nExecution Results:")
            click.echo(f"Status: {result['status']}")
            click.echo(f"Summary: {result['summary']}")
            click.echo(f"Execution Time: {result['execution_time_ms']}ms")
            
            if result.get('findings'):
                click.echo("\nFindings:")
                for finding in result['findings']:
                    severity = finding['severity']
                    color = {
                        'INFO': 'blue',
                        'WARN': 'yellow', 
                        'ERROR': 'red'
                    }.get(severity, 'white')
                    click.secho(f"  [{severity}] {finding['message']}", fg=color)
        
        # Output full JSON result
        click.echo("\n" + json.dumps(result, ensure_ascii=False, indent=2))
        
    except FileNotFoundError as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Execution failed: {e}", fg="red", bold=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
