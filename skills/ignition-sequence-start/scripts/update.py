#!/usr/bin/env python3
"""Keep this skill current with its GitHub repository. Safe to run every session.

Usage:
    python3 update.py [--quiet] [--check] [--force] [--target SKILL_DIR]

How it updates depends on how the skill was installed:
- Copied folder (npx skills, a manual copy, a zip): downloads the repository's main branch and
  replaces the skill's files, keeping a backup in ~/.cache/ignition-sequence-start/. Hashes of
  installed files go in .install-manifest.json, so files you edited are never overwritten
  (unless --force) and files you added are left alone.
- Git clone or fork: `git pull --ff-only`, only when the working tree is clean.
- Claude Code plugin: left to the plugin manager (`/plugin marketplace update`).

The source is `repository:` (owner/name on GitHub) in SKILL.md's metadata, or the official
repository when that line is missing; a fork points it at itself. Offline or blocked, it says nothing and changes nothing. Turn it off with
IGNITION_SKIP_UPDATE=1 or a `.no-auto-update` file in the skill folder.
Python 3.8+ standard library; falls back to curl if Python cannot verify HTTPS.
"""

import argparse
import datetime
import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request

DEFAULT_REPOSITORY = "imjustinliao/Skill-Ignition-Sequence-Start"
REPO_SUBPATH = "skills/ignition-sequence-start"
MANIFEST = ".install-manifest.json"
SKIP = {MANIFEST, ".no-auto-update", ".DS_Store"}
BACKUPS = pathlib.Path.home() / ".cache" / "ignition-sequence-start"
KEEP_BACKUPS = 3


