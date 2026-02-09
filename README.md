# ai4android (Termux non-root)

A lightweight offline AI chat setup for **Android + Termux (non-root)** using your own **custom GGUF model** via `llama.cpp`.

## What this gives you

- Runs entirely in Termux, no root required.
- Uses your local model file (`.gguf`), so it can work offline.
- Simple interactive chat loop with:
  - persistent chat history,
  - `/reset` to clear context,
  - configurable inference settings (threads, context size, temperature).

## 1) Install dependencies in Termux

```bash
pkg update && pkg upgrade -y
pkg install -y git clang cmake python
```

## 2) Build llama.cpp in Termux

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build -j$(nproc)
```

After build, your executable is usually:

- `~/llama.cpp/build/bin/llama-cli`

## 3) Clone this repo and run

```bash
git clone <your-repo-url> ai4android
cd ai4android
```

Run with default `llama-cli` in `PATH`:

```bash
./run-termux-ai.sh ~/models/your-model.gguf
```

Or run with explicit binary path:

```bash
python termux_ai.py \
  --model ~/models/your-model.gguf \
  --llama-cli ~/llama.cpp/build/bin/llama-cli
```

## 4) Useful options

```bash
python termux_ai.py \
  --model ~/models/your-model.gguf \
  --llama-cli ~/llama.cpp/build/bin/llama-cli \
  --threads 4 \
  --ctx-size 4096 \
  --temp 0.7 \
  --top-p 0.95
```

## In-chat commands

- `/help` : show commands
- `/reset` : clear saved history
- `/exit` : quit

## Recommended model sizes for phones

- 1B–3B (Q4/Q5): fastest and usually most practical.
- 7B quantized: usable on stronger devices, but slower and more RAM-heavy.

## Notes for non-root Termux

- No system service/background daemon is required.
- Keep model files in `$HOME` storage for easier access (`~/models`).
- If output is too slow, lower context size and thread count; use smaller quantized GGUF.

