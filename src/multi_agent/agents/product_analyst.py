"""Product Analyst agent implementation."""

from multi_agent.agents.base_agent import Agent
from multi_agent.context.models import Context
from multi_agent.core.models import AgentOutput, Task, ValidationResult, ValidationStatus


class ProductAnalystAgent(Agent):
    """Agent for product analysis and requirements definition."""

    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute product analysis task.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Agent output with requirements analysis
        """
        # Format prompt with task and context
        prompt = self.format_prompt(task, context)
        
        # Add specific instructions for product analysis
        analysis_prompt = f"""{prompt}

Please provide a comprehensive product analysis including:

1. **Problem Statement**: Clear definition of the problem being solved
2. **User Stories**: User stories in "As a... I want... So that..." format
3. **Success Metrics**: Measurable KPIs and success criteria
4. **Technical Constraints**: Any technical limitations or requirements
5. **Risk Assessment**: Potential risks and mitigation strategies
6. **Acceptance Criteria**: Clear, testable acceptance criteria for each user story

Format your response as a structured document."""
        
        # Generate analysis using LLM
        content = self.llm.generate(analysis_prompt)
        
        # Create output
        output = self._create_output(
            task_id=task.id,
            content=content,
            validation_status=ValidationStatus.PENDING,
        )
        
        return output

    def validate_output(self, output: AgentOutput) -> ValidationResult:
        """Validate product analysis output.
        
        Args:
            output: Output to validate
            
        Returns:
            Validation result
        """
        # Start with base validation
        result = super().validate_output(output)
        
        if not result.is_valid:
            return result
        
        content = output.content.lower()
        
        # Check for required sections
        required_sections = [
            ("user stor", "User stories section"),
            ("success", "Success metrics section"),
            ("acceptance", "Acceptance criteria section"),
        ]
        
        for keyword, section_name in required_sections:
            if keyword not in content:
                result.warnings.append(f"Missing or unclear {section_name}")
        
        # Check for user story format
        if "as a" not in content or "i want" not in content:
            result.warnings.append(
                "User stories may not follow standard format (As a... I want... So that...)"
            )
        
        return result
