"""Agent template parser for markdown configuration files."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentTemplate:
    """Parsed agent template configuration."""

    role_name: str
    responsibilities: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    system_prompt: str = ""
    input_format: str = ""
    output_format: str = ""
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)


class TemplateParser:
    """Parses markdown agent template files."""

    def __init__(self):
        """Initialize template parser."""
        self.section_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)
        self.list_item_pattern = re.compile(r'^\s*[-*]\s+(.+)$', re.MULTILINE)
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')

    def parse_file(self, filepath: Path) -> AgentTemplate:
        """Parse an agent template file.
        
        Args:
            filepath: Path to template file
            
        Returns:
            Parsed AgentTemplate
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)

    def parse_content(self, content: str) -> AgentTemplate:
        """Parse template content.
        
        Args:
            content: Template markdown content
            
        Returns:
            Parsed AgentTemplate
        """
        # Extract role name from title
        role_name = self._extract_role_name(content)
        
        # Split content into sections
        sections = self._split_sections(content)
        
        # Parse each section
        template = AgentTemplate(role_name=role_name)
        
        for section_name, section_content in sections.items():
            section_lower = section_name.lower()
            
            if 'responsibilit' in section_lower:
                template.responsibilities = self._extract_list_items(section_content)
            elif 'constraint' in section_lower:
                template.constraints = self._extract_list_items(section_content)
            elif 'system prompt' in section_lower:
                template.system_prompt = section_content.strip()
            elif 'input format' in section_lower:
                template.input_format = section_content.strip()
            elif 'output format' in section_lower:
                template.output_format = section_content.strip()
            elif 'validation' in section_lower:
                template.validation_rules = self._extract_list_items(section_content)
            elif 'metadata' in section_lower or 'variable' in section_lower:
                template.variables = self._extract_variables(section_content)
        
        return template

    def _extract_role_name(self, content: str) -> str:
        """Extract role name from template.
        
        Args:
            content: Template content
            
        Returns:
            Role name
        """
        # Look for "Agent Role: Name" pattern
        match = re.search(r'#\s+Agent Role:\s*(.+)', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Fallback to first heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return "Unknown"

    def _split_sections(self, content: str) -> Dict[str, str]:
        """Split content into sections by headings.
        
        Args:
            content: Template content
            
        Returns:
            Dictionary of section name to content
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            # Check if line is a section heading (##)
            match = re.match(r'^##\s+(.+)$', line)
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _extract_list_items(self, content: str) -> List[str]:
        """Extract list items from content.
        
        Args:
            content: Section content
            
        Returns:
            List of items
        """
        items = []
        for match in self.list_item_pattern.finditer(content):
            item = match.group(1).strip()
            if item:
                items.append(item)
        return items

    def _extract_variables(self, content: str) -> Dict[str, str]:
        """Extract variables from content.
        
        Args:
            content: Section content
            
        Returns:
            Dictionary of variable name to value
        """
        variables = {}
        # Look for key: value pairs
        for line in content.split('\n'):
            match = re.match(r'^\s*-?\s*(\w+):\s*(.+)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                variables[key] = value
        return variables

    def substitute_variables(
        self,
        template: AgentTemplate,
        variables: Dict[str, str],
    ) -> AgentTemplate:
        """Substitute variables in template.
        
        Args:
            template: Agent template
            variables: Variables to substitute
            
        Returns:
            Template with substituted variables
        """
        # Merge template variables with provided variables
        all_vars = {**template.variables, **variables}
        
        # Substitute in system prompt
        system_prompt = template.system_prompt
        for var_name, var_value in all_vars.items():
            pattern = f'{{{{{var_name}}}}}'
            system_prompt = system_prompt.replace(pattern, var_value)
        
        # Create new template with substituted values
        return AgentTemplate(
            role_name=template.role_name,
            responsibilities=template.responsibilities,
            constraints=template.constraints,
            system_prompt=system_prompt,
            input_format=template.input_format,
            output_format=template.output_format,
            validation_rules=template.validation_rules,
            metadata=template.metadata,
            variables=all_vars,
        )

    def validate_template(self, template: AgentTemplate) -> List[str]:
        """Validate template completeness.
        
        Args:
            template: Agent template to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not template.role_name or template.role_name == "Unknown":
            errors.append("Template missing role name")
        
        if not template.system_prompt:
            errors.append("Template missing system prompt")
        
        if not template.responsibilities:
            errors.append("Template missing responsibilities")
        
        return errors
