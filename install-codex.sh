#!/usr/bin/env bash
# Install the plain-precise rules into Codex, or remove them again.
#
#   bash install-codex.sh              install or update the block
#   bash install-codex.sh --dry-run    show what would change, write nothing
#   bash install-codex.sh --print      print the block to standard output
#   bash install-codex.sh --uninstall  remove the block again
#
# Codex reads a global instruction file at $CODEX_HOME/AGENTS.md, where
# CODEX_HOME defaults to ~/.codex. This script writes the rules into that file
# between two marker comments, so anything you wrote there yourself is kept and
# running the command twice replaces the block rather than adding a second copy.
# Your file is backed up before every write.
#
# Codex has no output-style mechanism and no equivalent of force-for-plugin, so
# the writing rules and the research-integrity rules go into the same file. In
# Claude Code they are split across two files, because there the two levels
# behave differently.
#
# The script reads codex/AGENTS.md from its own directory. If that file is not
# there, it downloads it from the repository instead.

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/oZwZo/agent-plain-precise-language/main"
BEGIN="<!-- BEGIN plain-precise. Managed by install-codex.sh. -->"
END="<!-- END plain-precise -->"

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET="$CODEX_DIR/AGENTS.md"

MODE="install"
case "${1:-}" in
  --uninstall) MODE="uninstall" ;;
  --dry-run)   MODE="dry-run" ;;
  --print)     MODE="print" ;;
  --help|-h)   sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  "")          ;;
  *)           echo "error: unknown option $1. Run with --help." >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/codex/AGENTS.md"
TMP_SOURCE=""

cleanup() {
  if [ -n "$TMP_SOURCE" ] && [ -f "$TMP_SOURCE" ]; then rm -f "$TMP_SOURCE"; fi
}
trap cleanup EXIT

if [ "$MODE" != "uninstall" ] && [ ! -f "$SOURCE" ]; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "error: cannot find $SOURCE and curl is not available." >&2
    exit 1
  fi
  TMP_SOURCE="$(mktemp)"
  echo "codex/AGENTS.md is not next to this script, so downloading it"
  if ! curl -fsSL "$REPO_RAW/codex/AGENTS.md" -o "$TMP_SOURCE"; then
    echo "error: could not download $REPO_RAW/codex/AGENTS.md" >&2
    echo "Nothing was written. Either the machine cannot reach GitHub, or the" >&2
    echo "file is not published yet. Clone the repository and run this script" >&2
    echo "from inside it instead." >&2
    exit 1
  fi
  SOURCE="$TMP_SOURCE"
fi

python3 - "$MODE" "$TARGET" "$SOURCE" "$BEGIN" "$END" <<'PY'
import os
import shutil
import sys
import time

mode, target, source_path, begin, end = sys.argv[1:6]


def strip_generated_comment(text):
    """Drop the leading 'do not edit' comment from the built file.

    That comment tells someone reading the repository to rerun the build
    script. Inside the installed file it would point at a path that the reader
    may not have, so it is removed here.
    """
    if text.startswith("<!--"):
        close = text.find("-->")
        if close >= 0:
            return text[close + 3:].lstrip("\n")
    return text


def split_on_markers(text):
    """Return the text before the block and the text after it, or None."""
    first = text.find(begin)
    if first < 0:
        return None
    last = text.find(end, first)
    if last < 0:
        sys.stderr.write(
            "error: %s has a begin marker but no end marker. "
            "Fix it by hand, then run this again.\n" % target
        )
        sys.exit(1)
    return text[:first], text[last + len(end):]


if mode != "uninstall":
    with open(source_path, encoding="utf-8") as handle:
        block = strip_generated_comment(handle.read()).strip() + "\n"

if mode == "print":
    sys.stdout.write(block)
    sys.exit(0)

existing = ""
if os.path.exists(target):
    with open(target, encoding="utf-8") as handle:
        existing = handle.read()

parts = split_on_markers(existing)

if mode == "uninstall":
    if parts is None:
        print("no plain-precise block in %s, nothing to remove" % target)
        sys.exit(0)
    before, after = parts
    new = (before.rstrip() + "\n" + after.lstrip("\n")).rstrip() + "\n"
    action = "removed the plain-precise block from"
else:
    wrapped = "%s\n\n%s\n%s\n" % (begin, block.rstrip(), end)
    if parts is None:
        head = existing.rstrip()
        new = (head + "\n\n" + wrapped) if head else wrapped
        action = "added the plain-precise block to"
    else:
        before, after = parts
        new = before.rstrip() + ("\n\n" if before.strip() else "") + wrapped + after.lstrip("\n")
        new = new.rstrip() + "\n"
        action = "updated the plain-precise block in"

if new == existing:
    print("%s is already up to date, nothing written" % target)
    sys.exit(0)

if mode == "dry-run":
    print("would have %s %s" % (action, target))
    print("the file would go from %d lines to %d lines" % (
        existing.count("\n"), new.count("\n")))
    sys.exit(0)

os.makedirs(os.path.dirname(target), exist_ok=True)
if os.path.exists(target):
    backup = "%s.bak-%s" % (target, time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy(target, backup)
    print("backed up %s -> %s" % (target, backup))

with open(target, "w", encoding="utf-8") as handle:
    handle.write(new)
print("%s %s" % (action, target))
PY

if [ "$MODE" = "install" ] || [ "$MODE" = "uninstall" ]; then
  echo
  echo "Codex reads the instruction file when a session starts, so start a new"
  echo "session for this to apply. An open session keeps the old rules."
fi
