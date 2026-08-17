#!/bin/bash
set -euo pipefail

CONDA_ENV="${CONDA_ENV:?set CONDA_ENV to the slime conda environment}"
SLIME_ROOT="${SLIME_ROOT:?set SLIME_ROOT to the slime checkout}"
MEGATRON_ROOT="${MEGATRON_ROOT:?set MEGATRON_ROOT to the Megatron-LM checkout}"
MODEL_CONFIG="${MODEL_CONFIG:-${SLIME_ROOT}/scripts/models/qwen2.5-3B.sh}"
CHECKPOINT_ROOT="${CHECKPOINT_ROOT:?set CHECKPOINT_ROOT for training outputs}"

PRESERVE_SGLANG=0
case " $* " in
   *" --use-opd "*) PRESERVE_SGLANG=1 ;;
esac

if [ "${SKIP_RAY_CLEANUP:-0}" != "1" ]; then
   if [ "${SKIP_SGLANG_CLEANUP:-0}" != "1" ] && [ "${PRESERVE_SGLANG}" != "1" ]; then
      pkill -9 sglang || true
   fi
   sleep 3
   timeout 30s "${CONDA_ENV}/bin/ray" stop --force || true
   ps -eo pid=,args= | awk '
     /ray::|raylet|gcs_server|ray\/dashboard|ray\/autoscaler|ray-dashboard|dashboard.py|monitor.py|log_monitor.py|ray status/ &&
     !/awk / { print $1 }
   ' | xargs -r kill -9 || true
   sleep 3
fi

set -x

export PYTHONUNBUFFERED=1
export APPS_AGENT_MAX_ACTIONS="${APPS_AGENT_MAX_ACTIONS:-4}"

export CUDA_HOME=${CONDA_ENV}
export LD_LIBRARY_PATH=${CONDA_ENV}/lib:${CONDA_ENV}/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}
export PATH=${CONDA_ENV}/bin:${PATH}

NUM_GPUS=1
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
source "${MODEL_CONFIG}"

HF_CHECKPOINT="${HF_CHECKPOINT:?set HF_CHECKPOINT to the Hugging Face model directory}"
REF_LOAD="${REF_LOAD:?set REF_LOAD to the converted reference checkpoint}"
LOAD="${LOAD:-${REF_LOAD}}"
PROMPT_DATA="${PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_eval_631.jsonl}"
EVAL_PROMPT_DATA="${EVAL_PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_eval_631.jsonl}"
RUN_TAG="${RUN_TAG:-qwen2.5_3b_code_r1}"

CKPT_ARGS=(
   --hf-checkpoint "${HF_CHECKPOINT}"
   --ref-load "${REF_LOAD}"
   --load "${LOAD}"
   --save "${CHECKPOINT_ROOT}/${RUN_TAG}/"
   --save-interval "${SAVE_INTERVAL:-50}"
)

if [ "${FINETUNE_FROM_CHECKPOINT:-1}" = "1" ]; then
   CKPT_ARGS+=(
      --finetune
      --no-load-rng
   )
   if [ "${RESET_OPTIMIZER:-1}" = "1" ]; then
      CKPT_ARGS+=(--no-load-optim)
   fi
fi

ROLLOUT_ARGS=(
   --prompt-data "${PROMPT_DATA}"
   --input-key prompt
   --label-key label
   --metadata-key metadata
   --apply-chat-template
   --rollout-shuffle
   --rollout-batch-size "${ROLLOUT_BATCH_SIZE:-1}"
   --n-samples-per-prompt "${N_SAMPLES_PER_PROMPT:-4}"
   --rollout-max-response-len "${ROLLOUT_MAX_RESPONSE_LEN:-4096}"
   --rollout-temperature 1
   --global-batch-size "${GLOBAL_BATCH_SIZE:-4}"
)
if [ -n "${OVER_SAMPLING_BATCH_SIZE:-}" ]; then
   ROLLOUT_ARGS+=(--over-sampling-batch-size "${OVER_SAMPLING_BATCH_SIZE}")
fi
if [ -n "${DYNAMIC_SAMPLING_FILTER_PATH:-}" ]; then
   ROLLOUT_ARGS+=(--dynamic-sampling-filter-path "${DYNAMIC_SAMPLING_FILTER_PATH}")
fi

if [ -n "${NUM_ROLLOUT:-}" ]; then
   ROLLOUT_ARGS+=(--num-rollout "${NUM_ROLLOUT}")
else
   ROLLOUT_ARGS+=(--num-epoch "${NUM_EPOCH:-1}")
fi

