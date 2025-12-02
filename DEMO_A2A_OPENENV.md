# Demo: How A2A (AgentBeats) Works with OpenEnv

This document demonstrates the complete integration between AgentBeats (A2A) and OpenEnv.

## 🎯 Overview

The integration creates a bridge where:
- **AgentBeats agents** (LLM-powered agents with tools) can execute actions in
- **OpenEnv environments** (standardized Docker-based environments like coding_env)

## 🏗️ Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. AgentBeats Agent (LLM + Agent Card)                 │
│     - GPT-4, Claude, or other LLMs                      │
│     - Configured via TOML agent card                    │
│     - Receives task instructions                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  2. Auto-Generated Tools (@agentbeats.tool)             │
│     ✓ execute_code(code: str)                           │
│     ✓ reset_environment()                               │
│     ✓ get_environment_status()                          │
└──────────────────┬──────────────────────────────────────┘
                   │ Agent calls tools
                   ▼
┌─────────────────────────────────────────────────────────┐
│  3. OpenEnvAdapter (Integration Layer)                  │
│     - Converts tool calls → OpenEnv actions             │
│     - Manages environment lifecycle                     │
│     - Tracks episode state                              │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/gRPC
                   ▼
┌─────────────────────────────────────────────────────────┐
│  4. OpenEnv Environment (Docker Container)              │
│     - coding_env: Python code execution                 │
│     - Returns: observation, reward, done                │
└─────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  5. OpenEnvEvaluator (Metrics Collection)               │
│     - Collects rewards, success rate, steps             │
│     - Saves results to JSON                             │
└─────────────────────────────────────────────────────────┘
```

## 📝 Step-by-Step Demo

### Step 1: Agent Configuration (Agent Card)

The agent is configured via a TOML file that defines its behavior:

```toml
# scenarios/openenv/coding_env_scenario/coding_agent_card.toml
name = "Python Coding Agent"
description = """
You are an expert Python programmer tasked with solving coding challenges.

Your capabilities:
1. Execute Python code using the execute_code() tool
2. Reset the environment if needed using reset_environment()
3. Check environment status using get_environment_status()

Guidelines:
- Write clear, well-commented Python code
- Test your solutions thoroughly
- Handle edge cases appropriately
"""
```

### Step 2: Starting the Evaluation

When you run the CLI command:

```bash
agentbeats run_openenv_eval \
  --agent_card scenarios/openenv/coding_env_scenario/coding_agent_card.toml \
  --env coding_env \
  --num_episodes 5 \
  --model_type openai \
  --model_name gpt-4o-mini
```

**What happens internally:**

1. **OpenEnvAdapter is created** (`openenv_adapter.py:28-66`):
   ```python
   adapter = OpenEnvAdapter(
       env_name="coding_env",
       docker_image="coding-env:latest",
       auto_start=True,
   )
   ```

2. **Docker container starts** (`openenv_environment.py`):
   - Spins up coding_env Docker container
   - Exposes HTTP/gRPC endpoint (e.g., localhost:8080)
   - Environment is ready to receive actions

3. **Tools are auto-generated** (`openenv_tools.py:16-119`):
   ```python
   @agentbeats.tool
   def execute_code(code: str) -> str:
       """Execute Python code in the coding environment."""
       action = CodeAction(code=code)
       result = env_manager.step(action)
       return format_result(result)
   ```

### Step 3: Agent Receives a Task

Let's say the coding_env gives this task:

```
Task: Write a function to calculate the nth Fibonacci number.
```

### Step 4: Agent Reasoning & Tool Usage

**Agent's thought process** (via LLM):

```
I need to solve this Fibonacci problem. Let me:
1. First understand the problem
2. Write a solution
3. Test it
4. Submit the result

I'll use the execute_code tool to run Python code.
```

**Agent calls the tool:**

```json
{
  "tool": "execute_code",
  "arguments": {
    "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# Test\nprint(fibonacci(10))"
  }
}
```

### Step 5: Tool Execution Flow

**Inside `execute_code()` tool** (`openenv_tools.py:27-70`):

```python
def execute_code(code: str) -> str:
    # 1. Import OpenEnv action type
    from envs.coding_env import CodeAction

    # 2. Create action object
    action = CodeAction(code=code)

    # 3. Send to OpenEnv via env_manager
    result = env_manager.step(action)

    # 4. Parse response
    obs = result["observation"]
    response = f"Execution completed.\n"
    response += f"Output:\n{obs.output}\n"
    response += f"Reward: {result['reward']}\n"

    return response
```

**OpenEnv returns:**

```python
{
    "observation": {
        "output": "55\n",
        "error": "",
        "success": True
    },
    "reward": 10.0,
    "done": True
}
```

### Step 6: Agent Receives Result

The tool returns to the agent:

```
Execution completed.
Output:
55

Reward: 10.0
Episode completed.
```

### Step 7: Metrics Collection

**OpenEnvEvaluator** tracks this episode (`openenv_evaluator.py:130-200`):

```python
episode_result = EpisodeResult(
    episode_id="ep_001",
    total_reward=10.0,
    step_count=1,
    success=True,
    duration_seconds=2.3
)
```

### Step 8: Multiple Episodes

This repeats for `num_episodes=5`:

```
Episode 1: ✓ Reward=10.0, Steps=1, Duration=2.3s
Episode 2: ✓ Reward=10.0, Steps=2, Duration=3.1s
Episode 3: ✓ Reward=8.0,  Steps=3, Duration=4.2s
Episode 4: ✓ Reward=10.0, Steps=1, Duration=2.1s
Episode 5: ✓ Reward=9.0,  Steps=2, Duration=2.8s

