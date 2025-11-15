"""Workflow manager for coordinating agent execution phases."""

from typing import Dict, List, Optional
from pathlib import Path

from multi_agent.workflow.models import (
    WorkflowState,
    WorkflowStatus,
    PhaseTransition,
    PhaseValidationResult,
    ValidationRule,
)
from multi_agent.core.models import (
    AgentOutput,
    AgentRole,
    ValidationError,
    WorkflowConfig,
    WorkflowPhase,
)


class WorkflowManager:
    """Manages workflow state and phase transitions."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize workflow manager.
        
        Args:
            storage_path: Path for workflow state persistence
        """
        self.storage_path = storage_path or Path(".multi_agent/workflows")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.workflows: Dict[str, WorkflowState] = {}
        self.validation_rules: Dict[WorkflowPhase, List[ValidationRule]] = {}

    def initialize_workflow(self, config: WorkflowConfig) -> str:
        """Initialize a new workflow.
        
        Args:
            config: Workflow configuration
            
        Returns:
            Workflow ID
        """
        state = WorkflowState(
            workflow_id=config.id,
            current_phase=config.phases[0] if config.phases else WorkflowPhase.ANALYSIS,
            status=WorkflowStatus.PENDING,
            metadata=config.metadata,
        )
        
        self.workflows[state.workflow_id] = state
        return state.workflow_id

    def transition_phase(
        self,
        workflow_id: str,
        next_phase: WorkflowPhase,
        agent_role: Optional[AgentRole] = None,
    ) -> bool:
        """Transition workflow to next phase.
        
        Args:
            workflow_id: ID of the workflow
            next_phase: Phase to transition to
            agent_role: Agent role performing the transition
            
        Returns:
            True if transition successful, False otherwise
        """
        if workflow_id not in self.workflows:
            return False
        
        state = self.workflows[workflow_id]
        
        # Create transition record
        transition = PhaseTransition(
            from_phase=state.current_phase,
            to_phase=next_phase,
            agent_role=agent_role,
            success=True,
        )
        
        # Update state
        state.current_phase = next_phase
        state.status = WorkflowStatus.RUNNING
        state.add_transition(transition)
        
        return True

    def validate_phase_completion(
        self,
        phase: WorkflowPhase,
        outputs: List[AgentOutput],
    ) -> PhaseValidationResult:
        """Validate that a phase has been completed successfully.
        
        Args:
            phase: Phase to validate
            outputs: Agent outputs from the phase
            
        Returns:
            Validation result
        """
        result = PhaseValidationResult(phase=phase, is_valid=True)
        
        # Check if we have any outputs
        if not outputs:
            error = ValidationError(
                code="NO_OUTPUT",
                message=f"No outputs generated for phase {phase.value}",
                severity="error",
            )
            result.add_error(error)
            return result
        
        # Apply validation rules for this phase
        if phase in self.validation_rules:
            for rule in self.validation_rules[phase]:
                if not rule.enabled:
                    continue
                
                # Here we would call the actual validation function
                # For now, we'll just check basic criteria
                pass
        
        return result

    def rollback_to_phase(
        self,
        workflow_id: str,
        target_phase: WorkflowPhase,
    ) -> None:
        """Rollback workflow to a previous phase.
        
        Args:
            workflow_id: ID of the workflow
            target_phase: Phase to rollback to
        """
        if workflow_id not in self.workflows:
            return
        
        state = self.workflows[workflow_id]
        
        # Create rollback transition
        transition = PhaseTransition(
            from_phase=state.current_phase,
            to_phase=target_phase,
            success=False,
            metadata={"rollback": True},
        )
        
        # Update state
        state.current_phase = target_phase
        state.status = WorkflowStatus.ROLLED_BACK
        state.mark_phase_failed(state.current_phase)
        state.add_transition(transition)

    def get_current_phase(self, workflow_id: str) -> Optional[WorkflowPhase]:
        """Get current phase of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Current phase or None if workflow not found
        """
        if workflow_id not in self.workflows:
            return None
        
        return self.workflows[workflow_id].current_phase

    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get complete workflow state.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow state or None if not found
        """
        return self.workflows.get(workflow_id)

    def mark_workflow_complete(self, workflow_id: str) -> None:
        """Mark a workflow as completed.
        
        Args:
            workflow_id: ID of the workflow
        """
        if workflow_id in self.workflows:
            state = self.workflows[workflow_id]
            state.status = WorkflowStatus.COMPLETED
            state.mark_phase_complete(state.current_phase)

    def mark_workflow_failed(self, workflow_id: str, reason: str = "") -> None:
        """Mark a workflow as failed.
        
        Args:
            workflow_id: ID of the workflow
            reason: Reason for failure
        """
        if workflow_id in self.workflows:
            state = self.workflows[workflow_id]
            state.status = WorkflowStatus.FAILED
            state.mark_phase_failed(state.current_phase)
            if reason:
                state.metadata["failure_reason"] = reason

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule for a phase.
        
        Args:
            rule: Validation rule to add
        """
        if rule.phase not in self.validation_rules:
            self.validation_rules[rule.phase] = []
        
        self.validation_rules[rule.phase].append(rule)

    def get_workflow_history(self, workflow_id: str) -> List[PhaseTransition]:
        """Get transition history for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            List of phase transitions
        """
        if workflow_id not in self.workflows:
            return []
        
        return self.workflows[workflow_id].transitions
