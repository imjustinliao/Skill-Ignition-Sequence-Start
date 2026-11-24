#!/usr/bin/env python3
"""Find recent coding-agent chats for this project folder, across tools and accounts. Read-only.

Usage:
    python3 sessions.py [project-dir] [--limit 8]
    python3 sessions.py [project-dir] --show 12 [--session ID]

Lists chats whose working folder is the project (or a folder inside it), newest first, with
the command to resume each one in its own tool. --show prints the last N user and assistant
messages of the newest chat (or --session ID) so another agent can pick up where it stopped.
Output is redacted for common key formats, but transcripts can still hold private details:
summarize what matters into docs/progress.md, never paste transcript text into the repo.

Reads: Claude Code (every config folder with a projects/ folder: ~/.claude*, nested ones such as
~/.claude/spares/*, ~/.config/claude*, CLAUDE_CONFIG_DIR, IGNITION_CLAUDE_DIRS), Codex (CODEX_HOME or ~/.codex,
.jsonl and .jsonl.zst; .zst needs the zstd command), Gemini CLI (~/.gemini/tmp), GitHub Copilot
CLI (COPILOT_HOME or ~/.copilot). Cursor, Windsurf, Cline and IDE chats keep history in their
own databases: open their chat history instead. Python 3.8+ standard library only.
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

from redact import redact

HOME = pathlib.Path.home()
TAIL_BYTES = 400_000
MAX_CODEX_FILES = 400
ACTIVE_SECONDS = 90  # a transcript written this recently is most likely the chat running this script


def short(text, width):
    text = " ".join(redact(text).split())
    return text if len(text) <= width else text[: width - 1] + "…"


def inside(cwd, root):
    if not cwd:
        return False
    cwd = os.path.normpath(cwd)
    return cwd == root or cwd.startswith(root + os.sep)


def when(path):
    return datetime.datetime.fromtimestamp(path.stat().st_mtime)


def read_lines(path):
    """All JSON objects in a .jsonl or .jsonl.zst file (empty list if unreadable)."""
    try:
        if path.suffix == ".zst":
            if not shutil.which("zstd"):
                return []
            raw = subprocess.run(["zstd", "-dc", str(path)], capture_output=True).stdout
            text = raw.decode("utf-8", "replace")
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    objects = []
    for line in text.splitlines():
        try:
            objects.append(json.loads(line))
        except ValueError:
            continue
    return objects


def first_line(path):
    try:
        if path.suffix == ".zst":
            if not shutil.which("zstd"):
                return None
            proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL)
            line = proc.stdout.readline()
            proc.kill()
            proc.wait()
        else:
            with path.open("rb") as handle:
                line = handle.readline()
        return json.loads(line.decode("utf-8", "replace"))
    except (OSError, ValueError):
        return None


def tail_objects(path):
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - TAIL_BYTES))
            chunk = handle.read().decode("utf-8", "replace")
    except OSError:
        return []
    objects = []
    for line in chunk.splitlines()[1:] if size > TAIL_BYTES else chunk.splitlines():
        try:
            objects.append(json.loads(line))
        except ValueError:
            continue
    return objects


# ---- Claude Code -------------------------------------------------------------

def claude_dirs():
    """Every Claude Code config folder on this machine, one per account.

    Accounts are usually separated with CLAUDE_CONFIG_DIR, and people put those folders in many
    places (~/.claude-work, ~/.claude/spares/x, ~/.config/claude-b, ...). So look at the obvious
    spots, then any hidden folder up to three levels under home that has a `projects` folder.
    Extra places: IGNITION_CLAUDE_DIRS (os.pathsep-separated).
    """
    candidates = []
    for var in ("CLAUDE_CONFIG_DIR", "IGNITION_CLAUDE_DIRS"):
        candidates += [pathlib.Path(p).expanduser() for p in os.environ.get(var, "").split(os.pathsep) if p]
    for pattern in (".claude*", ".claude*/*", ".claude*/*/*", ".config/claude*", ".config/claude*/*",
                    ".*/claude*", ".*/.claude*"):
        candidates += [pathlib.Path(p) for p in sorted(glob.glob(str(HOME / pattern)))]
    seen, result = set(), []
    for d in candidates:
        try:
            key = d.resolve()
            if d.is_dir() and (d / "projects").is_dir() and key not in seen:
                seen.add(key)
                result.append(d)
        except OSError:
            continue
    return result


def claude_text(message, role):
    content = (message or {}).get("content")
    if isinstance(content, str):
        return content if not content.lstrip().startswith("<") else ""
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    text = "\n".join(parts).strip()
    return "" if role == "user" and text.startswith("<") else text


def claude_messages(objects):
    for obj in objects:
        kind = obj.get("type")
        if kind not in ("user", "assistant") or obj.get("isSidechain") or obj.get("isMeta"):
            continue
        text = claude_text(obj.get("message"), kind)
        if text:
            yield kind, text


LIMIT_RE = re.compile(r"usage limit|hit your limit|limit reached|rate.?limit|out of (extra )?usage|"
                      r"credit balance|quota", re.I)


def ended_at_limit(tail):
    """True when a chat's last real entry is an API/limit error rather than finished work."""
    for obj in reversed(tail):
        if obj.get("type") not in ("user", "assistant") or obj.get("isSidechain"):
            continue
        text = claude_text(obj.get("message"), obj.get("type"))
        return bool(text) and (bool(obj.get("isApiErrorMessage")) or obj.get("type") == "assistant"
                               and len(text) < 400) and bool(LIMIT_RE.search(text))
    return False