if [ "${USE_EVAL:-1}" = "1" ] && [ -f "${EVAL_PROMPT_DATA}" ]; then
   ROLLOUT_ARGS+=(
      --eval-interval "${EVAL_INTERVAL:-100}"
      --eval-prompt-data apps "${EVAL_PROMPT_DATA}"
      --eval-input-key prompt
      --eval-label-key label
      --n-samples-per-eval-prompt "${N_SAMPLES_PER_EVAL_PROMPT:-4}"
      --eval-max-response-len "${ROLLOUT_MAX_RESPONSE_LEN:-4096}"
   )
   if [ "${SKIP_EVAL_BEFORE_TRAIN:-0}" = "1" ]; then
      ROLLOUT_ARGS+=(--skip-eval-before-train)
   fi
fi

CUSTOM_ARGS=(
   --custom-generate-function-path "${CUSTOM_GENERATE_FUNCTION_PATH:-generate_with_code.generate}"
   --custom-rm-path "${CUSTOM_RM_PATH:-generate_with_code.reward_func}"
   --custom-rollout-log-function-path "${CUSTOM_ROLLOUT_LOG_FUNCTION_PATH:-generate_with_code.log_rollout_data}"
   --custom-eval-rollout-log-function-path "${CUSTOM_EVAL_ROLLOUT_LOG_FUNCTION_PATH:-generate_with_code.log_eval_rollout_data}"
)

PERF_ARGS=(
   --tensor-model-parallel-size 1
   --pipeline-model-parallel-size 1
   --context-parallel-size 1
   --expert-model-parallel-size 1
   --expert-tensor-parallel-size 1
   --recompute-granularity full
   --recompute-method uniform
   --recompute-num-layers 1
   --use-dynamic-batch-size
   --max-tokens-per-gpu "${MAX_TOKENS_PER_GPU:-8192}"
   --log-probs-max-tokens-per-gpu "${LOG_PROBS_MAX_TOKENS_PER_GPU:-8192}"
   --log-probs-chunk-size 512
)

ADVANTAGE_ESTIMATOR="${ADVANTAGE_ESTIMATOR:-grpo}"
RL_ARGS=(
   --advantage-estimator "${ADVANTAGE_ESTIMATOR}"
   --kl-loss-coef "${KL_LOSS_COEF:-0.001}"
   --kl-loss-type low_var_kl
   --kl-coef "${KL_COEF:-0.0}"
   --entropy-coef "${ENTROPY_COEF:-0.0}"
   --eps-clip 0.2
   --eps-clip-high 0.28
)
if [ "${USE_KL_LOSS:-1}" = "1" ] && [ "${KL_LOSS_COEF:-0.001}" != "0" ] && \
   [ "${KL_LOSS_COEF:-0.001}" != "0.0" ]; then
   RL_ARGS+=(--use-kl-loss)
fi
if [ "${DISABLE_GRPO_STD_NORMALIZATION:-0}" = "1" ]; then
   RL_ARGS+=(--disable-grpo-std-normalization)
fi
if [ "${ADVANTAGE_ESTIMATOR}" = "reinforce_plus_plus" ] || \
   [ "${ADVANTAGE_ESTIMATOR}" = "reinforce_plus_plus_baseline" ]; then
   RL_ARGS+=(--normalize-advantages)
fi

OPTIMIZER_ARGS=(
   --optimizer adam
   --lr "${LR:-1e-6}"
   --lr-decay-style constant
   --weight-decay 0.1
   --adam-beta1 0.9
   --adam-beta2 0.98
   --optimizer-cpu-offload
   --optimizer-offload-fraction 1.0
   --overlap-cpu-optimizer-d2h-h2d
   --use-precision-aware-optimizer
)
if [ -n "${LR_DECAY_ITERS:-}" ]; then
   OPTIMIZER_ARGS+=(--lr-decay-iters "${LR_DECAY_ITERS}")
fi
if [ "${OVERRIDE_OPT_PARAM_SCHEDULER:-0}" = "1" ]; then
   OPTIMIZER_ARGS+=(--override-opt-param-scheduler)
fi

LOG_ARGS=(--use-tensorboard --tb-project-name apps-tool-agent --tb-experiment-name "${RUN_TAG}")
if [ "${USE_WANDB:-0}" = "1" ]; then
   LOG_ARGS+=(
      --use-wandb
      --wandb-project "${WANDB_PROJECT:-apps-tool-agent}"
      --wandb-group "${WANDB_GROUP:-${RUN_TAG}}"
      --wandb-exp-name "${WANDB_EXP_NAME:-${RUN_TAG}}"
   )
fi

SGLANG_ARGS=(
   --num-gpus-per-node 1
   --rollout-num-gpus-per-engine 1
   --sglang-mem-fraction-static "${SGLANG_MEM_FRACTION_STATIC:-0.20}"
   --sglang-cuda-graph-max-bs 4
)

MISC_ARGS=(
   --attention-dropout 0.0
   --hidden-dropout 0.0
   --accumulate-allreduce-grads-in-fp32
   --attention-softmax-in-fp32
   --attention-backend flash
)

