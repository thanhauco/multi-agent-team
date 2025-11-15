"""Architect agent implementation."""

from multi_agent.agents.base_agent import Agent
from multi_agent.context.models import Context
from multi_agent.core.models import AgentOutput, Task, ValidationResult, ValidationStatus


class ArchitectAgent(Agent):
    """Agent for system architecture design and validation."""

    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute architecture design task.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Agent output with architecture design
        """
        prompt = self.format_prompt(task, context)
        
        architecture_prompt = f"""{prompt}

Please provide a comprehensive architecture design including:

1. **System Overview**: High-level architecture description
2. **Component Design**: Detailed component specifications
3. **Data Flow**: How data moves through the system
4. **API Contracts**: Interface definitions between components
5. **Design Patterns**: Architectural patterns being used
6. **Technology Stack**: Recommended technologies and frameworks
7. **Scalability Considerations**: How the system will scale
8. **Security Considerations**: Security measures and best practices

Include diagrams where appropriate (using Mermaid syntax or ASCII art)."""
        
        content = self.llm.generate(architecture_prompt)
        
        output = self._create_output(
            task_id=task.id,
            content=content,
            validation_status=ValidationStatus.PENDING,
        )
        
        return output

    def validate_output(self, output: AgentOutput) -> ValidationResult:
        """Validate architecture design output.
        
        Args:
            output: Output to validate
            
        Returns:
            Validation result
        """
        result = super().validate_output(output)
        
        if not result.is_valid:
            return result
        
        content = output.content.lower()
        
        # Check for required architecture elements
        required_elements = [
            ("component", "Component design"),
            ("api", "API specifications"),
            ("security", "Security considerations"),
        ]
        
        for keyword, element_name in required_elements:
            if keyword not in content:
                result.warnings.append(f"Missing or unclear {element_name}")
        
        # Check for design patterns
        if "pattern" not in content:
            result.warnings.append("No design patterns mentioned")
        
        return result