===============================================
Average Reward: 9.4
Average Steps: 1.8
Success Rate: 100%
Total Duration: 14.5s
===============================================
```

### Step 9: Results Saved

Results are saved to JSON (`eval_results/coding_env/results.json`):

```json
{
  "env_name": "coding_env",
  "agent_name": "Python Coding Agent",
  "num_episodes": 5,
  "avg_reward": 9.4,
  "avg_steps": 1.8,
  "success_rate": 1.0,
  "total_duration_seconds": 14.5,
  "episodes": [
    {
      "episode_id": "ep_001",
      "total_reward": 10.0,
      "step_count": 1,
      "success": true,
      "duration_seconds": 2.3
    },
    ...
  ]
}
```

## 🔍 Key Integration Points

### 1. Tool Auto-Generation

**From** OpenEnv action types **To** AgentBeats tools:

```python
# OpenEnv defines:
class CodeAction:
    code: str

# AgentBeats creates:
@agentbeats.tool
def execute_code(code: str) -> str:
    action = CodeAction(code=code)
    return env_manager.step(action)
```

### 2. Action Mapping

| Agent Tool Call | OpenEnv Action | Environment Response |
|----------------|----------------|---------------------|
| `execute_code("print('hi')")` | `CodeAction(code="print('hi')")` | `{output: "hi\n", reward: 5}` |
| `reset_environment()` | `env.reset()` | `{observation: {...}, episode_id: "ep_002"}` |
| `get_environment_status()` | `env.get_state()` | `{step_count: 3, reward: 15}` |

### 3. Episode Lifecycle

```python
# Start episode
adapter.reset()  # → OpenEnv: start new episode

# Agent takes actions
for step in range(max_steps):
    agent.run()  # → calls tools → OpenEnv actions
    if done:
        break

# Collect metrics
evaluator.save_results()
```

## 🎮 Interactive Example

Let's simulate a complete interaction:

```
╔════════════════════════════════════════════════════════╗
║ EPISODE 1: Fibonacci Problem                          ║
╚════════════════════════════════════════════════════════╝

[OpenEnv] Task: Write a function for fibonacci(n)

[Agent] Received task. Let me solve this...
[Agent] Calling: execute_code(code="def fibonacci(n):\n...")

[OpenEnvAdapter] Converting to CodeAction...
[OpenEnv Docker] Executing code in sandbox...
[OpenEnv Docker] Output: 55, Error: None, Success: True
[OpenEnvAdapter] Returning result to agent...

[Agent] Received: "Execution completed. Output: 55\nReward: 10.0"
[Agent] Success! Task completed.

[Evaluator] Episode 1 complete:
            Reward: 10.0
            Steps: 1
            Duration: 2.3s
            Success: ✓
```

## 📊 What Makes This Integration Powerful?

### 1. **Seamless Tool Integration**
- OpenEnv actions automatically become AgentBeats tools
- No manual tool writing needed
- Type-safe conversion

### 2. **Standardized Evaluation**
- Consistent Docker environments
- Reproducible results
- Fair agent comparison

### 3. **Rich Metrics**
- Track rewards, success rates, steps
- Compare across models (GPT-4 vs Claude)
- Analyze performance over time

### 4. **Extensible Architecture**
- Support multiple environments (coding, games, git)
- Add custom tools easily
- Integrate with other frameworks

## 🚀 Use Cases

### 1. Benchmark LLMs on Coding Tasks

```bash
# Test GPT-4
agentbeats run_openenv_eval --model_name gpt-4 --env coding_env

# Test Claude
agentbeats run_openenv_eval --model_type openrouter \
  --model_name anthropic/claude-3.5-sonnet --env coding_env
```

### 2. Prompt Engineering

Iterate on agent instructions in the agent card and measure impact on success rate.

### 3. Tool Development

Test new tools in standardized environments:

```bash
agentbeats run_openenv_eval \
  --env coding_env \
  --tool my_custom_tools.py \
  --num_episodes 100
```

### 4. Continuous Evaluation (CI/CD)

```yaml
# .github/workflows/eval.yml
- name: Run Agent Evaluation
  run: |
    agentbeats run_openenv_eval \
      --env coding_env \
      --num_episodes 100 \
      --output_dir ./results

    # Check success rate
    python check_metrics.py --threshold 0.8
```

## 🎯 Summary

**How A2A works with OpenEnv:**

1. ✅ **Agent** (LLM + instructions) receives tasks
2. ✅ **Tools** (auto-generated from OpenEnv) are available to agent
3. ✅ **Adapter** converts tool calls → OpenEnv actions
4. ✅ **Environment** (Docker) executes actions, returns observations
5. ✅ **Evaluator** collects metrics across episodes
6. ✅ **Results** saved for analysis

**Key Benefits:**

- 🔄 **Automated**: Tools generated automatically
- 🎯 **Standardized**: Reproducible environments
- 📊 **Measurable**: Rich metrics collection
- 🔧 **Extensible**: Easy to add new environments
- 🚀 **Production-ready**: CLI + Python API

---

**Files to Review:**

- Architecture: `src/agentbeats/integrations/openenv/openenv_adapter.py`
- Tool Generation: `src/agentbeats/integrations/openenv/openenv_tools.py`
- Evaluation: `src/agentbeats/integrations/openenv/openenv_evaluator.py`
- Example: `scenarios/openenv/coding_env_scenario/coding_agent_card.toml`
- Documentation: `OPENENV_INTEGRATION.md`
