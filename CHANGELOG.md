# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Examples and Documentation**: Added comprehensive examples directory with a simple web app workflow example including:
  - `examples/simple-web-app/workflow.yaml`: Complete workflow configuration
  - `examples/simple-web-app/requirements.txt`: Sample requirements file
  - `examples/simple-web-app/expected_output/`: Expected output examples
  - Updated `agent-delegation.md` with module structure, CLI guide, templates, and agent definitions

- **Mermaid Diagrams**: Added visual documentation:
  - `mermaid/module_structure.md`: Module structure diagram
  - `mermaid/workflow_execution.md`: Workflow execution diagram

- **Schema Validation**: Added comprehensive schema validation:
  - `validate_schema.py`: Validation script for workflow configurations
  - Validated all templates and examples against the workflow schema

- **CI/CD Pipeline**: Added GitHub Actions workflow:
  - `.github/workflows/lint_and_test.yml`: Linting, testing, and validation workflow
  - Includes Black formatting, Flake8 linting, and schema validation

- **Policy Updates**: Updated file policies:
  - Added CI/CD file restrictions
  - Added examples directory permissions
  - Enhanced security constraints

### Changed

- **Code Formatting**: Applied Black code formatting to entire codebase
- **Static Analysis**: Fixed Flake8 issues throughout the codebase
- **Template Cleanup**: Removed duplicate YAML documents from templates
- **Import Optimization**: Cleaned up unused imports and dependencies

### Fixed

- **Schema Compliance**: Fixed workflow configuration to match schema requirements
- **CLI Issues**: Fixed ambiguous variable names in CLI error handling
- **Configuration Loading**: Fixed unused variables in config loader
- **Model Validation**: Fixed undefined name issues in Pydantic models

## [0.1.0] - 2024-01-01

### Added

- Initial project structure and core modules
- Basic orchestration framework
- Agent interface definitions
- Workflow schema definitions
- Core agent implementations
- Configuration loading and validation
- CLI interface
- Unit and integration tests

[Unreleased]: https://github.com/openhands/agent-delegate/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/openhands/agent-delegate/releases/tag/v0.1.0