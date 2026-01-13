# Workflow Execution Diagram

```mermaid
graph LR
    A[Start] --> B[Intake]
    B --> C[Requirements Check]
    C --> D[Plan]
    D --> E[Contract]
    E --> F[Implementation]
    F --> G[Review & QA]
    G --> H[Integration]
    H --> I[Done]
    
    G -->|NG| J[Progress Re-planning]
    J --> F
    
    subgraph "Core Agents"
    B1[client-liaison] --> B
    C1[requirements-auditor] --> C
    D1[planner] --> D
    E1[api-designer] --> E
    H1[integrator] --> H
    end
    
    subgraph "Development Agents"
    F1[backend-dev] --> F
    F2[frontend-dev] --> F
    end
    
    subgraph "Quality Agents"
    G1[reviewer-be] --> G
    G2[reviewer-fe] --> G
    G3[tester] --> G
    G4[quality-auditor] --> G
    end
    
    subgraph "Progress Management"
    J1[progress] --> J
    end
```

## Workflow Execution Description

This diagram illustrates the workflow execution process:

1. **Intake**: Client liaison gathers requirements from the customer
2. **Requirements Check**: Requirements auditor validates and checks for ambiguities
3. **Plan**: Planner creates the development plan and task breakdown
4. **Contract**: API designer creates the API specification (Single Source of Truth)
5. **Implementation**: Backend and frontend developers work in parallel
6. **Review & QA**: Multiple quality agents review and test the implementation
7. **Integration**: Integrator combines all components and performs final validation
8. **Progress Re-planning**: If any stage fails (NG), the progress agent creates a re-planning proposal

The workflow supports both sequential and parallel execution where appropriate, with automatic error handling and fallback mechanisms.