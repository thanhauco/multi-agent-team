"""Developer agent implementation."""

from multi_agent.agents.base_agent import Agent
from multi_agent.context.models import Context
from multi_agent.core.models import AgentOutput, Artifact, ArtifactType, Task, ValidationStatus


class DeveloperAgent(Agent):
    """Agent for code implementation."""

    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute code implementation task.
        
        Args:
            task: Task to execute
            context: Context from previous agents
            
        Returns:
            Agent output with code implementation
        """
        prompt = self.format_prompt(task, context)
        
        implementation_prompt = f"""{prompt}

Please implement the required functionality with:

1. **Clean Code**: Well-structured, readable code following best practices
2. **Error Handling**: Proper exception handling and error messages
3. **Documentation**: Docstrings and comments for complex logic
4. **Type Hints**: Use type annotations where applicable
5. **Tests**: Unit tests for the implemented functionality

Provide the code in clearly marked code blocks with file paths."""
        
        content = self.llm.generate(implementation_prompt)
        
        # Extract code artifacts from response
        artifacts = self._extract_code_artifacts(content)
        
        output = self._create_output(
            task_id=task.id,
            content=content,
            validation_status=ValidationStatus.PENDING,
        )
        output.artifacts = artifacts
        
        return output

    def _extract_code_artifacts(self, content: str) -> list[Artifact]:
        """Extract code artifacts from generated content.
        
        Args:
            content: Generated content
            
        Returns:
            List of code artifacts
        """
        artifacts = []
        
        # Simple extraction - look for code blocks
        # In production, this would be more sophisticated
        import re
        
        # Match code blocks with optional file paths
        pattern = r'```(?:python|javascript|typescript|java|go)?\s*(?:#\s*(.+?))?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for filepath, code in matches:
            if code.strip():
                artifact = Artifact(
                    type=ArtifactType.CODE,
                    path=filepath.strip() if filepath else "generated_code.py",
                    content=code.strip(),
                )
                artifacts.append(artifact)
        
        return artifacts