def claude_sessions(root):
    escaped = re.sub(r"[^A-Za-z0-9]", "-", root)
    found = []
    for config in claude_dirs():
        for project in (config / "projects").iterdir():
            name = project.name
            if not project.is_dir() or not (name == escaped or name.startswith(escaped + "-")
                                            or (len(escaped) > 200 and name.startswith(escaped[:150]))):
                continue
            for path in project.glob("*.jsonl"):
                tail = tail_objects(path)
                cwd = next((o.get("cwd") for o in tail if o.get("cwd")), None)
                if not inside(cwd, root):
                    continue
                title = next((o.get("customTitle") for o in reversed(tail) if o.get("customTitle")), "")
                last = next((t for k, t in reversed(list(claude_messages(tail))) if k == "user"), "")
                prefix = "" if config == HOME / ".claude" else "CLAUDE_CONFIG_DIR=%s " % config
                found.append({
                    "tool": "Claude Code", "id": path.stem, "path": path, "when": when(path),
                    "label": title or last, "resume": "%sclaude --resume %s" % (prefix, path.stem),
                    "reader": claude_messages, "limit": ended_at_limit(tail),
                    "account": str(config),
                })
    return found


# ---- Codex ---------------------------------------------------------------------

def codex_messages(objects):
    for obj in objects:
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
        if obj.get("type") != "response_item" or payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in ("user", "assistant"):
            continue
        text = "\n".join(c.get("text", "") for c in payload.get("content") or []
                         if isinstance(c, dict)).strip()
        if text and not (role == "user" and text.startswith("<")):
            yield role, text


def codex_sessions(root, limit):
    home = pathlib.Path(os.environ.get("CODEX_HOME", HOME / ".codex")).expanduser()
    files = []
    for sub in ("sessions", "archived_sessions"):
        base = home / sub
        if base.is_dir():
            files += [p for p in base.rglob("rollout-*") if p.name.endswith((".jsonl", ".jsonl.zst"))]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    found = []
    for path in files[:MAX_CODEX_FILES]:
        meta = first_line(path) or {}
        payload = meta.get("payload") if isinstance(meta.get("payload"), dict) else {}
        if not inside(payload.get("cwd"), root):
            continue
        session_id = payload.get("id") or payload.get("session_id") or path.stem
        found.append({
            "tool": "Codex", "id": session_id, "path": path, "when": when(path), "label": "",
            "resume": "codex resume %s" % session_id, "reader": codex_messages,
        })
        if len(found) >= limit:
            break
    for item in found:
        last = [t for k, t in codex_messages(read_lines(item["path"])) if k == "user"]
        item["label"] = last[-1] if last else ""
    return found


