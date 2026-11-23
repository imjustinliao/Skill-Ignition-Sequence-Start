#!/usr/bin/env python3
"""Health check for a project set up with Ignition Sequence Start. Read-only.

Usage:
    python3 check.py [project-dir] [--quiet]
    python3 check.py [project-dir] --secrets   (secret checks only; used by the pre-push hook)

Checks that setup is finished, the docs match git, no secret files or keys are tracked,
the docs stay small and only the expected Markdown files exist. Prints "ok", "warn" or
"FAIL" lines and exits 1 if anything failed. Run it when arriving in a project, before a
handoff and before every push. Python 3.8+ standard library only.
"""

import argparse
import pathlib
import re
import subprocess
import sys

from redact import find_tokens

EXPECTED_DOCS = {"product.md", "progress.md", "design.md", "architecture.md", "parallel-plan.md"}
ROOT_MD_OK = {"README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CHANGELOG.md",
              "CONTRIBUTING.md", "LICENSE.md", "SECURITY.md", "CODE_OF_CONDUCT.md"}
BUDGETS = {"AGENTS.md": 120, "docs/progress.md": 200}
SECRET_FILE = re.compile(
    r"(^|/)(\.env(\.[^/]+)?|\.envrc|\.dev\.vars|secrets\.h|credentials\.json"
    r"|[^/]*service-account[^/]*\.json|[^/]+\.(pem|key|p12|pfx|tfstate))$")
SAMPLE = re.compile(r"(\.|-|_)(example|sample|template)(\.[^/]+)?$")
LEGACY = {  # docs from versions before 0.3: where their content belongs now
    "spec.md": "docs/product.md › MVP features",
    "feedback.md": "docs/progress.md › Feedback",
    "research.md": "the Why column in docs/architecture.md › Stack",
}
PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
DATE_LINE = re.compile(r"\*\*(\d{4}-\d{2}-\d{2})\*\*")
MAX_SCAN_BYTES = 1_000_000

results = []


def report(level, message):
    results.append((level, message))


def git(root, *args):
    try:
        out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    except OSError:
        return None
    return out.stdout if out.returncode == 0 else None


def section(text, title):
    match = re.search(r"^## %s\s*$(.*?)(?=^## |\Z)" % re.escape(title), text, re.M | re.S)
    return match.group(1) if match else ""


def check_setup(root):
    agents = root / "AGENTS.md"
    if not agents.exists():
        report("FAIL", "no AGENTS.md: this project is not set up yet (run the setup first)")
        return
    text = agents.read_text(encoding="utf-8", errors="replace")
    holes = sorted(set(PLACEHOLDER.findall(text)))
    if holes:
        report("warn", "AGENTS.md still has placeholders, so setup is unfinished: " + ", ".join(holes))
    else:
        report("ok", "AGENTS.md is filled in")
    for doc in sorted(set(re.findall(r"`(docs/[\w./-]+\.md)`", text))):
        if not (root / doc).exists():
            report("warn", "AGENTS.md points at %s, which does not exist" % doc)


def check_progress(root, last_commit_date):
    path = root / "docs" / "progress.md"
    if not path.exists():
        report("FAIL", "no docs/progress.md: the next agent has nothing to resume from")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    open_items = re.findall(r"^- \[ \] (.+)$", section(text, "Setup"), re.M)
    if open_items:
        report("warn", "setup has %d open item(s), next: %s" % (len(open_items), open_items[0].split(" <!--")[0]))
    in_flight = re.search(r"\*\*In flight\*\*:\s*(.+)", text)
    if in_flight and not in_flight.group(1).strip().lower().startswith("none"):
        report("warn", "work in flight: " + in_flight.group(1).split("<!--")[0].strip())
    dates = DATE_LINE.findall(section(text, "Session log"))
    if last_commit_date and dates and max(dates) < last_commit_date:
        report("warn", "commits on %s are newer than the last session-log entry (%s): "
                       "progress.md may be stale" % (last_commit_date, max(dates)))
    elif last_commit_date and not dates and not open_items:
        report("warn", "the session log is empty")


