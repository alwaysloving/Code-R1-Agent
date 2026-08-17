# Code-R1 Agent

A Code-R1 post-training pipeline for coding agents. The model can run public
tests, use test feedback to revise its solution, and submit a final answer that
is evaluated against hidden tests.

This repository contains the final KodCode 631 workflow for data preparation,
SFT, GRPO, and evaluation.

> `src/sandbox_runner.py` applies resource limits, but it is not a hardened
> security boundary. Run untrusted generated code in an isolated container or
> VM.

## slime is required

Training and evaluation require
[`THUDM/slime`](https://github.com/THUDM/slime). This repository only provides
the Code-R1 data pipeline, sandbox, rollout function, and reward function; it is
not a standalone training framework.

`slime` provides the training runtime used by the launch scripts:

- Megatron-LM for model training and distributed checkpoints
- SGLang for rollout generation
- Ray for process coordination
- custom rollout and reward hooks loaded from `src/generate_with_code.py`

Install slime and its compatible PyTorch, SGLang, Ray, Megatron-LM, and CUDA
dependencies by following the upstream slime documentation before running this
project.

## Repository layout

```text
src/                 rollout, reward, and sandbox implementation
scripts/data/        data preparation and validation
scripts/training/    slime-based SFT, GRPO, and evaluation launchers
data/                KodCode 631 evaluation data and HumanEval fixtures
notebooks/           data inspection
```

## Configuration

Create a local environment file:

```bash
cp .env.example .env
```

Configure these paths in `.env`:

```bash
SLIME_ROOT=/path/to/slime
MEGATRON_ROOT=/path/to/Megatron-LM
CONDA_ENV=/path/to/conda/envs/slime
MODEL_CONFIG=/path/to/slime/scripts/models/qwen2.5-3B.sh
HF_CHECKPOINT=/path/to/Qwen2.5-3B-Instruct
REF_LOAD=/path/to/Qwen2.5-3B-Instruct_torch_dist
CHECKPOINT_ROOT=/path/to/checkpoints
```

Load the configuration and install the lightweight data dependency:

```bash
set -a
source .env
set +a
pip install -r requirements.txt
```

## Prepare data

Place `kodcode_light_rl_10k_raw.jsonl` in `data/`, then run:

```bash
PYTHONPATH=src python scripts/data/prepare-kodcode-code-r1-data.py \
  --skip-solution-validation
PYTHONPATH=src python scripts/data/validate-kodcode-code-r1-data.py
```

The final defaults generate 3,000 SFT prompts, 2,400 GRPO prompts, and 500
evaluation prompts.

## Train and evaluate with slime

```bash
# SFT
scripts/training/run-kodcode-code-r1-sft.sh

# Full GRPO from the SFT checkpoint
SFT_CKPT="${CHECKPOINT_ROOT}/qwen2.5_3b_code_r1_sft" \
  scripts/training/run-kodcode-code-r1-grpo.sh

# Evaluation
scripts/training/run-kodcode-code-r1-eval.sh \
  experiment_name /path/to/checkpoint
```

The launchers call slime's `train_async.py` for SFT and `train.py` for GRPO and
evaluation. They add `src/` to the Ray runtime `PYTHONPATH` so slime workers can
load these hooks:

```text
generate_with_code.generate
generate_with_code.reward_func
generate_with_code.log_rollout_data
generate_with_code.log_eval_rollout_data
```

## Agent protocol

- `<test>...</test>` runs public tests.
- `<information>...</information>` returns test feedback.
- `<answer>...</answer>` submits the final solution for hidden-test scoring.

## Validation

```bash
PYTHONPATH=src python -m py_compile src/*.py scripts/data/*.py
bash -n scripts/training/*.sh
```

Large datasets, checkpoints, logs, experiment trackers, and local configuration
are excluded by `.gitignore`. Review the slime, KodCode, HumanEval, and base
model licenses before publishing or redistributing artifacts.
