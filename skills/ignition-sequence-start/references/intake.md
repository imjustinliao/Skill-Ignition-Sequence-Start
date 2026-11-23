# Setup: from idea to approved plan

Setup turns the owner's idea into a plan any agent can build from, in about four short exchanges. Ask only what changes the plan. Decide everything else with stated defaults the owner can change at any time.

## Contents

- How every exchange works
- Before the first message: look around
- 1. The idea and the parts
- 2. MVP features
- 3. Direction for each part
- 4. The plan and how we'll work
- Express setup
- Match the owner
- Folder, git and GitHub
- Cost-aware research
- Existing code
- Out-of-order input

## How every exchange works

1. **One topic per message**: about 150 words, at most three numbered questions, each with a recommended answer. End with what to type: "You can reply: 1 yes, 2 both, 3 you suggest". "You suggest" accepts every default in that message.
2. **Never ask what you already know.** Skip questions the owner has answered or the folder shows, and merge exchanges when the answers are already in hand.
3. **Capture faithfully.** Keep the owner's words and order. Never drop or "improve" a requirement; interpretations go to Open questions, each with a default.
4. **Write the file, then show a short summary** of what it now says and what is still open.
5. **Tick the item** in `docs/progress.md` › Setup and set Next action, so another agent can continue mid-setup.
6. **Gate.** Wait for the owner. Never build during setup. When a short "ok" follows several questions, say what you take it to cover.

"Skip" or "later" on anything: mark it `- [~] skipped`, use the defaults, log them as one dated entry in `progress.md` › Decisions, continue. Pasted notes or documents are welcome: take them whole and split them into the right files.

## Before the first message: look around

Read-only: what is in the folder, git status and remote, the OS, tools relevant to likely stacks (`git`, `node`, `python3`, `gh`, `docker`, platform SDKs), and what this agent can do (subagents, browser or simulator, MCP servers, messaging). Install, download or create nothing yet; anything networked needs the owner's yes.

## 1. The idea and the parts

Open plainly, then ask:

```text
Ignition sequence start. We'll set this up in a few short steps and agree a plan before any code.
Answer in a few words, paste notes you have, or say "you suggest".

1. What are you building, and who is it for?
2. Which parts should I build here: the app people use (frontend), the server and data side
   (backend), both, or something else (a model, a device, a CLI…)? If just one: who builds the
   other side, or is it for later?
3. May I create the project files? And turn on version history (git), so every change can be
   undone? (recommended: yes to both)
```

Drop the git part of question 3 if git already exists. Infer the owner's experience from how they write; if it is unclear, ask in the next message ("Have you built software before? no / a bit / yes").

