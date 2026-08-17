#!/bin/bash
set -euo pipefail

export PYTHONUNBUFFERED=1
export NO_PROXY=localhost,127.0.0.1,0.0.0.0,${NO_PROXY:-}
export no_proxy=$NO_PROXY
CONDA_ENV="${CONDA_ENV:?set CONDA_ENV to the slime conda environment}"
SLIME_ROOT="${SLIME_ROOT:?set SLIME_ROOT to the slime checkout}"
MEGATRON_ROOT="${MEGATRON_ROOT:?set MEGATRON_ROOT to the Megatron-LM checkout}"
MODEL_CONFIG="${MODEL_CONFIG:-${SLIME_ROOT}/scripts/models/qwen2.5-3B.sh}"
CHECKPOINT_ROOT="${CHECKPOINT_ROOT:?set CHECKPOINT_ROOT for training outputs}"
export PATH=${CONDA_ENV}/bin:${PATH}

ray stop --force || true
pkill -9 -f 'ray::|raylet|gcs_server|ray/dashboard|ray/autoscaler' || true
sleep 3
set -x

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
source "${MODEL_CONFIG}"

HF_CHECKPOINT="${HF_CHECKPOINT:?set HF_CHECKPOINT to the Hugging Face model directory}"
REF_LOAD="${REF_LOAD:?set REF_LOAD to the converted reference checkpoint}"
SFT_DATA="${SFT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_sft.jsonl}"
RUN_TAG="${RUN_TAG:-qwen2.5_3b_code_r1_sft}"

CKPT_ARGS=(
   --hf-checkpoint "${HF_CHECKPOINT}"
   --ref-load "${REF_LOAD}"
   --load "${LOAD:-${REF_LOAD}}"
   --save "${CHECKPOINT_ROOT}/${RUN_TAG}/"
   --save-interval 100
)

SFT_ARGS=(
   --rollout-function-path slime.rollout.sft_rollout.generate_rollout
   --prompt-data "${SFT_DATA}"
   --input-key messages
   --rollout-shuffle
   --num-epoch "${NUM_EPOCH:-1}"
   --rollout-batch-size "${BATCH_SIZE:-4}"
   --global-batch-size "${BATCH_SIZE:-4}"
   --loss-type sft_loss
   --loss-mask-type qwen
   --calculate-per-token-loss
   --disable-compute-advantages-and-returns
   --debug-train-only
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
)

OPTIMIZER_ARGS=(
   --optimizer adam
   --lr "${LR:-5e-6}"
   --lr-decay-style cosine
   --min-lr 1e-6
   --lr-warmup-fraction 0.1
   --weight-decay 0.1
   --adam-beta1 0.9
   --adam-beta2 0.98
   --optimizer-cpu-offload
   --optimizer-offload-fraction 1.0
   --use-precision-aware-optimizer
)

MISC_ARGS=(
   --attention-dropout 0.0
   --hidden-dropout 0.0
   --accumulate-allreduce-grads-in-fp32
   --attention-softmax-in-fp32
   --attention-backend flash
)

WANDB_ARGS=()
if [ "${USE_WANDB:-0}" = "1" ]; then
   WANDB_ARGS=(
      --use-wandb
      --wandb-project "${WANDB_PROJECT:-apps-tool-agent}"
      --wandb-group "${WANDB_GROUP:-${RUN_TAG}}"
      --wandb-exp-name "${WANDB_EXP_NAME:-${RUN_TAG}}"
   )
fi

RAY_JOB_ARGS=()
if [ "${RAY_JOB_NO_WAIT:-0}" = "1" ]; then
   RAY_JOB_ARGS=(--no-wait)
fi

export MASTER_ADDR=${MASTER_ADDR:-$(hostname -I | awk '{print $1}')}
ray start --head --node-ip-address "${MASTER_ADDR}" --num-gpus 1 \
   --disable-usage-stats --dashboard-host=0.0.0.0 --dashboard-port=8265

RUNTIME_ENV_JSON="{
  \"env_vars\": {
    \"PYTHONPATH\": \"${MEGATRON_ROOT}:${SLIME_ROOT}:${REPO_ROOT}/src\",
    \"CUDA_DEVICE_MAX_CONNECTIONS\": \"1\"
  }
}"

ray job submit --address="http://127.0.0.1:8265" \
   --runtime-env-json="${RUNTIME_ENV_JSON}" \
   ${RAY_JOB_ARGS[@]} \
   -- ${CONDA_ENV}/bin/python "${SLIME_ROOT}/train_async.py" \
   --actor-num-nodes 1 \
   --actor-num-gpus-per-node 1 \
   ${MODEL_ARGS[@]} \
   ${CKPT_ARGS[@]} \
   ${SFT_ARGS[@]} \
   ${OPTIMIZER_ARGS[@]} \
   ${PERF_ARGS[@]} \
   ${MISC_ARGS[@]} \
   ${WANDB_ARGS[@]}