def check_git(root):
    if git(root, "rev-parse", "--is-inside-work-tree") is None:
        report("warn", "not a git repository: offer `git init` so there is version history")
        return None
    dirty = [line for line in (git(root, "status", "--porcelain") or "").splitlines() if line]
    if dirty:
        report("warn", "%d uncommitted change(s)" % len(dirty))
    else:
        report("ok", "working tree clean")
    if not (git(root, "remote") or "").strip():
        report("warn", "no remote: work exists only on this machine")
    else:
        ahead = git(root, "rev-list", "--count", "@{upstream}..HEAD")
        if ahead and ahead.strip() != "0":
            report("warn", "%s commit(s) not pushed" % ahead.strip())
    last = git(root, "log", "-1", "--format=%cs")
    return last.strip() if last else None


def check_secrets(root, in_git):
    if not in_git:
        if (root / ".env").exists() and not (root / ".gitignore").exists():
            report("FAIL", ".env exists and there is no .gitignore")
        return
    tracked = (git(root, "ls-files") or "").splitlines()
    leaked = [f for f in tracked if SECRET_FILE.search(f) and not SAMPLE.search(f)]
    for name in leaked:
        report("FAIL", "secret file tracked by git: %s (untrack it and rotate what it holds)" % name)
    if git(root, "check-ignore", "-q", "--no-index", ".env") is None:
        report("warn", ".gitignore does not ignore .env")
    found = 0
    for name in tracked:
        path = root / name
        try:
            if not path.is_file() or path.stat().st_size > MAX_SCAN_BYTES:
                continue
            data = path.read_bytes()
        except OSError:
            continue
        if b"\0" in data[:1024]:
            continue
        for lineno, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            for kind in find_tokens(line):
                report("FAIL", "possible %s in %s:%d (rotate it if real)" % (kind, name, lineno))
                found += 1
    if not leaked and not found:
        report("ok", "no secret files or key patterns in tracked files")


def check_tidiness(root, in_git):
    docs = root / "docs"
    if docs.is_dir():
        for md in sorted(docs.rglob("*.md")):
            rel = md.relative_to(docs).as_posix()
            if rel.startswith("milestones/") or rel in EXPECTED_DOCS or rel.startswith("archive/"):
                continue
            if rel in LEGACY:
                report("warn", "docs/%s is from an older version of this skill: move its content "
                               "into %s, then delete it" % (rel, LEGACY[rel]))
                continue
            report("warn", "extra doc docs/%s: merge it into the right doc or delete it" % rel)
    for md in sorted(root.glob("*.md")):
        if md.name not in ROOT_MD_OK:
            report("warn", "extra Markdown file %s: merge it into docs/ or delete it" % md.name)
    if (docs / "parallel-plan.md").exists() and in_git:
        branches = git(root, "branch", "-a", "--list", "*milestone/*") or ""
        if not branches.strip():
            report("warn", "docs/parallel-plan.md exists but no milestone/* branches: "
                           "delete it and docs/milestones/ if parallel work is finished")
    for rel, limit in BUDGETS.items():
        path = root / rel
        if path.exists():
            count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
            if count > limit:
                report("warn", "%s has %d lines (budget %d): prune it" % (rel, count, limit))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_dir", nargs="?", default=".", type=pathlib.Path)
    parser.add_argument("--quiet", action="store_true", help="print only warnings and failures")
    parser.add_argument("--secrets", action="store_true", help="run only the secret checks")
    args = parser.parse_args()
    root = args.project_dir.resolve()

    if args.secrets:
        check_secrets(root, git(root, "rev-parse", "--is-inside-work-tree") is not None)
        failures = [m for level, m in results if level == "FAIL"]
        for message in failures:
            print("FAIL " + message)
        if failures:
            print("Push stopped by the ignition-sequence-start secret check. Fix the items above "
                  "(or, only if they are false alarms, push with --no-verify).")
        return 1 if failures else 0

    check_setup(root)
    last_commit = check_git(root)
    in_git = git(root, "rev-parse", "--is-inside-work-tree") is not None
    check_progress(root, last_commit)
    check_secrets(root, in_git)
    check_tidiness(root, in_git)

    for level, message in results:
        if args.quiet and level == "ok":
            continue
        print("%-4s %s" % (level, message))
    failed = any(level == "FAIL" for level, _ in results)
    if not failed and all(level == "ok" for level, _ in results) and args.quiet:
        print("ok   all checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
