"""Tests for logging system."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from multi_agent.integrations.logging_system import (
    LoggingSystem,
    Activity,
    ActivityType,
    Decision,
    LogFilters,
)
from multi_agent.core.models import AgentRole, WorkflowPhase


def test_logging_system_initialization():
    """Test logging system initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        system = LoggingSystem(log_dir=log_dir)
        
        assert system.log_dir == log_dir
        assert system.log_dir.exists()
        assert len(system.entries) == 0


def test_log_agent_activity():
    """Test logging agent activity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        activity = Activity(
            activity_type=ActivityType.TASK_START,
            description="Starting task",
        )
        
        system.log_agent_activity("agent-1", activity, "Starting new task")
        
        assert len(system.entries) == 1
        assert system.entries[0].activity == activity
        assert system.entries[0].reasoning == "Starting new task"


def test_log_workflow_transition():
    """Test logging workflow transitions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        system.log_workflow_transition(
            "workflow-1",
            WorkflowPhase.ANALYSIS,
            WorkflowPhase.ARCHITECTURE,
        )
        
        assert len(system.entries) == 1
        assert system.entries[0].workflow_phase == WorkflowPhase.ARCHITECTURE
        assert "from_phase" in system.entries[0].metadata


def test_log_decision():
    """Test logging agent decisions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        decision = Decision(
            decision_type="architecture_choice",
            rationale="Chose microservices for scalability",
            alternatives_considered=["Monolith", "Serverless"],
        )
        
        system.log_decision("agent-arch", decision, "Based on requirements")
        
        assert len(system.entries) == 1
        assert system.entries[0].decision == decision


def test_query_logs_by_agent_role():
    """Test querying logs by agent role."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        # Add entries for different roles
        activity1 = Activity(ActivityType.TASK_START, "Task 1")
        entry1 = system.entries.append(
            system._create_entry(activity=activity1, agent_role=AgentRole.DEVELOPER)
        )
        
        activity2 = Activity(ActivityType.TASK_START, "Task 2")
        system.log_agent_activity("agent-arch", activity2)
        
        # Query for developer role
        filters = LogFilters(agent_role=AgentRole.DEVELOPER)
        results = system.query_logs(filters)
        
        # Should only get developer entries
        assert all(e.agent_role == AgentRole.DEVELOPER for e in results if e.agent_role)


def test_query_logs_by_time_range():
    """Test querying logs by time range."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        # Add entries
        activity = Activity(ActivityType.TASK_START, "Task")
        system.log_agent_activity("agent-1", activity)
        
        # Query with time range
        now = datetime.now()
        filters = LogFilters(
            start_time=now - timedelta(minutes=1),
            end_time=now + timedelta(minutes=1),
        )
        results = system.query_logs(filters)
        
        assert len(results) > 0


def test_query_logs_by_search_text():
    """Test querying logs by search text."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        activity1 = Activity(ActivityType.TASK_START, "Implementing feature X")
        system.log_agent_activity("agent-1", activity1)
        
        activity2 = Activity(ActivityType.TASK_START, "Reviewing code")
        system.log_agent_activity("agent-2", activity2)
        
        # Search for "feature"
        filters = LogFilters(search_text="feature")
        results = system.query_logs(filters)
        
        assert len(results) == 1
        assert "feature" in results[0].activity.description.lower()


def test_generate_summary_report():
    """Test generating summary report."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = LoggingSystem(log_dir=Path(tmpdir))
        
        # Add workflow entries
        system.log_workflow_transition(
            "workflow-1",
            WorkflowPhase.ANALYSIS,
            WorkflowPhase.ARCHITECTURE,
        )
        
        activity = Activity(ActivityType.TASK_COMPLETE, "Completed task")
        system.log_agent_activity("agent-1", activity)
        system.entries[-1].metadata["workflow_id"] = "workflow-1"
        
        # Generate report
        report = system.generate_summary_report("workflow-1")
        
        assert report["workflow_id"] == "workflow-1"
        assert report["total_entries"] >= 1
        assert "activity_counts" in report
        assert "timeline" in report


def test_log_persistence():
    """Test that logs are persisted to disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        system = LoggingSystem(log_dir=log_dir)
        
        activity = Activity(ActivityType.TASK_START, "Test")
        system.log_agent_activity("agent-1", activity)
        
        # Check that log file was created
        log_files = list(log_dir.glob("*.jsonl"))
        assert len(log_files) > 0
        
        # Check that file has content
        with open(log_files[0], "r") as f:
            content = f.read()
            assert len(content) > 0


def test_log_entry_to_dict():
    """Test log entry serialization."""
    from multi_agent.integrations.logging_system import LogEntry
    
    activity = Activity(ActivityType.TASK_START, "Test activity")
    entry = LogEntry(
        agent_role=AgentRole.DEVELOPER,
        workflow_phase=WorkflowPhase.IMPLEMENTATION,
        activity=activity,
        reasoning="Test reasoning",
    )
    
    data = entry.to_dict()
    
    assert data["agent_role"] == "developer"
    assert data["workflow_phase"] == "implementation"
    assert data["activity"]["type"] == "task_start"
    assert data["reasoning"] == "Test reasoning"
