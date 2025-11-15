"""Tests for workflow models."""

import pytest
from multi_agent.workflow.models import (
    WorkflowState,
    WorkflowStatus,
    PhaseTransition,
    PhaseValidationResult,
    ValidationRule,
)
from multi_agent.core.models import WorkflowPhase, AgentRole, ValidationError


def test_workflow_state_creation():
    """Test WorkflowState creation."""
    state = WorkflowState()
    assert state.workflow_id is not None
    assert state.current_phase == WorkflowPhase.ANALYSIS
    assert state.status == WorkflowStatus.PENDING
    assert len(state.transitions) == 0


def test_add_transition():
    """Test adding phase transitions."""
    state = WorkflowState()
    transition = PhaseTransition(
        from_phase=WorkflowPhase.ANALYSIS,
        to_phase=WorkflowPhase.ARCHITECTURE,
        agent_role=AgentRole.ARCHITECT,
    )
    
    state.add_transition(transition)
    assert len(state.transitions) == 1
    assert state.transitions[0].to_phase == WorkflowPhase.ARCHITECTURE


def test_mark_phase_complete():
    """Test marking phases as complete."""
    state = WorkflowState()
    state.mark_phase_complete(WorkflowPhase.ANALYSIS)
    
    assert WorkflowPhase.ANALYSIS in state.completed_phases
    assert len(state.completed_phases) == 1


def test_mark_phase_failed():
    """Test marking phases as failed."""
    state = WorkflowState()
    state.mark_phase_failed(WorkflowPhase.IMPLEMENTATION)
    
    assert WorkflowPhase.IMPLEMENTATION in state.failed_phases
    assert len(state.failed_phases) == 1


def test_workflow_state_to_dict():
    """Test serializing workflow state."""
    state = WorkflowState(
        current_phase=WorkflowPhase.ARCHITECTURE,
        status=WorkflowStatus.RUNNING,
    )
    state.mark_phase_complete(WorkflowPhase.ANALYSIS)
    
    data = state.to_dict()
    assert data["current_phase"] == "architecture"
    assert data["status"] == "running"
    assert "analysis" in data["completed_phases"]


def test_phase_validation_result():
    """Test PhaseValidationResult."""
    result = PhaseValidationResult(
        phase=WorkflowPhase.IMPLEMENTATION,
        is_valid=True,
    )
    
    assert result.is_valid
    assert len(result.errors) == 0
    
    # Add error
    error = ValidationError(code="E001", message="Test error")
    result.add_error(error)
    
    assert not result.is_valid
    assert len(result.errors) == 1


def test_phase_validation_warnings():
    """Test adding warnings to validation result."""
    result = PhaseValidationResult(
        phase=WorkflowPhase.REVIEW,
        is_valid=True,
    )
    
    result.add_warning("Consider adding more tests")
    result.add_suggestion("Use async/await pattern")
    
    assert result.is_valid  # Warnings don't invalidate
    assert len(result.warnings) == 1
    assert len(result.suggestions) == 1


def test_validation_rule():
    """Test ValidationRule creation."""
    rule = ValidationRule(
        rule_id="rule-001",
        name="Architecture Compliance",
        description="Ensure code follows architecture patterns",
        phase=WorkflowPhase.IMPLEMENTATION,
        validator_function="validate_architecture",
        severity="error",
    )
    
    assert rule.rule_id == "rule-001"
    assert rule.phase == WorkflowPhase.IMPLEMENTATION
    assert rule.enabled


def test_phase_transition():
    """Test PhaseTransition creation."""
    transition = PhaseTransition(
        from_phase=WorkflowPhase.DEBUGGING,
        to_phase=WorkflowPhase.REVIEW,
        agent_role=AgentRole.CODE_REVIEWER,
        success=True,
    )
    
    assert transition.from_phase == WorkflowPhase.DEBUGGING
    assert transition.to_phase == WorkflowPhase.REVIEW
    assert transition.success
