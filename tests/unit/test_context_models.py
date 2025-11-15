"""Tests for context data models."""

import pytest
from multi_agent.context.models import Context, ContextEntry
from multi_agent.core.models import AgentOutput, AgentRole


def test_context_entry_creation():
    """Test ContextEntry creation."""
    output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-123",
        content="Test content",
    )
    entry = ContextEntry(
        agent_role=AgentRole.DEVELOPER,
        output=output,
        metadata={"key": "value"},
    )
    
    assert entry.id is not None
    assert entry.agent_role == AgentRole.DEVELOPER
    assert entry.output.content == "Test content"
    assert entry.metadata["key"] == "value"
    assert len(entry.dependencies) == 0


def test_context_add_entry():
    """Test adding entries to context."""
    context = Context()
    output = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-456",
        content="Architecture design",
    )
    entry = ContextEntry(agent_role=AgentRole.ARCHITECT, output=output)
    
    context.add_entry(entry)
    assert len(context.entries) == 1
    assert context.entries[0].agent_role == AgentRole.ARCHITECT


def test_context_get_by_agent_role():
    """Test filtering entries by agent role."""
    context = Context()
    
    dev_output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-1",
        content="Code",
    )
    arch_output = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-2",
        content="Design",
    )
    
    context.add_entry(ContextEntry(agent_role=AgentRole.DEVELOPER, output=dev_output))
    context.add_entry(ContextEntry(agent_role=AgentRole.ARCHITECT, output=arch_output))
    context.add_entry(ContextEntry(agent_role=AgentRole.DEVELOPER, output=dev_output))
    
    dev_entries = context.get_by_agent_role(AgentRole.DEVELOPER)
    assert len(dev_entries) == 2
    
    arch_entries = context.get_by_agent_role(AgentRole.ARCHITECT)
    assert len(arch_entries) == 1


def test_context_get_by_id():
    """Test getting entry by ID."""
    context = Context()
    output = AgentOutput(
        agent_role=AgentRole.DEBUGGER,
        task_id="task-789",
        content="Debug info",
    )
    entry = ContextEntry(agent_role=AgentRole.DEBUGGER, output=output)
    context.add_entry(entry)
    
    retrieved = context.get_by_id(entry.id)
    assert retrieved is not None
    assert retrieved.id == entry.id
    assert retrieved.agent_role == AgentRole.DEBUGGER


def test_context_get_dependencies():
    """Test getting dependencies."""
    context = Context()
    
    output1 = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-1",
        content="Design",
    )
    entry1 = ContextEntry(agent_role=AgentRole.ARCHITECT, output=output1)
    context.add_entry(entry1)
    
    output2 = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-2",
        content="Code",
    )
    entry2 = ContextEntry(
        agent_role=AgentRole.DEVELOPER,
        output=output2,
        dependencies=[entry1.id],
    )
    context.add_entry(entry2)
    
    deps = context.get_dependencies(entry2.id)
    assert len(deps) == 1
    assert deps[0].id == entry1.id


def test_context_to_dict():
    """Test context serialization."""
    context = Context()
    output = AgentOutput(
        agent_role=AgentRole.CODE_REVIEWER,
        task_id="task-review",
        content="Review comments",
    )
    entry = ContextEntry(agent_role=AgentRole.CODE_REVIEWER, output=output)
    context.add_entry(entry)
    
    data = context.to_dict()
    assert "entries" in data
    assert len(data["entries"]) == 1
    assert data["entries"][0]["agent_role"] == "code_reviewer"
