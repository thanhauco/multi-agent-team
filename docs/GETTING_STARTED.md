# Getting Started with Multi-Agent Development System

## Installation

```bash
# Clone the repository
git clone https://github.com/thanhauco/multi-agent-team.git
cd multi-agent-team

# Install dependencies
pip install -r requirements.txt

# Or install with pip
pip install -e .
```

## Configuration

1. Set up your API keys:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
# or
export OPENAI_API_KEY="your-api-key-here"
```

2. Configure the system (optional):

Edit `config/system_config.yaml` and `config/llm_config.yaml` to customize settings.

## Quick Start

### Using the CLI

```bash
# Start a workflow
multi-agent start

# Check workflow status
multi-agent status <workflow-id>

# View logs
multi-agent logs --limit 20
```

### Using Python API

```python
from multi_agent.core.models import WorkflowConfig, WorkflowPhase
from multi_agent.integrations.claude_provider import ClaudeProvider
from multi_agent.orchestration.orchestrator import AgentOrchestrator

# Initialize
llm_provider = ClaudeProvider(api_key="your-key")
orchestrator = AgentOrchestrator(llm_provider=llm_provider)

# Create workflow
config = WorkflowConfig(
    name="My Workflow",
    phases=[WorkflowPhase.ANALYSIS, WorkflowPhase.ARCHITECTURE],
)

# Execute
workflow_id = orchestrator.execute_workflow(config)
```

## Next Steps

- Read the [Architecture Guide](ARCHITECTURE.md)
- Explore [Examples](../examples/)
- Customize [Agent Templates](../agents/templates/)
