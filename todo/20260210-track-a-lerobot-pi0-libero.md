# Track A LeRobot pi0 LIBERO Eval

## Goal
- [ ] Validate Track A from `initial_plan.md` by running `lerobot-eval` with a pretrained pi0 flow policy on LIBERO in headless mode on an 8xH100 machine and capturing reproducible results.

## Plan
- [ ] Step 1: Prepare environment and dependencies for LeRobot LIBERO evaluation.
  - [ ] Substep: Create a Python 3.10 env (`vla_pi0`) and verify all 8 H100 GPUs are visible (`nvidia-smi`).
  - [ ] Substep: Clone `lerobot` and install with `pip install -e ".[libero]"`.
  - [ ] Substep: Configure offscreen rendering (headless, no monitor/X display) for the host before running eval.
- [ ] Step 2: Run a baseline evaluation with a small episode count.
  - [ ] Substep: Execute a headless baseline `lerobot-eval --policy.path=lerobot/pi0_libero_finetuned --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=2`.
- [ ] Step 3: Scale evaluation and collect artifacts.
  - [ ] Substep: Increase episode count and batch size based on available GPU/CPU resources, targeting efficient use of 8xH100.
  - [ ] Substep: Save final commands, suite name, episode count, success rate, and log/video paths in a downloadable directory.

## Progress
- Created: Detailed action plan at `tasks/20260210-track-a-lerobot-pi0-libero/plan.md`.
- Issue: None.
- Next action: Run `$todo-impl` to execute the plan.

## Verification
- [ ] `lerobot-eval` completes without runtime errors on `libero_object`.
- [ ] Eval runs without an attached monitor and without requiring an active GUI session.
- [ ] Results include suite name, episode count, success rate, and artifact locations.
- [ ] Video artifacts are written to a known path for later download from this environment.
- [ ] A concise runbook of exact commands used for the successful run is documented.
