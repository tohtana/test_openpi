# Run OpenPI LIBERO Fine-Tuning Example

## Goal
- [ ] Execute one documented openpi LIBERO fine-tuning example (`compute_norm_stats` + `train`) and capture reproducible commands and artifact locations.

## Plan
- [ ] Step 1: Validate training prerequisites against openpi docs/config.
  - [ ] Substep: Confirm chosen training config exists in `openpi/src/openpi/training/config.py` (target: `pi05_libero`).
  - [ ] Substep: Confirm required command sequence in `openpi/README.md` (`scripts/compute_norm_stats.py` then `scripts/train.py`).
- [ ] Step 2: Run normalization stats computation.
  - [ ] Substep: Execute `uv run scripts/compute_norm_stats.py --config-name pi05_libero`.
  - [ ] Substep: Verify norm-stats artifacts are produced and readable.
- [ ] Step 3: Run a bounded fine-tuning example.
  - [ ] Substep: Launch training with explicit experiment name and overwrite flag.
  - [ ] Substep: For this task, use a bounded/short run configuration (or resume-safe limit) to validate pipeline execution without full convergence runtime.
  - [ ] Substep: Verify checkpoint directory creation and log outputs.
- [ ] Step 4: Document outcomes.
  - [ ] Substep: Save exact commands, config used, and produced artifact paths under `tasks/20260219-openpi-libero-finetune-example/`.
  - [ ] Substep: Record any blockers (dataset access, memory, dependency mismatch) and mitigation steps.

## Progress
- Created: Detailed action plan at `tasks/20260219-openpi-libero-finetune-example/plan.md`
- Issue: None
- Next action: Run `$todo-impl` to execute the plan

## Verification
- [ ] `uv run scripts/compute_norm_stats.py --config-name pi05_libero` completes successfully.
- [ ] Training command starts and writes checkpoints under `openpi/checkpoints/...` (or configured checkpoint path).
- [ ] A concise run record exists under `tasks/20260219-openpi-libero-finetune-example/` with commands, config, and artifact paths.
- [ ] Any deviations from docs are explicitly captured with reason and workaround.
