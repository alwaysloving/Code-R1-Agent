#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

NAME="${1:?usage: $0 NAME LOAD_PATH [REF_PATH]}"
LOAD_PATH="${2:?usage: $0 NAME LOAD_PATH [REF_PATH]}"
REF_PATH="${3:-${LOAD_PATH}}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="${LOG_FILE:-${REPO_ROOT}/logs/eval-code-r1-${NAME}-${TS}.log}"
mkdir -p "$(dirname -- "${LOG_FILE}")"

env \
  RUN_TAG="eval_code_r1_${NAME}" \
  LOAD="${LOAD_PATH}" \
  REF_LOAD="${REF_PATH}" \
  PROMPT_DATA="${PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_eval_631.jsonl}" \
  EVAL_PROMPT_DATA="${EVAL_PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_eval_631.jsonl}" \
  CUSTOM_GENERATE_FUNCTION_PATH=generate_with_code.generate \
  CUSTOM_RM_PATH=generate_with_code.reward_func \
  CUSTOM_ROLLOUT_LOG_FUNCTION_PATH=generate_with_code.log_rollout_data \
  CUSTOM_EVAL_ROLLOUT_LOG_FUNCTION_PATH=generate_with_code.log_eval_rollout_data \
  APPS_AGENT_ALLOWED_TOOLS=run_public_tests,submit \
  APPS_AGENT_MAX_ACTIONS=4 \
  CODE_R1_MAX_TURNS=4 \
  CODE_R1_RETURN_LOGPROB=1 \
  APPS_AGENT_REWARD_STYLE=search_r1 \
  NUM_ROLLOUT=0 \
  USE_EVAL=1 \
  EVAL_INTERVAL=1 \
  N_SAMPLES_PER_EVAL_PROMPT=4 \
  ROLLOUT_MAX_RESPONSE_LEN=1536 \
  FINETUNE_FROM_CHECKPOINT=1 \
  RESET_OPTIMIZER=1 \
  OVERRIDE_OPT_PARAM_SCHEDULER=1 \
  USE_KL_LOSS=1 \
  KL_LOSS_COEF=0.001 \
  KL_COEF=0.0 \
  ENTROPY_COEF=0.0 \
  LR_DECAY_ITERS=1 \
  USE_WANDB=1 \
  WANDB_PROJECT=apps-tool-agent \
  WANDB_GROUP=code-r1-eval \
  WANDB_EXP_NAME="eval_code_r1_${NAME}" \
  "${SCRIPT_DIR}/run-qwen2.5-3B-tool-agent.sh" >"${LOG_FILE}" 2>&1

echo "${LOG_FILE}"
