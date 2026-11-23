---
name: ignition-sequence-start
description: Takes a new project from idea to shipped MVP with any coding agent - frontends, backends or both, ML models, hardware, CLIs. Asks only what matters, records decisions in a lean AGENTS.md plus docs/, and builds in small verified milestones with security, cleanup and refactoring built in. Keeps work resumable across chats, agents, accounts and machines, including finding the previous chat. Plain words for beginners, terse for pros. Use when the user says "ignition sequence start", starts a new project, says continue or asks for status, switches agent or account, adds a frontend, backend or features, needs API keys or accounts set up, wants to ship, or wants parallel agents.
license: MIT
compatibility: Any coding agent that can read files and run shell commands. Python 3.8+ is optional, for the scripts.
metadata:
  author: Justin Liao
  version: "0.3.0"
---

# Ignition Sequence Start

Takes a new idea from an empty folder to a shipped MVP with any coding agent: a website or app, a backend or API, both, a trained model, firmware and a device, a CLI or a library. The owner talks in plain language; the agent asks only what it needs, recommends a default for the rest, builds in small verified steps, and keeps the project in the repo so any agent, account or machine can carry on.

`<skill>` means this skill's folder. Reference paths are relative to it; run scripts from the project folder as `python3 <skill>/scripts/<name>.py`.

## Principles

Drawn from how leading agentic-coding practitioners and teams work (sources in the README):

- **Ask little, decide well.** Never ask what the owner already said or the folder shows. Ask only when the decision is theirs: money, data, architecture, design direction, anything public or irreversible. Every question carries a recommended answer.
- **Success criteria over instructions.** Every milestone has a check the agent runs itself and shows; nothing is done on assumption.
- **Small steps, human at the decision points.** Autonomy grows with trust and the owner's experience, not by default. Follow their pace.
- **Plan, then build; re-plan instead of patching.** After two failed attempts at the same thing, stop and rethink.
- **Settle what is expensive to reverse first** (data model, auth, stack, parts to buy); decide everything else just in time.
- **Simplest thing that works.** Boring, managed technology and no speculative layers; agents over-build, so watch for it. Defaults are starting points: the owner's preferences and constraints win.
- **The repo is the memory.** Rules, goals, decisions and status live in a few files; chat history is a fallback, never the source of truth.
- **The stakes set the care, and shipping is the goal.** An MVP gets speed on a clean base; launch means real people using it.
- **Fix repeated mistakes at the strongest level.** Make it impossible, then catch it with a test or lint, and only then add a written rule. Process is scaffolding: delete what no longer helps.

## Route the request

Whenever project docs exist, run the arrival check first (`references/continuity.md` › Arriving) and lead with its short status. Then:

| Situation or phrase | Do | Read |
|---------------------|----|------|
| "Ignition sequence start" or a new idea, and no `AGENTS.md` yet | **Setup** | `references/intake.md`, then the track files below |
| "Ignition sequence start" in a project already set up | **Resume**, then offer to revisit a setup step | `references/continuity.md` › Arriving |
| `docs/progress.md` › Setup has open items | **Continue setup** at the first open item | `references/intake.md` |
| Docs exist; new chat, agent or account; "continue", "where were we" | **Resume** | `references/continuity.md` › Arriving |
| "Continue from my other chat", or `progress.md` doesn't explain the latest work | **Find the last chat** | `references/continuity.md` › Finding the last chat |
| "Handoff", switching agent, account or machine, context running low | **Hand off** | `references/continuity.md` › Leaving |
| "Status", a list of fixes, "new feature", "add backend", "change …", "clean up", "keep going" | **Build loop** | `references/workflow.md` (matching section) |
| "Ship it", deploy, publish, launch | **Ship** | `references/workflow.md` › Shipping, then the track file |
| API keys, accounts, logins, billing, anything secret | **Handle access safely** | `references/security.md` |
| "Run these in parallel", prompts for other agents, broad research | **Parallel work** | `references/parallel.md` |
| An established codebase, not a new project | Say the skill is built for new projects; offer a light setup | `references/intake.md` › Existing code |
| "Help", "what can I say" | Show the cheat sheet | — |

If the situation is unclear, say what you found and ask.

## Setup

Read `references/intake.md`, then the track file for each part the owner wants built:

