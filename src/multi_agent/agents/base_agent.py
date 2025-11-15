"""Base agent class for all specialized agents."""

from abc import ABC, abstractmethod
from typing import Optional

from multi_agent.agents.template_parser import AgentTemplate
from multi_agent.context.models import Context
from multi_agent.core.models import AgentOutput, AgentRole, Task, ValidationResult, ValidationStatus
from multi_agent.integrations.llm_provider import LLMProvider


class Agent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        role: AgentRole,
        template: AgentTemplate,
        llm_provider: LLMProvider,
    ):
        """Initialize agent.
        
        Args:
            role: Agent role
            template: Agent template configuration
            llm_provider: LLM provider for generation
        """
        self.role = role
        self.template = template
        self.llm = llm_provider

    @abstractmethod
    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute a task with given context.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Agent output
        """
        pass

    def validate_output(self, output: AgentOutput) -> ValidationResult:
        """Validate agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            Validation result
        """
        # Default validation - can be overridden by subclasses
        errors = []
        warnings = []
        
        # Check if output has content
        if not output.content:
            from multi_agent.core.models import ValidationError
            errors.append(
                ValidationError(
                    code="EMPTY_OUTPUT",
                    message="Agent output is empty",
                    severity="error",
                )
            )
        
        # Check if output is too short (likely incomplete)
        if output.content and len(output.content) < 50:
            warnings.append("Output seems very short, may be incomplete")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )

    def format_prompt(self, task: Task, context: Context) -> str:
        """Format prompt for LLM.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Formatted prompt
        """
        # Build context summary
        context_summary = self._build_context_summary(context)
        
        # Build task description
        task_description = self._build_task_description(task)
        
        # Combine with system prompt
        prompt = f"""{self.template.system_prompt}

{context_summary}

{task_description}

Please provide your response following the output format specified in your role."""
        
        return prompt

    def _build_context_summary(self, context: Context) -> str:
        """Build summary of context for prompt.
        
        Args:
            context: Context to summarize
            
        Returns:
            Context summary string
        """
        if not context.entries:
            return "## Context\n\nNo previous context available."
        
        summary_parts = ["## Context from Previous Agents\n"]
        
        for entry in context.get_recent(limit=5):
            summary_parts.append(
                f"\n### {entry.agent_role.value.replace('_', ' ').title()}\n"
            )
            # Truncate long content
            content = entry.output.content
            if len(content) > 1000:
                content = content[:1000] + "...[truncated]"
            summary_parts.append(content)
        
        return "\n".join(summary_parts)

    def _build_task_description(self, task: Task) -> str:
        """Build task description for prompt.
        
        Args:
            task: Task to describe
            
        Returns:
            Task description string
        """
        parts = ["## Current Task\n"]
        
        if task.description:
            parts.append(f"**Description:** {task.description}\n")
        
        if task.requirements:
            parts.append("\n**Requirements:**")
            for req in task.requirements:
                parts.append(f"- {req}")
        
        if task.priority:
            parts.append(f"\n**Priority:** {task.priority.value}")
        
        return "\n".join(parts)

    def _create_output(
        self,
        task_id: str,
        content: str,
        validation_status: ValidationStatus = ValidationStatus.PENDING,
    ) -> AgentOutput:
        """Create agent output.
        
        Args:
            task_id: ID of the task
            content: Output content
            validation_status: Validation status
            
        Returns:
            Agent output
        """
        return AgentOutput(
            agent_role=self.role,
            task_id=task_id,
            content=content,
            validation_status=validation_status,
        )
