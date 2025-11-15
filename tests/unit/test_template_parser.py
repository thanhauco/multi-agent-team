"""Tests for agent template parser."""

import pytest
import tempfile
from pathlib import Path

from multi_agent.agents.template_parser import TemplateParser, AgentTemplate


SAMPLE_TEMPLATE = """# Agent Role: Developer

## Responsibilities
- Write clean, maintainable code
- Follow coding standards
- Implement features according to specifications

## Constraints
- Must write tests for all code
- Must follow architecture patterns
- Must document all public APIs

## System Prompt
You are an expert Developer agent. Your role is to write high-quality code.

When implementing features:
1. Follow the architecture design
2. Write clean, readable code
3. Include appropriate tests

Project type: {{project_type}}
Language: {{language}}

## Input Format
- Task description
- Requirements
- Architecture design

## Output Format
- Source code files
- Test files
- Documentation

## Validation Rules
- Code must pass linting
- All tests must pass
- Code coverage must be > 80%
"""


def test_parse_content():
    """Test parsing template content."""
    parser = TemplateParser()
    template = parser.parse_content(SAMPLE_TEMPLATE)
    
    assert template.role_name == "Developer"
    assert len(template.responsibilities) == 3
    assert "Write clean, maintainable code" in template.responsibilities
    assert len(template.constraints) == 3
    assert "You are an expert Developer agent" in template.system_prompt


def test_parse_file():
    """Test parsing template from file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(SAMPLE_TEMPLATE)
        filepath = Path(f.name)
    
    try:
        parser = TemplateParser()
        template = parser.parse_file(filepath)
        
        assert template.role_name == "Developer"
        assert len(template.responsibilities) > 0
    finally:
        filepath.unlink()


def test_extract_role_name():
    """Test role name extraction."""
    parser = TemplateParser()
    
    content1 = "# Agent Role: Architect"
    assert parser._extract_role_name(content1) == "Architect"
    
    content2 = "# My Custom Agent"
    assert parser._extract_role_name(content2) == "My Custom Agent"


def test_extract_list_items():
    """Test list item extraction."""
    parser = TemplateParser()
    
    content = """
- Item 1
- Item 2
* Item 3
  - Nested item
"""
    items = parser._extract_list_items(content)
    assert len(items) >= 3
    assert "Item 1" in items
    assert "Item 2" in items


def test_extract_variables():
    """Test variable extraction."""
    parser = TemplateParser()
    
    content = """
project_type: web_application
language: python
framework: fastapi
"""
    variables = parser._extract_variables(content)
    assert variables["project_type"] == "web_application"
    assert variables["language"] == "python"
    assert variables["framework"] == "fastapi"


def test_substitute_variables():
    """Test variable substitution."""
    parser = TemplateParser()
    template = parser.parse_content(SAMPLE_TEMPLATE)
    
    variables = {
        "project_type": "web_application",
        "language": "Python"
    }
    
    substituted = parser.substitute_variables(template, variables)
    
    assert "web_application" in substituted.system_prompt
    assert "Python" in substituted.system_prompt
    assert "{{project_type}}" not in substituted.system_prompt


def test_validate_template_valid():
    """Test validation of valid template."""
    parser = TemplateParser()
    template = parser.parse_content(SAMPLE_TEMPLATE)
    
    errors = parser.validate_template(template)
    assert len(errors) == 0


def test_validate_template_missing_fields():
    """Test validation of incomplete template."""
    parser = TemplateParser()
    
    # Template with missing fields
    incomplete_template = AgentTemplate(
        role_name="",
        system_prompt="",
        responsibilities=[],
    )
    
    errors = parser.validate_template(incomplete_template)
    assert len(errors) > 0
    assert any("role name" in e.lower() for e in errors)
    assert any("system prompt" in e.lower() for e in errors)


def test_split_sections():
    """Test section splitting."""
    parser = TemplateParser()
    
    content = """
# Title

## Section 1
Content 1

## Section 2
Content 2
More content

## Section 3
Content 3
"""
    sections = parser._split_sections(content)
    assert "Section 1" in sections
    assert "Section 2" in sections
    assert "Section 3" in sections
    assert "Content 1" in sections["Section 1"]


def test_parse_minimal_template():
    """Test parsing minimal template."""
    minimal = """# Agent Role: Minimal

## System Prompt
Basic prompt

## Responsibilities
- Do something
"""
    parser = TemplateParser()
    template = parser.parse_content(minimal)
    
    assert template.role_name == "Minimal"
    assert template.system_prompt == "Basic prompt"
    assert len(template.responsibilities) == 1
