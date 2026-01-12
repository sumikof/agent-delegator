"""
Pydantic models for configuration validation and type safety.

These models mirror the YAML schema structure defined in schemas/workflow-schema.yaml
and schemas/agent-interface.yaml.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re

from orchestrator.utils.constants import (
    ProjectType,
    ExecutionMode,
    AgentRole,
    Status,
    RequiredStatus,
    Severity,
    ArtifactType,
    BackoffType,
    OnFailureAction,
    FallbackCondition,
    FallbackAction,
    AgentTemplateCategory,
    DEFAULT_AGENT_TIMEOUT_MS,
    DEFAULT_STAGE_TIMEOUT_MS,
    DEFAULT_WORKFLOW_TIMEOUT_MS,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_INITIAL_DELAY_MS,
    DEFAULT_MAX_DELAY_MS,
    DEFAULT_BACKOFF_MULTIPLIER,
    DEFAULT_JITTER_FACTOR,
    DEFAULT_FAILURE_THRESHOLD,
    DEFAULT_SUCCESS_THRESHOLD,
    DEFAULT_HALF_OPEN_MAX_CALLS,
    DEFAULT_RECOVERY_TIMEOUT_MS,
    DEFAULT_CUSTOMER_FACING_LANG,
    DEFAULT_DEVELOPMENT_LANG,
    MAX_ERRORS_DEFAULT,
)


# ===== Language Policy =====

class LanguagePolicy(BaseModel):
    """Language policy for agent communication."""
    customer_facing: str = DEFAULT_CUSTOMER_FACING_LANG
    development: str = DEFAULT_DEVELOPMENT_LANG
    documentation: Optional[str] = DEFAULT_DEVELOPMENT_LANG
    code_comments: Optional[str] = DEFAULT_DEVELOPMENT_LANG
    commit_messages: Optional[str] = DEFAULT_DEVELOPMENT_LANG


class AgentLanguageOverride(BaseModel):
    """Agent-specific language policy override."""
    all: Optional[str] = None
    customer_facing: Optional[str] = None
    internal: Optional[str] = None


# ===== Project Configuration =====

class ProjectConfig(BaseModel):
    """Project metadata configuration."""
    name: str
    type: ProjectType
    description: Optional[str] = None
    language_policy: Optional[LanguagePolicy] = Field(default_factory=LanguagePolicy)


# ===== Error Handling Configuration =====

class RetryPolicy(BaseModel):
    """Retry policy configuration."""
    max_attempts: int = Field(DEFAULT_MAX_RETRY_ATTEMPTS, ge=1, le=10)
    backoff_type: BackoffType = BackoffType.EXPONENTIAL
    initial_delay_ms: int = Field(DEFAULT_INITIAL_DELAY_MS, ge=100)
    max_delay_ms: int = DEFAULT_MAX_DELAY_MS
    multiplier: float = DEFAULT_BACKOFF_MULTIPLIER
    jitter: bool = True
    jitter_factor: float = Field(DEFAULT_JITTER_FACTOR, ge=0.0, le=1.0)


class CircuitBreaker(BaseModel):
    """Circuit breaker configuration."""
    enabled: bool = True
    failure_threshold: int = DEFAULT_FAILURE_THRESHOLD
    success_threshold: int = DEFAULT_SUCCESS_THRESHOLD
    half_open_max_calls: int = DEFAULT_HALF_OPEN_MAX_CALLS
    recovery_timeout_ms: int = DEFAULT_RECOVERY_TIMEOUT_MS


class FallbackStrategy(BaseModel):
    """Fallback strategy configuration."""
    condition: FallbackCondition
    action: FallbackAction


class ErrorHandling(BaseModel):
    """Error handling configuration."""
    retry_policy: Optional[RetryPolicy] = Field(default_factory=RetryPolicy)
    circuit_breaker: Optional[CircuitBreaker] = Field(default_factory=CircuitBreaker)
    fallback_strategies: list[FallbackStrategy] = Field(default_factory=list)


# ===== Workflow Stage Configuration =====

class Gate(BaseModel):
    """Quality gate configuration."""
    required_status: RequiredStatus = RequiredStatus.OK
    allow_warnings: bool = True
    max_errors: int = MAX_ERRORS_DEFAULT


class StageConfig(BaseModel):
    """Workflow stage configuration."""
    name: str
    description: Optional[str] = None
    agents: list[str]
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    gate: Optional[Gate] = None
    on_failure: OnFailureAction = OnFailureAction.ABORT
    timeout_ms: Optional[int] = Field(None, gt=0)

    @field_validator('agents')
    @classmethod
    def validate_agents_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError('agents list cannot be empty')
        return v


# ===== Agent Configuration =====

class AgentResponsibilities(BaseModel):
    """Agent responsibility definitions."""
    must_do: list[str]
    must_not_do: list[str]
    may_do: list[str] = Field(default_factory=list)


class AgentFilePatterns(BaseModel):
    """File access patterns for agent boundaries."""
    allowed: list[str] = Field(default_factory=list)
    forbidden: list[str] = Field(default_factory=list)


class AgentActions(BaseModel):
    """Action permissions for agent boundaries."""
    allowed: list[str] = Field(default_factory=list)
    forbidden: list[str] = Field(default_factory=list)


class AgentBoundaries(BaseModel):
    """Agent operational boundaries."""
    file_patterns: Optional[AgentFilePatterns] = None
    actions: Optional[AgentActions] = None


class AgentEscalation(BaseModel):
    """Agent escalation paths."""
    on_ambiguity: Optional[str] = None
    on_blocker: Optional[str] = None
    on_security_concern: Optional[str] = None
    on_scope_creep: Optional[str] = None


class AgentConfig(BaseModel):
    """Complete agent configuration."""
    id: str
    name: str
    role: AgentRole
    description: str
    capabilities: list[str] = Field(default_factory=list)
    responsibilities: AgentResponsibilities
    boundaries: Optional[AgentBoundaries] = None
    language_policy: Optional[AgentLanguageOverride] = None
    escalation: Optional[AgentEscalation] = None
    timeout_ms: int = Field(DEFAULT_AGENT_TIMEOUT_MS, ge=10000, le=3600000)
    retry_policy: Optional[RetryPolicy] = None

    @field_validator('id')
    @classmethod
    def validate_id_kebab_case(cls, v: str) -> str:
        """Validate agent ID is in kebab-case format."""
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError(f'agent ID must be in kebab-case format: {v}')
        return v


# ===== Agents Section (for workflow config) =====

class CustomAgentDefinition(BaseModel):
    """Custom agent definition in workflow configuration."""
    id: str
    name: str
    role: AgentRole
    description: Optional[str] = None
    capabilities: list[str] = Field(default_factory=list)
    language_policy: Optional[AgentLanguageOverride] = None
    timeout_ms: Optional[int] = Field(None, ge=10000, le=3600000)
    retry_policy: Optional[RetryPolicy] = None

    @field_validator('id')
    @classmethod
    def validate_id_kebab_case(cls, v: str) -> str:
        """Validate agent ID is in kebab-case format."""
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError(f'agent ID must be in kebab-case format: {v}')
        return v


class AgentsSection(BaseModel):
    """Agent configuration section in workflow."""
    include_templates: list[str] = Field(default_factory=list)
    custom: list[CustomAgentDefinition] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)


# ===== Workflow Section =====

class WorkflowSection(BaseModel):
    """Workflow execution configuration."""
    stages: list[StageConfig]
    error_handling: Optional[ErrorHandling] = Field(default_factory=ErrorHandling)
    global_timeout_ms: int = Field(DEFAULT_WORKFLOW_TIMEOUT_MS, gt=0)

    @field_validator('stages')
    @classmethod
    def validate_stages_not_empty(cls, v: list[StageConfig]) -> list[StageConfig]:
        if not v:
            raise ValueError('workflow must have at least one stage')
        return v


# ===== Top-level Workflow Configuration =====

class WorkflowConfig(BaseModel):
    """Complete workflow configuration (top-level)."""
    version: str
    project: ProjectConfig
    agents: Optional[AgentsSection] = Field(default_factory=AgentsSection)
    workflow: WorkflowSection

    @field_validator('version')
    @classmethod
    def validate_version_format(cls, v: str) -> str:
        """Validate version follows major.minor format."""
        if not re.match(r'^[0-9]+\.[0-9]+$', v):
            raise ValueError(f'version must match format "major.minor": {v}')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version": "1.0",
                    "project": {
                        "name": "Example Project",
                        "type": "web",
                        "description": "An example web project"
                    },
                    "agents": {
                        "include_templates": ["core", "web-development"]
                    },
                    "workflow": {
                        "stages": [
                            {
                                "name": "planning",
                                "agents": ["planner"],
                                "execution_mode": "sequential"
                            }
                        ]
                    }
                }
            ]
        }
    }


# ===== Common Response Schema (for agent outputs) =====

class Finding(BaseModel):
    """Agent finding/issue."""
    severity: Severity
    message: str
    ref: Optional[str] = None
    suggestion: Optional[str] = None


class Artifact(BaseModel):
    """Agent artifact output."""
    path: str
    type: ArtifactType
    desc: Optional[str] = None
    checksum: Optional[str] = None


class AgentResponse(BaseModel):
    """Common response schema for all agents."""
    status: Status
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    trace_id: Optional[str] = None
    execution_time_ms: Optional[int] = None
