# Continuity: chats, agents, accounts and machines

A project outlives every chat. The owner opens a fresh chat, switches agent (Codex to Cursor), switches account in the same tool after hitting a usage limit, moves to another machine, or a session simply dies mid-task. All of these are the same event: **the next agent reads the repo and continues.** Chat transcripts are a fallback for what the repo missed.

## Contents

- Leaving: keep the handoff current
- Arriving: the resume check
- Finding the last chat
- Switching agents
- Switching accounts
- Switching machines
- Two agents at once
- Context compaction
- Signs the docs are stale

## Leaving: keep the handoff current

Don't wait for "handoff". Sessions end without warning, so after every commit and before any long step, keep `docs/progress.md` › Now current:

- **Phase** and **Milestone**.
- **Next action**: one concrete step, and whether the owner approved it.
- **In flight**: branch, uncommitted files, the half-done step, running jobs or servers, anything a newcomer would trip over. "none" when clean.

On "handoff", when context runs low, or before ending a session, also:

1. Commit finished work if the approval mode allows; otherwise list exactly what is uncommitted and why.
2. Make sure feedback items show their real status.
3. Add one session-log line: date, agent and tool, version, what happened.
4. Push if switching machines or at a milestone end (a work-in-progress branch is fine; name it in In flight).

Write for a stranger: no "as discussed", no references to the chat.

## Arriving: the resume check

1. Read `AGENTS.md` (usually loaded automatically), then `docs/progress.md`. Check `git status`, `git log -5` and the current branch.
2. If this skill is installed, run `python3 <skill>/scripts/check.py` and read its warnings, then `python3 <skill>/scripts/sessions.py`. **Always**, not only when something looks off: a chat cut off by a usage limit leaves nothing in the docs to say so. Read its flags: "newer than docs/progress.md" or "ended at a usage limit" on a chat that is not this one means work was cut off.
3. Checklist:
   - Does git match `progress.md`: last commit, branch, In flight? Does the last commit's content match its message?
   - Placeholders left in `AGENTS.md`, or open Setup items? Offer to finish them before building.
   - Did the owner edit `docs/` or `AGENTS.md` since the last session (`git log -- docs AGENTS.md`)? Mention it and follow their version.
   - Is the approval mode blank? Treat it as `ask`.
   - Is the version marker at the top of `progress.md` older than this skill (or missing)? Offer the upgrade at a safe point for the project's stage (`upgrade.md`).
4. **Take over the earlier chat when any of these hold**: `sessions.py` flags a chat as newer than `progress.md` or ended at a usage limit; `progress.md` does not explain the latest commits or uncommitted changes; In flight describes work you cannot see; or the owner says they are continuing or switching. Read its tail (`sessions.py --show 20`, below) before answering or guessing, and say which chat you took over. Never start fresh when an unsaved earlier chat exists.
5. Reply to the first message:
   - Greeting or "where were we": three lines (phase, last done, next action and anything in flight), plus a short Discrepancies list with numbered questions. Then wait for a go.
   - "Continue" or "go": start the approved next action.
   - A specific task: one line of orientation, any discrepancy that affects it, then the task within current approvals. A new feature is new scope (`workflow.md`).

Plain factual slips in `progress.md` (a branch name, a missing log line) can be fixed on arrival; say so. Ask before changing meaning, scope or a decision.

## Finding the last chat

When the repo does not explain where work stopped, or the owner says "continue from my other chat":

1. **Same tool**: its own resume brings back the full context.

| Tool | Resume |
|------|--------|
| Claude Code | `claude --continue` (latest in this folder), `claude --resume` (pick, or pass an id) |
| Codex | `codex resume` (pick), `codex resume --last`; `--all` includes other folders |
| Gemini CLI | `gemini --resume`, `gemini --list-sessions` (run in the project folder) |
| Copilot CLI | `copilot --continue`, `copilot --resume` |
| Cursor | the chat history panel; CLI: `agent ls`, `agent resume` |
| Others | the tool's chat history |

2. **Another tool or account on this machine**: run `python3 <skill>/scripts/sessions.py` in the project folder. It lists this folder's chats from Claude Code (every config folder with a `projects/` folder: `~/.claude*`, nested ones like `~/.claude/spares/*`, `~/.config/claude*`, `CLAUDE_CONFIG_DIR`, plus any in `IGNITION_CLAUDE_DIRS`, so separate accounts are covered), Codex (including compressed transcripts), Gemini CLI and Copilot CLI, newest first, with the resume command for each. `--show 20` prints the newest chat's last messages, redacted.
3. **Use it, don't copy it.** Read only the tail, write what was in progress into `progress.md` › Now in your own words, tell the owner which chat you used, and confirm the next action. Never paste transcript text into the repo.
4. **Without the script**, check the locations below yourself, or ask the owner to resume in the original tool and say "handoff" there.

If a new agent skips the arrival check, the owner can paste this (it works without the skill installed):

