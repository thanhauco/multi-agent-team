"""Logging system for agent activities and decisions."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from multi_agent.core.models import AgentRole, WorkflowPhase


class ActivityType(Enum):
    """Types of agent activities."""
    
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    GENERATION = "generation"
    VALIDATION = "validation"
    ERROR = "error"


@dataclass
class Activity:
    """Represents an agent activity."""
    
    activity_type: ActivityType
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Decision:
    """Represents an agent decision."""
    
    decision_type: str
    rationale: str
    alternatives_considered: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LogEntry:
    """Represents a log entry."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    agent_role: Optional[AgentRole] = None
    workflow_phase: Optional[WorkflowPhase] = None
    activity: Optional[Activity] = None
    decision: Optional[Decision] = None
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent_role": self.agent_role.value if self.agent_role else None,
            "workflow_phase": self.workflow_phase.value if self.workflow_phase else None,
            "activity": {
                "type": self.activity.activity_type.value,
                "description": self.activity.description,
                "metadata": self.activity.metadata,
                "timestamp": self.activity.timestamp.isoformat(),
            } if self.activity else None,
            "decision": {
                "type": self.decision.decision_type,
                "rationale": self.decision.rationale,
                "alternatives": self.decision.alternatives_considered,
                "metadata": self.decision.metadata,
                "timestamp": self.decision.timestamp.isoformat(),
            } if self.decision else None,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LogFilters:
    """Filters for querying logs."""
    
    agent_role: Optional[AgentRole] = None
    workflow_phase: Optional[WorkflowPhase] = None
    activity_type: Optional[ActivityType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    search_text: Optional[str] = None


class LoggingSystem:
    """System for logging agent activities and decisions."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize logging system.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = log_dir or Path(".multi_agent/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.entries: List[LogEntry] = []
        self.current_log_file = self.log_dir / f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def log_agent_activity(
        self,
        agent_id: str,
        activity: Activity,
        reasoning: str = "",
    ) -> None:
        """Log an agent activity.
        
        Args:
            agent_id: Agent identifier
            activity: Activity to log
            reasoning: Reasoning for the activity
        """
        entry = LogEntry(
            activity=activity,
            reasoning=reasoning,
            metadata={"agent_id": agent_id},
        )
        self._add_entry(entry)
    
    def log_workflow_transition(
        self,
        workflow_id: str,
        from_phase: WorkflowPhase,
        to_phase: WorkflowPhase,
    ) -> None:
        """Log a workflow phase transition.
        
        Args:
            workflow_id: Workflow identifier
            from_phase: Source phase
            to_phase: Target phase
        """
        activity = Activity(
            activity_type=ActivityType.TASK_COMPLETE,
            description=f"Transition from {from_phase.value} to {to_phase.value}",
            metadata={"workflow_id": workflow_id},
        )
        entry = LogEntry(
            workflow_phase=to_phase,
            activity=activity,
            metadata={"workflow_id": workflow_id, "from_phase": from_phase.value},
        )
        self._add_entry(entry)
    
    def log_decision(
        self,
        agent_id: str,
        decision: Decision,
        rationale: str,
    ) -> None:
        """Log an agent decision.
        
        Args:
            agent_id: Agent identifier
            decision: Decision to log
            rationale: Rationale for the decision
        """
        entry = LogEntry(
            decision=decision,
            reasoning=rationale,
            metadata={"agent_id": agent_id},
        )
        self._add_entry(entry)
    
    def query_logs(self, filters: LogFilters) -> List[LogEntry]:
        """Query logs with filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            Filtered log entries
        """
        results = self.entries
        
        if filters.agent_role:
            results = [e for e in results if e.agent_role == filters.agent_role]
        
        if filters.workflow_phase:
            results = [e for e in results if e.workflow_phase == filters.workflow_phase]
        
        if filters.activity_type and filters.activity_type:
            results = [
                e for e in results
                if e.activity and e.activity.activity_type == filters.activity_type
            ]
        
        if filters.start_time:
            results = [e for e in results if e.timestamp >= filters.start_time]
        
        if filters.end_time:
            results = [e for e in results if e.timestamp <= filters.end_time]
        
        if filters.search_text:
            search_lower = filters.search_text.lower()
            results = [
                e for e in results
                if search_lower in e.reasoning.lower()
                or (e.activity and search_lower in e.activity.description.lower())
            ]
        
        return results
    
    def generate_summary_report(self, workflow_id: str) -> Dict[str, Any]:
        """Generate summary report for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Summary report
        """
        workflow_entries = [
            e for e in self.entries
            if e.metadata.get("workflow_id") == workflow_id
        ]
        
        # Count activities by type
        activity_counts = {}
        for entry in workflow_entries:
            if entry.activity:
                activity_type = entry.activity.activity_type.value
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        # Count by agent role
        agent_counts = {}
        for entry in workflow_entries:
            if entry.agent_role:
                role = entry.agent_role.value
                agent_counts[role] = agent_counts.get(role, 0) + 1
        
        # Timeline
        timeline = [
            {
                "timestamp": e.timestamp.isoformat(),
                "phase": e.workflow_phase.value if e.workflow_phase else None,
                "activity": e.activity.description if e.activity else None,
            }
            for e in workflow_entries
        ]
        
        return {
            "workflow_id": workflow_id,
            "total_entries": len(workflow_entries),
            "activity_counts": activity_counts,
            "agent_counts": agent_counts,
            "timeline": timeline,
            "start_time": workflow_entries[0].timestamp.isoformat() if workflow_entries else None,
            "end_time": workflow_entries[-1].timestamp.isoformat() if workflow_entries else None,
        }
    
    def _add_entry(self, entry: LogEntry) -> None:
        """Add entry to logs and persist.
        
        Args:
            entry: Log entry to add
        """
        self.entries.append(entry)
        self._persist_entry(entry)
    
    def _persist_entry(self, entry: LogEntry) -> None:
        """Persist entry to disk.
        
        Args:
            entry: Entry to persist
        """
        with open(self.current_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")
