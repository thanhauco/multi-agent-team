"""Simple workflow example."""

import os
from pathlib import Path

from multi_agent.core.models import WorkflowConfig, WorkflowPhase, AgentRole
from multi_agent.integrations.claude_provider import ClaudeProvider
from multi_agent.orchestration.orchestrator import AgentOrchestrator


def main():
    """Run a simple workflow example."""
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        return
    
    # Initialize LLM provider
    llm_provider = ClaudeProvider(api_key=api_key)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(
        llm_provider=llm_provider,
        storage_path=Path(".multi_agent_example"),
    )
    
    # Create workflow configuration
    workflow_config = WorkflowConfig(
        name="Simple Feature Development",
        phases=[
            WorkflowPhase.ANALYSIS,
            WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.IMPLEMENTATION,
        ],
        agent_roles=[
            AgentRole.PRODUCT_ANALYST,
            AgentRole.ARCHITECT,
            AgentRole.DEVELOPER,
        ],
    )
    
    # Execute workflow
    print("Starting workflow...")
    try:
        workflow_id = orchestrator.execute_workflow(workflow_config)
        print(f"✓ Workflow completed: {workflow_id}")
        
        # Get status
        status = orchestrator.get_workflow_status(workflow_id)
        print(f"Status: {status}")
        
    except Exception as e:
        print(f"✗ Workflow failed: {e}")


if __name__ == "__main__":
    main()
