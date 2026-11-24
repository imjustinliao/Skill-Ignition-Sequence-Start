# Upgrading a project set up with an older version

A project keeps the skill version that set it up at the top of `docs/progress.md`: `<!-- ignition-sequence-start: X -->`. No marker, but `AGENTS.md` and `docs/progress.md` exist: treat it as 0.2. This skill's version is in `SKILL.md`. When the project is older (major or minor version; patch releases never change project docs), bring it forward in place: nothing lost, setup not re-run, the plan unchanged.

## When, by stage

Check on arrival (`continuity.md` › Arriving), and right after the skill updates itself.

| Stage (`progress.md` › Phase) | Do |
|-------------------------------|----|
| Setup (or the old Intake) with items still open | Upgrade the docs first, then continue setup at the first open item with the new flow. Never re-ask what is already answered. |
| Building, Refining, Shipping | Finish or commit the change in flight, then upgrade. Milestones, IDs, feedback and decisions carry over exactly; no re-planning. |
| Live or Paused | Docs only, as above. Product code is never touched by an upgrade. |
| Parallel sessions in flight (`docs/parallel-plan.md` with unmerged milestone branches) | Wait until everything is merged: those sessions follow the docs as they are. Say so, note it under Blockers. |

## How

1. **Tell the owner, in one short message**: what is new for them since their version (the "New for the owner" lines below, in plain words), what changes in their docs (merged, renamed, added, removed), that product code is not touched and git keeps the old files. Ask for one yes. "Later" is fine: note it under Blockers and offer again at the next milestone end.
2. **On yes, one docs-only commit** (`<next version> - Upgrade project docs to ignition-sequence-start <version>`):
   - Apply each version's migration below, oldest first.
   - Merge `assets/templates/AGENTS.md` into the project's `AGENTS.md`: keep every project value and owner rule (pitch, stack, commands, approval mode, commit format, scope, custom rules), add the sections it lacks, and replace only the generic text the new template supersedes. Show what moved where.
   - Run `python3 <skill>/scripts/scaffold.py . --with <the docs it should have>` to add missing docs and secret guards (it never overwrites), and act on its notes and warnings.
   - Set the marker to this skill's version; add a session-log line.
3. Run `python3 <skill>/scripts/check.py`, fix what it flags, and report in three lines.

An upgrade never changes the owner's approval mode, commit format, stack or plan. New options are mentioned, not applied.

## Versions

### 0.5.1

- **New for the owner**: a live preview link (localhost, or the project's equivalent) stays open while the agent builds, so every change shows up as it lands.
- **Migration**: add the Live preview line and the paragraph under it to `AGENTS.md` › Verify, filled with the project's preview command and link.

### 0.4.0

- **New for the owner**: the skill updates itself at the start of each session, and projects set up with older versions are upgraded in place, at a safe point.
- **Migration**: none beyond the marker.

### 0.3.0

- **New for the owner**: a shorter setup with defaults; tracks for frontend, backend, models, hardware and more, with "add backend" (or frontend) any time; API keys never pass through the agent, and a pre-push check blocks leaked keys; "continue" finds the previous chat after switching agent, account or machine; new shortcuts (add backend, faster or slower, ship it); a tidy and refactor pass at every milestone end.
- **Migration from 0.2 or earlier**:

| Old | New |
|-----|-----|
| `docs/spec.md` | Requirements (IDs and acceptance items unchanged), Terms and Structure → `docs/product.md` › MVP features. Out of scope → Not doing. Assumptions, Ambiguities and Open questions → Open questions, each with a default. Delete `spec.md`. |
| `docs/product.md` headings | What and Why, Differentiation → Pitch; Target users → Users and the core workflow; Goal, Success metrics → Goals; Non-goals → Not doing. |
| `docs/feedback.md` | Open and in-progress rows → `progress.md` › Feedback (keep IDs). Delete the file. |
| `docs/research.md` | Each finding → the "Why (source)" of the choice it informed in `docs/architecture.md` › Stack or in `docs/design.md`; drop findings that informed nothing. Delete the file. |
| `references/README.md` | Patterns and index → `docs/design.md` › References. Delete the README; keep the images. |
| `docs/design.md` | Vision → Feel; Design direction → System and Patterns; Pending from owner → `progress.md` › Blockers. Add the Status line: approved, with the original date. |
| `docs/architecture.md` | New. Create it if the project has a backend, data, a model, hardware, or a contract with another team; fill it from `AGENTS.md` (stack, commands), the research findings and the decisions. |
| `docs/progress.md` | Current status → Now. External dependencies → Blockers. Add a Feedback section. An Intake checklist that is complete is removed; an unfinished one becomes Setup: steps 0, 1, 4 and 5 → Folder and version history; 2 → Goal, users and the parts to build; 3 → MVP features; 6 → Design direction; 7 → Architecture (if any); 8 → Plan approved. Decisions and Session log carry over. |
| Approval mode | Keep it. `commit-on-green` is now called `auto-push`. Mention `auto-commit`. |
