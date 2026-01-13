"""Unit tests for CLI commands."""

import pytest
from click.testing import CliRunner
from orchestrator.cli import validate, show, list_templates, info


def test_validate_command():
    """Test the validate CLI command."""
    runner = CliRunner()
    result = runner.invoke(validate, ["--help"])
    assert result.exit_code == 0
    assert "Validate a workflow configuration" in result.output


def test_show_command():
    """Test the show CLI command."""
    runner = CliRunner()
    result = runner.invoke(show, ["--help"])
    assert result.exit_code == 0
    assert "Display workflow configuration details" in result.output


def test_list_templates_command():
    """Test the list-templates CLI command."""
    runner = CliRunner()
    result = runner.invoke(list_templates, ["--help"])
    assert result.exit_code == 0
    assert "List all available workflow templates" in result.output


def test_info_command():
    """Test the info CLI command."""
    runner = CliRunner()
    result = runner.invoke(info, ["--help"])
    assert result.exit_code == 0
    assert "Show detailed information about a template" in result.output
