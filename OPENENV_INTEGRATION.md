# AgentBeats + OpenEnv Integration

This integration combines **AgentBeats** (multi-agent battle platform) with **OpenEnv** (agentic execution environments) to create a comprehensive evaluation harness for AI agents on standardized Python coding tasks and other environments.

## 🎯 Overview

The integration enables AgentBeats agents to be evaluated on OpenEnv's standardized, Docker-based execution environments. This provides:

✅ **Standardized Evaluation** - Use OpenEnv's reproducible environments
✅ **Python Coding Tasks** - Primary focus on coding environment
✅ **Automated Metrics** - Track rewards, success rates, and performance
✅ **Easy CLI** - Simple command-line interface for evaluation
✅ **Extensible** - Support for multiple OpenEnv environment types

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AgentBeats Agent                           │
│  (with tools, instructions, and model)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         OpenEnvAdapter (Integration Layer)              │
│  • Converts A2A to OpenEnv actions                      │
│  • Manages environment lifecycle                        │
│  • Auto-generates tools from env                        │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────┐
│     OpenEnv Environment (Docker Container)              │
│  • coding_env: Python code execution                    │
│  • openspiel_env: Game playing                          │
│  • git_env: Git task completion                         │
└─────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- Python >= 3.11
- Docker (for OpenEnv environments)
- OpenAI API key or other LLM provider

### Setup

1. **Clone and install AgentBeats** (with OpenEnv integration):
   ```bash
   cd /home/hamidnazeri/agentbeats
   git checkout openenv-integration
   pip install -e .
   ```

2. **Install OpenEnv**:
   ```bash
   cd /home/hamidnazeri/OpenEnv
   pip install -e .
   ```

3. **Set API keys**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Build OpenEnv Docker images** (for environments you want to use):
   ```bash
   # For coding environment
   cd /home/hamidnazeri/OpenEnv/src/envs/coding_env/server
   docker build -t coding-env:latest .
   ```

## 🚀 Quick Start

### Basic Evaluation

Run an agent on the coding environment for 5 episodes:

```bash
agentbeats run_openenv_eval \
  --agent_card scenarios/openenv/coding_env_scenario/coding_agent_card.toml \
  --env coding_env \
  --num_episodes 5 \
  --model_type openai \
  --model_name gpt-4o-mini
```

### With Custom Tools

Add your own tools to the agent:

```bash
agentbeats run_openenv_eval \
  --agent_card my_agent.toml \
  --env coding_env \
  --num_episodes 10 \
  --tool my_custom_tools.py \
  --output_dir ./results
```

## 📚 Components

### 1. OpenEnv Adapter (`src/agentbeats/integrations/openenv/`)

The core integration layer that bridges AgentBeats and OpenEnv:

- **`openenv_adapter.py`**: Main adapter class, manages environment connection
- **`openenv_environment.py`**: Environment lifecycle manager (start/stop/reset)
- **`openenv_tools.py`**: Auto-generates AgentBeats tools from environment actions
- **`openenv_evaluator.py`**: Evaluation harness with metrics collection

### 2. Example Scenarios (`scenarios/openenv/`)

Pre-configured scenarios for different environments:

- **`coding_env_scenario/`**: Python coding challenges
  - Agent card optimized for coding tasks
  - Example usage scripts
  - Detailed README

### 3. CLI Command

New `run_openenv_eval` command added to AgentBeats CLI:

```bash
agentbeats run_openenv_eval --help
```

## 🎮 Available Environments

### Coding Environment (Priority)

Python code execution environment for solving programming challenges.

**Tools:**
- `execute_code(code: str)` - Execute Python code
- `reset_environment()` - Start fresh episode
- `get_environment_status()` - Check episode info

**Use Cases:**
- Algorithm implementation
- Code debugging
- Problem solving
- Test writing

**Example:**
```bash
agentbeats run_openenv_eval \
  --agent_card scenarios/openenv/coding_env_scenario/coding_agent_card.toml \
  --env coding_env \
  --num_episodes 10
```

### OpenSpiel Environment (Future)

Game playing environment for strategic games.

**Supported Games:** Tic-tac-toe, Connect4, Chess, Go, etc.

### Git Environment (Future)

Version control task environment.

**Tasks:** Git operations, repository management, etc.

## 📊 Evaluation Metrics

The evaluator automatically tracks:

- **Total Reward**: Cumulative reward across episodes
- **Success Rate**: Percentage of successful episodes
- **Average Steps**: Mean steps per episode
- **Duration**: Total evaluation time
- **Per-Episode Data**: Individual episode results

### Example Output

```json
{
  "env_name": "coding_env",
  "agent_name": "Python Coding Agent",
  "num_episodes": 10,
  "avg_reward": 16.8,
  "avg_steps": 9.2,
  "success_rate": 0.9,
  "total_duration_seconds": 125.4,
  "episodes": [...]
}
```

## 🔧 Advanced Usage

### Python API

Use the integration programmatically:

```python
from agentbeats.integrations.openenv import OpenEnvAdapter, OpenEnvEvaluator

# Create adapter
adapter = OpenEnvAdapter.create_for_coding_env(
    docker_image="coding-env:latest"
)

# Get tools for agent
tools = adapter.get_tools()

# Create evaluator
evaluator = OpenEnvEvaluator(
    adapter=adapter,
    agent_name="My Agent",
    num_episodes=10,
    output_dir="./results"
)

# Run evaluation
results = evaluator.run(agent_runner=my_agent)
print(f"Average reward: {results.avg_reward}")

# Cleanup
adapter.close()
```

