# Simple Web Application Example

This example demonstrates a simple web application development workflow using the OpenHands Agent Delegation system.

## Overview

This example shows how to:
1. Set up a basic web application workflow
2. Configure agents for different development phases
3. Run the orchestration process

## Files

- `workflow.yaml`: Main workflow configuration
- `requirements.txt`: Sample requirements file
- `expected_output/`: Directory containing expected output examples

## Running the Example

```bash
cd /workspace/examples/simple-web-app
python -m orchestrator.cli run --config workflow.yaml
```

## Workflow Description

This workflow includes:
1. Client liaison to gather requirements
2. Planner to create development plan
3. API designer for API specification
4. Backend developer for server-side code
5. Frontend developer for client-side code
6. Reviewers for code quality checks
7. Tester for validation
8. Integrator for final integration

## Expected Output

The workflow will generate:
- API specification files
- Backend and frontend code
- Test reports
- Integration results