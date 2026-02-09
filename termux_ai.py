#!/usr/bin/env python3
"""Local Termux AI chat client for GGUF models via llama.cpp.

Designed for Android + Termux in non-root environments.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


DEFAULT_SYSTEM_PROMPT = (
    "You are a fast, practical offline assistant running on Android Termux. "
    "Keep answers concise, safe, and actionable."
)


@dataclass
class ChatConfig:
    llama_cli: str
    model: Path
    ctx_size: int = 4096
    threads: int = 2
    temp: float = 0.7
    top_p: float = 0.95
    repeat_penalty: float = 1.1
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    history_file: Path | None = None


def default_threads() -> int:
    """Pick a low but useful thread count for mobile CPUs."""
    return max(1, min(4, (os.cpu_count() or 2) - 1))


def read_history(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return []


def write_history(path: Path, messages: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def build_prompt(system_prompt: str, messages: List[dict]) -> str:
    parts = [f"<|system|>\n{system_prompt}\n"]
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "assistant":
            parts.append(f"<|assistant|>\n{content}\n")
        else:
            parts.append(f"<|user|>\n{content}\n")
    parts.append("<|assistant|>\n")
    return "".join(parts)


def call_llama(config: ChatConfig, prompt: str) -> str:
    cmd = [
        config.llama_cli,
        "-m",
        str(config.model),
        "--ctx-size",
        str(config.ctx_size),
        "--threads",
        str(config.threads),
        "--temp",
        str(config.temp),
        "--top-p",
        str(config.top_p),
        "--repeat-penalty",
        str(config.repeat_penalty),
        "--no-display-prompt",
        "-n",
        "512",
        "-p",
        prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Could not find llama.cpp executable: {config.llama_cli}. "
            "Install llama.cpp and pass --llama-cli with full path if needed."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        details = stderr or stdout or "No output"
        raise RuntimeError(f"llama.cpp failed: {details}") from exc

    return (result.stdout or "").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Offline AI chat in Termux using llama.cpp and your custom GGUF model"
    )
    parser.add_argument("--model", required=True, help="Path to local GGUF model")
    parser.add_argument(
        "--llama-cli",
        default="llama-cli",
        help="llama.cpp executable name/path (default: llama-cli)",
    )
    parser.add_argument(
        "--ctx-size", type=int, default=4096, help="Context size (default: 4096)"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=default_threads(),
        help="CPU threads (default: auto for phone CPU)",
    )
    parser.add_argument("--temp", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--repeat-penalty", type=float, default=1.1)
    parser.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="System prompt text",
    )
    parser.add_argument(
        "--history-file",
        default=str(Path.home() / ".termux-ai" / "history.json"),
        help="Conversation history file (default ~/.termux-ai/history.json)",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Disable saving/loading conversation history",
    )
    return parser.parse_args()


def print_help_commands() -> None:
    print("\nCommands: /exit, /reset, /help")


def main() -> int:
    args = parse_args()
    model_path = Path(args.model).expanduser().resolve()
    if not model_path.exists():
        print(f"Model file not found: {model_path}", file=sys.stderr)
        return 2

    history_path = None if args.no_history else Path(args.history_file).expanduser()
    messages: List[dict] = read_history(history_path) if history_path else []

    config = ChatConfig(
        llama_cli=args.llama_cli,
        model=model_path,
        ctx_size=args.ctx_size,
        threads=args.threads,
        temp=args.temp,
        top_p=args.top_p,
        repeat_penalty=args.repeat_penalty,
        system_prompt=args.system_prompt,
        history_file=history_path,
    )

    print("Termux AI ready. Type /help for commands.")
    while True:
        try:
            user_text = input("you> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            return 0

        if not user_text:
            continue
        if user_text == "/exit":
            print("Bye.")
            return 0
        if user_text == "/help":
            print_help_commands()
            continue
        if user_text == "/reset":
            messages = []
            if history_path and history_path.exists():
                history_path.unlink()
            print("History cleared.")
            continue

        messages.append({"role": "user", "content": user_text})
        prompt = build_prompt(config.system_prompt, messages)

        try:
            answer = call_llama(config, prompt)
        except RuntimeError as err:
            print(f"error> {err}")
            messages.pop()
            continue

        print(f"ai> {answer}\n")
        messages.append({"role": "assistant", "content": answer})

        if history_path:
            write_history(history_path, messages)


if __name__ == "__main__":
    raise SystemExit(main())