### Custom Environment

Extend the integration to support new OpenEnv environments:

1. **Add environment tools** in `openenv_tools.py`:
   ```python
   def create_my_env_tools(env_manager):
       @agentbeats.tool
       def my_action(param: str) -> str:
           """Description of action."""
           # Implementation
           return result

       return [my_action]
   ```

2. **Register in tool creator**:
   ```python
   tool_creators = {
       "my_env": create_my_env_tools,
       ...
   }
   ```

3. **Use it**:
   ```bash
   agentbeats run_openenv_eval --env my_env ...
   ```

## 📁 Project Structure

```
agentbeats/
├── src/agentbeats/
│   ├── integrations/                    # NEW
│   │   └── openenv/
│   │       ├── __init__.py
│   │       ├── openenv_adapter.py       # Adapter layer
│   │       ├── openenv_environment.py   # Env management
│   │       ├── openenv_evaluator.py     # Evaluation harness
│   │       └── openenv_tools.py         # Tool generation
│   └── cli.py                           # MODIFIED: added run_openenv_eval
├── scenarios/
│   └── openenv/                         # NEW
│       └── coding_env_scenario/
│           ├── coding_agent_card.toml
│           ├── README.md
│           └── example_usage.sh
├── environment.yml                      # NEW: conda env
├── requirements-openenv.txt             # NEW: pip requirements
└── OPENENV_INTEGRATION.md               # NEW: this file
```

## 🛠️ Development

### Running Tests

```bash
# TODO: Add unit tests for integration
cd agentbeats
pytest tests/test_openenv_integration/
```

### Adding New Features

1. Create feature branch from `openenv-integration`
2. Implement changes in `src/agentbeats/integrations/openenv/`
3. Add tests and documentation
4. Submit PR

## 🐛 Troubleshooting

### Common Issues

**"Docker container failed to start"**
- Check Docker is running: `docker ps`
- Build the environment image (see Installation)
- Check port availability

**"ModuleNotFoundError: No module named 'envs.coding_env'"**
- Install OpenEnv: `cd /home/hamidnazeri/OpenEnv && pip install -e .`
- Add OpenEnv to PYTHONPATH: `export PYTHONPATH=/home/hamidnazeri/OpenEnv/src:$PYTHONPATH`

**"OPENAI_API_KEY not set"**
- Set API key: `export OPENAI_API_KEY="your-key"`
- Or use different model: `--model_type openrouter`

**"Environment not responding"**
- Check Docker logs: `docker logs <container-id>`
- Verify network connectivity to container
- Try rebuilding the Docker image

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Environment Requirements

Create a conda environment with all dependencies:

```bash
conda env create -f environment.yml
conda activate agentbeats-openenv
```

Or use pip:

```bash
pip install -r requirements-openenv.txt
pip install -e /home/hamidnazeri/agentbeats
pip install -e /home/hamidnazeri/OpenEnv
```

**Key Dependencies:**
- agentbeats
- openenv-core
- docker
- smolagents (for coding_env)
- openai-agents
- fastapi
- pydantic

## 🎯 Use Cases

### 1. Agent Benchmarking

Evaluate different LLMs on coding tasks:

```bash
# Test GPT-4
agentbeats run_openenv_eval --model_name gpt-4 --env coding_env

# Test Claude
agentbeats run_openenv_eval --model_type openrouter \
  --model_name anthropic/claude-3.5-sonnet --env coding_env
```

### 2. Prompt Engineering

Test different agent instructions:

1. Modify agent card instructions
2. Run evaluation
3. Compare results
4. Iterate

### 3. Tool Development

Test custom tools with standardized environments:

```bash
agentbeats run_openenv_eval \
  --env coding_env \
  --tool my_new_tools.py \
  --num_episodes 20
```

### 4. Continuous Evaluation

Integrate into CI/CD:

```yaml
# .github/workflows/eval.yml
- name: Run Agent Evaluation
  run: |
    agentbeats run_openenv_eval \
      --env coding_env \
      --num_episodes 100 \
      --output_dir ./results
```

## 📈 Roadmap

- [x] Core integration layer
- [x] Coding environment support
- [x] CLI command
- [x] Example scenario
- [x] Documentation
- [ ] Unit tests
- [ ] OpenSpiel environment support
- [ ] Git environment support
- [ ] Web UI integration
- [ ] Multi-agent scenarios
- [ ] Leaderboard integration

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the `openenv-integration` branch
2. Make your changes
3. Add tests and documentation
4. Submit a PR

## 📄 License

MIT License (same as AgentBeats)

## 🔗 Resources

- [AgentBeats Repository](https://github.com/agentbeats/agentbeats)
- [OpenEnv Repository](https://github.com/meta-pytorch/OpenEnv)
- [OpenEnv Documentation](https://github.com/meta-pytorch/OpenEnv/blob/main/README.md)
- [AgentBeats Documentation](https://github.com/agentbeats/agentbeats/tree/main/docs)

## 📞 Support

- Open an issue on GitHub
- Check existing documentation
- Review example scenarios

---

**Built with ❤️ to make agent evaluation standardized and reproducible!**
