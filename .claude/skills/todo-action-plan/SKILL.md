---
name: todo-action-plan
description: Create and review detailed action plans from TODO items in todo/. Generates plans in tasks/<slug>/ using AI review cycles. Use when the user wants to generate or refine an action plan for a TODO item.
user_invocable: true
---

# TODO Action Plan Workflow

## When to use
- User asks to create an action plan from a TODO item
- User wants to generate a detailed, agent-executable plan from a `todo/` item
- User wants to review or refine an existing action plan in `tasks/<slug>/`

## Workflow

1. **Identify the TODO slug**
   - The slug follows the pattern `YYYYMMDD-short-slug` (e.g. `20260208-qwen3-vl-throughput-bench`)
   - Verify `todo/<slug>.md` exists
   - If the user provides a partial name, match against files in `todo/`

2. **Run the action plan script**
   - Script location: `scripts/agent/todo_action_plan.py`
   - Basic usage:
     ```bash
     cd /home/ray/default/moe_bench
     python scripts/agent/todo_action_plan.py <slug> --reviewer claude --cycles 2
     ```
   - This creates `tasks/<slug>/plan.md` from `todo/<slug>.md`
   - The plan is designed for AI agent execution (phased, testable, specific)

3. **Review an existing plan**
   - If `tasks/<slug>/plan.md` already exists, the script skips creation and goes straight to review cycles
   - Run with `--cycles N` to do N rounds of review
   - Run with `--cycles 0` to only create the plan without review

4. **Update TODO tracking**
   - After plan creation, note in `todo/<slug>.md` Progress section that the detailed plan exists at `tasks/<slug>/plan.md`
   - Use the standard Progress format:
     ```
     ## Progress
     - Created: Detailed action plan at `tasks/<slug>/plan.md`
     - Issue: None
     - Next action: Run `/todo-impl` to execute the plan
     ```
   - Keep the corresponding checkbox unchecked in `todo/TODO.md` (do **not** mark it `[x]` — that happens during `/todo-impl` on completion)

## Script options

| Flag | Default | Description |
|------|---------|-------------|
| `<slug>` | (required) | TODO slug, reads `todo/<slug>.md` |
| `--plan-doc PATH` | `tasks/<slug>/plan.md` | Override plan file location |
| `--reviewer PRESET` | (interactive) | Reviewer preset: `claude`, `codex`, `cursor-opus`, `cursor-gpt` |
| `--cycles N` | 3 | Number of review rounds (0 = create only) |
| `--context TEXT` | — | Extra context for prompts (repeatable) |
| `--context-file FILE` | — | File with extra context (repeatable) |
| `--no-commit` | false | Skip git commits |
| `--timeout SECS` | 1800 | Hard per-reviewer timeout (0 = no limit) |
| `--stall-timeout SECS` | 0 | Kill reviewer if no output/CPU activity for this long (triggers fallback; 0 = disable) |
| `--heartbeat-secs SECS` | 30 | Emit liveness heartbeat while reviewer runs (0 = disable) |
| `--no-fallback` | false | Disable automatic fallback to alternative reviewers |
| `--reviewer-cmd CMD` | — | Custom reviewer shell command (pair with `--reviewer-name`) |
| `--reviewer-name NAME` | — | Display name for custom reviewer |
| `--comments-dir DIR` | `task_comments/<slug>/` | Override comments directory |

## Examples

```bash
# Create a plan and review it 2 times with Claude
python scripts/agent/todo_action_plan.py 20260208-qwen3-vl-throughput-bench \
    --reviewer claude --cycles 2

# Create plan only, no review
python scripts/agent/todo_action_plan.py 20260208-qwen3-vl-throughput-bench \
    --reviewer claude --cycles 0

# Review an existing plan with two reviewers
python scripts/agent/todo_action_plan.py 20260208-qwen3-vl-throughput-bench \
    --reviewer claude --reviewer cursor-opus --cycles 3

# With extra context
python scripts/agent/todo_action_plan.py 20260208-qwen3-vl-throughput-bench \
    --reviewer claude --context "Focus on memory optimization"
```

## Directory structure
```
todo/<slug>.md               # Source TODO item (lightweight)
tasks/<slug>/plan.md         # Detailed action plan (agent-ready)
task_comments/<slug>/        # Reviewer comments from each cycle
```
