#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

export SFT_DATA="${SFT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_sft.jsonl}"
export RUN_TAG="${RUN_TAG:-qwen2.5_3b_code_r1_sft}"
export BATCH_SIZE="${BATCH_SIZE:-4}"
export NUM_EPOCH="${NUM_EPOCH:-1}"
export LR="${LR:-5e-6}"
export MAX_TOKENS_PER_GPU="${MAX_TOKENS_PER_GPU:-8192}"

exec "${SCRIPT_DIR}/run-qwen2.5-3B-tool-agent-sft.sh"
