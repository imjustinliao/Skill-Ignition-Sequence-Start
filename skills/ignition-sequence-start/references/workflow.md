# Building, reviewing and shipping

After the plan is approved, every milestone and every review round runs the same loop: slow where mistakes are expensive (before code, before calling it done, before anything public), fast everywhere else.

## Contents

- The loop
- Verification gate
- Presenting results
- Quality bar
- Tidy and refactor pass
- Feedback rounds
- Status
- Sign-off and drift
- Revising
- New scope
- Adding a part
- Approval modes and commits
- Away mode
- Shipping
- Versioning

## The loop

1. **Re-read** `docs/progress.md` and the milestone's feature IDs.
2. **Plan** in a few lines: files, risks, and the "done when" check. A new milestone needs the owner's approval; inside an approved one, proceed.
3. **Build** in small, focused, commit-sized changes. Nothing unrelated. Keep the owner's live preview running (`AGENTS.md` › Verify) so they see each change as it lands, and keep `progress.md` › Now current as you go (`continuity.md` › Leaving).
4. **Verify** (gate below).
5. **Present** the result. In `ask` mode, stop for the owner after each change; in the other modes keep going and stop at milestone end, or sooner when a decision is the owner's.
6. **Commit** per the approval mode.
7. **Milestone end**: fresh-eyes review, tidy pass, sign-off, update `progress.md`.

Stop and tell the owner when: two attempts at the same fix have failed (re-plan instead of patching); a decision falls outside what was approved; the check cannot run here.

## Verification gate

Done means all of this, checked by the agent itself:

