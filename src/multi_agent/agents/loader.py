"""Agent loader for loading and managing agent configurations."""

from pathlib import Path
from typing import Dict, List, Optional
import time

from multi_agent.agents.template_parser import TemplateParser, AgentTemplate
from multi_agent.core.models import AgentRole


class AgentLoader:
    """Loads and manages agent configurations from templates."""

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        custom_templates_dir: Optional[Path] = None,
    ):
        """Initialize agent loader.
        
        Args:
            templates_dir: Directory containing default templates
            custom_templates_dir: Directory containing custom templates
        """
        self.templates_dir = templates_dir or Path("agents/templates")
        self.custom_templates_dir = custom_templates_dir or Path("agents/custom")
        self.parser = TemplateParser()
        self.templates: Dict[AgentRole, AgentTemplate] = {}
        self.template_mtimes: Dict[Path, float] = {}
        
        # Load templates on initialization
        self._load_all_templates()

    def load_agent(
        self,
        role: AgentRole,
        variables: Optional[Dict[str, str]] = None,
    ) -> AgentTemplate:
        """Load agent template for a role.
        
        Args:
            role: Agent role to load
            variables: Variables to substitute in template
            
        Returns:
            Agent template
        """
        if role not in self.templates:
            raise ValueError(f"No template found for role: {role.value}")
        
        template = self.templates[role]
        
        # Substitute variables if provided
        if variables:
            template = self.parser.substitute_variables(template, variables)
        
        return template

    def reload_configurations(self) -> None:
        """Reload all agent configurations from disk."""
        self._load_all_templates()

    def validate_template(self, template_path: Path) -> List[str]:
        """Validate a template file.
        
        Args:
            template_path: Path to template file
            
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            template = self.parser.parse_file(template_path)
            return self.parser.validate_template(template)
        except Exception as e:
            return [f"Failed to parse template: {str(e)}"]

    def get_available_roles(self) -> List[AgentRole]:
        """Get list of available agent roles.
        
        Returns:
            List of agent roles with loaded templates
        """
        return list(self.templates.keys())

    def _load_all_templates(self) -> None:
        """Load all templates from directories."""
        # Load default templates
        if self.templates_dir.exists():
            self._load_templates_from_dir(self.templates_dir)
        
        # Load custom templates (override defaults)
        if self.custom_templates_dir.exists():
            self._load_templates_from_dir(self.custom_templates_dir)

    def _load_templates_from_dir(self, directory: Path) -> None:
        """Load templates from a directory.
        
        Args:
            directory: Directory to load templates from
        """
        for template_file in directory.glob("*.md"):
            try:
                # Check if file has been modified
                mtime = template_file.stat().st_mtime
                if template_file in self.template_mtimes:
                    if self.template_mtimes[template_file] == mtime:
                        continue  # Skip unchanged files
                
                # Parse template
                template = self.parser.parse_file(template_file)
                
                # Validate template
                errors = self.parser.validate_template(template)
                if errors:
                    print(f"Warning: Template {template_file.name} has errors: {errors}")
                    continue
                
                # Map to agent role
                role = self._map_role_name(template.role_name)
                if role:
                    self.templates[role] = template
                    self.template_mtimes[template_file] = mtime
                
            except Exception as e:
                print(f"Error loading template {template_file.name}: {e}")

    def _map_role_name(self, role_name: str) -> Optional[AgentRole]:
        """Map template role name to AgentRole enum.
        
        Args:
            role_name: Role name from template
            
        Returns:
            AgentRole or None if not found
        """
        role_name_lower = role_name.lower().replace(" ", "_").replace("-", "_")
        
        # Try direct mapping
        for role in AgentRole:
            if role.value == role_name_lower:
                return role
        
        # Try fuzzy matching
        role_mapping = {
            "product_analyst": AgentRole.PRODUCT_ANALYST,
            "product": AgentRole.PRODUCT_ANALYST,
            "analyst": AgentRole.PRODUCT_ANALYST,
            "architect": AgentRole.ARCHITECT,
            "architecture": AgentRole.ARCHITECT,
            "developer": AgentRole.DEVELOPER,
            "dev": AgentRole.DEVELOPER,
            "coder": AgentRole.DEVELOPER,
            "debugger": AgentRole.DEBUGGER,
            "debug": AgentRole.DEBUGGER,
            "code_reviewer": AgentRole.CODE_REVIEWER,
            "reviewer": AgentRole.CODE_REVIEWER,
            "review": AgentRole.CODE_REVIEWER,
            "data_scientist": AgentRole.DATA_SCIENTIST,
            "data": AgentRole.DATA_SCIENTIST,
            "ai_engineer": AgentRole.AI_ENGINEER,
            "ai": AgentRole.AI_ENGINEER,
            "ml_engineer": AgentRole.ML_ENGINEER,
            "ml": AgentRole.ML_ENGINEER,
            "machine_learning": AgentRole.ML_ENGINEER,
        }
        
        return role_mapping.get(role_name_lower)

    def hot_reload_if_changed(self) -> bool:
        """Check for template changes and reload if needed.
        
        Returns:
            True if templates were reloaded, False otherwise
        """
        changed = False
        
        # Check all tracked template files
        for template_file, old_mtime in list(self.template_mtimes.items()):
            if not template_file.exists():
                # File was deleted
                changed = True
                continue
            
            current_mtime = template_file.stat().st_mtime
            if current_mtime != old_mtime:
                changed = True
                break
        
        if changed:
            self.reload_configurations()
            return True
        
        return False
