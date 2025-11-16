"""Technical debt tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from uuid import uuid4


@dataclass
class DebtItem:
    """Represents a technical debt item."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    location: str = ""
    complexity_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class TechnicalDebtTracker:
    """Tracks technical debt across the codebase."""
    
    def __init__(self):
        """Initialize debt tracker."""
        self.debt_items: List[DebtItem] = []
        self.complexity_threshold = 10.0
    
    def track_debt(self, item: DebtItem) -> str:
        """Track a debt item.
        
        Args:
            item: Debt item to track
            
        Returns:
            Debt item ID
        """
        self.debt_items.append(item)
        return item.id
    
    def get_high_priority_debt(self) -> List[DebtItem]:
        """Get high priority debt items."""
        return [
            item for item in self.debt_items
            if item.severity in ["high", "critical"]
        ]
    
    def should_trigger_review(self, complexity: float) -> bool:
        """Check if complexity triggers mandatory review."""
        return complexity > self.complexity_threshold
