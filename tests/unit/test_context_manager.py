"""Tests for ContextManager."""

import pytest
from pathlib import Path

from multi_agent.context.manager import ContextManager
from multi_agent.core.models import AgentOutput, AgentRole


def test_context_manager_initialization():
    """Test ContextManager initialization."""
    manager = ContextManager()
    assert manager.context is not None
    assert len(manager.context.entries) == 0


def test_store_output():
    """Test storing agent output."""
    manager = ContextManager()
    output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-123",
        content="Generated code",
    )
    
    entry_id = manager.store_output(
        agent_id="agent-dev-1",
        output=output,
        metadata={"version": "1.0"},
    )
    
    assert entry_id is not None
    assert len(manager.context.entries) == 1
    
    entry = manager.get_entry_by_id(entry_id)
    assert entry is not None
    assert entry.output.content == "Generated code"
    assert entry.metadata["agent_id"] == "agent-dev-1"
    assert entry.metadata["version"] == "1.0"


def test_get_context_for_agent():
    """Test getting context for an agent."""
    manager = ContextManager()
    
    # Store outputs from different agents
    arch_output = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-1",
        content="Architecture design",
    )
    manager.store_output("agent-arch-1", arch_output)
    
    dev_output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-2",
        content="Code implementation",
    )
    manager.store_output("agent-dev-1", dev_output)
    
    # Developer should see architect's context but not other developers
    dev_context = manager.get_context_for_agent(AgentRole.DEVELOPER)
    assert len(dev_context.entries) == 1
    assert dev_context.entries[0].agent_role == AgentRole.ARCHITECT


def test_track_dependency():
    """Test tracking dependencies between entries."""
    manager = ContextManager()
    
    output1 = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-1",
        content="Design",
    )
    entry1_id = manager.store_output("agent-arch-1", output1)
    
    output2 = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-2",
        content="Code",
    )
    entry2_id = manager.store_output("agent-dev-1", output2)
    
    # Track that entry2 depends on entry1
    manager.track_dependency(entry1_id, entry2_id)
    
    deps = manager.get_dependencies(entry2_id)
    assert len(deps) == 1
    assert deps[0].id == entry1_id


def test_get_context_history():
    """Test getting context history."""
    manager = ContextManager()
    
    for i in range(3):
        output = AgentOutput(
            agent_role=AgentRole.DEVELOPER,
            task_id=f"task-{i}",
            content=f"Content {i}",
        )
        manager.store_output(f"agent-{i}", output)
    
    history = manager.get_context_history()
    assert len(history) == 3
    # Should be in chronological order
    assert history[0].output.task_id == "task-0"
    assert history[2].output.task_id == "task-2"


def test_clear_context():
    """Test clearing context."""
    manager = ContextManager()
    
    output = AgentOutput(
        agent_role=AgentRole.DEBUGGER,
        task_id="task-debug",
        content="Debug info",
    )
    manager.store_output("agent-debug-1", output)
    
    assert len(manager.context.entries) == 1
    
    manager.clear_context()
    assert len(manager.context.entries) == 0


def test_get_entries_by_role():
    """Test getting entries by agent role."""
    manager = ContextManager()
    
    # Add multiple entries from different roles
    for role in [AgentRole.DEVELOPER, AgentRole.ARCHITECT, AgentRole.DEVELOPER]:
        output = AgentOutput(
            agent_role=role,
            task_id=f"task-{role.value}",
            content=f"Content from {role.value}",
        )
        manager.store_output(f"agent-{role.value}", output)
    
    dev_entries = manager.get_entries_by_role(AgentRole.DEVELOPER)
    assert len(dev_entries) == 2
    
    arch_entries = manager.get_entries_by_role(AgentRole.ARCHITECT)
    assert len(arch_entries) == 1
