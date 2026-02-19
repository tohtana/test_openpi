# AGENT.md

This file provides guidance to Codex when working with code in this repository.

## WARNING

- Never kill Ray's processes
- Other processes for distributed training may be running. Please use a non-default port when needed.
- **ALWAYS save large files to `/mnt/local_storage/`, NOT under `~/` or the project directory.**

## Repository Overview

<WRITE_HERE>

## Environment Setup

For the repeatable Track A LeRobot/LIBERO rebuild procedure, see:
- [ENV_SETUP_TRACK_A_LIBERO.md](ENV_SETUP_TRACK_A_LIBERO.md)

ENV_NAME=<WRITE_HERE>

Use the dedicated conda environment `${ENV_NAME}` for this workspace:

```bash
# Activate the environment
conda activate ${ENV_NAME}

# If it doesn't exist, create it
conda create -n ${ENV_NAME} python=3.10 -y && conda activate ${ENV_NAME}
```

### HuggingFace Environment Variables

```bash
# HuggingFace cache directory (use /mnt/local_storage to avoid filling home directory)
export HF_HOME=/mnt/local_storage/huggingface

# HuggingFace token (already set in environment)
# export HF_TOKEN="<your-token>"  # Already available as env var

# Model paths for Qwen3-VL finetuning
export HF_MODEL_PATH="Qwen/Qwen3-VL-30B-A3B-Instruct"
export MEGATRON_MODEL_PATH="/mnt/local_storage/checkpoints/qwen3vl30b_moe"
export SAVE_DIR="/mnt/local_storage/experiments"
```

## Build & Installation

${ENV_NAME}


## TODO Workflow

Three slash-command skills manage work items. See [todo/WORKFLOW.md](todo/WORKFLOW.md) for the full reference.

**Flow:** `/todo-docs` → `/todo-action-plan` (optional) → `/todo-impl`

| Skill | Purpose | Creates/Updates |
|-------|---------|-----------------|
| `/todo-docs` | Add a TODO grounded in `docs/` | Bullet in `todo/TODO.md` + plan at `todo/<slug>.md` |
| `/todo-action-plan` | Expand into a detailed, agent-executable plan | `tasks/<slug>/plan.md` via AI review cycles |
| `/todo-impl` | Implement the TODO (prefers `tasks/` plan if it exists) | Code changes; marks checkbox `[x]` in `todo/TODO.md` on completion |

**Slug format:** `YYYYMMDD-short-name` (e.g., `20260208-qwen3-vl-throughput-bench`)

**Progress section** — all three skills maintain this at the bottom of plan files (fields are overwritten, not appended):
```markdown
## Progress
- Created: [what was implemented/updated]
- Issue: [current blocker, or "None"]
- Next action: [next concrete step, or "None (completed)"]
```
