# AGENTS.md

How every coding agent works on {{PROJECT_NAME}}. This file is a map: rules live here, knowledge lives in `docs/`. Keep it under ~100 lines; add a rule only after a mistake repeats.

## Project

- **{{PROJECT_NAME}}**: {{ONE_LINE_PITCH}}
- **Stakes**: MVP. Working, clean and shipped beats complete. <!-- change to "production" once real users depend on it -->
- **Built here**: {{PARTS}} <!-- e.g. "frontend and backend", or "frontend only; backend by another team against docs/architecture.md › Interfaces" -->
- **Stack**: {{STACK}}
- **Owner**: {{EXPERIENCE}} <!-- new to coding / some experience / pro: sets how much to explain -->

## Docs

| File | Holds | Read |
|------|-------|------|
| `docs/progress.md` | Now (status, next action, in flight), milestones, feedback, decisions, blockers, session log | First, every session |
| `docs/product.md` | Pitch, users, goals, MVP features with IDs, what was cut | Before feature work |
| `docs/design.md` | Feel, design system, patterns, references | Before user-facing work | <!-- if:design -->
| `docs/architecture.md` | Shape, stack and why, data, interfaces, environments and secret names, deploy | Before system work | <!-- if:architecture -->

Everything goes in one of these: a technical choice and its source in the doc it shapes; why X beat Y in Decisions; notes, plans and summaries folded in, then deleted. No other Markdown files. Design and architecture docs are current truth: rewrite them in place (git keeps history).

## Start of every session

1. Read `docs/progress.md`, then `git status` and `git log -5`. If they disagree, trust git and fix `progress.md`.
2. Look for an earlier chat for this folder, in any tool or account, every time (a usage limit or crash leaves no note). Run `scripts/sessions.py` from the ignition-sequence-start skill (in a `skills/` folder under `~/.claude*`, `~/.agents` or this tool's config) if you have it; it ends with a "Take over:" line when a chat was cut off. Without it: this tool's resume list, or for Claude Code the newest `.jsonl` in `~/.claude*/projects/<this folder's path with every non-alphanumeric character as ->/`. If a chat was cut off, read its end and continue from it instead of starting fresh; say which chat you used.
3. If this file still has `{{placeholders}}`, setup is unfinished: finish it before building.
4. Run the smoke check, if one is set: `{{SMOKE_COMMAND}}`. If it fails, fix or report that first.
5. "Where were we": three lines (phase, last done, next action), then wait. "Continue": finish the cut-off step, if any, then the approved next action. A specific task: one line of orientation, then the task.

## Owner shortcuts

| Owner says | Do |
|------------|----|
| continue, go | The approved next action. |
| status | Phase, milestone, done / in progress / waiting on the owner, open feedback IDs. |
| handoff | Update `progress.md` › Now and the session log, commit if allowed, list anything uncommitted. |
| 1. … 2. … | Add each to `progress.md` › Feedback with an ID, work through them, report per ID. |
| new feature: … | Add to `docs/product.md` with an ID, propose where it fits in the plan, wait for approval. |
| add backend (or frontend, an app, …) | Agree the new part's direction and contract with the owner, then plan it like a milestone. |
| change … | Edit the doc where it lives, say what it affects, get approval if it adds work. |
| keep going | Agree the boundary first; stay inside it; queue questions under Blockers. |
| faster / slower | Fewer check-ins and terser updates, or more explanation and smaller steps. |
| ship it | Run the ship checklist for this project and get approval before anything goes public. |
| help | List these shortcuts in plain words. |

## How we build

1. Plan the milestone in a few lines: what, which files, the check that proves it works. New milestones need the owner's approval.
2. Build in small, focused changes. Simplest thing that works; no speculative layers; nothing unrelated.
3. Verify (below) and show the evidence.
4. Commit per the approval mode. In `ask` mode, stop for the owner after each change; otherwise keep going and stop at milestone end or when a decision is the owner's.
5. Milestone end: tidy pass (below), then update `docs/progress.md`.

If two attempts at the same fix fail, stop, re-plan, and tell the owner.

## Verify

- Build: `{{BUILD_COMMAND}}`
- Test: `{{TEST_COMMAND}}`
- Run it: {{RUN_CHECK}} <!-- e.g. "open it in the browser at phone and desktop width, click through the main flow" -->
- Live preview: {{PREVIEW}} <!-- e.g. "npm run dev → http://localhost:3000, phone: the Network URL it prints". Other projects: the simulator or Expo Go, the API docs page, the demo app, the serial monitor -->

While building, keep the live preview running and give the owner its link, so they watch every change as it lands; after each change, say what to look at. List it under In flight; stop it when the session ends.

Done means checked, not assumed: show the command and its result, or a screenshot. Never edit or delete a test to make it pass. What only a person or a real device can check goes under Blockers, with exact steps.

## Quality bar

- **Security, always.** Follow the secrets rules below. Validate input at every boundary. Least privilege for keys, tokens and database access.
- **Performance and scale, as far as the goals need** (`docs/product.md` › Goals). Measure before optimizing.
- **No duplication.** When the same logic appears a third time, extract it. Refactor in its own commit, tests green before and after.

## Secrets

- Never ask for, read, print or commit secret values. Refer to them by name. Values live in `.env` (gitignored) or the host's secret settings; `.env.example` lists names only.
- Do not run commands that print secrets (`cat .env`, `printenv`, `env`, `echo $KEY`). To check a key is set, test that it exists, never show it.
- Keys for paid or private services never go in frontend code: call them from a server.
- If a secret appears in chat, a log or a commit, tell the owner to revoke and replace it now.

## Ask the owner first

Changing the stack or architecture · a dependency outside the approved stack · anything that costs money · deleting the owner's files (your own scratch files and build output are fine) · deploying or publishing · auth, payments or personal data · CI, signing, credentials · rewriting git history.

## Git

- **Approval mode: auto-commit.** Commit after each passing check; push at milestone end once the owner signs off. Other modes: `ask` (after each verified change ask: improve further, commit, or commit and push?), `auto-push` (commit and push after each passing check), `none` (no git: no commits, and every deletion is permanent, so ask first). Only the owner changes the mode.
- **Commits:** `MAJOR.MINOR.PATCH - What changed` (1–15 words, no period; next unused version from `git log`; patch for fixes, minor for a new feature, major for a release). Stage only project files; check `git diff --cached` for secrets first.
- Before pushing, the skill's `check.py --secrets` runs as a git pre-push hook (if installed). Never bypass it with `--no-verify` unless the owner confirms a false alarm.
- Never force-push or rewrite published history.

## Handoff

Sessions can end without warning (limits, crashes, a switch of agent or account). So after every commit and before any long step, keep `docs/progress.md` › Now current: phase, next action, in flight. Push at milestone end so another machine can continue. Write for a stranger: no "as discussed".

## Tidy pass (every milestone end)

Remove what is no longer used: files, assets, dependencies, dead code, temporary docs, `references/` images nobody needs. Show the list with the milestone summary; delete once the owner approves (git keeps history). Keep this file under ~100 lines and `progress.md` under ~200 (done feedback rows out, ~15 decisions, ~10 log lines).
