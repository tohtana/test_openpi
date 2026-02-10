---
name: todo-impl
description: Implement TODO items created via todo-docs, updating todo/ plans with issues, progress, and next actions. Use when the user asks to implement a TODO item or references a todo/ plan.
user_invocable: true
---

# TODO Implementation Workflow

## When to use
- User asks to implement a TODO item from `todo/TODO.md`
- User references a plan under `todo/` and wants it executed

## Workflow
1. **Locate the TODO and plan**
   - Find the relevant bullet in `todo/TODO.md`.
   - Open the matching plan file in `todo/YYYYMMDD-<slug>.md`.
   - Also check for a detailed action plan at `tasks/YYYYMMDD-<slug>/plan.md` (created by `$todo-action-plan`). If it exists, **prefer** it over the lightweight plan in `todo/` — it contains phased, agent-executable steps.
2. **Align with docs**
   - Read any relevant files under `docs/` to confirm expected behavior.
3. **Implement the change**
   - Update code to satisfy the TODO.
   - Keep edits scoped to the plan and note any deviations.
   - Place final results, reports, and other artifacts in `tasks/YYYYMMDD-<slug>/` (alongside the plan file).
4. **Add tests when possible**
   - Prefer adding or extending tests under the appropriate tests directory.
   - If tests are not feasible, document why in the plan's **Issue** field.
5. **Update the plan progress**
   - Keep **Progress** entries accurate after each change:
     - **Created**: what was implemented or updated
     - **Issue**: current blockers or risks (use "None" if unblocked)
     - **Next action**: what remains if not completed
6. **Update TODO tracking**
   - If completed, mark the TODO checkbox as done in `todo/TODO.md` by changing `- [ ]` to `- [x]`.
   - If not completed, keep it unchecked and ensure the plan reflects current status.
   - Always update the Progress section in both `todo/YYYYMMDD-<slug>.md` **and** `tasks/YYYYMMDD-<slug>/plan.md` (if the latter exists).

## Progress update template
```
## Progress
- Created: [what was implemented/updated]
- Issue: [blocker or "None"]
- Next action: [next concrete step if not completed]
```

## Example completion note
```
## Progress
- Created: Added collocated transfer test and assertions for CUDA IPC path.
- Issue: None.
- Next action: None (completed).
```