export MASTER_ADDR=${MASTER_ADDR:-$(hostname -I | awk '{print $1}')}
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,${MASTER_ADDR},${NO_PROXY:-}"
export no_proxy="${NO_PROXY}"
if [ "${SKIP_RAY_START:-0}" != "1" ]; then
   ray start --head --node-ip-address "${MASTER_ADDR}" --num-gpus ${NUM_GPUS} \
      --disable-usage-stats --dashboard-host="${RAY_DASHBOARD_HOST:-127.0.0.1}" --dashboard-port=8265
fi

RUNTIME_ENV_JSON="{
  \"env_vars\": {
    \"PYTHONPATH\": \"${MEGATRON_ROOT}:${SLIME_ROOT}:${REPO_ROOT}/src\",
    \"PATH\": \"${PATH}\",
    \"LD_LIBRARY_PATH\": \"${LD_LIBRARY_PATH}\",
    \"CUDA_HOME\": \"${CUDA_HOME}\",
    \"CUDA_DEVICE_MAX_CONNECTIONS\": \"1\",
    \"APPS_AGENT_MAX_ACTIONS\": \"${APPS_AGENT_MAX_ACTIONS}\",
    \"APPS_AGENT_ALLOWED_TOOLS\": \"${APPS_AGENT_ALLOWED_TOOLS:-}\",
    \"APPS_AGENT_PUBLIC_TEST_COST\": \"${APPS_AGENT_PUBLIC_TEST_COST:-0.0}\",
    \"APPS_AGENT_CUSTOM_TEST_COST\": \"${APPS_AGENT_CUSTOM_TEST_COST:-0.005}\",
    \"APPS_AGENT_INVALID_ACTION_COST\": \"${APPS_AGENT_INVALID_ACTION_COST:-0.05}\",
    \"APPS_AGENT_REPEATED_PUBLIC_TEST_COST\": \"${APPS_AGENT_REPEATED_PUBLIC_TEST_COST:-0.01}\",
    \"APPS_AGENT_NO_VALIDATION_PENALTY\": \"${APPS_AGENT_NO_VALIDATION_PENALTY:-0.02}\",
    \"APPS_AGENT_NO_TEST_SUBMIT_PENALTY\": \"${APPS_AGENT_NO_TEST_SUBMIT_PENALTY:-0.0}\",
    \"APPS_AGENT_RESPONSE_LIMIT_PENALTY\": \"${APPS_AGENT_RESPONSE_LIMIT_PENALTY:-0.0}\",
    \"APPS_AGENT_REPAIR_BONUS\": \"${APPS_AGENT_REPAIR_BONUS:-0.03}\",
    \"APPS_AGENT_REWARD_STYLE\": \"${APPS_AGENT_REWARD_STYLE:-legacy}\",
    \"CODE_R1_MAX_TURNS\": \"${CODE_R1_MAX_TURNS:-${APPS_AGENT_MAX_ACTIONS}}\",
    \"CODE_R1_RETURN_LOGPROB\": \"${CODE_R1_RETURN_LOGPROB:-1}\",
    \"CODE_R1_OBSERVATION_FIELD_CHARS\": \"${CODE_R1_OBSERVATION_FIELD_CHARS:-200}\",
    \"APPS_OPD_TEACHER_TIMEOUT\": \"${APPS_OPD_TEACHER_TIMEOUT:-120}\",
    \"APPS_OPD_TEACHER_RETRIES\": \"${APPS_OPD_TEACHER_RETRIES:-3}\",
    \"APPS_OPD_TEACHER_RETRY_BACKOFF\": \"${APPS_OPD_TEACHER_RETRY_BACKOFF:-2}\",
    \"WANDB_INIT_TIMEOUT\": \"${WANDB_INIT_TIMEOUT:-300}\",
    \"NO_PROXY\": \"${NO_PROXY}\",
    \"no_proxy\": \"${no_proxy}\"
  }
}"

ray job submit --address="http://127.0.0.1:8265" \
   ${RAY_JOB_SUBMIT_ARGS:-} \
   --runtime-env-json="${RUNTIME_ENV_JSON}" \
   -- ${CONDA_ENV}/bin/python "${SLIME_ROOT}/train.py" \
   --actor-num-nodes 1 \
   --actor-num-gpus-per-node ${NUM_GPUS} \
   --colocate \
   ${MODEL_ARGS[@]} \
   ${CKPT_ARGS[@]} \
   ${ROLLOUT_ARGS[@]} \
   ${OPTIMIZER_ARGS[@]} \
   ${RL_ARGS[@]} \
   ${LOG_ARGS[@]} \
   ${PERF_ARGS[@]} \
   ${CUSTOM_ARGS[@]} \
   ${SGLANG_ARGS[@]} \
   ${MISC_ARGS[@]} \
   "$@"
