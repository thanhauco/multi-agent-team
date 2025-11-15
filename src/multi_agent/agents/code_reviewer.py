"""Code Reviewer agent implementation."""

from multi_agent.agents.base_agent import Agent
from multi_agent.context.models import Context
from multi_agent.core.models import AgentOutput, Task, ValidationStatus


class CodeReviewerAgent(Agent):
    """Agent for code quality review and assessment."""

    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute code review task.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Agent output with code review
        """
        prompt = self.format_prompt(task, context)
        
        review_prompt = f"""{prompt}

Please provide a comprehensive code review including:

1. **Code Quality Assessment**:
   - Readability and clarity
   - Code organization and structure
   - Naming conventions
   - Code complexity

2. **Best Practices**:
   - Design patterns usage
   - SOLID principles adherence
   - DRY principle compliance
   - Error handling

3. **Performance**:
   - Potential bottlenecks
   - Resource usage
   - Optimization opportunities

4. **Security**:
   - Security vulnerabilities
   - Input validation
   - Data protection

5. **Testing**:
   - Test coverage
   - Test quality
   - Edge cases

6. **Documentation**:
   - Code comments
   - Docstrings
   - API documentation

7. **Technical Debt**:
   - Code smells
   - Refactoring opportunities
   - Maintenance concerns

Provide specific examples and actionable recommendations."""
        
        content = self.llm.generate(review_prompt)
        
        output = self._create_output(
            task_id=task.id,
            content=content,
            validation_status=ValidationStatus.PENDING,
        )
        
        # Add review metadata
        output.metadata["review_type"] = "comprehensive"
        output.metadata["approval_required"] = True
        
        return output
