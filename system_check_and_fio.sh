#!/usr/bin/env bash
# Stable entry point; collection and escaping use Python's standard library.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3.10+ is required. Install python3 using your distribution package manager.' >&2
  exit 1
fi
exec python3 "$SCRIPT_DIR/scripts/system_report.py" "$@"
