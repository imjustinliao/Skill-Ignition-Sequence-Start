#!/usr/bin/env python3
"""Create the Ignition Sequence Start files in a new project. Never overwrites anything.

Usage:
    python3 scaffold.py <project-dir> [--name NAME] [--with design,architecture]
                        [--agents claude,gemini,cursor,aider] [--parallel] [--no-hook] [--dry-run]

Run it after `git init`, so the secret guards can be checked and the pre-push hook installed.

Always:   AGENTS.md, docs/product.md, docs/progress.md, and .gitignore if there is none.
--with design        docs/design.md, for anything with a user interface.
--with architecture  docs/architecture.md, for a backend, data, APIs, a model, hardware,
                     or a contract with another team.
--agents             extra files for the agents the owner uses (default: claude):
    claude  CLAUDE.md (imports AGENTS.md) and .claude/settings.json (blocks reading secret files)
    gemini  GEMINI.md (imports AGENTS.md) and .geminiignore
    cursor  .cursorignore
    aider   .aider.conf.yml (loads AGENTS.md)
    Codex, Copilot, OpenCode, Windsurf, Amp and most others read AGENTS.md as is.
--parallel           docs/parallel-plan.md and docs/milestones/TEMPLATE.md (temporary files).
--no-hook            skip the git pre-push hook that runs `check.py --secrets` before every push
                     (installed by default in git repositories that have no pre-push hook yet).
--dry-run            list what would be created and write nothing.

Template lines ending in <!-- if:design --> or <!-- if:architecture --> are kept only when that
doc is created, so AGENTS.md and progress.md never point at files that do not exist.
{{PROJECT_NAME}} (with --name) and {{DATE}} are filled in; the agent fills the other placeholders.
Python 3.8+ standard library only.
"""

import argparse
import datetime
import pathlib
import re
import shlex
import stat
import subprocess
import sys

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates"

# (template file, path in the project)
BASE = [
    ("AGENTS.md", "AGENTS.md"),
    ("docs/product.md", "docs/product.md"),
    ("docs/progress.md", "docs/progress.md"),
    ("gitignore", ".gitignore"),
]
DOCS = {
    "design": [("docs/design.md", "docs/design.md")],
    "architecture": [("docs/architecture.md", "docs/architecture.md")],
}
AGENTS = {
    "claude": [("CLAUDE.md", "CLAUDE.md"), ("claude-settings.json", ".claude/settings.json")],
    "gemini": [("GEMINI.md", "GEMINI.md"), ("ignore-secrets", ".geminiignore")],
    "cursor": [("ignore-secrets", ".cursorignore")],
    "aider": [(".aider.conf.yml", ".aider.conf.yml")],
}
NATIVE = {"codex", "copilot", "opencode", "windsurf", "amp", "goose", "other", "none"}
PARALLEL = [
    ("docs/parallel-plan.md", "docs/parallel-plan.md"),
    ("docs/milestones/TEMPLATE.md", "docs/milestones/TEMPLATE.md"),
]
CONDITION = re.compile(r"\s*<!-- if:(\w+) -->\s*$")
CHECK = pathlib.Path(__file__).resolve().parent / "check.py"
HOOK = """#!/bin/sh
# Added by ignition-sequence-start: stops a push that contains secret files or key patterns.
# Delete this file to turn it off. It does nothing if Python or the skill is not available.
CHECK=%s
command -v python3 >/dev/null 2>&1 || exit 0
[ -f "$CHECK" ] || exit 0
exec python3 "$CHECK" --secrets "$(git rev-parse --show-toplevel)"
"""


def csv(value):
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("project_dir", type=pathlib.Path)
    parser.add_argument("--name", help="project name for {{PROJECT_NAME}}")
    parser.add_argument("--with", dest="docs", type=csv, default=[],
                        help="optional docs: design, architecture")
    parser.add_argument("--agents", type=csv, default=["claude"],
                        help="agents the owner uses (default: claude)")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--no-hook", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    unknown_docs = set(args.docs) - set(DOCS)
    unknown_agents = set(args.agents) - set(AGENTS) - NATIVE
    if unknown_docs:
        parser.error("unknown --with value(s): " + ", ".join(sorted(unknown_docs)))
    if unknown_agents:
        parser.error("unknown --agents value(s): " + ", ".join(sorted(unknown_agents))
                     + " (use 'other' for agents that read AGENTS.md natively)")
    return args


