"""Tests for core data models."""

import pytest
from multi_agent.core.models import (
    AgentRole,
    WorkflowPhase,
    ValidationStatus,
    Priority,
    ArtifactType,
    Task,
    AgentOutput,
    Artifact,
    ValidationResult,
    ValidationError,
    WorkflowConfig,
)


def test_agent_role_enum():
    """Test AgentRole enum values."""
    assert AgentRole.PRODUCT_ANALYST.value == "product_analyst"
    assert AgentRole.ARCHITECT.value == "architect"
    assert AgentRole.DEVELOPER.value == "developer"
    assert AgentRole.DEBUGGER.value == "debugger"
    assert AgentRole.CODE_REVIEWER.value == "code_reviewer"
    assert AgentRole.DATA_SCIENTIST.value == "data_scientist"
    assert AgentRole.AI_ENGINEER.value == "ai_engineer"
    assert AgentRole.ML_ENGINEER.value == "ml_engineer"


def test_workflow_phase_enum():
    """Test WorkflowPhase enum values."""
    assert WorkflowPhase.ANALYSIS.value == "analysis"
    assert WorkflowPhase.ARCHITECTURE.value == "architecture"
    assert WorkflowPhase.IMPLEMENTATION.value == "implementation"
    assert WorkflowPhase.DEBUGGING.value == "debugging"
    assert WorkflowPhase.REVIEW.value == "review"


def test_task_creation():
    """Test Task dataclass creation."""
    task = Task(
        description="Test task",
        requirements=["req1", "req2"],
        priority=Priority.HIGH,
    )
    assert task.description == "Test task"
    assert len(task.requirements) == 2
    assert task.priority == Priority.HIGH
    assert task.id is not None


def test_agent_output_creation():
    """Test AgentOutput dataclass creation."""
    output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-123",
        content="Generated code",
    )
    assert output.agent_role == AgentRole.DEVELOPER
    assert output.task_id == "task-123"
    assert output.content == "Generated code"
    assert output.validation_status == ValidationStatus.PENDING


def test_validation_result():
    """Test ValidationResult dataclass."""
    error = ValidationError(
        code="E001",
        message="Test error",
        severity="error",
    )
    result = ValidationResult(
        is_valid=False,
        errors=[error],
        warnings=["Warning 1"],
    )
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].code == "E001"
    assert len(result.warnings) == 1


def test_workflow_config():
    """Test WorkflowConfig dataclass."""
    config = WorkflowConfig(
        name="Test Workflow",
        phases=[WorkflowPhase.ANALYSIS, WorkflowPhase.ARCHITECTURE],
        agent_roles=[AgentRole.PRODUCT_ANALYST, AgentRole.ARCHITECT],
    )
    assert config.name == "Test Workflow"
    assert len(config.phases) == 2
    assert len(config.agent_roles) == 2
    assert config.id is not None
