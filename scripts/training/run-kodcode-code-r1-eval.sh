#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

NAME="${1:?usage: $0 NAME LOAD_PATH [REF_PATH]}"
LOAD_PATH="${2:?usage: $0 NAME LOAD_PATH [REF_PATH]}"
REF_PATH="${3:-${LOAD_PATH}}"

PROMPT_DATA="${PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_grpo_631.jsonl}" \
EVAL_PROMPT_DATA="${EVAL_PROMPT_DATA:-${REPO_ROOT}/data/kodcode_code_r1_eval_631.jsonl}" \
"${SCRIPT_DIR}/run-code-r1-eval.sh" "${NAME}" "${LOAD_PATH}" "${REF_PATH}"