| Part | Track file | Adds |
|------|------------|------|
| Anything people see or touch: web, mobile, desktop | `references/track-frontend.md` | `docs/design.md` |
| Servers, APIs, data, accounts, integrations | `references/track-backend.md` | `docs/architecture.md` |
| A model: training, fine-tuning, evaluation | `references/track-ml.md` | `docs/architecture.md` |
| Firmware, electronics, a physical device | `references/track-hardware.md` | `docs/architecture.md` |
| CLI, library, automation, pipeline, extension, bot, game | `references/track-other.md` | `docs/architecture.md` when there are parts or contracts |

Four exchanges, after a read-only look around; nothing is written until the owner agrees:

| # | Owner gives | Agent writes |
|---|-------------|--------------|
| 1 | The idea and who it's for; which parts to build here and who builds the rest; OK to create files and, separately, to turn on version history | `git init` if agreed, then the skeleton via `scripts/scaffold.py` |
| 2 | What the first version must do, in any form, or "you suggest" | `docs/product.md`: features with IDs, the MVP cut |
| 3 | For each part, one reply: a few answers and a yes to the drafted direction | `docs/design.md`, `docs/architecture.md` |
| 4 | A yes to the milestone plan and the working defaults | `docs/progress.md`, `AGENTS.md`, first commit |

Messages stay short: about 150 words and at most three numbered questions, each with a default, ending with what to type next. Proposals lead with a plain summary; the detail goes into the doc, marked "proposed" until approved. "Express" setup is one message and one approval. Never build during setup.

## Building

Each milestone: plan with a runnable "done when" check, build in small focused changes, verify like a user and show the evidence, commit per the approval mode, then a fresh-eyes review, a tidy and refactor pass, and an update to `docs/progress.md`. Security always; performance and scale as far as the goals need. Details: `references/workflow.md`.

## Working with the owner

- **Match their experience** (`AGENTS.md` › Project; `references/intake.md` › Match the owner). When unsure, start plain.
- **Wait at every gate.** "Faster" means bigger steps and fewer check-ins; "slower" means smaller steps and more explanation.
- **When the owner must act** (an account, billing, a key, a device), give numbered steps: console clicks for beginners and one-off tasks, the CLI for pros and repeatable ones. Say why, what it costs, and what they should see. Secrets go into `.env` or the host's settings, never into the chat.
- **Approvals mean exactly what was approved.** Read a short "ok" back with its scope; never assume or relay one.

## Use what the harness offers

Check what this agent can do rather than assume: plan mode for plans; subagents for independent research and fresh-eyes reviews; a browser or simulator to check UI; documentation MCP servers for current library docs before general search; messaging between sessions for parallel work; hooks to enforce checks. Use MCP servers only from trusted publishers with the narrowest access. If something cannot be verified with the tools at hand, say so and list it for the owner.

## Scripts

Run them; no need to read them first. Python 3.8+ standard library only.

- `scaffold.py . --name "<Name>" [--with design,architecture] [--agents claude,cursor,gemini,aider] [--parallel] [--dry-run]`: creates the docs and secret guards and a git pre-push hook that blocks leaked secrets. Never overwrites.
- `check.py`: health check: unfinished setup, docs vs git, tracked secrets and key patterns, stray Markdown files, oversized docs. Run on arrival and before a handoff.
- `sessions.py [--show N]`: finds earlier chats for this folder in Claude Code, Codex, Gemini CLI and Copilot CLI (any account on this machine), with resume commands; `--show` prints the last messages of the most recent earlier chat, redacted.

Without Python, copy `assets/templates/` by hand (`gitignore` → `.gitignore`, `claude-settings.json` → `.claude/settings.json`) and find chats as `references/continuity.md` describes.

## Cheat sheet

Show this when setup ends and whenever the owner asks for help, in the owner's language:

<!-- Keep in sync with README.md › Keep going and assets/templates/AGENTS.md › Owner shortcuts. -->
```text
You're set up. From here, just talk to me normally. These also work in any agent:

  continue        pick up where we left off (new chat, another agent or account)
  status          where things stand and what's waiting on you
  handoff         save progress before closing the chat or switching
  1. … 2. …       a numbered list of fixes, each tracked and reported back
  new feature: …  added to the plan before any code
  add backend     add a part you skipped (or frontend, a mobile app, …)
  change …        update anything from setup: goal, features, design, plan, rules
  keep going      work on its own while you're away, within limits you agree first
  faster/slower   fewer check-ins, or more explanation
  ship it         get it live or published, with your approval at each public step
  help            show this list
```
