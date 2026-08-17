# KodCode Code-R1 Agent

Final, cleaned Code-R1 post-training workflow for teaching a coding model to
run public tests, use test feedback, and submit a final answer. Historical APPS
implementations and intermediate dataset/script versions have been removed.

> `src/sandbox_runner.py` applies resource limits, but it is not a hardened
> security boundary. Run untrusted model-generated code in an isolated VM or
> container.

## Layout

```text
src/                 final rollout, reward, and sandbox implementation
scripts/data/        final KodCode preparation/validation and HumanEval builder
scripts/training/    final SFT, GRPO, and evaluation entry points
data/                final KodCode 631 evaluation data and HumanEval fixtures
notebooks/           data-inspection notebooks
```

## Environment

This project requires Linux, Python 3.10+, CUDA, and
[`slime`](https://github.com/THUDM/slime) with its compatible PyTorch, SGLang,
Ray, and Megatron-LM dependencies.

```bash
cp .env.example .env
set -a
source .env
set +a
pip install -r requirements.txt
```

Configure `SLIME_ROOT`, `MEGATRON_ROOT`, `CONDA_ENV`, `HF_CHECKPOINT`,
`REF_LOAD`, and `CHECKPOINT_ROOT` in `.env`.

## Rebuild the final data

The large raw, SFT, and GRPO files are intentionally excluded from Git. Place
`kodcode_light_rl_10k_raw.jsonl` in `data/`, then run from the repository root:

```bash
PYTHONPATH=src python scripts/data/prepare-kodcode-code-r1-data.py \
  --skip-solution-validation
PYTHONPATH=src python scripts/data/validate-kodcode-code-r1-data.py
```

The final defaults reproduce 3,000 SFT prompts, 2,400 GRPO prompts, and the
500-example `kodcode_code_r1_eval_631.jsonl` evaluation set.

## Train and evaluate

```bash
# SFT (requires generated data/kodcode_code_r1_sft.jsonl)
scripts/training/run-kodcode-code-r1-sft.sh

# Final full GRPO configuration
scripts/training/run-kodcode-code-r1-grpo.sh

# Evaluate a checkpoint on the final 631 split
scripts/training/run-kodcode-code-r1-eval.sh \
  experiment_name /path/to/checkpoint
```

The runtime protocol uses `<test>...</test>` for public-test feedback,
`<answer>...</answer>` for final submission, and
`<information>...</information>` for tool observations.

## Validation

```bash
PYTHONPATH=src python -m py_compile src/*.py scripts/data/*.py
bash -n scripts/training/*.sh
```

Runtime logs, experiment trackers, checkpoints, caches, raw datasets, and large
generated training data are excluded by `.gitignore`. Choose an open-source
license and verify the KodCode, HumanEval, and base-model terms before publishing.
