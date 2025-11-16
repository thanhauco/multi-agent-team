"""CLI interface for multi-agent system."""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: typer and rich not installed. Install with: pip install typer rich")
    sys.exit(1)

from multi_agent.config.loader import ConfigurationLoader
from multi_agent.core.models import WorkflowConfig, WorkflowPhase, AgentRole
from multi_agent.integrations.claude_provider import ClaudeProvider
from multi_agent.orchestration.orchestrator import AgentOrchestrator

app = typer.Typer(help="Multi-Agent Development System CLI")
console = Console()


@app.command()
def start(
    workflow: Optional[str] = typer.Option(None, help="Path to workflow configuration"),
    provider: str = typer.Option("claude", help="LLM provider (claude/openai)"),
):
    """Start a new workflow."""
    console.print("[bold green]Starting Multi-Agent Workflow[/bold green]")
    
    # Load configuration
    config_loader = ConfigurationLoader()
    llm_config = config_loader.load_llm_config()
    
    # Get API key
    provider_config = llm_config["providers"][provider]
    api_key = os.getenv(provider_config["api_key_env"])
    
    if not api_key:
        console.print(f"[bold red]Error: {provider_config['api_key_env']} not set[/bold red]")
        raise typer.Exit(1)
    
    # Initialize LLM provider
    if provider == "claude":
        llm_provider = ClaudeProvider(api_key=api_key)
    else:
        console.print(f"[bold red]Provider {provider} not yet implemented[/bold red]")
        raise typer.Exit(1)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(llm_provider=llm_provider)
    
    # Create workflow config
    workflow_config = WorkflowConfig(
        name="Default Workflow",
        phases=[
            WorkflowPhase.ANALYSIS,
            WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.IMPLEMENTATION,
            WorkflowPhase.DEBUGGING,
            WorkflowPhase.REVIEW,
        ],
        agent_roles=[
            AgentRole.PRODUCT_ANALYST,
            AgentRole.ARCHITECT,
            AgentRole.DEVELOPER,
            AgentRole.DEBUGGER,
            AgentRole.CODE_REVIEWER,
        ],
    )
    
    # Execute workflow
    try:
        workflow_id = orchestrator.execute_workflow(workflow_config)
        console.print(f"[bold green]Workflow completed: {workflow_id}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Workflow failed: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def status(workflow_id: str):
    """Check workflow status."""
    console.print(f"[bold]Workflow Status: {workflow_id}[/bold]")
    
    # Initialize orchestrator
    api_key = os.getenv("ANTHROPIC_API_KEY", "dummy")
    llm_provider = ClaudeProvider(api_key=api_key)
    orchestrator = AgentOrchestrator(llm_provider=llm_provider)
    
    # Get status
    status_info = orchestrator.get_workflow_status(workflow_id)
    
    # Display status
    table = Table(title="Workflow Status")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in status_info.items():
        table.add_row(key, str(value))
    
    console.print(table)


@app.command()
def logs(
    workflow_id: Optional[str] = typer.Option(None, help="Filter by workflow ID"),
    limit: int = typer.Option(10, help="Number of log entries to show"),
):
    """View agent logs."""
    console.print("[bold]Agent Logs[/bold]")
    
    from multi_agent.integrations.logging_system import LoggingSystem
    
    logging_system = LoggingSystem()
    
    # Get recent entries
    entries = logging_system.entries[-limit:]
    
    for entry in entries:
        console.print(f"[{entry.timestamp}] {entry.reasoning}")


if __name__ == "__main__":
    app()