- The "done when" check was decided before building, and it passes.
- It builds with no new warnings, and the tests pass. Read the result line; never chain a push blindly after a test command.
- **It was used like a user would**: UI driven in a browser or simulator at phone and desktop widths, in each theme the design uses, interactions exercised (tap, type, drag, keyboard). APIs called for real, including failure and permission cases. Models evaluated against the baseline. Firmware compiled and simulated where possible. CLIs run with real arguments.
- **Evidence** in the report: the command and its result, screenshots, sample output.
- **Tests are never edited or deleted to make them pass.** Test hardest where bugs are costly and quiet: auth, payments, data loss, permissions.
- **Fresh eyes before a milestone is done**: a review by a subagent that did not write the code (or the harness's review command), against the feature IDs and the quality bar.
- What cannot be checked here (real hardware, payments, third-party accounts, how it feels) goes under Blockers with exact steps for the owner.

## Presenting results

Short and checkable, with the preview link and what to look at: what changed per feature or feedback ID (done, partly done and what's missing, not done and why); how it was verified and what could not be; screenshots or output to look at; then the question the approval mode asks. Plain words for beginners.

## Quality bar

The goals in `docs/product.md` set how far to go beyond the baseline:

| Concern | Always, even for an MVP | When the goals demand it |
|---------|-------------------------|--------------------------|
| Security | Secrets rules; input validated at boundaries; authorization checked on every data access; least privilege; approved dependencies only | Threat model, audit logs, external review |
| Performance | No obvious waste: N+1 queries, unbounded lists, giant bundles, blocking the UI thread | Measured budgets (p95 latency, page load), profiling |
| Scale | Stateless servers, indexes on queried fields, pagination, migrations | Caching, queues, replicas: after measuring |
| Cost and efficiency | Free tiers, scale to zero, spend limits | Reserved capacity, tuning |

When a goal forces a trade-off, explain it in one line and let the owner choose.

## Tidy and refactor pass

At every milestone end, and whenever the owner asks:

- **Duplication**: the same logic in three places gets extracted; near-identical components become one.
- **Dead weight**: unused files, assets, dependencies, feature flags, debug leftovers, temporary docs, stale `references/` images.
- **Docs**: current truth rewritten in place; `AGENTS.md` under ~100 lines and `progress.md` under ~200 (done feedback rows out, ~15 decisions, ~10 log lines); no extra Markdown files (`check.py` flags them).
- **Rules**: refactors change no behavior and go in their own commit, with tests green before and after. Deletions are listed in the milestone summary and done after the owner's OK (git keeps history). Mid-milestone, don't refactor code you aren't otherwise touching: note it for this pass.

## Feedback rounds

1. Split the owner's message into items and add each to `progress.md` › Feedback with an ID (`FB-012`), in their words, before starting.
2. Items added mid-work get their own IDs; finish or park the current one cleanly first.
3. Work through them; when two conflict, ask.
4. Report per ID; mark done items with the commit.

## Status

```text
Phase and milestone: …
Done: …   In progress: …   Not started: …
Feedback: N done, N open (IDs)
Skipped or deferred: …
Waiting on you: numbered questions
```

## Sign-off and drift

- Sign off each milestone against its feature IDs: every acceptance item met, met in the owner's newer form, or listed as a gap.
- After several rounds of ad-hoc fixes the docs fall behind what the owner now wants. Every few rounds, or on "status", fold their newer decisions back into `docs/product.md` and `docs/design.md`, and re-ask unanswered questions instead of letting them sit in Blockers.

## Revising

Anything from setup can change. Change it where it lives:

| The owner changes | Update | Then |
|-------------------|--------|------|
| Goal, users, targets | `docs/product.md` | Check the plan and architecture still fit; say so if not |
| A feature | `docs/product.md`, in place, dated | Re-check the affected milestones |
| Look and feel | `docs/design.md`, rewritten in place | List built screens that no longer match, as feedback items |
| Architecture or stack | `docs/architecture.md` | Explain cost and rework; needs approval |
| The plan | `progress.md` › Milestones | Approval before building on it |
| How agents work | `AGENTS.md` | Applies from the next action |

Show the current wording, make the change in the owner's words, summarize what it affects in two or three lines, and log a dated decision. A change that adds work or reorders the plan needs a yes before code. When the owner edits docs by hand, their version wins: mention it on arrival and follow it.

## New scope

1. Capture the features in `docs/product.md` with new IDs (setup rules: faithful wording, open questions separate).
2. Update `docs/design.md` or `docs/architecture.md` if affected; research only what blocks it.
3. Propose milestones, including rework of finished ones, and get approval.

New scope never goes straight from chat into code: unwritten requirements are the ones that get lost.

## Adding a part

When the owner adds a part they skipped ("now build the backend too", "add a mobile app"):

1. Run that part's direction step from its track file (`intake.md` › 3). Create its doc if missing (`python3 <skill>/scripts/scaffold.py . --with architecture` or `--with design`) and add its rows to `AGENTS.md` › Docs and the plan.
2. The existing contract in `docs/architecture.md` › Interfaces is the starting point: the new part implements it, and mocks are replaced one endpoint at a time behind the same interface.
3. Update `AGENTS.md` › Built here, propose milestones, get approval.

If someone else was building that part, agree with the owner who owns the contract from now on.

## Approval modes and commits

Set in `AGENTS.md` › Git; only the owner changes it (log the change as a decision):

- **`auto-commit`** (default): commit after each passing check; push at milestone end after the owner signs off. Frequent local commits also mean a crashed session loses almost nothing.
- **`ask`**: after a verified change, ask: improve further, commit, or commit and push?
- **`auto-push`**: commit and push after each passing check. Never on a failed or unfinished check.
- **`none`**: no git. No commits; every deletion is permanent, so ask first. Offer git again at milestone ends.

Every commit: stage only project paths, check `git diff --cached` for secrets and machine-specific files, one logical change, never force-push or rewrite published history. The pre-push hook runs `check.py --secrets`; without it, run `python3 <skill>/scripts/check.py` before pushing. Bypass the hook (`--no-verify`) only when the owner confirms a false alarm.

## Away mode

- Agree the boundary first: which milestones or feedback IDs, and the commit mode. Log it as a dated decision.
- Stay inside it. Never cross a gate that wasn't granted: a new milestone, a dependency, money, deletion, anything public.
- Use recorded defaults for small questions; queue real ones under Blockers instead of waiting.
- Leave a report readable in two minutes: done per ID, verified how, waiting on the owner.

## Shipping

1. Run the track file's Ship checklist.
2. Always: a README that shows the product off (one-line pitch, screenshot or GIF, live link or install command, quickstart, stack, license); `check.py` clean; no secrets anywhere; production settings in the host, not in code.
3. **The owner approves every public step**: production deploy, publishing a package, making the repo public, a launch post.
4. After launch: error tracking and an uptime check where it applies, a known rollback path, and first users' feedback into `progress.md` › Feedback. Phase becomes Live.

## Versioning

With the default `MAJOR.MINOR.PATCH - What changed` commits:

- **PATCH**: fixes, refinements, small improvements. **MINOR**: a new feature, screen or capability (reset patch). **MAJOR**: a release milestone or breaking change. A new screen or behavior users can see is a minor bump, even in a long refinement phase.
- Each commit takes the next unused version from `git log`. Parallel sessions use reserved ranges.
- A commit version is not the app's or package's release version; change those only when the owner asks.
