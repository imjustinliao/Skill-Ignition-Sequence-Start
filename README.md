# Ignition Sequence Start

**Start any new project with your coding agent, and ship it.**

Describe your idea in plain words. The agent asks a few short questions, agrees a plan with you, then builds it in small, checked steps until it's live and ready to show people. It works for websites and apps, backends and APIs, full-stack products, ML models, hardware and firmware, CLIs and more. Switch chats, agents or accounts whenever you like: it picks up where you left off.

Works with Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot and most other coding agents. Made for people just starting with coding agents, and quick enough for pros.

## 1. Install

```bash
npx skills add imjustinliao/Skill-Ignition-Sequence-Start
```

Pick your agent when asked. Other ways to install are further down.

## 2. Start

Open a project folder in your agent and type:

```text
ignition sequence start
```

Best is an empty GitHub repository you've cloned, but any folder works. If there's no version history yet, the agent offers to set it up.

It asks about four short things:

1. What you're building, who it's for, and which parts it should build: the app people use, the server side, both, or something else (a model, a device, a CLI…)
2. What the first version must do
3. Your OK on the design and the architecture it proposes
4. Your OK on the plan

Answer in a few words, paste notes you already have, or say **"you suggest"**. Nothing is built until you approve the plan.

In a hurry? Type `ignition sequence start, express` and describe only the idea and the must-have features.

## 3. Keep going

After setup, just talk to your agent normally. These phrases also work in any agent, any time:

<!-- Keep in sync with skills/ignition-sequence-start/SKILL.md › Cheat sheet and assets/templates/AGENTS.md › Owner shortcuts. -->
| Say | What happens |
|-----|--------------|
| **continue** | Picks up where the last session stopped, even in another agent or account |
| **status** | Where things stand and what's waiting on you |
| **handoff** | Saves progress before you close the chat or switch |
| a numbered list of fixes | Each fix is tracked and reported back one by one |
| **new feature: …** | Added to the plan before any code is written |
| **add backend** | Adds a part you skipped at the start (or the frontend, a mobile app, …) |
| **change …** | Updates anything from setup, for example *"change the plan: do login first"*, *"update the design: darker colors"* |
| **keep going** | Works on its own while you're away, within limits you agree first |
| **faster** / **slower** | Fewer check-ins, or more explanation and smaller steps |
| **ship it** | Gets it live or published, with your OK at each public step |
| **help** | Shows this list |

That's it. The rest is optional.

---

## Switching chats, agents or accounts

- Everything that matters lives in your project's files, not in the chat, so a new chat or a different agent can continue right away.
- Hit a usage limit mid-task? Open another account or agent in the same folder and say **continue**. If the last chat ended before it saved its progress, the agent finds that chat on your computer (Claude Code, Codex, Gemini CLI and Copilot CLI) and picks up from there.
- Moving to another computer? Say **handoff** first, so everything is pushed.

## Your keys stay yours

- Never paste API keys or passwords into the chat: chats are sent to the AI provider and saved on your computer.
- When a key is needed, the agent tells you exactly where to get it and where to put it (a local `.env` file or your hosting dashboard). It never reads or prints the values.
- Setup adds guards: `.gitignore` rules for secret files, rules that stop Claude Code reading them, ignore files for Cursor and Gemini, and a check that scans for leaked keys before every push.
- If a key ever ends up in a chat or a commit, the agent tells you to replace it right away.

## Your project's docs

Everything you decide is written into a few plain Markdown files, and the agent keeps them current and tidy:

```
AGENTS.md              how agents work on this project (read automatically)
docs/product.md        your idea, users, goals, and the features with IDs
docs/progress.md       the plan, where things stand, feedback, decisions
docs/design.md         how it looks and feels (when it has a user interface)
docs/architecture.md   how it's built: stack, data, interfaces (when there's more than a UI)
```

No other notes files pile up: at the end of each stage the agent proposes removing unused files, assets and code. You can read and edit these files yourself any time; the next agent follows your version.

