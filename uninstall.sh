#!/usr/bin/env bash
# Undo install.sh. Removes the style file and the outputStyle key.
# If you installed via the plugin route instead, run:
#     claude plugin uninstall plain-precise@wz369-writing

set -euo pipefail

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DEST="$CLAUDE_DIR/output-styles/plain-precise.md"
SETTINGS="$CLAUDE_DIR/settings.json"

if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  rm -f "$DEST"
  echo "removed $DEST"
else
  echo "no style file at $DEST"
fi

python3 - "$SETTINGS" <<'PY'
import json, os, shutil, sys

path = sys.argv[1]
if not os.path.exists(path):
    print("no settings file at %s" % path)
    sys.exit(0)

with open(path) as fh:
    text = fh.read().strip()
if not text:
    sys.exit(0)
try:
    data = json.loads(text)
except ValueError as exc:
    sys.stderr.write("error: %s is not valid JSON (%s). Nothing changed.\n" % (path, exc))
    sys.exit(1)

if data.get("outputStyle") != "plain-precise":
    print('settings.json does not select plain-precise, left alone')
    sys.exit(0)

shutil.copy(path, path + ".bak")
del data["outputStyle"]
with open(path, "w") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
print('removed the "outputStyle" key from %s (backup at %s.bak)' % (path, path))
PY

echo
echo "Done. Claude Code returns to the default style after /clear or a new session."
