# Release notes

## Open-source snapshot — 2026-08-17

This snapshot preserves the final local Code-R1 workflow built around
`src/generate_with_code.py` and `src/sandbox_runner.py`.

- Includes only the final KodCode 631 preparation, validation, SFT, full GRPO,
  and evaluation workflow, plus the HumanEval evaluation builder.
- Replaces workstation-specific paths in executable code with documented
  environment variables.
- Excludes experiment logs, W&B/TensorBoard caches, checkpoints, bytecode, and
  very large generated datasets from normal Git tracking.
- Keeps only the final compact evaluation fixtures and validation reports;
  historical APPS code and intermediate 532/unversioned KodCode variants are
  omitted from the publishable snapshot.

Before publishing, the maintainer still needs to choose a license and confirm
that each redistributed dataset artifact is compatible with that license.