# ---- Gemini CLI and Copilot CLI -------------------------------------------------

def gemini_sessions(root):
    chats = HOME / ".gemini" / "tmp" / hashlib.sha256(root.encode()).hexdigest() / "chats"
    if not chats.is_dir():
        return []
    return [{"tool": "Gemini CLI", "id": p.stem, "path": p, "when": when(p), "label": "",
             "resume": "gemini --resume (run in the project folder; --list-sessions to pick)",
             "reader": None} for p in chats.glob("*.json")]


def copilot_sessions(root):
    home = pathlib.Path(os.environ.get("COPILOT_HOME", HOME / ".copilot")).expanduser()
    found = []
    needles = (root.encode(), json.dumps(root)[1:-1].encode())
    for events in (home / "session-state").glob("*/events.jsonl"):
        try:
            with events.open("rb") as handle:
                head = handle.read(65536)
        except OSError:
            continue
        if any(n in head for n in needles):
            sid = events.parent.name
            found.append({"tool": "Copilot CLI", "id": sid, "path": events, "when": when(events),
                          "label": "", "resume": "copilot --resume %s" % sid, "reader": None})
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_dir", nargs="?", default=".", type=pathlib.Path)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--show", type=int, metavar="N", help="print the last N messages")
    parser.add_argument("--session", help="session id for --show (default: newest)")
    args = parser.parse_args()
    root = os.path.normpath(str(args.project_dir.resolve()))

    sessions = (claude_sessions(root) + codex_sessions(root, args.limit)
                + gemini_sessions(root) + copilot_sessions(root))
    sessions.sort(key=lambda s: s["when"], reverse=True)
    unique, seen = [], set()
    for s in sessions:  # one row per conversation (Codex splits long threads across files)
        if (s["tool"], s["id"]) not in seen:
            seen.add((s["tool"], s["id"]))
            unique.append(s)
    sessions = unique

    if not sessions:
        print("No chats found for %s." % root)
        print("Cursor, Windsurf, Cline and IDE chats: open that tool's chat history in this folder.")
        return 1

    progress = pathlib.Path(root) / "docs" / "progress.md"
    saved = when(progress) if progress.is_file() else None
    now = datetime.datetime.now()
    active = [s for s in sessions if (now - s["when"]).total_seconds() < ACTIVE_SECONDS]

    if args.show:
        if args.session:
            chosen = next((s for s in sessions if s["id"] == args.session), None)
        else:
            chosen = next((s for s in sessions if s not in active), None)
            for s in active:
                print("Skipped %s %s: active right now, probably this chat (pass --session to "
                      "read it anyway)." % (s["tool"], s["id"]))
        if chosen is None:
            print("No matching earlier session.")
            return 1
        print("%s session %s, last active %s" % (chosen["tool"], chosen["id"],
                                                 chosen["when"].strftime("%Y-%m-%d %H:%M")))
        print("Resume it in that tool: %s\n" % chosen["resume"])
        if chosen["reader"] is None:
            print("Reading this tool's transcript is not supported; resume it in the tool instead.")
            return 0
        messages = list(chosen["reader"](read_lines(chosen["path"])))[-args.show:]
        for role, text in messages:
            print("[%s] %s\n" % (role, short(text, 600)))
        return 0

    print("Chats for %s (newest first; redacted):\n" % root)
    for s in sessions[: args.limit]:
        note = "  (active now: probably this chat)" if s in active else ""
        if s.get("limit"):
            note += "  [ended at a usage limit: work was probably cut off mid-task]"
        if saved and s["when"] > saved and s not in active:
            note += "  [newer than docs/progress.md: its latest work may be unsaved]"
        print("%s  %-11s  %s%s" % (s["when"].strftime("%Y-%m-%d %H:%M"), s["tool"], s["id"], note))
        if s["label"]:
            print("    %s" % short(s["label"], 100))
        print("    resume: %s" % s["resume"])
    print("\nNext: if the top chat is newer than docs/progress.md or ended at a limit, run "
          "`sessions.py --show 20` to read where it stopped, then continue from it.")
    print("\nNot listed: Cursor, Windsurf, Cline and IDE chats (see their chat history).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
