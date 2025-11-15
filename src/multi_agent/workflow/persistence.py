"""Workflow state persistence."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from multi_agent.workflow.models import (
    WorkflowState,
    WorkflowStatus,
    PhaseTransition,
)
from multi_agent.core.models import AgentRole, WorkflowPhase


class WorkflowPersistence:
    """Handles saving and loading workflow state."""

    def __init__(self, storage_path: Path):
        """Initialize persistence layer.
        
        Args:
            storage_path: Directory for storing workflow files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save(self, state: WorkflowState) -> None:
        """Save workflow state to disk.
        
        Args:
            state: Workflow state to save
        """
        filename = f"{state.workflow_id}.json"
        filepath = self.storage_path / filename
        
        data = state.to_dict()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state from disk.
        
        Args:
            workflow_id: ID of workflow to load
            
        Returns:
            WorkflowState if found, None otherwise
        """
        filename = f"{workflow_id}.json"
        filepath = self.storage_path / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return self._deserialize_state(data)

    def _deserialize_state(self, data: Dict[str, Any]) -> WorkflowState:
        """Deserialize workflow state from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            WorkflowState object
        """
        # Deserialize transitions
        transitions = []
        for t_data in data.get("transitions", []):
            transition = PhaseTransition(
                from_phase=WorkflowPhase(t_data["from_phase"]) if t_data["from_phase"] else None,
                to_phase=WorkflowPhase(t_data["to_phase"]),
                timestamp=datetime.fromisoformat(t_data["timestamp"]),
                agent_role=AgentRole(t_data["agent_role"]) if t_data["agent_role"] else None,
                success=t_data["success"],
                metadata=t_data.get("metadata", {}),
            )
            transitions.append(transition)
        
        # Create state
        state = WorkflowState(
            workflow_id=data["workflow_id"],
            current_phase=WorkflowPhase(data["current_phase"]),
            status=WorkflowStatus(data["status"]),
            transitions=transitions,
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_phases=[WorkflowPhase(p) for p in data.get("completed_phases", [])],
            failed_phases=[WorkflowPhase(p) for p in data.get("failed_phases", [])],
        )
        
        return state

    def list_workflows(self) -> list[str]:
        """List all saved workflow IDs.
        
        Returns:
            List of workflow IDs
        """
        if not self.storage_path.exists():
            return []
        
        return [f.stem for f in self.storage_path.glob("*.json")]

    def delete(self, workflow_id: str) -> bool:
        """Delete a saved workflow.
        
        Args:
            workflow_id: ID of workflow to delete
            
        Returns:
            True if deleted, False if not found
        """
        filename = f"{workflow_id}.json"
        filepath = self.storage_path / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
