#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/2b-coder.gguf [extra termux_ai.py args...]"
  exit 1
fi

MODEL_PATH="$1"
shift

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python "$SCRIPT_DIR/termux_ai.py" --model "$MODEL_PATH" --preset coding-2b "$@"
