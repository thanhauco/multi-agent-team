"""Agent orchestrator for coordinating multi-agent workflows."""

from pathlib import Path
from typing import Dict, Optional

from multi_agent.agents.base_agent import Agent
from multi_agent.agents.loader import AgentLoader
from multi_agent.context.manager import ContextManager
from multi_agent.core.models import (
    AgentOutput,
    AgentRole,
    Task,
    ValidationError,
    WorkflowConfig,
    WorkflowPhase,
)
from multi_agent.integrations.llm_provider import LLMProvider
from multi_agent.integrations.logging_system import Activity, ActivityType, LoggingSystem
from multi_agent.workflow.manager import WorkflowManager


class AgentOrchestrator:
    """Orchestrates agent execution and workflow coordination."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        storage_path: Optional[Path] = None,
    ):
        """Initialize orchestrator.
        
        Args:
            llm_provider: LLM provider for agents
            storage_path: Base path for storage
        """
        self.llm_provider = llm_provider
        self.storage_path = storage_path or Path(".multi_agent")
        
        # Initialize managers
        self.context_manager = ContextManager(
            storage_path=self.storage_path / "context"
        )
        self.workflow_manager = WorkflowManager(
            storage_path=self.storage_path / "workflows"
        )
        self.logging_system = LoggingSystem(
            log_dir=self.storage_path / "logs"
        )
        self.agent_loader = AgentLoader()
        
        # Cache for instantiated agents
        self.agents: Dict[AgentRole, Agent] = {}

    def execute_workflow(self, config: WorkflowConfig) -> str:
        """Execute a complete workflow.
        
        Args:
            config: Workflow configuration
            
        Returns:
            Workflow ID
        """
        # Initialize workflow
        workflow_id = self.workflow_manager.initialize_workflow(config)
        
        self.logging_system.log_workflow_transition(
            workflow_id,
            WorkflowPhase.ANALYSIS,
            config.phases[0] if config.phases else WorkflowPhase.ANALYSIS,
        )
        
        try:
            # Execute each phase
            for i, phase in enumerate(config.phases):
                # Get agent role for this phase
                agent_role = self._get_agent_for_phase(phase)
                if not agent_role:
                    continue
                
                # Create task for this phase
                task = Task(
                    description=f"Execute {phase.value} phase",
                    metadata={"workflow_id": workflow_id, "phase": phase.value},
                )
                
                # Execute agent
                output = self.invoke_agent(agent_role, task)
                
                # Validate output
                agent = self._get_agent(agent_role)
                validation = agent.validate_output(output)
                
                if not validation.is_valid:
                    self.handle_validation_failure(phase, validation.errors)
                    self.workflow_manager.mark_workflow_failed(
                        workflow_id,
                        f"Validation failed in {phase.value}",
                    )
                    return workflow_id
                
                # Transition to next phase
                if i < len(config.phases) - 1:
                    next_phase = config.phases[i + 1]
                    self.workflow_manager.transition_phase(
                        workflow_id,
                        next_phase,
                        agent_role,
                    )
            
            # Mark workflow complete
            self.workflow_manager.mark_workflow_complete(workflow_id)
            
        except Exception as e:
            self.workflow_manager.mark_workflow_failed(workflow_id, str(e))
            raise
        
        return workflow_id

    def invoke_agent(self, agent_role: AgentRole, task: Task) -> AgentOutput:
        """Invoke a specific agent.
        
        Args:
            agent_role: Role of agent to invoke
            task: Task to execute
            
        Returns:
            Agent output
        """
        # Get agent instance
        agent = self._get_agent(agent_role)
        
        # Log activity
        activity = Activity(
            activity_type=ActivityType.TASK_START,
            description=f"Starting task: {task.description}",
            metadata={"task_id": task.id, "agent_role": agent_role.value},
        )
        self.logging_system.log_agent_activity(
            agent_id=f"{agent_role.value}-1",
            activity=activity,
        )
        
        # Get context for agent
        context = self.context_manager.get_context_for_agent(agent_role)
        
        # Execute agent
        try:
            output = agent.execute(task, context)
            
            # Store output in context
            self.context_manager.store_output(
                agent_id=f"{agent_role.value}-1",
                output=output,
            )
            
            # Log completion
            completion_activity = Activity(
                activity_type=ActivityType.TASK_COMPLETE,
                description=f"Completed task: {task.description}",
                metadata={"task_id": task.id, "agent_role": agent_role.value},
            )
            self.logging_system.log_agent_activity(
                agent_id=f"{agent_role.value}-1",
                activity=completion_activity,
            )
            
            return output
            
        except Exception as e:
            # Log error
            error_activity = Activity(
                activity_type=ActivityType.ERROR,
                description=f"Error executing task: {str(e)}",
                metadata={"task_id": task.id, "agent_role": agent_role.value},
            )
            self.logging_system.log_agent_activity(
                agent_id=f"{agent_role.value}-1",
                activity=error_activity,
            )
            raise

    def handle_validation_failure(
        self,
        phase: WorkflowPhase,
        errors: list[ValidationError],
    ) -> None:
        """Handle validation failure.
        
        Args:
            phase: Phase that failed validation
            errors: Validation errors
        """
        error_messages = [f"{e.code}: {e.message}" for e in errors]
        
        activity = Activity(
            activity_type=ActivityType.VALIDATION,
            description=f"Validation failed in {phase.value}",
            metadata={"errors": error_messages},
        )
        self.logging_system.log_agent_activity(
            agent_id="orchestrator",
            activity=activity,
            reasoning=f"Phase {phase.value} failed validation",
        )

    def get_workflow_status(self, workflow_id: str) -> dict:
        """Get workflow status.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow status information
        """
        state = self.workflow_manager.get_workflow_state(workflow_id)
        if not state:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow_id,
            "status": state.status.value,
            "current_phase": state.current_phase.value,
            "completed_phases": [p.value for p in state.completed_phases],
            "failed_phases": [p.value for p in state.failed_phases],
        }

    def _get_agent(self, role: AgentRole) -> Agent:
        """Get or create agent instance.
        
        Args:
            role: Agent role
            
        Returns:
            Agent instance
        """
        if role not in self.agents:
            # Load template
            template = self.agent_loader.load_agent(role)
            
            # Import and instantiate agent class
            agent_class = self._get_agent_class(role)
            self.agents[role] = agent_class(role, template, self.llm_provider)
        
        return self.agents[role]

    def _get_agent_class(self, role: AgentRole):
        """Get agent class for role.
        
        Args:
            role: Agent role
            
        Returns:
            Agent class
        """
        from multi_agent.agents.product_analyst import ProductAnalystAgent
        from multi_agent.agents.architect import ArchitectAgent
        from multi_agent.agents.developer import DeveloperAgent
        from multi_agent.agents.debugger import DebuggerAgent
        from multi_agent.agents.code_reviewer import CodeReviewerAgent
        
        agent_classes = {
            AgentRole.PRODUCT_ANALYST: ProductAnalystAgent,
            AgentRole.ARCHITECT: ArchitectAgent,
            AgentRole.DEVELOPER: DeveloperAgent,
            AgentRole.DEBUGGER: DebuggerAgent,
            AgentRole.CODE_REVIEWER: CodeReviewerAgent,
        }
        
        return agent_classes.get(role, DeveloperAgent)

    def _get_agent_for_phase(self, phase: WorkflowPhase) -> Optional[AgentRole]:
        """Get agent role for workflow phase.
        
        Args:
            phase: Workflow phase
            
        Returns:
            Agent role or None
        """
        phase_to_agent = {
            WorkflowPhase.ANALYSIS: AgentRole.PRODUCT_ANALYST,
            WorkflowPhase.ARCHITECTURE: AgentRole.ARCHITECT,
            WorkflowPhase.IMPLEMENTATION: AgentRole.DEVELOPER,
            WorkflowPhase.DEBUGGING: AgentRole.DEBUGGER,
            WorkflowPhase.REVIEW: AgentRole.CODE_REVIEWER,
        }
        
        return phase_to_agent.get(phase)
