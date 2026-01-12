# Agent-Delegate Orchestration System

Multi-agent orchestration system using OpenHands SDK for virtual development organizations.

## Overview

This system provides a configuration-driven framework for orchestrating multiple AI agents to work together on software development projects. Agents are organized into workflows with defined stages, responsibilities, and quality gates.

## Installation

### Using Python Virtual Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Commands

The CLI can be run using Python module syntax:

```bash
python -m orchestrator.cli [COMMAND] [OPTIONS]
```

Or use the provided wrapper script:

```bash
./agent-delegate [COMMAND] [OPTIONS]
```

#### Available Commands

**1. Validate a workflow configuration**
```bash
python -m orchestrator.cli validate <workflow-file>
python -m orchestrator.cli validate templates/web-fullstack.yaml
python -m orchestrator.cli validate my-workflow.yaml --verbose
```

**2. Display workflow structure**
```bash
python -m orchestrator.cli show <workflow-file>
python -m orchestrator.cli show templates/web-fullstack.yaml
python -m orchestrator.cli show templates/web-fullstack.yaml --format=json
```

**3. List available templates**
```bash
python -m orchestrator.cli list-templates
```

**4. Show template details**
```bash
python -m orchestrator.cli info <template-name>
python -m orchestrator.cli info web-fullstack
```

**5. Show version**
```bash
python -m orchestrator.cli --version
```

### Example Output

```
$ python -m orchestrator.cli show templates/web-fullstack.yaml

Workflow Configuration: Web Fullstack Project
============================================================

Project Details:
  Name: Web Fullstack Project
  Type: web
  Description: Full-stack web application with API backend and frontend

Agent Templates:
  ✓ core
  ✓ quality
  ✓ web-development

Workflow Stages (7):
  1. intake [sequential]
     → client-liaison
  2. requirements-audit [sequential]
     → requirements-auditor
  ...
```

## Project Structure

```
agent-delegate/
├── orchestrator/               # Main package
│   ├── config/                # Configuration loading & validation
│   │   ├── loader.py         # YAML workflow loader
│   │   ├── validator.py      # JSON Schema validator
│   │   └── models.py         # Pydantic data models
│   ├── display/              # Output formatting
│   │   └── formatter.py      # Workflow formatter
│   ├── utils/                # Utilities & constants
│   │   └── constants.py      # Enums & constants
│   └── cli.py                # CLI application
├── schemas/                   # JSON Schema definitions
│   ├── workflow-schema.yaml  # Workflow configuration schema
│   └── agent-interface.yaml  # Agent interface schema
├── templates/                 # Built-in workflow templates
│   └── web-fullstack.yaml    # Web fullstack template
├── policies/                  # System policies
│   ├── language-policy.yaml  # Language usage rules
│   └── file-policy.yaml      # File operation rules
└── tests/                     # Unit tests
```

## Configuration Files

### Workflow Configuration

Workflows are defined in YAML files following the schema in `schemas/workflow-schema.yaml`:

```yaml
version: "1.0"
project:
  name: "My Project"
  type: web
  description: "Project description"

agents:
  include_templates:
    - core
    - web-development

workflow:
  stages:
    - name: "planning"
      agents: ["planner"]
      execution_mode: sequential
      gate:
        required_status: OK
```

### Available Templates

- **web-fullstack**: Full-stack web application (7 stages, 14 agents)
  - Includes: customer liaison, requirements audit, API design, parallel BE/FE implementation, review/QA, integration

More templates (mobile, infrastructure, data-pipeline) will be added in future iterations.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=orchestrator --cov-report=html
```

### Code Quality

```bash
# Format code
black orchestrator/ tests/

# Lint
ruff check orchestrator/ tests/

# Type checking
mypy orchestrator/
```

## Architecture

This implementation (Iteration 1) provides:
- ✓ Configuration loading from YAML files
- ✓ JSON Schema validation
- ✓ Pydantic model validation
- ✓ CLI interface for validation and display
- ✓ Template system

Future iterations will add:
- Orchestration engine (workflow execution)
- OpenHands SDK integration (agent spawning)
- State management
- Context management
- Error handling implementation
- Logging infrastructure

## Design Principles

1. **Configuration-Driven**: All workflows defined in YAML
2. **Type-Safe**: Pydantic models for validation
3. **Incremental**: Minimal viable features first
4. **Extensible**: Clear extension points for future features

## References

- Design Document: `agent-delegation.md`
- Project Guide: `CLAUDE.md`
- Schemas: `schemas/`
- Implementation Plan: `.claude/plans/linked-toasting-quiche.md`

## Version

Current version: 0.1.0 (Iteration 1)
