#!/usr/bin/env bash
# Fallback installer for machines where the plugin route is not available.
#
# The plugin route is the recommended one and needs no script:
#     claude plugin marketplace add <owner>/claude-plain-precise
#     claude plugin install plain-precise@wz369-writing
#
# Use this script instead when the machine has no network access to the git
# host, or when you want the style file copied into ~/.claude directly.
#
# What it does:
#   1. copies (or symlinks, with --link) the style into ~/.claude/output-styles/
#   2. sets "outputStyle": "plain-precise" in ~/.claude/settings.json
#   3. backs up settings.json first
#
# It does not touch CLAUDE.md. See claude-md-snippet.md for that part.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO/plugins/plain-precise/output-styles/plain-precise.md"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DEST_DIR="$CLAUDE_DIR/output-styles"
DEST="$DEST_DIR/plain-precise.md"
SETTINGS="$CLAUDE_DIR/settings.json"

MODE="copy"
if [ "${1:-}" = "--link" ]; then MODE="link"; fi

if [ ! -f "$SRC" ]; then
  echo "error: cannot find the style file at $SRC" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

if [ "$MODE" = "link" ]; then
  ln -sfn "$SRC" "$DEST"
  echo "linked  $DEST -> $SRC"
else
  cp "$SRC" "$DEST"
  echo "copied  $SRC -> $DEST"
fi

# Set the outputStyle key without disturbing anything else in settings.json.
python3 - "$SETTINGS" <<'PY'
import json, os, shutil, sys

path = sys.argv[1]
data = {}
if os.path.exists(path):
    shutil.copy(path, path + ".bak")
    print("backed up %s -> %s.bak" % (path, path))
    with open(path) as fh:
        text = fh.read().strip()
    if text:
        try:
            data = json.loads(text)
        except ValueError as exc:
            sys.stderr.write("error: %s is not valid JSON (%s). Nothing changed.\n" % (path, exc))
            sys.exit(1)

if data.get("outputStyle") == "plain-precise":
    print('settings.json already has "outputStyle": "plain-precise"')
else:
    data["outputStyle"] = "plain-precise"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    print('set "outputStyle": "plain-precise" in %s' % path)
PY

echo
echo "Done. The style is part of the system prompt, which Claude Code reads once"
echo "at session start, so run /clear or start a new session for it to apply."
