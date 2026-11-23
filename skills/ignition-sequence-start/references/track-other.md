# Track: CLIs, libraries, automations and everything else

For projects that are not a UI, a server or a model: command-line tools, libraries and SDKs, scripts and automations, data pipelines, browser extensions, bots, games. Same flow; "run it and look" means whatever the product's real use is.

## Questions

Ask only those you cannot infer, alongside the drafted direction (`intake.md` › 3).

1. **Who runs it and how**: a developer in a terminal, another program importing it, a schedule, a chat app, a browser?
2. **Where does it run**: the owner's machine (default), a server, a user's browser, CI?
3. **Anything it must connect to** (APIs, files, accounts)? Those may need keys: follow `security.md`.

## The draft

The message summarizes: interface (commands and flags, public API, triggers), language and packaging, dependencies, how it is tested, and how people get it. Write `docs/architecture.md` when there are several parts, external services or a public interface; a single script needs only `AGENTS.md` and `docs/product.md`.

## Defaults and checks by type

| Type | Default | Verify by | Ship |
|------|---------|-----------|------|
| CLI | Python (Typer) or TypeScript (Node) or Go for a single binary; `--help` that reads well | Running real commands, including bad input; output and exit codes | PyPI, npm or a GitHub release; Homebrew tap later |
| Library or SDK | The ecosystem's standard packaging; a tiny, typed public API | Tests on the public API; an example that runs from a clean install | PyPI or npm with a changelog; trusted publishing from CI |
| Script or automation | One file, standard library first, settings from the environment | A dry-run mode, then a real run on test data | A README with the exact command or schedule |
| Data pipeline | SQL or pandas/Polars; DuckDB locally, Postgres or a warehouse later | Row counts, schema checks, a sample of output rows | A scheduled job (GitHub Actions or the host's cron) with alerts on failure |
| Browser extension | Manifest V3 with the platform's official tooling | Loading it unpacked and using it on real pages | The Chrome Web Store or Firefox Add-ons (developer account: owner approval) |
| Bot | The platform's official SDK; webhooks over polling where possible | A test server or channel, real messages | Hosted on Render, Railway or Fly; the token in the host's secrets |
| Game | Godot, Phaser (web) or the owner's engine of choice | Playing the core loop; frame rate on target hardware | itch.io or a web link |

## Principles

- A small, obvious interface beats a flexible one. Good defaults; errors that say what to do next.
- Treat the README as part of the product: install, one example, done.
- Pin dependencies; test a clean install before every release.

## Pitfalls

Tools that only work on the author's machine (hard-coded paths, missing dependencies) · silent failures in scheduled jobs · breaking a public API without a major version · tokens committed in config files.
