#!/usr/bin/env bash
# Add the research-integrity rules to ~/.claude/CLAUDE.md, or remove them again.
#
# This automates step 3 of the install. A plugin cannot ship a CLAUDE.md, so
# this part does not travel with the plugin and needs its own command.
#
#   bash install-claude-md.sh              install or update the block
#   bash install-claude-md.sh --dry-run    show what would change, write nothing
#   bash install-claude-md.sh --print      print the block to standard output
#   bash install-claude-md.sh --uninstall  remove the block again
#
# The block sits between two marker comments, so running the command twice
# replaces the block rather than adding a second copy, and nothing you wrote
# yourself is touched. Your file is backed up before every write.
#
# The script reads claude-md-snippet.md from its own directory. If that file is
# not there, for example because you piped this script in on its own, it
# downloads the snippet from the repository instead.

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/oZwZo/agent-plain-precise-language/main"
BEGIN="<!-- BEGIN plain-precise integrity rules. Managed by install-claude-md.sh. -->"
END="<!-- END plain-precise integrity rules -->"

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
TARGET="$CLAUDE_DIR/CLAUDE.md"

MODE="install"
case "${1:-}" in
  --uninstall) MODE="uninstall" ;;
  --dry-run)   MODE="dry-run" ;;
  --print)     MODE="print" ;;
  --help|-h)   sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  "")          ;;
  *)           echo "error: unknown option $1. Run with --help." >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SNIPPET="$SCRIPT_DIR/claude-md-snippet.md"
TMP_SNIPPET=""

cleanup() {
  if [ -n "$TMP_SNIPPET" ] && [ -f "$TMP_SNIPPET" ]; then rm -f "$TMP_SNIPPET"; fi
}
trap cleanup EXIT

if [ "$MODE" != "uninstall" ] && [ ! -f "$SNIPPET" ]; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "error: cannot find $SNIPPET and curl is not available." >&2
    exit 1
  fi
  TMP_SNIPPET="$(mktemp)"
  echo "claude-md-snippet.md is not next to this script, so downloading it"
  if ! curl -fsSL "$REPO_RAW/claude-md-snippet.md" -o "$TMP_SNIPPET"; then
    echo "error: could not download $REPO_RAW/claude-md-snippet.md" >&2
    echo "Nothing was written. Either the machine cannot reach GitHub, or the" >&2
    echo "file is not published yet. Clone the repository and run this script" >&2
    echo "from inside it instead." >&2
    exit 1
  fi
  SNIPPET="$TMP_SNIPPET"
fi

python3 - "$MODE" "$TARGET" "$SNIPPET" "$BEGIN" "$END" <<'PY'
import os
import shutil
import sys
import time

mode, target, snippet_path, begin, end = sys.argv[1:6]


def fenced_block(path):
    """Return the contents of the first ```markdown block in the snippet."""
    with open(path, encoding="utf-8") as handle:
        lines = handle.readlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "```markdown":
            start = index + 1
            break
    if start is None:
        sys.stderr.write("error: no ```markdown block found in %s\n" % path)
        sys.exit(1)
    for index in range(start, len(lines)):
        if lines[index].strip() == "```":
            return "".join(lines[start:index]).strip() + "\n"
    sys.stderr.write("error: the ```markdown block in %s is never closed\n" % path)
    sys.exit(1)


def split_on_markers(text):
    """Return the text before the block, and the text after it.

    Returns None when the file holds no block yet.
    """
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
    block = fenced_block(snippet_path)

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

if [ "$MODE" = "install" ] || [ "$MODE" = "dry-run" ]; then
  # A line that caps output length fights the style directly, because
  # compression is what produces the noun stacks and the dropped subjects that
  # the style exists to remove. Report such lines rather than delete them,
  # because they are yours.
  if [ -f "$TARGET" ] && grep -nEi 'be concise|under [0-9]+ (lines|words)|no more than [0-9]+ (lines|words)|keep (it |summaries )?short|brief(ly)? as possible' "$TARGET" >/dev/null 2>&1; then
    echo
    echo "Check these lines in $TARGET. A cap on output length works against the style,"
    echo "because compression is what produces the noun stacks and the dropped subjects"
    echo "that the style exists to remove. Delete any line that caps length."
    grep -nEi 'be concise|under [0-9]+ (lines|words)|no more than [0-9]+ (lines|words)|keep (it |summaries )?short|brief(ly)? as possible' "$TARGET" | sed 's/^/  /'
  fi
fi

if [ "$MODE" = "install" ] || [ "$MODE" = "uninstall" ]; then
  echo
  echo "CLAUDE.md is read at session start, so run /clear or start a new session."
fi
