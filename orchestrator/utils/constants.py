"""
Constants and enumerations for the orchestrator system.
"""

from enum import Enum
from pathlib import Path

# ===== Path Definitions =====

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configuration directories
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
POLICIES_DIR = PROJECT_ROOT / "policies"

# Schema file paths
WORKFLOW_SCHEMA_PATH = SCHEMAS_DIR / "workflow-schema.yaml"
AGENT_INTERFACE_SCHEMA_PATH = SCHEMAS_DIR / "agent-interface.yaml"

# Policy file paths
LANGUAGE_POLICY_PATH = POLICIES_DIR / "language-policy.yaml"
FILE_POLICY_PATH = POLICIES_DIR / "file-policy.yaml"


# ===== Enumerations =====


class ProjectType(str, Enum):
    """Project type enumeration."""

    WEB = "web"
    MOBILE = "mobile"
    INFRASTRUCTURE = "infrastructure"
    DATA_PIPELINE = "data-pipeline"
    HYBRID = "hybrid"
    CUSTOM = "custom"


class ExecutionMode(str, Enum):
    """Stage execution mode."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class AgentRole(str, Enum):
    """Agent role categories."""

    LIAISON = "liaison"
    PLANNING = "planning"
    AUDIT = "audit"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    TESTING = "testing"
    INTEGRATION = "integration"


class Status(str, Enum):
    """Agent execution status."""

    OK = "OK"
    NG = "NG"


class RequiredStatus(str, Enum):
    """Gate required status."""

    OK = "OK"
    OK_WITH_WARNINGS = "OK_WITH_WARNINGS"


class Severity(str, Enum):
    """Finding severity levels."""

    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class ArtifactType(str, Enum):
    """Artifact type categories."""

    CODE = "code"
    SPEC = "spec"
    DOC = "doc"
    CONFIG = "config"
    REPORT = "report"


class BackoffType(str, Enum):
    """Retry backoff strategy."""

    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class OnFailureAction(str, Enum):
    """Action to take on stage failure."""

    ABORT = "abort"
    RETRY = "retry"
    FALLBACK = "fallback"
    CONTINUE = "continue"


class FallbackCondition(str, Enum):
    """Fallback trigger conditions."""

    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CIRCUIT_OPEN = "circuit_open"
    TIMEOUT = "timeout"
    CRITICAL_FAILURE = "critical_failure"


class FallbackAction(str, Enum):
    """Fallback actions."""

    DELEGATE_TO_HUMAN = "delegate_to_human"
    USE_CACHED_RESULT = "use_cached_result"
    ESCALATE_TO_ORCHESTRATOR = "escalate_to_orchestrator"
    SKIP_STAGE = "skip_stage"
    ABORT_WORKFLOW = "abort_workflow"


class AgentTemplateCategory(str, Enum):
    """Built-in agent template categories."""

    CORE = "core"
    QUALITY = "quality"
    WEB_DEVELOPMENT = "web-development"
    MOBILE_DEVELOPMENT = "mobile-development"
    INFRASTRUCTURE = "infrastructure"
    DATA_ENGINEERING = "data-engineering"
    DEVOPS = "devops"


# ===== Default Values =====

# Timeout defaults (milliseconds)
DEFAULT_AGENT_TIMEOUT_MS = 300000  # 5 minutes
DEFAULT_STAGE_TIMEOUT_MS = 600000  # 10 minutes
DEFAULT_WORKFLOW_TIMEOUT_MS = 3600000  # 1 hour

# Retry defaults
DEFAULT_MAX_RETRY_ATTEMPTS = 3
DEFAULT_INITIAL_DELAY_MS = 1000
DEFAULT_MAX_DELAY_MS = 60000
DEFAULT_BACKOFF_MULTIPLIER = 2.0
DEFAULT_JITTER_FACTOR = 0.1

# Circuit breaker defaults
DEFAULT_FAILURE_THRESHOLD = 5
DEFAULT_SUCCESS_THRESHOLD = 3
DEFAULT_HALF_OPEN_MAX_CALLS = 3
DEFAULT_RECOVERY_TIMEOUT_MS = 60000

# Language defaults
DEFAULT_CUSTOMER_FACING_LANG = "ja"
DEFAULT_DEVELOPMENT_LANG = "en"

# File naming
MAX_FILENAME_LENGTH = 100

# Validation
MAX_ERRORS_DEFAULT = 0  # No errors allowed by default
