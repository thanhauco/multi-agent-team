"""Workflow state models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from multi_agent.core.models import AgentRole, ValidationError, WorkflowPhase


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class PhaseTransition:
    """Represents a transition between workflow phases."""

    from_phase: Optional[WorkflowPhase]
    to_phase: WorkflowPhase
    timestamp: datetime = field(default_factory=datetime.now)
    agent_role: Optional[AgentRole] = None
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """Represents the current state of a workflow."""

    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    current_phase: WorkflowPhase = WorkflowPhase.ANALYSIS
    status: WorkflowStatus = WorkflowStatus.PENDING
    transitions: List[PhaseTransition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_phases: List[WorkflowPhase] = field(default_factory=list)
    failed_phases: List[WorkflowPhase] = field(default_factory=list)

    def add_transition(self, transition: PhaseTransition) -> None:
        """Add a phase transition to history."""
        self.transitions.append(transition)
        self.updated_at = datetime.now()

    def mark_phase_complete(self, phase: WorkflowPhase) -> None:
        """Mark a phase as completed."""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
        self.updated_at = datetime.now()

    def mark_phase_failed(self, phase: WorkflowPhase) -> None:
        """Mark a phase as failed."""
        if phase not in self.failed_phases:
            self.failed_phases.append(phase)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "workflow_id": self.workflow_id,
            "current_phase": self.current_phase.value,
            "status": self.status.value,
            "transitions": [
                {
                    "from_phase": t.from_phase.value if t.from_phase else None,
                    "to_phase": t.to_phase.value,
                    "timestamp": t.timestamp.isoformat(),
                    "agent_role": t.agent_role.value if t.agent_role else None,
                    "success": t.success,
                    "metadata": t.metadata,
                }
                for t in self.transitions
            ],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_phases": [p.value for p in self.completed_phases],
            "failed_phases": [p.value for p in self.failed_phases],
        }


@dataclass
class ValidationRule:
    """Represents a validation rule for a workflow phase."""

    rule_id: str
    name: str
    description: str
    phase: WorkflowPhase
    validator_function: str  # Name of the validation function
    severity: str = "error"  # error, warning, info
    enabled: bool = True


@dataclass
class PhaseValidationResult:
    """Result of validating a workflow phase."""

    phase: WorkflowPhase
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.now)

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)

    def add_suggestion(self, suggestion: str) -> None:
        """Add a validation suggestion."""
        self.suggestions.append(suggestion)
