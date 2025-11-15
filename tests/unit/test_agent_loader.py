"""Tests for AgentLoader."""

import pytest
import tempfile
from pathlib import Path
import time

from multi_agent.agents.loader import AgentLoader
from multi_agent.core.models import AgentRole


DEVELOPER_TEMPLATE = """# Agent Role: Developer

## Responsibilities
- Write code
- Follow standards

## System Prompt
You are a developer agent.

## Constraints
- Write tests
"""

ARCHITECT_TEMPLATE = """# Agent Role: Architect

## Responsibilities
- Design systems
- Define patterns

## System Prompt
You are an architect agent.
Project: {{project_name}}

## Constraints
- Follow best practices
"""


def test_agent_loader_initialization():
    """Test AgentLoader initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = AgentLoader(templates_dir=Path(tmpdir))
        assert loader.templates_dir == Path(tmpdir)
        assert isinstance(loader.templates, dict)


def test_load_agent():
    """Test loading an agent template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        
        # Create template file
        template_file = templates_dir / "developer.md"
        template_file.write_text(DEVELOPER_TEMPLATE)
        
        loader = AgentLoader(templates_dir=templates_dir)
        
        # Load agent
        template = loader.load_agent(AgentRole.DEVELOPER)
        assert template.role_name == "Developer"
        assert "Write code" in template.responsibilities


def test_load_agent_with_variables():
    """Test loading agent with variable substitution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        
        template_file = templates_dir / "architect.md"
        template_file.write_text(ARCHITECT_TEMPLATE)
        
        loader = AgentLoader(templates_dir=templates_dir)
        
        # Load with variables
        template = loader.load_agent(
            AgentRole.ARCHITECT,
            variables={"project_name": "MyProject"}
        )
        
        assert "MyProject" in template.system_prompt
        assert "{{project_name}}" not in template.system_prompt


def test_load_nonexistent_agent():
    """Test loading agent that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = AgentLoader(templates_dir=Path(tmpdir))
        
        with pytest.raises(ValueError, match="No template found"):
            loader.load_agent(AgentRole.DEVELOPER)


def test_reload_configurations():
    """Test reloading configurations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        
        # Create initial template
        template_file = templates_dir / "developer.md"
        template_file.write_text(DEVELOPER_TEMPLATE)
        
        loader = AgentLoader(templates_dir=templates_dir)
        assert AgentRole.DEVELOPER in loader.templates
        
        # Modify template
        modified_template = DEVELOPER_TEMPLATE.replace("Write code", "Write awesome code")
        template_file.write_text(modified_template)
        
        # Reload
        loader.reload_configurations()
        template = loader.load_agent(AgentRole.DEVELOPER)
        assert "Write awesome code" in template.responsibilities


def test_validate_template():
    """Test template validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        
        # Valid template
        valid_file = templates_dir / "valid.md"
        valid_file.write_text(DEVELOPER_TEMPLATE)
        
        loader = AgentLoader(templates_dir=templates_dir)
        errors = loader.validate_template(valid_file)
        assert len(errors) == 0
        
        # Invalid template
        invalid_file = templates_dir / "invalid.md"
        invalid_file.write_text("# Invalid\n\nNo proper sections")
        
        errors = loader.validate_template(invalid_file)
        assert len(errors) > 0


def test_get_available_roles():
    """Test getting available roles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        
        # Create multiple templates
        (templates_dir / "developer.md").write_text(DEVELOPER_TEMPLATE)
        (templates_dir / "architect.md").write_text(ARCHITECT_TEMPLATE)
        
        loader = AgentLoader(templates_dir=templates_dir)
        roles = loader.get_available_roles()
        
        assert AgentRole.DEVELOPER in roles
        assert AgentRole.ARCHITECT in roles


def test_custom_templates_override():
    """Test that custom templates override defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        default_dir = Path(tmpdir) / "default"
        custom_dir = Path(tmpdir) / "custom"
        default_dir.mkdir()
        custom_dir.mkdir()
        
        # Create default template
        (default_dir / "developer.md").write_text(DEVELOPER_TEMPLATE)
        
        # Create custom template with different content
        custom_template = DEVELOPER_TEMPLATE.replace(
            "You are a developer agent",
            "You are a CUSTOM developer agent"
        )
        (custom_dir / "developer.md").write_text(custom_template)
        
        loader = AgentLoader(
            templates_dir=default_dir,
            custom_templates_dir=custom_dir
        )
        
        template = loader.load_agent(AgentRole.DEVELOPER)
        assert "CUSTOM" in template.system_prompt


def test_role_name_mapping():
    """Test role name mapping."""
    loader = AgentLoader()
    
    # Test various role name formats
    assert loader._map_role_name("Developer") == AgentRole.DEVELOPER
    assert loader._map_role_name("developer") == AgentRole.DEVELOPER
    assert loader._map_role_name("Dev") == AgentRole.DEVELOPER
    assert loader._map_role_name("Architect") == AgentRole.ARCHITECT
    assert loader._map_role_name("Code Reviewer") == AgentRole.CODE_REVIEWER
    assert loader._map_role_name("Data Scientist") == AgentRole.DATA_SCIENTIST


def test_hot_reload_if_changed():
    """Test hot reload detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        template_file = templates_dir / "developer.md"
        template_file.write_text(DEVELOPER_TEMPLATE)
        
        loader = AgentLoader(templates_dir=templates_dir)
        
        # No changes initially
        changed = loader.hot_reload_if_changed()
        assert not changed
        
        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        template_file.write_text(DEVELOPER_TEMPLATE + "\n# Modified")
        
        # Should detect change
        changed = loader.hot_reload_if_changed()
        assert changed


def test_load_templates_with_errors():
    """Test loading templates with errors doesn't crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir)
        
        # Create invalid template
        invalid_file = templates_dir / "invalid.md"
        invalid_file.write_text("# Invalid Template\n\nMissing required sections")
        
        # Should not crash
        loader = AgentLoader(templates_dir=templates_dir)
        
        # Invalid template should not be loaded
        roles = loader.get_available_roles()
        assert len(roles) == 0
