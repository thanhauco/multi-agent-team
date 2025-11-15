"""Debugger agent implementation."""

from multi_agent.agents.base_agent import Agent
from multi_agent.context.models import Context
from multi_agent.core.models import AgentOutput, Task, ValidationStatus


class DebuggerAgent(Agent):
    """Agent for code debugging and issue resolution."""

    def __init__(self, *args, **kwargs):
        """Initialize debugger agent."""
        super().__init__(*args, **kwargs)
        self.max_iterations = 3

    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute debugging task.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Agent output with debugging results
        """
        prompt = self.format_prompt(task, context)
        
        debug_prompt = f"""{prompt}

Please analyze the code for issues and provide:

1. **Issue Identification**: List all identified issues with severity levels
2. **Root Cause Analysis**: Explain the root cause of each issue
3. **Proposed Fixes**: Specific code changes to fix each issue
4. **Test Validation**: How to verify the fixes work
5. **Prevention**: Recommendations to prevent similar issues

For each issue, provide:
- Issue type (syntax, logic, runtime, performance, security)
- Severity (critical, high, medium, low)
- Location (file and line number if applicable)
- Fix code with clear before/after examples"""
        
        content = self.llm.generate(debug_prompt)
        
        output = self._create_output(
            task_id=task.id,
            content=content,
            validation_status=ValidationStatus.PENDING,
        )
        
        # Track iteration count
        output.metadata["iteration"] = 1
        output.metadata["max_iterations"] = self.max_iterations
        
        return output
