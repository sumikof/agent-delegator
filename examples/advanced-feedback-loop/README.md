# Advanced Feedback Loop Example

This example demonstrates the advanced feedback loop workflow with quality reviews, iterative improvements, and error handling.

## Overview

This example shows how to:
1. Set up a feedback loop workflow with quality reviews
2. Configure agents for iterative development and review cycles
3. Handle error conditions and implement fallback mechanisms
4. Use the extended task status system (IN_REVIEW, NEEDS_FIXES, APPROVED, REJECTED)

## Files

- `workflow.yaml`: Main workflow configuration with feedback loop
- `requirements.txt`: Sample requirements file
- `expected_output/`: Directory containing expected output examples
- `tutorial/`: Step-by-step guide for the feedback loop process

## Running the Example

```bash
cd /workspace/examples/advanced-feedback-loop
python -m orchestrator.cli run --config workflow.yaml
```

## Workflow Description

This workflow includes:
1. Client liaison to gather requirements
2. Planner to create development plan
3. API designer for API specification
4. Backend developer for server-side code
5. Frontend developer for client-side code
6. Quality auditor for code quality reviews
7. Requirements auditor for specification compliance
8. Reviewers for detailed code reviews
9. Tester for validation
10. Integrator for final integration

The workflow demonstrates:
- Automatic feedback generation from quality audits
- Task status transitions (NEW → IN_PROGRESS → IN_REVIEW → NEEDS_FIXES → IN_PROGRESS → IN_REVIEW → APPROVED → DONE)
- Error handling and fallback mechanisms
- Parallel processing of independent tasks
- Resource monitoring and load balancing

## Expected Output

The workflow will generate:
- API specification files
- Backend and frontend code
- Quality audit reports with detailed findings
- Review comments and improvement suggestions
- Test reports with coverage analysis
- Integration results with performance metrics
- Complete audit trail of task status transitions