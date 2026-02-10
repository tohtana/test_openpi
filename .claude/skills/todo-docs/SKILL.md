---
name: todo-docs
description: Validate new TODO requests against docs/, append to todo/TODO.md, and write a concrete action plan in todo/. Use when the user asks to add a TODO item or requests a TODO with a plan tied to docs.
user_invocable: true
---

# TODO Docs Workflow

## When to use
- User asks to add a TODO item
- User requests a TODO plus a concrete action plan grounded in docs

## Workflow
1. **Check docs for reasonableness**
   - Read relevant files under `docs/` (broad scan by default).
   - If the request conflicts with docs, adjust the TODO to align and note the assumption in the response.
2. **Append the TODO**
   - Add a new checkbox bullet to `todo/TODO.md` using `- [ ]` prefix.
   - Keep wording concise and action-oriented.
   - If the request includes subtasks or phases, express them as nested checkbox items (`  - [ ]`) under the parent.
   - Link the TODO to its plan file using a markdown link labeled "plan" in parentheses, e.g. `([plan](todo/YYYYMMDD-short-slug.md))`.
3. **Create or update action plan**
   - Ensure `todo/` exists; create if missing.
   - Save a new plan file named `todo/YYYYMMDD-<short-slug>.md`.
   - If a plan already exists for the same topic, update it instead of creating a duplicate.
   - Use the checklist template below and keep the **Progress** section current.

## Action plan template (markdown checklist)
```
# [Short title]

## Goal
- [ ] [One-sentence goal aligned with docs]

## Plan
- [ ] Step 1: [concrete action]
- [ ] Step 2: [concrete action]
- [ ] Step 3: [concrete action]
  - [ ] Substep: [nested subtask if needed]

## Progress
- Created: [what was created/updated so far]
- Issue: [what issue was found or what is blocked]
- Next action: [what to do next if not completed]

## Verification
- [ ] [How to confirm the change is correct]
```

## Notes
- Prefer docs-backed phrasing; avoid speculative TODOs.
- If docs are silent, state the assumption in the user response.