def render(text, active, replacements):
    lines = []
    for line in text.splitlines(keepends=True):
        match = CONDITION.search(line)
        if match:
            if match.group(1) not in active:
                continue
            line = line[: match.start()] + "\n"
        lines.append(line)
    text = "".join(lines)
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text


def install_hook(root, dry_run):
    """Install the pre-push secret check. Returns a message, or None if not applicable."""
    try:
        out = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=root,
                             capture_output=True, text=True)
    except OSError:
        return None
    if out.returncode != 0:
        return "note: not a git repository yet. Run this again after `git init` to add the pre-push secret check."
    hook = (root / out.stdout.strip() / "pre-push").resolve()
    if hook.exists():
        return "kept (already exists): git pre-push hook. Add `%s --secrets` to it by hand." % CHECK
    if not dry_run:
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(HOOK % shlex.quote(str(CHECK)), encoding="utf-8")
        hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return "%s: git pre-push hook (secret check before every push)" % (
        "would create" if dry_run else "created")


def env_is_ignored(root):
    """True or False if git can tell, None if this is not a git repository."""
    try:
        result = subprocess.run(["git", "check-ignore", "-q", "--no-index", ".env"], cwd=root,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return None
    return {0: True, 1: False}.get(result.returncode)


def main():
    args = parse_args()
    root = args.project_dir.resolve()
    if not root.is_dir():
        print("error: %s is not a directory" % root, file=sys.stderr)
        return 1
    if not TEMPLATES.is_dir():
        print("error: templates not found at %s" % TEMPLATES, file=sys.stderr)
        return 1

    files = list(BASE)
    for doc in args.docs:
        files += DOCS[doc]
    for agent in args.agents:
        files += AGENTS.get(agent, [])
    if args.parallel:
        files += PARALLEL

    replacements = {"{{DATE}}": datetime.date.today().isoformat()}
    if args.name:
        replacements["{{PROJECT_NAME}}"] = args.name

    created, kept, seen = [], [], set()
    for template, target_rel in files:
        if target_rel in seen:
            continue
        seen.add(target_rel)
        target = root / target_rel
        if target.exists():
            kept.append(target_rel)
            continue
        text = render((TEMPLATES / template).read_text(encoding="utf-8"),
                      set(args.docs), replacements)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        created.append(target_rel)

    verb = "would create" if args.dry_run else "created"
    for path in created:
        print("%s: %s" % (verb, path))
    for path in kept:
        print("kept (already exists): %s" % path)

    if not args.no_hook:
        message = install_hook(root, args.dry_run)
        if message:
            print(message)

    kept_set = set(kept)
    new_docs = [doc for doc in args.docs if DOCS[doc][0][1] in created]
    if "AGENTS.md" in kept_set and "AGENTS.md" not in created:
        if new_docs:
            print("note: add the %s row to the AGENTS.md › Docs table by hand." % " and ".join(new_docs))
        else:
            print("note: AGENTS.md already existed. Merge in the rules from %s (secrets, verify, "
                  "handoff) rather than replacing the owner's." % (TEMPLATES / "AGENTS.md"))
    settings = root / ".claude" / "settings.json"
    if ".claude/settings.json" in kept_set and ".env" not in settings.read_text(encoding="utf-8", errors="replace"):
        print("warning: .claude/settings.json has no rules blocking secret files. Merge in the "
              "deny rules from %s." % (TEMPLATES / "claude-settings.json"))
    if ".gitignore" in kept_set and not args.dry_run and env_is_ignored(root) is False:
        print("warning: .gitignore does not ignore .env. Add the secret patterns from %s."
              % (TEMPLATES / "gitignore"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
