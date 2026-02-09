#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/model.gguf [extra args]"
  exit 1
fi

MODEL="$1"
shift

python termux_ai.py --model "$MODEL" --llama-cli "${LLAMA_CLI:-$HOME/bin/llama-cli}" "$@"
