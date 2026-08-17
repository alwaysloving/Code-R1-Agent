#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

SFT_CKPT="${SFT_CKPT:-${CHECKPOINT_ROOT:?set CHECKPOINT_ROOT}/qwen2.5_3b_kodcode_code_r1_sft}"
if [ ! -f "${SFT_CKPT}/latest_checkpointed_iteration.txt" ]; then
   echo "missing SFT checkpoint: ${SFT_CKPT}" >&2
   exit 1
fi

export LOAD="${LOAD:-${SFT_CKPT}}"
export REF_LOAD="${REF_LOAD:-${SFT_CKPT}}"
export PROMPT_DATA="${PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_grpo_631.jsonl}"
export EVAL_PROMPT_DATA="${EVAL_PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_eval_631.jsonl}"

export CUSTOM_GENERATE_FUNCTION_PATH=generate_with_code.generate
export CUSTOM_RM_PATH=generate_with_code.reward_func
export CUSTOM_ROLLOUT_LOG_FUNCTION_PATH=generate_with_code.log_rollout_data
export CUSTOM_EVAL_ROLLOUT_LOG_FUNCTION_PATH=generate_with_code.log_eval_rollout_data

export APPS_AGENT_ALLOWED_TOOLS="run_public_tests,submit"
export APPS_AGENT_MAX_ACTIONS="${APPS_AGENT_MAX_ACTIONS:-4}"
export CODE_R1_MAX_TURNS="${CODE_R1_MAX_TURNS:-${APPS_AGENT_MAX_ACTIONS}}"
export CODE_R1_RETURN_LOGPROB="${CODE_R1_RETURN_LOGPROB:-1}"
export CODE_R1_OBSERVATION_FIELD_CHARS="${CODE_R1_OBSERVATION_FIELD_CHARS:-200}"
export ROLLOUT_MAX_RESPONSE_LEN="${ROLLOUT_MAX_RESPONSE_LEN:-1536}"

export FINETUNE_FROM_CHECKPOINT=1
export RESET_OPTIMIZER=1
export OVERRIDE_OPT_PARAM_SCHEDULER=1

export ADVANTAGE_ESTIMATOR=grpo
export ROLLOUT_BATCH_SIZE="${ROLLOUT_BATCH_SIZE:-4}"
export N_SAMPLES_PER_PROMPT="${N_SAMPLES_PER_PROMPT:-4}"
export GLOBAL_BATCH_SIZE="${GLOBAL_BATCH_SIZE:-16}"
export OVER_SAMPLING_BATCH_SIZE="${OVER_SAMPLING_BATCH_SIZE:-4}"
export DYNAMIC_SAMPLING_FILTER_PATH="${DYNAMIC_SAMPLING_FILTER_PATH:-slime.rollout.filter_hub.dynamic_sampling_filters.check_reward_nonzero_std}"

export USE_KL_LOSS="${USE_KL_LOSS:-1}"
export KL_LOSS_COEF="${KL_LOSS_COEF:-0.001}"
export KL_COEF="${KL_COEF:-0.0}"
export ENTROPY_COEF="${ENTROPY_COEF:-0.0}"
export DISABLE_GRPO_STD_NORMALIZATION="${DISABLE_GRPO_STD_NORMALIZATION:-0}"
export LR="${LR:-3e-7}"

export APPS_AGENT_REWARD_STYLE=search_r1

# 2400 prompts / rollout_batch_size 4 = 600 rollout steps.
export NUM_ROLLOUT="${NUM_ROLLOUT:-600}"
export EVAL_INTERVAL="${EVAL_INTERVAL:-100}"
export SAVE_INTERVAL="${SAVE_INTERVAL:-100}"
export N_SAMPLES_PER_EVAL_PROMPT="${N_SAMPLES_PER_EVAL_PROMPT:-2}"
export SKIP_EVAL_BEFORE_TRAIN="${SKIP_EVAL_BEFORE_TRAIN:-1}"

export MAX_TOKENS_PER_GPU="${MAX_TOKENS_PER_GPU:-12288}"
export LOG_PROBS_MAX_TOKENS_PER_GPU="${LOG_PROBS_MAX_TOKENS_PER_GPU:-12288}"
export SGLANG_MEM_FRACTION_STATIC="${SGLANG_MEM_FRACTION_STATIC:-0.30}"

export RUN_TAG="${RUN_TAG:-qwen2.5_3b_kodcode_code_r1_grpo_631_full}"
export USE_WANDB="${USE_WANDB:-1}"
export WANDB_PROJECT="${WANDB_PROJECT:-apps-tool-agent}"
export WANDB_GROUP="${WANDB_GROUP:-kodcode-grpo-631}"
export WANDB_EXP_NAME="${WANDB_EXP_NAME:-${RUN_TAG}}"

exec "${SCRIPT_DIR}/run-qwen2.5-3B-tool-agent.sh"
