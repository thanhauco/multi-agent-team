"""Tests for workflow persistence."""

import pytest
import tempfile
from pathlib import Path

from multi_agent.workflow.models import WorkflowState, WorkflowStatus, PhaseTransition
from multi_agent.workflow.persistence import WorkflowPersistence
from multi_agent.core.models import WorkflowPhase, AgentRole


def test_save_and_load_workflow():
    """Test saving and loading workflow state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = WorkflowPersistence(Path(tmpdir))
        
        # Create workflow state
        state = WorkflowState(
            workflow_id="test-workflow-123",
            current_phase=WorkflowPhase.ARCHITECTURE,
            status=WorkflowStatus.RUNNING,
        )
        state.mark_phase_complete(WorkflowPhase.ANALYSIS)
        
        # Save
        persistence.save(state)
        
        # Load
        loaded_state = persistence.load("test-workflow-123")
        
        assert loaded_state is not None
        assert loaded_state.workflow_id == "test-workflow-123"
        assert loaded_state.current_phase == WorkflowPhase.ARCHITECTURE
        assert loaded_state.status == WorkflowStatus.RUNNING
        assert WorkflowPhase.ANALYSIS in loaded_state.completed_phases


def test_save_workflow_with_transitions():
    """Test saving workflow with phase transitions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = WorkflowPersistence(Path(tmpdir))
        
        state = WorkflowState(workflow_id="workflow-456")
        
        # Add transitions
        transition1 = PhaseTransition(
            from_phase=WorkflowPhase.ANALYSIS,
            to_phase=WorkflowPhase.ARCHITECTURE,
            agent_role=AgentRole.ARCHITECT,
        )
        state.add_transition(transition1)
        
        transition2 = PhaseTransition(
            from_phase=WorkflowPhase.ARCHITECTURE,
            to_phase=WorkflowPhase.IMPLEMENTATION,
            agent_role=AgentRole.DEVELOPER,
        )
        state.add_transition(transition2)
        
        # Save and load
        persistence.save(state)
        loaded_state = persistence.load("workflow-456")
        
        assert loaded_state is not None
        assert len(loaded_state.transitions) == 2
        assert loaded_state.transitions[0].to_phase == WorkflowPhase.ARCHITECTURE
        assert loaded_state.transitions[1].to_phase == WorkflowPhase.IMPLEMENTATION


def test_load_nonexistent_workflow():
    """Test loading a workflow that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = WorkflowPersistence(Path(tmpdir))
        
        state = persistence.load("nonexistent-workflow")
        assert state is None


def test_list_workflows():
    """Test listing saved workflows."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = WorkflowPersistence(Path(tmpdir))
        
        # Save multiple workflows
        state1 = WorkflowState(workflow_id="workflow-1")
        state2 = WorkflowState(workflow_id="workflow-2")
        state3 = WorkflowState(workflow_id="workflow-3")
        
        persistence.save(state1)
        persistence.save(state2)
        persistence.save(state3)
        
        workflows = persistence.list_workflows()
        assert len(workflows) == 3
        assert "workflow-1" in workflows
        assert "workflow-2" in workflows
        assert "workflow-3" in workflows


def test_delete_workflow():
    """Test deleting a saved workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = WorkflowPersistence(Path(tmpdir))
        
        state = WorkflowState(workflow_id="to-delete")
        persistence.save(state)
        
        # Delete
        result = persistence.delete("to-delete")
        assert result is True
        
        # Verify deleted
        loaded = persistence.load("to-delete")
        assert loaded is None
        
        # Try to delete again
        result = persistence.delete("to-delete")
        assert result is False


def test_workflow_with_failed_phases():
    """Test saving workflow with failed phases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = WorkflowPersistence(Path(tmpdir))
        
        state = WorkflowState(workflow_id="failed-workflow")
        state.mark_phase_failed(WorkflowPhase.IMPLEMENTATION)
        state.mark_phase_complete(WorkflowPhase.ANALYSIS)
        
        persistence.save(state)
        loaded_state = persistence.load("failed-workflow")
        
        assert loaded_state is not None
        assert WorkflowPhase.IMPLEMENTATION in loaded_state.failed_phases
        assert WorkflowPhase.ANALYSIS in loaded_state.completed_phases


def test_workflow_manager_integration():
    """Test WorkflowManager with persistence."""
    from multi_agent.workflow.manager import WorkflowManager
    from multi_agent.core.models import WorkflowConfig
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = WorkflowManager(storage_path=Path(tmpdir))
        
        # Create and save workflow
        config = WorkflowConfig(name="Test Workflow")
        workflow_id = manager.initialize_workflow(config)
        manager.transition_phase(workflow_id, WorkflowPhase.ARCHITECTURE)
        manager.save_workflow(workflow_id)
        
        # Create new manager and load
        manager2 = WorkflowManager(storage_path=Path(tmpdir))
        success = manager2.load_workflow(workflow_id)
        
        assert success
        assert manager2.get_current_phase(workflow_id) == WorkflowPhase.ARCHITECTURE