```text
Continue this project. Read AGENTS.md and docs/progress.md, check git, then tell me in three lines where things stand and what's next. If progress.md doesn't explain the latest work, look for the previous chat for this folder before guessing.
```

| Tool | Where chats live | How a chat maps to the project |
|------|------------------|--------------------------------|
| Claude Code | `~/.claude/projects/<folder>/<id>.jsonl` (moved by `CLAUDE_CONFIG_DIR`; deleted after 30 days by default) | `<folder>` is the project path with every non-alphanumeric character as `-`; each line has `cwd` |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` or `.jsonl.zst` (moved by `CODEX_HOME`) | first line `session_meta` › `payload.cwd` |
| Gemini CLI | `~/.gemini/tmp/<project hash>/chats/` | hash of the project path |
| Copilot CLI | `~/.copilot/session-state/<id>/events.jsonl` (moved by `COPILOT_HOME`) | the path appears in the events |
| Cursor, Windsurf, Cline, IDE chats | the tool's own database | open the tool's history |

Transcripts are plain text and hold whatever the owner pasted, secrets included. Read them only for this project, only to continue the work, and never repeat a secret you see; tell the owner to rotate it instead.

## Switching agents

- `AGENTS.md` is the single rule file; other tools get a pointer (table below), never a copy, so rules cannot drift. Adding a tool mid-project means adding its pointer: `python3 <skill>/scripts/scaffold.py . --agents <tool>`.
- Keep tool-specific state out of the docs: session ids, local paths, a personal device name. Personal preferences go in the tool's local settings.
- Tools differ (subagents, browsers, simulators, messaging). The docs say *what* to verify; each agent picks *how*, and reports what it could not check.

| Agent | Reads `AGENTS.md` | Pointer (`scaffold.py --agents`) |
|-------|-------------------|----------------------------------|
| Codex, Cursor, GitHub Copilot, OpenCode, Windsurf, Amp, Goose and most others | Natively | None (`cursor` adds `.cursorignore`) |
| Claude Code | Natively only when there is no `CLAUDE.md` | `CLAUDE.md` with `@AGENTS.md`, plus `.claude/settings.json` deny rules |
| Gemini CLI | When configured | `GEMINI.md` with `@AGENTS.md`, plus `.geminiignore` |
| Aider | When configured | `.aider.conf.yml` with `read: AGENTS.md` |
| Cline, Zed and others | Varies | One line in the tool's rules file: "Read and follow AGENTS.md in the repository root." Make sure no other rules file shadows it. |

Some agents cap instruction files (Codex reads 32 KiB of `AGENTS.md` by default), one more reason to keep it short. Support changes often; check the agent's current docs when unsure.

## Switching accounts

- Same tool, same machine: chats belong to the folder, not the account. Claude Code, Codex and Copilot CLI keep them locally, so after logging in with another account `claude --resume` or `codex resume` usually still finds them.
- If each account uses its own config folder (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`), the new account won't list the other's chats. `sessions.py` searches every Claude config folder it can find and prints the right resume command (with the `CLAUDE_CONFIG_DIR=` prefix the other account needs). If the other account's folder is somewhere unusual, set `IGNITION_CLAUDE_DIRS=/path/one:/path/two`. It also flags a chat that ended at a usage limit.
- **After a usage limit the chat stopped mid-task and `progress.md` is probably behind.** On "continue", find that chat first (`sessions.py --show 20`), finish the interrupted step from it, then bring `progress.md` up to date. Don't ask the owner to explain what was happening; the transcript says.
- Account-tied things do not move: synced skills and plugins, MCP logins, usage limits. Check the new account has the MCP servers and logins the project needs.
- A usage limit hitting mid-task is the usual reason to switch, which is why Now must always be current.

## Switching machines

Only the repo travels. Commit and push first (a work-in-progress branch is fine). Chats stay on the old machine. Secrets never travel through git: on the new machine the owner recreates `.env` from `.env.example` and their secret manager.

## Two agents at once

Two agents writing in the same checkout overwrite each other and confuse git. Give each writer its own worktree and branch (`git worktree add ../<repo>-<name> -b <branch>`), or keep all but one read-only (reviewing, researching, answering questions). If both must change code, set it up as parallel work (`parallel.md`).

## Context compaction

When a conversation is about to be summarized, details not written down are at risk. Before it happens (or right after): put exact commands, IDs, flags, device names and gotchas the next steps depend on into `progress.md` › In flight. Recurring project knowledge (how to launch a debug screen, a flaky test) goes into `AGENTS.md` or `docs/architecture.md`.

## Signs the docs are stale

- The Next action is already done in git.
- A milestone is "in progress" with no commits for a long time.
- Decisions contradict the code.
- The owner corrects something the docs state.
- `check.py` warns that commits are newer than the session log.

Fix the docs first, then continue. Stale docs mislead every agent that comes after.
