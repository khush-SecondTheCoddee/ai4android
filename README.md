# TermuxAI (Non-root Android AI)

This repo provides a **local/offline AI chat runner for Android Termux (non-root)**.
It is built around `llama.cpp` + your own custom `.gguf` model.

## What this gives you
- Works in Termux without root.
- Uses your custom local LLM (GGUF).
- Interactive chat UI in terminal.
- Runtime commands to adjust temp/tokens/threads.

## 1) Install in Termux

```bash
git clone <your-repo-url> ai4android
cd ai4android
bash setup_termux.sh
```

## 2) Download a model

Put a GGUF model file on your phone, for example:
- `~/models/qwen2.5-1.5b-instruct-q4_k_m.gguf`

(Choose a size your device can handle.)

## 3) Run

```bash
bash run_termux_ai.sh ~/models/your-model.gguf
```

Optional runtime flags:

```bash
bash run_termux_ai.sh ~/models/your-model.gguf --threads 6 --context 4096 --tokens 300 --temp 0.6
```

## Chat commands
- `/help`
- `/config`
- `/set temp 0.6`
- `/set tokens 300`
- `/set threads 8`
- `/clear`
- `/exit`

## Notes for non-root Android
- Keep model sizes small enough for RAM limits.
- Start with Q4 quantized models for speed/memory balance.
- If Termux cannot execute `llama-cli`, ensure `~/bin` is in `PATH`:

```bash
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```
