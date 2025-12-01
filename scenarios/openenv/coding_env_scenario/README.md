# OpenEnv Coding Environment Scenario

This scenario demonstrates how to evaluate an AgentBeats agent on the OpenEnv coding environment for Python programming tasks.

## Overview

The coding environment provides a sandboxed Python execution environment where agents can:
- Execute Python code
- Receive output, errors, and rewards
- Complete coding challenges

## Files

- `coding_agent_card.toml` - Agent card configured for coding tasks
- `README.md` - This file
- `example_usage.sh` - Example command to run evaluation

## Prerequisites

1. **AgentBeats installed** with OpenEnv integration:
   ```bash
   cd /home/hamidnazeri/agentbeats
   pip install -e .
   ```

2. **OpenEnv installed**:
   ```bash
   cd /home/hamidnazeri/OpenEnv
   pip install -e .
   ```

3. **Docker running** (for OpenEnv environment containers)

4. **OpenAI API key** set:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

## Quick Start

### 1. Run Evaluation

```bash
cd /home/hamidnazeri/agentbeats

agentbeats run_openenv_eval \
  --agent_card scenarios/openenv/coding_env_scenario/coding_agent_card.toml \
  --env coding_env \
  --num_episodes 5 \
  --model_type openai \
  --model_name gpt-4o-mini \
  --output_dir ./eval_results/coding_env
```

### 2. View Results

Results will be saved to `./eval_results/coding_env/` as JSON files with metrics like:
- Average reward per episode
- Success rate
- Steps per episode
- Total duration

## What the Agent Can Do

The agent has access to these tools:

### 1. `execute_code(code: str)`
Execute Python code in the environment.

**Example:**
```python
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
```

### 2. `reset_environment()`
Reset the environment to start fresh (clears all previous state).

### 3. `get_environment_status()`
Get current episode information (episode ID, step count, total reward).

## Customization

### Modify Agent Instructions

Edit `coding_agent_card.toml` to change:
- Agent personality and approach
- Skills and capabilities
- Problem-solving strategy

### Add Custom Tools

Create a `custom_tools.py` file:

```python
import agentbeats

@agentbeats.tool
def search_documentation(query: str) -> str:
    """Search Python documentation for help."""
    # Your implementation
    return result
```

Then run with:
```bash
agentbeats run_openenv_eval \
  --agent_card coding_agent_card.toml \
  --env coding_env \
  --tool custom_tools.py
```

## Evaluation Metrics

The evaluation tracks:
- **Total Reward**: Cumulative reward across all episodes
- **Success Rate**: Percentage of episodes completed successfully
- **Average Steps**: Mean number of steps per episode
- **Duration**: Time taken for evaluation

## Docker Image

The default Docker image is `coding-env:latest`. To build it:

```bash
cd /home/hamidnazeri/OpenEnv/src/envs/coding_env/server
docker build -t coding-env:latest .
```

Or use a remote image:
```bash
agentbeats run_openenv_eval \
  --env coding_env \
  --docker_image your-registry/coding-env:v1.0 \
  ...
```

## Troubleshooting

### Docker Container Fails to Start

1. Check Docker is running: `docker ps`
2. Check image exists: `docker images | grep coding-env`
3. Build image if missing (see above)

### Import Errors

Make sure both AgentBeats and OpenEnv are installed:
```bash
python -c "import agentbeats; import envs.coding_env; print('OK')"
```

### API Key Issues

Verify API key is set:
```bash
echo $OPENAI_API_KEY
```

## Example Output

```
============================================================
AgentBeats + OpenEnv Evaluation
============================================================

Agent Card: scenarios/openenv/coding_env_scenario/coding_agent_card.toml
Environment: coding_env
Docker Image: coding-env:latest
Episodes: 5
Model: openai/gpt-4o-mini
Output Dir: ./eval_results/coding_env

Initializing OpenEnv environment...
Loading custom tools...
Loaded 3 OpenEnv environment tools

Creating agent...
Agent configured successfully!

============================================================
Starting Evaluation...
============================================================

Episode 1/5: ✓ Reward=15.20, Steps=8, Duration=12.3s
Episode 2/5: ✓ Reward=18.50, Steps=10, Duration=15.1s
...

============================================================
Evaluation Results: Python Coding Agent on coding_env
============================================================
Episodes: 5
Average Reward: 16.80
Average Steps: 9.2
Success Rate: 100.0%
Total Duration: 65.3s
============================================================
```

## Next Steps

1. Try different coding challenges
2. Experiment with different models (gpt-4, claude, etc.)
3. Add custom tools for specific tasks
4. Integrate with CI/CD for continuous evaluation
5. Compare different agent strategies

## Resources

- [AgentBeats Documentation](https://github.com/agentbeats/agentbeats)
- [OpenEnv Documentation](https://github.com/meta-pytorch/OpenEnv)
- [OpenEnv Coding Environment](https://github.com/meta-pytorch/OpenEnv/tree/main/src/envs/coding_env)
