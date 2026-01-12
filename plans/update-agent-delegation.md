# Plan for Updating agent-delegation.md

## Objective
Update the agent-delegation.md file to accurately reflect the current implementation of the orchestrator system.

## Current Status Analysis
The current agent-delegation.md file contains design documentation that doesn't fully align with the actual implementation:

1. The documented orchestrator module structure doesn't match the actual implementation
2. Missing documentation for CLI commands and usage patterns
3. No information about configuration loading and validation processes
4. Missing examples of workflow execution and agent delegation
5. No troubleshooting or error handling guidance

## Implementation Plan

### 1. Correct Orchestrator Module Structure Documentation
- Update Section 14 "Python オーケストレーション実装方針" to match actual implementation
- Document the actual module structure:
  ```
  orchestrator/
  ├── config/                # Configuration loading & validation
  │   ├── loader.py         # YAML workflow loader
  │   ├── validator.py      # JSON Schema validator
  │   └── models.py         # Pydantic data models
  ├── display/              # Output formatting
  │   └── formatter.py     # Workflow formatter
  ├── utils/                # Utilities & constants
  │   └── constants.py      # Enums & constants
  └── cli.py                # CLI application
  ```

### 2. Document CLI Commands and Usage Patterns
- Add a new section documenting all CLI commands with examples:
  - `validate` - Workflow validation
  - `show` - Display workflow structure
  - `list-templates` - List available templates
  - `info` - Show template details
  - `--version` - Show version

### 3. Add Configuration Loading and Validation Processes
- Document how workflow configurations are loaded from YAML files
- Explain JSON Schema validation process
- Describe Pydantic model validation
- Detail template resolution mechanism

### 4. Include Examples of Workflow Execution and Agent Delegation
- Add practical examples of using the system
- Show how to create custom workflows
- Document agent delegation patterns
- Provide template usage examples

### 5. Add Troubleshooting and Common Error Handling Guidance
- Document common validation errors and solutions
- Provide troubleshooting guidance for CLI usage
- Explain error handling mechanisms
- Include debugging tips

## Expected Outcome
A comprehensive, accurate documentation that serves as both a design reference and a practical guide for developers using the system.