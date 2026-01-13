# Examples Directory

This directory contains sample projects demonstrating how to use the OpenHands Agent Delegation system.

## Available Examples

- `simple-web-app/`: A simple web application development workflow example

## How to Use

Each example directory contains:
- A workflow configuration file
- Sample input files
- Expected output examples
- A README explaining how to run the example

To run an example:

```bash
cd examples/<example-name>
python -m orchestrator.cli run --config workflow.yaml
```