"""Context manager for storing and retrieving agent outputs."""

from typing import Any, Dict, List, Optional
from pathlib import Path

from multi_agent.context.models import Context, ContextEntry
from multi_agent.core.models import AgentOutput, AgentRole


class ContextManager:
    """Manages shared context across agents."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize context manager.
        
        Args:
            storage_path: Path for context persistence (optional)
        """
        self.context = Context()
        self.storage_path = storage_path or Path(".multi_agent/context")
        self._dependency_graph: Dict[str, List[str]] = {}

    def store_output(
        self,
        agent_id: str,
        output: AgentOutput,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store agent output in context.
        
        Args:
            agent_id: Unique identifier for the agent instance
            output: Agent output to store
            metadata: Additional metadata
            
        Returns:
            ID of the created context entry
        """
        entry = ContextEntry(
            agent_role=output.agent_role,
            output=output,
            metadata=metadata or {},
        )
        entry.metadata["agent_id"] = agent_id
        
        self.context.add_entry(entry)
        return entry.id

    def get_context_for_agent(self, agent_role: AgentRole) -> Context:
        """Get relevant context for an agent.
        
        Args:
            agent_role: Role of the agent requesting context
            
        Returns:
            Context object with relevant entries
        """
        # Get all entries except from the same role (to avoid circular context)
        relevant_entries = [
            e for e in self.context.entries
            if e.agent_role != agent_role
        ]
        
        filtered_context = Context(entries=relevant_entries)
        return filtered_context

    def track_dependency(self, source_id: str, target_id: str) -> None:
        """Track dependency between context entries.
        
        Args:
            source_id: ID of the source entry
            target_id: ID of the entry that depends on source
        """
        if target_id not in self._dependency_graph:
            self._dependency_graph[target_id] = []
        
        if source_id not in self._dependency_graph[target_id]:
            self._dependency_graph[target_id].append(source_id)
        
        # Update the target entry's dependencies
        target_entry = self.context.get_by_id(target_id)
        if target_entry and source_id not in target_entry.dependencies:
            target_entry.dependencies.append(source_id)

    def get_context_history(self) -> List[ContextEntry]:
        """Get complete context history.
        
        Returns:
            List of all context entries in chronological order
        """
        return sorted(self.context.entries, key=lambda e: e.timestamp)

    def clear_context(self) -> None:
        """Clear all context entries."""
        self.context = Context()
        self._dependency_graph = {}

    def get_entry_by_id(self, entry_id: str) -> Optional[ContextEntry]:
        """Get a specific context entry by ID.
        
        Args:
            entry_id: ID of the entry to retrieve
            
        Returns:
            ContextEntry if found, None otherwise
        """
        return self.context.get_by_id(entry_id)

    def get_dependencies(self, entry_id: str) -> List[ContextEntry]:
        """Get all dependencies for an entry.
        
        Args:
            entry_id: ID of the entry
            
        Returns:
            List of dependent context entries
        """
        return self.context.get_dependencies(entry_id)

    def get_entries_by_role(self, role: AgentRole) -> List[ContextEntry]:
        """Get all entries from a specific agent role.
        
        Args:
            role: Agent role to filter by
            
        Returns:
            List of context entries from that role
        """
        return self.context.get_by_agent_role(role)
