"""Context management data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from multi_agent.core.models import AgentOutput, AgentRole


@dataclass
class ContextEntry:
    """Represents a single context entry from an agent."""

    id: str = field(default_factory=lambda: str(uuid4()))
    agent_role: AgentRole = AgentRole.DEVELOPER
    output: AgentOutput = field(default_factory=lambda: AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="",
        content=""
    ))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "agent_role": self.agent_role.value,
            "output": {
                "agent_role": self.output.agent_role.value,
                "task_id": self.output.task_id,
                "content": self.output.content,
                "artifacts": [
                    {
                        "type": a.type.value,
                        "path": a.path,
                        "content": a.content,
                        "metadata": a.metadata,
                    }
                    for a in self.output.artifacts
                ],
                "validation_status": self.output.validation_status.value,
                "metadata": self.output.metadata,
                "created_at": self.output.created_at.isoformat(),
            },
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "dependencies": self.dependencies,
        }


@dataclass
class Context:
    """Aggregates multiple context entries for agent consumption."""

    entries: List[ContextEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_entry(self, entry: ContextEntry) -> None:
        """Add a context entry."""
        self.entries.append(entry)

    def get_by_agent_role(self, role: AgentRole) -> List[ContextEntry]:
        """Get all entries from a specific agent role."""
        return [e for e in self.entries if e.agent_role == role]

    def get_by_id(self, entry_id: str) -> ContextEntry | None:
        """Get entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def get_dependencies(self, entry_id: str) -> List[ContextEntry]:
        """Get all dependencies for an entry."""
        entry = self.get_by_id(entry_id)
        if not entry:
            return []
        
        deps = []
        for dep_id in entry.dependencies:
            dep_entry = self.get_by_id(dep_id)
            if dep_entry:
                deps.append(dep_entry)
        return deps

    def get_recent(self, limit: int = 10) -> List[ContextEntry]:
        """Get most recent entries."""
        sorted_entries = sorted(self.entries, key=lambda e: e.timestamp, reverse=True)
        return sorted_entries[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "metadata": self.metadata,
        }