<details>
<summary><b>Run several agents in parallel</b></summary>

After the plan is approved, ask for it, for example: *"run M3 and M4 in parallel"*.

The agent checks that the work splits cleanly, sets up shared contracts and rules for who edits what, and gives you one prompt per agent. Each agent works on its own branch and reports back when done. The first agent merges everything and reviews it with you. Two to four agents at once works best.

</details>

<details>
<summary><b>Other ways to install</b></summary>

**Claude Code plugin**

```text
/plugin marketplace add imjustinliao/Skill-Ignition-Sequence-Start
/plugin install ignition-sequence-start@skill-ignition-sequence-start
```

**Manual:** copy `skills/ignition-sequence-start/` into your agent's skills folder.

| Agent | Folder |
|-------|--------|
| Claude Code | `~/.claude/skills/` |
| Codex, Cursor, Gemini CLI, Copilot, OpenCode, Goose, Amp and most others | `~/.agents/skills/` |

**Claude apps:** zip the `ignition-sequence-start` folder and upload it under Customize › Skills.

**Agents without skill support** (such as Aider): ask the agent to read `skills/ignition-sequence-start/SKILL.md` from this repo and follow it.

</details>

<details>
<summary><b>If an agent doesn't pick up where you left off</b></summary>

Paste this into the agent. It works even without the skill installed:

```text
Continue this project. Read AGENTS.md and docs/progress.md, check git, then tell me in three lines where things stand and what's next. If progress.md doesn't explain the latest work, look for the previous chat for this folder before guessing.
```

</details>

<details>
<summary><b>Customize it</b></summary>

Fork this repo and edit:

- `skills/ignition-sequence-start/assets/templates/AGENTS.md`: default rules, approvals, commit format
- `skills/ignition-sequence-start/references/intake.md`: the setup questions
- `skills/ignition-sequence-start/references/track-*.md`: the defaults per kind of project

</details>

<details>
<summary><b>How the skill is organized</b></summary>

```
skills/ignition-sequence-start/
├── SKILL.md         entry point: picks what to do from your repo and your words
├── references/      guides loaded only when needed: setup, build loop, continuity,
│                    security, parallel work, and one track per kind of project
│                    (frontend, backend, ML, hardware, other)
├── assets/          templates copied into your project, plus prompts
└── scripts/         scaffold.py (creates the docs), check.py (health and secret scan),
                     sessions.py (finds earlier chats for a folder)
```

</details>

<details>
<summary><b>What it's built on</b></summary>

The workflow distills published practice from people and teams who build with coding agents every day:

- Anthropic: [Claude Code best practices](https://code.claude.com/docs/en/best-practices), [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Boris Cherny's Claude Code workflow ([InfoQ](https://www.infoq.com/news/2026/01/claude-code-creator-workflow)) and Thariq Shihipar ([Latent Space](https://latent.space/p/thariq)): verification loops, plan first, small instruction files
- OpenAI: [Harness engineering](https://openai.com/index/harness-engineering/), [AGENTS.md](https://agents.md)
- Cursor: [Agent best practices](https://cursor.com/blog/agent-best-practices), Michael Truell's [The third era](https://cursor.com/blog/third-era)
- Andrej Karpathy: [Software Is Changing (Again)](https://www.latent.space/p/s3) (keep AI on a leash, small diffs) and [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/)
- Andrew Ng: [Three key loops](https://www.deeplearning.ai/the-batch/three-key-loops-for-building-great-software), [Agentic coding and testing](https://www.deeplearning.ai/the-batch/agentic-coding-and-agentic-software-testing-go-together)
- Y Combinator: [One order of operations for starting a startup](https://www.ycombinator.com/blog/one-order-of-operations-for-starting-a-startup)
- [Choose boring technology](https://boringtechnology.club/), Apple's [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/), [MCP security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)

</details>

## License

[MIT](LICENSE) © 2026 Justin Liao
