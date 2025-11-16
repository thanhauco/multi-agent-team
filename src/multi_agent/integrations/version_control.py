"""Version control integration for tracking agent changes."""

from pathlib import Path
from typing import Optional

try:
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from multi_agent.core.models import AgentRole


class VersionControlManager:
    """Manages git operations for agent outputs."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize version control manager.
        
        Args:
            repo_path: Path to git repository
        """
        if not GIT_AVAILABLE:
            raise ImportError("GitPython not installed. Install with: pip install gitpython")
        
        self.repo_path = repo_path or Path(".")
        try:
            self.repo = Repo(self.repo_path)
        except Exception:
            # Initialize new repo if doesn't exist
            self.repo = Repo.init(self.repo_path)

    def commit_changes(
        self,
        agent_role: AgentRole,
        task_id: str,
        message: str,
    ) -> str:
        """Commit changes with agent metadata.
        
        Args:
            agent_role: Agent that made changes
            task_id: Task identifier
            message: Commit message
            
        Returns:
            Commit SHA
        """
        # Add all changes
        self.repo.git.add(A=True)
        
        # Create commit with metadata
        full_message = f"[{agent_role.value}] {message}\n\nTask: {task_id}"
        
        try:
            commit = self.repo.index.commit(full_message)
            return commit.hexsha
        except Exception as e:
            # No changes to commit
            return ""

    def create_branch(self, workflow_id: str) -> str:
        """Create branch for workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Branch name
        """
        branch_name = f"workflow/{workflow_id}"
        
        try:
            # Create and checkout new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            return branch_name
        except Exception:
            # Branch might already exist
            return branch_name

    def handle_conflict(self, conflict_info: dict) -> dict:
        """Handle merge conflict.
        
        Args:
            conflict_info: Conflict information
            
        Returns:
            Resolution information
        """
        # For now, just return conflict info for manual resolution
        return {
            "status": "manual_resolution_required",
            "conflicts": conflict_info,
            "message": "Please resolve conflicts manually",
        }

    def tag_release(self, workflow_id: str, metadata: dict) -> None:
        """Tag release with workflow metadata.
        
        Args:
            workflow_id: Workflow identifier
            metadata: Release metadata
        """
        tag_name = f"release/{workflow_id}"
        tag_message = f"Release from workflow {workflow_id}"
        
        if metadata:
            tag_message += f"\n\nMetadata: {metadata}"
        
        try:
            self.repo.create_tag(tag_name, message=tag_message)
        except Exception:
            # Tag might already exist
            pass

    def get_status(self) -> dict:
        """Get repository status.
        
        Returns:
            Status information
        """
        return {
            "branch": self.repo.active_branch.name,
            "modified": [item.a_path for item in self.repo.index.diff(None)],
            "untracked": self.repo.untracked_files,
            "commits": len(list(self.repo.iter_commits())),
        }
