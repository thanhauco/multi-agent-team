"""Core data models and enums."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class AgentRole(Enum):
    """Agent role types."""

    PRODUCT_ANALYST = "product_analyst"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    DEBUGGER = "debugger"
    CODE_REVIEWER = "code_reviewer"
    DATA_SCIENTIST = "data_scientist"
    AI_ENGINEER = "ai_engineer"
    ML_ENGINEER = "ml_engineer"


class WorkflowPhase(Enum):
    """Workflow phase types."""

    ANALYSIS = "analysis"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DEBUGGING = "debugging"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    # ML-specific phases
    DATA_ANALYSIS = "data_analysis"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_DEVELOPMENT = "model_development"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"


class ValidationStatus(Enum):
    """Validation status types."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class Priority(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ArtifactType(Enum):
    """Artifact types produced by agents."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    DIAGRAM = "diagram"
    TEST = "test"
    CONFIG = "config"
    DATA = "data"
    MODEL = "model"
    REPORT = "report"


@dataclass
class Task:
    """Represents a task for an agent to execute."""

    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    context_ids: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Artifact:
    """Represents an artifact produced by an agent."""

    type: ArtifactType
    path: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    """Represents output from an agent."""

    agent_role: AgentRole
    task_id: str
    content: str
    artifacts: List[Artifact] = field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationError:
    """Represents a validation error."""

    code: str
    message: str
    severity: str = "error"
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Represents the result of a validation."""

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    phases: List[WorkflowPhase] = field(default_factory=list)
    agent_roles: List[AgentRole] = field(default_factory=list)
    validation_rules: Dict[WorkflowPhase, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
