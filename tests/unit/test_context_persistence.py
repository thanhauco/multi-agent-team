"""Tests for context persistence."""

import pytest
import tempfile
from pathlib import Path

from multi_agent.context.models import Context, ContextEntry
from multi_agent.context.persistence import ContextPersistence
from multi_agent.core.models import AgentOutput, AgentRole, Artifact, ArtifactType


def test_save_and_load_context():
    """Test saving and loading context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = ContextPersistence(Path(tmpdir))
        
        # Create context with entries
        context = Context()
        output = AgentOutput(
            agent_role=AgentRole.DEVELOPER,
            task_id="task-123",
            content="Test content",
        )
        entry = ContextEntry(agent_role=AgentRole.DEVELOPER, output=output)
        context.add_entry(entry)
        
        # Save
        persistence.save(context, "test_context.json")
        
        # Load
        loaded_context = persistence.load("test_context.json")
        
        assert len(loaded_context.entries) == 1
        assert loaded_context.entries[0].output.content == "Test content"
        assert loaded_context.entries[0].agent_role == AgentRole.DEVELOPER


def test_save_context_with_artifacts():
    """Test saving context with artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = ContextPersistence(Path(tmpdir))
        
        artifact = Artifact(
            type=ArtifactType.CODE,
            path="src/main.py",
            content="print('hello')",
            metadata={"language": "python"},
        )
        
        output = AgentOutput(
            agent_role=AgentRole.DEVELOPER,
            task_id="task-456",
            content="Generated code",
            artifacts=[artifact],
        )
        
        context = Context()
        entry = ContextEntry(agent_role=AgentRole.DEVELOPER, output=output)
        context.add_entry(entry)
        
        # Save and load
        persistence.save(context)
        loaded_context = persistence.load()
        
        assert len(loaded_context.entries) == 1
        assert len(loaded_context.entries[0].output.artifacts) == 1
        assert loaded_context.entries[0].output.artifacts[0].type == ArtifactType.CODE
        assert loaded_context.entries[0].output.artifacts[0].path == "src/main.py"


def test_load_nonexistent_context():
    """Test loading a context that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = ContextPersistence(Path(tmpdir))
        
        # Should return empty context
        context = persistence.load("nonexistent.json")
        assert len(context.entries) == 0


def test_list_saved_contexts():
    """Test listing saved context files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = ContextPersistence(Path(tmpdir))
        
        # Save multiple contexts
        context = Context()
        persistence.save(context, "context1.json")
        persistence.save(context, "context2.json")
        
        files = persistence.list_saved_contexts()
        assert len(files) == 2
        assert "context1.json" in files
        assert "context2.json" in files


def test_delete_context():
    """Test deleting a saved context."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = ContextPersistence(Path(tmpdir))
        
        context = Context()
        persistence.save(context, "to_delete.json")
        
        # Delete
        result = persistence.delete("to_delete.json")
        assert result is True
        
        # Try to delete again
        result = persistence.delete("to_delete.json")
        assert result is False


def test_context_with_dependencies():
    """Test saving and loading context with dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = ContextPersistence(Path(tmpdir))
        
        context = Context()
        
        # Create two entries with dependency
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
        
        # Save and load
        persistence.save(context)
        loaded_context = persistence.load()
        
        assert len(loaded_context.entries) == 2
        # Find the developer entry
        dev_entry = [e for e in loaded_context.entries if e.agent_role == AgentRole.DEVELOPER][0]
        assert len(dev_entry.dependencies) == 1
        assert dev_entry.dependencies[0] == entry1.id
