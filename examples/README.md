# Examples Directory

This directory contains sample projects demonstrating how to use the OpenHands Agent Delegation system.

## Available Examples

- `simple-web-app/`: A simple web application development workflow example
- `advanced-feedback-loop/`: An advanced example demonstrating feedback loops, quality reviews, and iterative improvements

## How to Use

Each example directory contains:
- A workflow configuration file
- Sample input files
- Expected output examples
- A README explaining how to run the example
- Tutorial documentation (for advanced examples)

To run an example:

```bash
cd examples/<example-name>
python -m orchestrator.cli run --config workflow.yaml
```

## Example Comparison

| Example | Complexity | Features | Best For |
|---------|------------|----------|----------|
| `simple-web-app` | Basic | Linear workflow, basic agents | Getting started, simple projects |
| `advanced-feedback-loop` | Advanced | Feedback loops, quality reviews, parallel processing, error handling | Production use, complex projects, quality assurance |

## Tutorials

The `advanced-feedback-loop` example includes a comprehensive step-by-step guide covering:
- Feedback loop mechanics and status transitions
- Quality audit processes
- Error handling and fallback strategies
- Performance optimization techniques
- Troubleshooting common issues

See `examples/advanced-feedback-loop/tutorial/step-by-step-guide.md` for detailed instructions.