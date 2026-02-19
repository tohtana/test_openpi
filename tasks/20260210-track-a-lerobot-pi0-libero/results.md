# Track A Results

## Final Status

- Status: **Blocked**
- Blocking phase: **Phase 3 baseline evaluation**
- Root cause: Hugging Face gated model access error for `google/paligemma-3b-pt-224` during `lerobot/pi0_libero_finetuned` load.

## Environment / Preflight

- Task suite: `libero_object`
- Policy path: `lerobot/pi0_libero_finetuned`
- GPUs detected: `8x NVIDIA H100 80GB HBM3`
- Selected backend: `egl`
- Preflight artifact: `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/preflight/preflight.json`

## Baseline Attempt

- Run id: `baseline_b1_e2`
- Episodes requested: `2`
- Exit code: `1`
- Successes: `null`
- Success rate: `null`
- Result artifact: `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/runs/baseline_b1_e2/result.json`
- Error log: `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/runs/baseline_b1_e2/stderr.log`

## Current Artifacts

- Baseline summary CSV: `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/summary/baseline_summary.csv`
- All-runs summary CSV: `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/summary/all_runs.csv`
- Failures CSV: `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/summary/failures.csv`
- Phase handoffs:
  - `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/state/phase1_handoff.json`
  - `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/state/phase2_handoff.json`
  - `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/state/phase3_handoff.json`
  - `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/state/phase4_handoff.json`
  - `tasks/20260210-track-a-lerobot-pi0-libero/artifacts/state/phase5_handoff.json`

## Required Next Step

Grant/access-approve the gated repository dependency for the running Hugging Face account, then rerun baseline and scaled sweeps using the runbook commands.
