# Subagents and parallel agents

Parallel work buys speed with coordination cost and tokens. Done well, several milestones land in the time of one with no merge conflicts. Done carelessly: duplicated components, inconsistent behavior, a choking machine and a long cleanup. **Default to one agent**; parallelize only what is truly independent, and only once single-agent output is reliable.

## Contents

- Two kinds of parallelism
- Subagents: fan out reading, keep writing central
- Should this run in parallel?
- Asked for prompts before the project is ready
- 1. Land the base and freeze the contracts
- 2. Write the parallel plan
- 3. Write one prompt per session
- 4. While sessions run
- 5. Merge, integrate, review
- 6. Sign-off and cleanup
- Parallel fixes during review rounds

## Two kinds of parallelism

| | Subagents | Parallel sessions |
|--|-----------|-------------------|
| What | Helpers inside one session | Separate agent sessions, often separate tools or windows |
| Good for | Research, reading many files or images, fresh-eyes reviews, audits | Building independent milestones |
| Writes code? | Rarely; when they do, in an isolated worktree | Yes, each on its own branch and worktree |
| Context | Gets a brief, returns a summary | Gets a self-contained prompt, returns a report file |
| Coordination | The main agent synthesizes | A named coordinator session merges |

Use whatever the harness provides: built-in subagents, background agents, messaging between sessions (for example `ListAgents` and `SendMessage` in Claude Code), isolated worktrees. If it provides none, run the same steps one after another.

## Subagents: fan out reading, keep writing central

- One independent question per subagent, with everything it needs; it does not share your history.
- Ask for a structured, sourced summary with a length limit. The main agent writes the docs.
- Good fan-outs: one per research topic when there are several; a few reference images each; one read-only auditor per milestone checking feature IDs; independent critics (security, accessibility, performance) before a merge.
- **Mind the cost.** Agents with tools use several times the tokens of a chat, and multi-agent runs many times more. A quick fact needs no subagent; a comparison of a few options needs two to four; a broad fan-out is rarely worth it for an MVP decision.
- When a subagent must write code (parallel fixes), give it an isolated worktree and the same rules a parallel session gets, and merge its result yourself.

## Should this run in parallel?

Say yes only if all of these hold:

- The plan is approved and the milestones touch **different files**. Overlap means conflicts, or one milestone quietly rebuilding another's UI.
- What they share can be pinned down as **contracts** before anyone starts.
- The machine can take it. Each session runs its own builds, tests, devices or servers. Recommend **2–4 writers**, in waves if there are more. Check cores and memory (`sysctl -n hw.ncpu` or `nproc`); a session with its own builds and a simulator or dev server wants about two cores and several GB of memory.
- The coordinator and the owner have time to merge and review what comes back.

Otherwise run milestones one after another and use subagents for research and review only. Say what you recommend and why; the owner may still choose more, and then make it as safe as you can.

## Asked for prompts before the project is ready

Don't hand out prompts that cannot work: a session without contracts or acceptance items will guess, and three sessions guess three different ways. Check readiness:

- [ ] The milestones are approved and each has acceptance items in `docs/product.md`.
- [ ] `AGENTS.md` has real smoke, build, test and run commands (no placeholders).
- [ ] The main branch is clean: work in flight is committed, parked on a branch, or becomes one of the sessions.
- [ ] The base and contracts are on the main branch, with tests.
- [ ] `docs/parallel-plan.md` is committed.

List what is missing, offer to do it now (most items take one focused pass), and give the prompts as soon as the list is done.

## 1. Land the base and freeze the contracts

Before any session starts, the coordinator puts on the main branch:

- **Shared foundations**: design tokens, base components, the app shell or entry point, domain models.
- **Contracts**: types and schemas, routes, API specs, events, stores, plus **mock implementations** so each session can run its part alone. Record them in `docs/architecture.md` › Interfaces.
- **Tests for the contracts**: they catch broken shared code once instead of in every session.
- **A toolchain check**: SDKs, simulators, runtimes and services all present. A missing tool found by every session at once blocks all of them.

Push the base, record its version, and name the coordinating session (for example "Main"). Only then tell the owner to launch sessions.

## 2. Write the parallel plan

`python3 <skill>/scripts/scaffold.py . --parallel` creates `docs/parallel-plan.md` and `docs/milestones/TEMPLATE.md`. Fill in:

- **Waves and sessions**: milestone, branch `milestone/<slug>`, worktree folder, reserved commit versions, and the isolated resources each session gets (ports, simulators, build caches, databases, `.env` copies).
- **Ownership map**: which paths each milestone may edit. Shared things (contracts, foundations, entry point, dependency manifests, `docs/` except the session's own report, `AGENTS.md`) belong to the coordinator.
- **Reserved names** per milestone (types, routes, tables, CSS classes).
- **Rules**: new shared pieces go in the session's own folder under a specific name (the coordinator promotes them); contract changes are requested in the report, never made; temporary edits to shared files are reverted before every commit; never merge or rebase the main branch into a session branch; never push to main.

Commit the plan to the main branch before sessions start, so every session reads the same rules.

## 3. Write one prompt per session

Fill `assets/prompts/parallel-session.md` once per session. Each prompt stands alone and states:

- The owner's pre-approval: plan and build end to end without stopping, commit and push **its own branch only**, record defaults instead of asking. Without this, every session stops and waits.
- What to read first, the isolation commands, its resources, what it must not edit, the secrets rules.
- Its scope, deliverables and the defaults for open questions.
- No large fan-outs of its own: they multiply machine load and cost.
- How to finish: report file, reserved versions, push, report back with the first line `<M> done: <branch> pushed at <hash>` (or ask the owner to paste the report), then stop.

Give the owner plain instructions: open N new sessions, paste one prompt into each, come back to the coordinator.

## 4. While sessions run

- Watch for reports. Agents that can message each other report directly; otherwise the owner pastes `docs/milestones/<m>.md` into the coordinator.
- Broadcast rule changes to every session at once when something shared changes.
- Answer contract questions with explicit conditions, and record them in the plan.
- **Never relay an approval the owner did not give.**
- For a session that went quiet, give the owner a short nudge prompt: finish the current step, write the report, push, report back.

## 5. Merge, integrate, review

For each finished branch, in dependency order where possible:

1. Merge into the main branch with a merge commit and the next free version.
2. Run the full verification gate.
3. Wire it in as a **separate commit**, following the report's integration steps.
4. Promote shared components built locally, and apply requested contract changes yourself.
5. Record the merge in the plan's Merge log.

After all merges, run a **consistency pass** (fresh-eyes subagents are good at it): duplicated components, different behavior for the same state, features nobody asked for, mismatched styles. Then bump to the next minor version above every reserved range (`0.8.0 - Integrate M2–M7`).

## 6. Sign-off and cleanup

- Sign off each milestone with the owner against its feature IDs.
- Remove worktrees (`git worktree remove`), delete merged branches (ask before deleting remote ones), shut down the extra simulators, servers and caches.
- **Delete `docs/parallel-plan.md` and `docs/milestones/`** once everything is merged: they are temporary and git keeps them.
- Update `docs/progress.md`: milestone statuses, decisions, next action.

## Parallel fixes during review rounds

When a review round has several independent areas, the coordinator can run them as background subagents in isolated worktrees:

- One shared brief: the owner's feedback verbatim with IDs, plus rules for every agent (owned paths, own port or device, one commit and no push, what to return: branch and hash, changes per feedback ID, interpretations, screenshots, test results, decisions needed).
- Merge (squash is fine) and version on the main branch yourself; run the gate after each.
- If the owner prefers it done in the main session, do that. Parallelism is a tool, not a rule.
