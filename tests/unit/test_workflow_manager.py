"""Tests for WorkflowManager."""

import pytest
from multi_agent.workflow.manager import WorkflowManager
from multi_agent.workflow.models import ValidationRule
from multi_agent.core.models import (
    AgentOutput,
    AgentRole,
    WorkflowConfig,
    WorkflowPhase,
)


def test_initialize_workflow():
    """Test workflow initialization."""
    manager = WorkflowManager()
    config = WorkflowConfig(
        name="Test Workflow",
        phases=[WorkflowPhase.ANALYSIS, WorkflowPhase.ARCHITECTURE],
    )
    
    workflow_id = manager.initialize_workflow(config)
    assert workflow_id is not None
    assert workflow_id in manager.workflows
    
    state = manager.get_workflow_state(workflow_id)
    assert state is not None
    assert state.current_phase == WorkflowPhase.ANALYSIS


def test_transition_phase():
    """Test phase transitions."""
    manager = WorkflowManager()
    config = WorkflowConfig(phases=[WorkflowPhase.ANALYSIS])
    workflow_id = manager.initialize_workflow(config)
    
    # Transition to next phase
    success = manager.transition_phase(
        workflow_id,
        WorkflowPhase.ARCHITECTURE,
        AgentRole.ARCHITECT,
    )
    
    assert success
    assert manager.get_current_phase(workflow_id) == WorkflowPhase.ARCHITECTURE
    
    # Check transition history
    history = manager.get_workflow_history(workflow_id)
    assert len(history) == 1
    assert history[0].to_phase == WorkflowPhase.ARCHITECTURE


def test_validate_phase_completion():
    """Test phase validation."""
    manager = WorkflowManager()
    
    # Valid case - with outputs
    outputs = [
        AgentOutput(
            agent_role=AgentRole.DEVELOPER,
            task_id="task-1",
            content="Code",
        )
    ]
    result = manager.validate_phase_completion(WorkflowPhase.IMPLEMENTATION, outputs)
    assert result.is_valid
    
    # Invalid case - no outputs
    result = manager.validate_phase_completion(WorkflowPhase.IMPLEMENTATION, [])
    assert not result.is_valid
    assert len(result.errors) > 0


def test_rollback_to_phase():
    """Test rolling back to previous phase."""
    manager = WorkflowManager()
    config = WorkflowConfig(phases=[WorkflowPhase.ANALYSIS])
    workflow_id = manager.initialize_workflow(config)
    
    # Transition forward
    manager.transition_phase(workflow_id, WorkflowPhase.IMPLEMENTATION)
    
    # Rollback
    manager.rollback_to_phase(workflow_id, WorkflowPhase.ARCHITECTURE)
    
    assert manager.get_current_phase(workflow_id) == WorkflowPhase.ARCHITECTURE
    state = manager.get_workflow_state(workflow_id)
    assert WorkflowPhase.IMPLEMENTATION in state.failed_phases


def test_mark_workflow_complete():
    """Test marking workflow as complete."""
    manager = WorkflowManager()
    config = WorkflowConfig()
    workflow_id = manager.initialize_workflow(config)
    
    manager.mark_workflow_complete(workflow_id)
    
    state = manager.get_workflow_state(workflow_id)
    assert state.status.value == "completed"


def test_mark_workflow_failed():
    """Test marking workflow as failed."""
    manager = WorkflowManager()
    config = WorkflowConfig()
    workflow_id = manager.initialize_workflow(config)
    
    manager.mark_workflow_failed(workflow_id, "Test failure")
    
    state = manager.get_workflow_state(workflow_id)
    assert state.status.value == "failed"
    assert state.metadata["failure_reason"] == "Test failure"


def test_add_validation_rule():
    """Test adding validation rules."""
    manager = WorkflowManager()
    
    rule = ValidationRule(
        rule_id="rule-001",
        name="Test Rule",
        description="Test validation rule",
        phase=WorkflowPhase.IMPLEMENTATION,
        validator_function="test_validator",
    )
    
    manager.add_validation_rule(rule)
    
    assert WorkflowPhase.IMPLEMENTATION in manager.validation_rules
    assert len(manager.validation_rules[WorkflowPhase.IMPLEMENTATION]) == 1


def test_get_workflow_history():
    """Test getting workflow transition history."""
    manager = WorkflowManager()
    config = WorkflowConfig()
    workflow_id = manager.initialize_workflow(config)
    
    # Make several transitions
    manager.transition_phase(workflow_id, WorkflowPhase.ARCHITECTURE)
    manager.transition_phase(workflow_id, WorkflowPhase.IMPLEMENTATION)
    
    history = manager.get_workflow_history(workflow_id)
    assert len(history) == 2
    assert history[0].to_phase == WorkflowPhase.ARCHITECTURE
    assert history[1].to_phase == WorkflowPhase.IMPLEMENTATION


def test_nonexistent_workflow():
    """Test operations on nonexistent workflow."""
    manager = WorkflowManager()
    
    # Should handle gracefully
    assert manager.get_current_phase("nonexistent") is None
    assert manager.get_workflow_state("nonexistent") is None
    assert manager.get_workflow_history("nonexistent") == []
    
    success = manager.transition_phase("nonexistent", WorkflowPhase.REVIEW)
    assert not success
