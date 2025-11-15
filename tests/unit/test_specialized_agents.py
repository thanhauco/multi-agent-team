"""Tests for specialized agent implementations."""

import pytest
from unittest.mock import Mock

from multi_agent.agents.product_analyst import ProductAnalystAgent
from multi_agent.agents.architect import ArchitectAgent
from multi_agent.agents.developer import DeveloperAgent
from multi_agent.agents.debugger import DebuggerAgent
from multi_agent.agents.code_reviewer import CodeReviewerAgent
from multi_agent.agents.template_parser import AgentTemplate
from multi_agent.context.models import Context
from multi_agent.core.models import AgentRole, Task
from multi_agent.integrations.llm_provider import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def generate(self, prompt: str, config=None) -> str:
        return """# Product Analysis

## User Stories
As a user, I want to login so that I can access my account.

## Success Metrics
- User login success rate > 95%

## Acceptance Criteria
- User can login with email and password
"""

    def generate_structured(self, prompt: str, schema: dict, config=None) -> dict:
        return {"result": "structured"}


def create_test_template(role_name: str) -> AgentTemplate:
    """Create a test template."""
    return AgentTemplate(
        role_name=role_name,
        system_prompt=f"You are a {role_name}",
        responsibilities=["Test responsibility"],
    )


def test_product_analyst_execute():
    """Test ProductAnalystAgent execution."""
    template = create_test_template("Product Analyst")
    llm = MockLLMProvider(api_key="test")
    agent = ProductAnalystAgent(AgentRole.PRODUCT_ANALYST, template, llm)
    
    task = Task(description="Analyze product requirements")
    context = Context()
    
    output = agent.execute(task, context)
    
    assert output.agent_role == AgentRole.PRODUCT_ANALYST
    assert output.task_id == task.id
    assert len(output.content) > 0


def test_product_analyst_validation():
    """Test ProductAnalystAgent output validation."""
    template = create_test_template("Product Analyst")
    llm = MockLLMProvider(api_key="test")
    agent = ProductAnalystAgent(AgentRole.PRODUCT_ANALYST, template, llm)
    
    task = Task(description="Test")
    context = Context()
    output = agent.execute(task, context)
    
    result = agent.validate_output(output)
    assert result.is_valid


def test_architect_execute():
    """Test ArchitectAgent execution."""
    template = create_test_template("Architect")
    llm = MockLLMProvider(api_key="test")
    agent = ArchitectAgent(AgentRole.ARCHITECT, template, llm)
    
    task = Task(description="Design system architecture")
    context = Context()
    
    output = agent.execute(task, context)
    
    assert output.agent_role == AgentRole.ARCHITECT
    assert len(output.content) > 0


def test_developer_execute():
    """Test DeveloperAgent execution."""
    template = create_test_template("Developer")
    llm = MockLLMProvider(api_key="test")
    agent = DeveloperAgent(AgentRole.DEVELOPER, template, llm)
    
    task = Task(description="Implement feature")
    context = Context()
    
    output = agent.execute(task, context)
    
    assert output.agent_role == AgentRole.DEVELOPER
    assert len(output.content) > 0


def test_developer_extract_code_artifacts():
    """Test code artifact extraction."""
    template = create_test_template("Developer")
    llm = MockLLMProvider(api_key="test")
    agent = DeveloperAgent(AgentRole.DEVELOPER, template, llm)
    
    content = """
Here is the code:

```python
# main.py
def hello():
    print("Hello")
```

And another file:

```python
# utils.py
def helper():
    return True
```
"""
    
    artifacts = agent._extract_code_artifacts(content)
    assert len(artifacts) == 2


def test_debugger_execute():
    """Test DebuggerAgent execution."""
    template = create_test_template("Debugger")
    llm = MockLLMProvider(api_key="test")
    agent = DebuggerAgent(AgentRole.DEBUGGER, template, llm)
    
    task = Task(description="Debug code")
    context = Context()
    
    output = agent.execute(task, context)
    
    assert output.agent_role == AgentRole.DEBUGGER
    assert "iteration" in output.metadata
    assert output.metadata["max_iterations"] == 3


def test_code_reviewer_execute():
    """Test CodeReviewerAgent execution."""
    template = create_test_template("Code Reviewer")
    llm = MockLLMProvider(api_key="test")
    agent = CodeReviewerAgent(AgentRole.CODE_REVIEWER, template, llm)
    
    task = Task(description="Review code")
    context = Context()
    
    output = agent.execute(task, context)
    
    assert output.agent_role == AgentRole.CODE_REVIEWER
    assert output.metadata["approval_required"] is True


def test_all_agents_have_unique_roles():
    """Test that all agents have correct roles."""
    template = create_test_template("Test")
    llm = MockLLMProvider(api_key="test")
    
    agents = [
        (ProductAnalystAgent, AgentRole.PRODUCT_ANALYST),
        (ArchitectAgent, AgentRole.ARCHITECT),
        (DeveloperAgent, AgentRole.DEVELOPER),
        (DebuggerAgent, AgentRole.DEBUGGER),
        (CodeReviewerAgent, AgentRole.CODE_REVIEWER),
    ]
    
    for agent_class, expected_role in agents:
        agent = agent_class(expected_role, template, llm)
        assert agent.role == expected_role
