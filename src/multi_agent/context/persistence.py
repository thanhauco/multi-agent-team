"""Context persistence layer for saving and loading context."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from multi_agent.context.models import Context, ContextEntry
from multi_agent.core.models import (
    AgentOutput,
    AgentRole,
    Artifact,
    ArtifactType,
    ValidationStatus,
)


class ContextPersistence:
    """Handles saving and loading context to/from disk."""

    def __init__(self, storage_path: Path):
        """Initialize persistence layer.
        
        Args:
            storage_path: Directory path for storing context files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save(self, context: Context, filename: str = "context.json") -> None:
        """Save context to JSON file.
        
        Args:
            context: Context object to save
            filename: Name of the file to save to
        """
        filepath = self.storage_path / filename
        data = context.to_dict()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, filename: str = "context.json") -> Context:
        """Load context from JSON file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded Context object
        """
        filepath = self.storage_path / filename
        
        if not filepath.exists():
            return Context()
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return self._deserialize_context(data)

    def _deserialize_context(self, data: Dict[str, Any]) -> Context:
        """Deserialize context from dictionary.
        
        Args:
            data: Dictionary representation of context
            
        Returns:
            Context object
        """
        entries = []
        for entry_data in data.get("entries", []):
            entry = self._deserialize_entry(entry_data)
            entries.append(entry)
        
        context = Context(
            entries=entries,
            metadata=data.get("metadata", {}),
        )
        return context

    def _deserialize_entry(self, data: Dict[str, Any]) -> ContextEntry:
        """Deserialize a context entry.
        
        Args:
            data: Dictionary representation of entry
            
        Returns:
            ContextEntry object
        """
        output_data = data["output"]
        
        # Deserialize artifacts
        artifacts = []
        for art_data in output_data.get("artifacts", []):
            artifact = Artifact(
                type=ArtifactType(art_data["type"]),
                path=art_data["path"],
                content=art_data["content"],
                metadata=art_data.get("metadata", {}),
            )
            artifacts.append(artifact)
        
        # Deserialize agent output
        output = AgentOutput(
            agent_role=AgentRole(output_data["agent_role"]),
            task_id=output_data["task_id"],
            content=output_data["content"],
            artifacts=artifacts,
            validation_status=ValidationStatus(output_data["validation_status"]),
            metadata=output_data.get("metadata", {}),
            created_at=datetime.fromisoformat(output_data["created_at"]),
        )
        
        # Deserialize context entry
        entry = ContextEntry(
            id=data["id"],
            agent_role=AgentRole(data["agent_role"]),
            output=output,
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            dependencies=data.get("dependencies", []),
        )
        
        return entry

    def list_saved_contexts(self) -> list[str]:
        """List all saved context files.
        
        Returns:
            List of context filenames
        """
        if not self.storage_path.exists():
            return []
        
        return [f.name for f in self.storage_path.glob("*.json")]

    def delete(self, filename: str = "context.json") -> bool:
        """Delete a saved context file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deleted, False if file didn't exist
        """
        filepath = self.storage_path / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False