On yes:
- `git init -b main` first, if they agreed and there was no repository.
- Scaffold: `python3 <skill>/scripts/scaffold.py . --name "<Name>" --with <docs> --agents <agents>`. Docs: `design` for anything with a user interface; `architecture` for servers, data, a model, hardware, or a contract with another team. Agents: this one plus any the owner mentioned (`continuity.md` › Switching agents). In a git repository it also installs the pre-push secret check.
- Fill `AGENTS.md` › Project (pitch, built here, owner's experience). Tick the first two Setup items.

If they decline git: set `AGENTS.md` › Git to mode `none`, skip every commit step, treat deletions as permanent (ask each time), and offer git again at the first milestone end.

**One part only.** If the owner builds just the frontend, the backend contract goes in `docs/architecture.md` › Interfaces and the frontend runs on mocks behind it; ask whether the other team already has an API spec to paste or link, and use it as the contract. If just the backend, the same section holds the API the frontend team will build against. Either way, adding the other part later is normal (`workflow.md` › Adding a part).

## 2. MVP features

Ask what the first version must do, in any form: a list, a story, a pasted doc.

- Give every feature a stable ID by area (`AUTH-01`, `FEED-02`, `FW-01`) with acceptance items in the owner's words. Re-read the source against the file: nothing dropped, down to the last sub-item.
- **Propose the cut**: the one core workflow, end to end, sized to about two or three weeks of work. Everything else goes to Later, with a one-line reason: launch fast, then learn from real users.
- Fill Pitch, Users and Goals. Ask about targets (users at launch, budget, deadline) only where they change decisions.
- Ask at most three open questions now: the ones that change the architecture or the design. The rest wait for the milestone that needs them, with a default.

Write `docs/product.md`.

## 3. Direction for each part

One message per part (combine them when small), so one reply both answers and approves:

1. Research only what blocks the decision (below), then draft **one** direction from the track file's defaults and what you already know. Track defaults are starting points: the owner's preferences, existing accounts and constraints win, and versions and prices must be checked as current. Write it to the doc (`docs/design.md` for the frontend; `docs/architecture.md` for backend, model, hardware or other, including monthly cost and the accounts the owner will need), with Status: proposed.
2. Send a plain summary of about 150 words plus at most three of the track's questions that you could not answer yourself, each with your default. "You can reply: looks good; or 1 dark only, 2 …"
3. On the owner's yes, apply their answers, set Status: approved with the date, and tick the item.

Hard-to-reverse choices need that explicit yes: stack, data model, auth, hosting and its cost, paid services, parts to buy. Money and sharing data with third parties are always called out on their own line.

## 4. The plan and how we'll work

Propose milestones in `docs/progress.md` › Milestones:

- **M1 is the thinnest runnable slice**: the app opens, the endpoint answers, the model trains on 100 samples, the LED blinks. Its "done when" includes filling the smoke, build, test, run and preview commands in `AGENTS.md`, and the owner opening the live preview themselves (in the harness's preview pane, if it has one).
- Each milestone: feature IDs, a "done when" check the agent can run, and what the owner will see.
- **The last MVP milestone is Ship** (`workflow.md` › Shipping).
- Mark milestones that could run in parallel once a base exists (`parallel.md`). The default is one agent.

Show the working defaults in one short block: approval mode `auto-commit` (commit after each passing check, push at milestone end after sign-off; `ask` if they prefer to approve every commit), the commit format, working on `main`. "Change any of these now or any time."

On approval:
- Fill the remaining `AGENTS.md` placeholders. Commands that only exist after M1 read "none yet (M1)".
- Set Phase to Building, remove the Setup section, add the first session-log line, run `python3 <skill>/scripts/check.py`.
- Commit (`0.0.1 - Set up project docs and plan`) unless git is off; push only if a remote exists and the owner agrees.
- Show the cheat sheet from `SKILL.md`, then start M1 when they say go.

## Express setup

For "express", "just build", "skip the questions": send one message with what you found, the parts you assume, the default direction for each part, and the working defaults. Ask only for the idea, who it is for, and the must-have features. A yes approves all of it. Log the defaults used as one dated entry in `progress.md` › Decisions, so they stay visible after the Setup section is removed.

## Match the owner

**New to coding**:
- Plain words: "stack" → "the tools it's built with"; "repo" → "project folder"; "commit" → "save a version"; "push" → "upload to GitHub"; "deploy" → "put it online"; "milestone" → "stage"; "environment variable" → "a setting stored outside the code".
- Recommend, don't ask. One step at a time. Say how they will see progress ("after each stage you'll open it in your browser").
- When they must do something (an account, a key, plugging in a device), give click-by-click steps and what they should see. Don't assume terminal skills; when a command is needed, give exactly one and say what it does.
- Explain an error in one line, then the fix.

**Some experience**: brief explanations; the why on request.

**Pro**: terse and technical; ask about stack preferences directly; CLI first.

## Folder, git and GitHub

- Best start: an empty GitHub repository, cloned and opened in the agent. Any folder works too.
- No git: offer `git init` in one line ("version history, so every change can be undone").
- No remote: fine for now. Offer GitHub when they want a backup or to ship. Beginners: the github.com/new steps and the two commands that connect the folder. Pros: `gh repo create <name> --private --source . --push`. Logins that open a browser (`gh auth login`) are run by the owner.
- The agent was started outside a project folder (for example the home folder): ask the owner to create and open a project folder, with the steps for this tool.
- A monorepo (several apps in one repository): one root `AGENTS.md` with shared rules, a short nested `AGENTS.md` per package for its own commands, one `docs/` at the root.

## Cost-aware research

- Research only what changes a decision in the plan. One pass, then plan.
- Scale effort to the question: a fact is one quick lookup; comparing two or three options is a few lookups, or 2–4 subagents if the harness has them; never a broad fan-out for an MVP decision. Subagents and deep research multiply token cost.
- Prefer primary sources: official docs, changelogs, pricing pages. Note dates; check versions are current.
- Prefer what fast, highly technical teams use and document (managed services, the platform's official starters, boring technology) over novelty. Spend novelty only on what makes the product different.
- Record each choice and its source in the "Why" column of `docs/architecture.md` or in `docs/design.md`. No separate research notes.
- Money is a cost too: free tiers first, state the monthly cost, set spend limits (`security.md`).

## Existing code

This skill is built for new projects. A folder with a README, a starter template or a few files counts as new. In an established codebase, say so and offer a light setup: an `AGENTS.md` map (commands, how to verify, do-nots) plus `docs/progress.md`, with inferred facts marked "(inferred; confirm)". Merge any existing agent rules (`CLAUDE.md`, `.cursor/rules`, `.github/copilot-instructions.md`) into `AGENTS.md`, turn the old files into pointers, and show what moved where. Never silently discard someone's rules.

## Out-of-order input

When the owner says something that belongs to another exchange (a design idea while listing features), write it where it belongs now, say where, and continue.
