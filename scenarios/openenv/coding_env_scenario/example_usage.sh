#!/bin/bash

# Example usage of AgentBeats + OpenEnv integration for coding environment

echo "Running AgentBeats agent on OpenEnv coding environment..."

agentbeats run_openenv_eval \
  --agent_card scenarios/openenv/coding_env_scenario/coding_agent_card.toml \
  --env coding_env \
  --num_episodes 5 \
  --model_type openai \
  --model_name gpt-4o-mini \
  --output_dir ./eval_results/coding_env

echo ""
echo "Evaluation complete! Check ./eval_results/coding_env/ for detailed results."