def meta(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    front = text.split("---")[1] if text.startswith("---") else ""
    get = lambda key: (re.search(r"^\s*%s:\s*\"?([^\"\n]+)\"?\s*$" % key, front, re.M) or [None, None])[1]
    return get("version") or "unknown", get("repository") or DEFAULT_REPOSITORY


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local_hashes(skill_dir):
    hashes = {}
    for path in skill_dir.rglob("*"):
        rel = path.relative_to(skill_dir).as_posix()
        if path.is_file() and path.name not in SKIP and "__pycache__" not in rel.split("/"):
            hashes[rel] = sha(path.read_bytes())
    return hashes


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            return response.read()
    except Exception:
        if not shutil.which("curl"):
            raise
        out = subprocess.run(["curl", "-fsSL", "--max-time", "15", url], capture_output=True)
        if out.returncode != 0:
            raise OSError("download failed")
        return out.stdout


def remote_files(repository):
    """{relative path: (bytes, executable)} for the skill folder on the main branch."""
    data = fetch("https://codeload.github.com/%s/tar.gz/refs/heads/main" % repository)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            parts = member.name.split("/", 1)
            if len(parts) < 2 or not parts[1].startswith(REPO_SUBPATH + "/"):
                continue
            rel = parts[1][len(REPO_SUBPATH) + 1:]
            if not rel or rel.startswith("/") or ".." in rel.split("/") or pathlib.PurePath(rel).name in SKIP:
                continue
            files[rel] = (archive.extractfile(member).read(), bool(member.mode & 0o111))
    if "SKILL.md" not in files:
        raise ValueError("no skill found at %s in %s" % (REPO_SUBPATH, repository))
    return files


def git(skill_dir, *args, timeout=20):
    try:
        out = subprocess.run(["git", "-C", str(skill_dir), *args], capture_output=True,
                             text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def update_git(skill_dir, check, say):
    if git(skill_dir, "status", "--porcelain") != "":
        say("Skill folder has local changes (git); not updating. Commit or stash them, then `git pull`.")
        return
    before = git(skill_dir, "rev-parse", "HEAD")
    if check:
        git(skill_dir, "fetch", "--quiet")
        behind = git(skill_dir, "rev-list", "--count", "HEAD..@{upstream}")
        if behind and behind != "0":
            say("%s update(s) available: run update.py without --check." % behind)
        return
    if git(skill_dir, "pull", "--ff-only", "--quiet") is None:
        return  # offline, no upstream, or diverged: leave it alone
    if git(skill_dir, "rev-parse", "HEAD") != before:
        say("Skill updated to %s (git pull). Re-read SKILL.md before continuing." % meta(skill_dir)[0])


def update_copy(skill_dir, repository, check, force, say):
    old_version = meta(skill_dir)[0]
    manifest_path = skill_dir / MANIFEST
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    local = local_hashes(skill_dir)
    try:
        remote = remote_files(repository)
    except Exception:
        return  # offline or blocked: never get in the way of the session
    remote_hashes = {rel: sha(data) for rel, (data, _) in remote.items()}

    tracked = set(manifest) if manifest else set(local)
    current = {rel: h for rel, h in local.items() if rel in tracked}
    if current == remote_hashes:
        if manifest is None and not check:
            manifest_path.write_text(json.dumps(remote_hashes, indent=1, sort_keys=True))
        return
    edited = sorted(rel for rel in (manifest or {}) if rel in local and local[rel] != manifest[rel])
    if edited and not force:
        say("Skill update available, but these files were edited locally and would be replaced: "
            "%s. Keep them, or run update.py --force (a backup is kept)." % ", ".join(edited))
        return
    new_version = meta_from_bytes(remote["SKILL.md"][0])
    if check:
        say("Skill update available: %s -> %s." % (old_version, new_version))
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUPS / ("backup-%s-%s" % (old_version, stamp))
    shutil.copytree(skill_dir, backup, ignore=shutil.ignore_patterns("__pycache__"))
    for old in sorted(BACKUPS.glob("backup-*"), key=lambda p: p.stat().st_mtime)[:-KEEP_BACKUPS]:
        shutil.rmtree(old, ignore_errors=True)

    changed = 0
    for rel, (data, executable) in remote.items():
        target = skill_dir / rel
        if local.get(rel) == remote_hashes[rel]:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".updating")
        temp.write_bytes(data)
        if executable:
            temp.chmod(temp.stat().st_mode | 0o111)
        os.replace(temp, target)
        changed += 1
    removed = 0
    for rel in sorted(tracked - set(remote)):
        path = skill_dir / rel
        if path.is_file():
            path.unlink()
            removed += 1
    for folder in sorted((p for p in skill_dir.rglob("*") if p.is_dir()), reverse=True):
        if not any(folder.iterdir()):
            folder.rmdir()
    manifest_path.write_text(json.dumps(remote_hashes, indent=1, sort_keys=True))
    say("Skill updated %s -> %s (%d file(s) changed, %d removed; backup in %s). "
        "Re-read SKILL.md before continuing." % (old_version, new_version, changed, removed, backup))


def meta_from_bytes(data):
    match = re.search(r"^\s*version:\s*\"?([^\"\n]+)\"?\s*$", data.decode("utf-8", "replace"), re.M)
    return match.group(1) if match else "unknown"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true", help="print only when something changed")
    parser.add_argument("--check", action="store_true", help="report, change nothing")
    parser.add_argument("--force", action="store_true", help="replace locally edited files too")
    parser.add_argument("--target", type=pathlib.Path, help="skill folder to update (default: this one)")
    args = parser.parse_args()

    skill_dir = (args.target or pathlib.Path(__file__).parent.parent).expanduser().resolve()
    messages = []
    say = messages.append
    if not (skill_dir / "SKILL.md").exists():
        print("No SKILL.md in %s." % skill_dir)
        return 1
    version, repository = meta(skill_dir)

    if os.environ.get("IGNITION_SKIP_UPDATE") or (skill_dir / ".no-auto-update").exists():
        say("Auto-update is off for this skill.")
    elif "/.claude/plugins/" in skill_dir.as_posix():
        say("Installed as a Claude Code plugin: update with `/plugin marketplace update`.")
    elif git(skill_dir, "rev-parse", "--is-inside-work-tree") == "true":
        update_git(skill_dir, args.check, say)
    else:
        try:
            update_copy(skill_dir, repository, args.check, args.force, say)
        except OSError as error:
            say("Could not update the skill folder (%s). It still works as is." % error)

    for message in messages:
        print(message)
    if not messages and not args.quiet:
        print("Skill is up to date (%s)." % version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
