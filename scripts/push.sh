#!/usr/bin/env bash
#
# push.sh: verify, then commit and push the current state of the repo.
#
# Usage:
#   ./scripts/push.sh "docs: clarify the smoothing choice"
#   ./scripts/push.sh                # uses a default commit message
#
# It refuses to push unless the test suite passes AND the analysis reproduces
# cleanly, so a broken increment can never reach the public repo. Re-running the
# analysis also regenerates the figures README.md embeds, which is why it
# happens before the commit. Run it from anywhere inside the repo.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Prefer the project virtualenv if present. Override with PYTHON=... if desired.
if [ -z "${PYTHON:-}" ] && [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="${PYTHON:-python3}"
fi
MSG="${1:-chore: update sunspot-rise-time-vs-cycle-strength-exploratory-analysis}"

echo "==> Running test suite"
"$PYTHON" -m pytest -q

echo "==> Reproducing the analysis (regenerates the committed figures)"
"$PYTHON" analysis.py

# Before the first commit exists, HEAD is meaningless: fail with a useful message.
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "ERROR: this repository has no commits yet." >&2
    echo "Make the first commit by hand, then use this script for every push after:" >&2
    echo "  git add -A && git commit -m 'feat: ...'" >&2
    exit 1
fi

# `git status --porcelain` (unlike `git diff`) also reports untracked files.
if [ -z "$(git status --porcelain)" ]; then
    echo "==> No local changes. Pushing any unpushed commits."
else
    echo "==> Staging and committing changes"
    git add -A
    git commit -m "$MSG"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
    echo "ERROR: no 'origin' remote configured." >&2
    echo "Set it once with:" >&2
    echo "  git remote add origin git@github.com:DefinitelyScott/sunspot-rise-time-vs-cycle-strength-exploratory-analysis.git" >&2
    exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "==> Pushing $BRANCH to origin"
git push -u origin "$BRANCH"
echo "==> Done."
