"""Tests for base Agent class."""

import pytest
from unittest.mock import Mock

from multi_agent.agents.base_agent import Agent
from multi_agent.agents.template_parser import AgentTemplate
from multi_agent.context.models import Context, ContextEntry
from multi_agent.core.models import (
    AgentOutput,
    AgentRole,
    Priority,
    Task,
    ValidationStatus,
)
from multi_agent.integrations.llm_provider import LLMProvider


class ConcreteAgent(Agent):
    """Concrete agent for testing."""

    def execute(self, task: Task, context: Context) -> AgentOutput:
        """Execute task."""
        prompt = self.format_prompt(task, context)
        content = self.llm.generate(prompt)
        return self._create_output(task.id, content)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider."""

    def generate(self, prompt: str, config=None) -> str:
        return "Generated response"

    def generate_structured(self, prompt: str, schema: dict, config=None) -> dict:
        return {"result": "structured"}


def test_agent_initialization():
    """Test agent initialization."""
    template = AgentTemplate(
        role_name="Test Agent",
        system_prompt="You are a test agent",
        responsibilities=["Test things"],
    )
    llm = MockLLMProvider(api_key="test")
    
    agent = ConcreteAgent(
        role=AgentRole.DEVELOPER,
        template=template,
        llm_provider=llm,
    )
    
    assert agent.role == AgentRole.DEVELOPER
    assert agent.template.role_name == "Test Agent"
    assert agent.llm is not None


def test_format_prompt_with_context():
    """Test prompt formatting with context."""
    template = AgentTemplate(
        role_name="Developer",
        system_prompt="You are a developer",
    )
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    # Create context
    context = Context()
    arch_output = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-1",
        content="Architecture design document",
    )
    context.add_entry(ContextEntry(
        agent_role=AgentRole.ARCHITECT,
        output=arch_output,
    ))
    
    # Create task
    task = Task(
        description="Implement feature X",
        requirements=["Req 1", "Req 2"],
        priority=Priority.HIGH,
    )
    
    prompt = agent.format_prompt(task, context)
    
    assert "You are a developer" in prompt
    assert "Implement feature X" in prompt
    assert "Req 1" in prompt
    assert "Architecture design document" in prompt


def test_format_prompt_without_context():
    """Test prompt formatting without context."""
    template = AgentTemplate(
        role_name="Developer",
        system_prompt="You are a developer",
    )
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    task = Task(description="Simple task")
    context = Context()
    
    prompt = agent.format_prompt(task, context)
    
    assert "You are a developer" in prompt
    assert "Simple task" in prompt
    assert "No previous context" in prompt


def test_validate_output_valid():
    """Test output validation with valid output."""
    template = AgentTemplate(role_name="Test", system_prompt="Test")
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-1",
        content="This is a valid output with sufficient content to pass validation.",
    )
    
    result = agent.validate_output(output)
    assert result.is_valid
    assert len(result.errors) == 0


def test_validate_output_empty():
    """Test output validation with empty output."""
    template = AgentTemplate(role_name="Test", system_prompt="Test")
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-1",
        content="",
    )
    
    result = agent.validate_output(output)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("empty" in e.message.lower() for e in result.errors)


def test_validate_output_short():
    """Test output validation with short output."""
    template = AgentTemplate(role_name="Test", system_prompt="Test")
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    output = AgentOutput(
        agent_role=AgentRole.DEVELOPER,
        task_id="task-1",
        content="Short",
    )
    
    result = agent.validate_output(output)
    assert result.is_valid  # Still valid, just has warning
    assert len(result.warnings) > 0


def test_execute_task():
    """Test executing a task."""
    template = AgentTemplate(
        role_name="Developer",
        system_prompt="You are a developer",
    )
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    task = Task(description="Test task")
    context = Context()
    
    output = agent.execute(task, context)
    
    assert output.agent_role == AgentRole.DEVELOPER
    assert output.task_id == task.id
    assert output.content == "Generated response"


def test_create_output():
    """Test creating agent output."""
    template = AgentTemplate(role_name="Test", system_prompt="Test")
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    output = agent._create_output(
        task_id="task-123",
        content="Test content",
        validation_status=ValidationStatus.PASSED,
    )
    
    assert output.agent_role == AgentRole.DEVELOPER
    assert output.task_id == "task-123"
    assert output.content == "Test content"
    assert output.validation_status == ValidationStatus.PASSED


def test_build_context_summary_truncates_long_content():
    """Test that context summary truncates long content."""
    template = AgentTemplate(role_name="Test", system_prompt="Test")
    llm = MockLLMProvider(api_key="test")
    agent = ConcreteAgent(AgentRole.DEVELOPER, template, llm)
    
    # Create context with long content
    context = Context()
    long_content = "x" * 2000
    output = AgentOutput(
        agent_role=AgentRole.ARCHITECT,
        task_id="task-1",
        content=long_content,
    )
    context.add_entry(ContextEntry(agent_role=AgentRole.ARCHITECT, output=output))
    
    summary = agent._build_context_summary(context)
    
    assert "[truncated]" in summary
    assert len(summary) < len(long_content)
