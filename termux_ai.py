#!/usr/bin/env python3
"""Simple local AI chat runner for Termux (non-root).

Uses llama.cpp's `llama-cli` binary and a GGUF model file.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


DEFAULT_SYSTEM_PROMPT = (
    "You are TermuxAI, a practical Android terminal assistant. "
    "Be concise, explain commands safely, and avoid destructive steps unless asked."
)


@dataclass
class ChatConfig:
    llama_cli: str
    model: Path
    threads: int = 4
    context_size: int = 2048
    temperature: float = 0.7
    max_tokens: int = 256
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


@dataclass
class ChatState:
    history: List[str] = field(default_factory=list)

    def add_turn(self, role: str, message: str) -> None:
        self.history.append(f"{role}: {message.strip()}")

    def render_prompt(self, system_prompt: str, max_chars: int = 8000) -> str:
        base = [f"system: {system_prompt}"] + self.history
        rendered = "\n".join(base)
        if len(rendered) <= max_chars:
            return rendered + "\nassistant:"
        trimmed = rendered[-max_chars:]
        return trimmed + "\nassistant:"


class LlamaRunner:
    def __init__(self, config: ChatConfig) -> None:
        self.config = config

    def validate(self) -> None:
        if not self.config.model.exists():
            raise FileNotFoundError(f"Model not found: {self.config.model}")

    def generate(self, prompt: str) -> str:
        cmd = [
            self.config.llama_cli,
            "-m",
            str(self.config.model),
            "-t",
            str(self.config.threads),
            "-c",
            str(self.config.context_size),
            "-n",
            str(self.config.max_tokens),
            "--temp",
            str(self.config.temperature),
            "-p",
            prompt,
            "--no-display-prompt",
        ]
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else "(no stderr)"
            raise RuntimeError(f"llama-cli failed: {stderr}") from exc

        output = (result.stdout or "").strip()
        if not output:
            return "[No response from model]"
        return output


def print_help() -> None:
    print(
        """
Commands:
  /help                 Show this help
  /exit                 Quit
  /clear                Clear chat history
  /config               Show active model/runtime configuration
  /set temp <float>     Set temperature (e.g. /set temp 0.6)
  /set tokens <int>     Set max output tokens (e.g. /set tokens 200)
  /set threads <int>    Set threads (e.g. /set threads 8)
""".strip()
    )


def handle_command(line: str, config: ChatConfig, state: ChatState) -> bool:
    parts = shlex.split(line)
    cmd = parts[0]

    if cmd == "/exit":
        print("Bye.")
        return False
    if cmd == "/help":
        print_help()
        return True
    if cmd == "/clear":
        state.history.clear()
        print("History cleared.")
        return True
    if cmd == "/config":
        print(config)
        return True
    if cmd == "/set" and len(parts) == 3:
        key, value = parts[1], parts[2]
        if key == "temp":
            config.temperature = float(value)
            print(f"temperature={config.temperature}")
            return True
        if key == "tokens":
            config.max_tokens = int(value)
            print(f"max_tokens={config.max_tokens}")
            return True
        if key == "threads":
            config.threads = int(value)
            print(f"threads={config.threads}")
            return True

    print("Unknown command. Type /help")
    return True


def run_chat(config: ChatConfig) -> int:
    runner = LlamaRunner(config)
    runner.validate()
    state = ChatState()

    print("TermuxAI started. Type /help for commands.")
    while True:
        try:
            line = input("you> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            return 0

        if not line:
            continue

        if line.startswith("/"):
            keep_going = handle_command(line, config, state)
            if not keep_going:
                return 0
            continue

        state.add_turn("user", line)
        prompt = state.render_prompt(config.system_prompt)

        try:
            response = runner.generate(prompt)
        except Exception as exc:
            print(f"error> {exc}")
            continue

        state.add_turn("assistant", response)
        print(f"ai> {response}\n")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local AI chat for Termux using llama.cpp")
    parser.add_argument("--model", required=True, help="Path to GGUF model")
    parser.add_argument("--llama-cli", default="llama-cli", help="Path to llama-cli binary")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--context", type=int, default=2048)
    parser.add_argument("--temp", type=float, default=0.7)
    parser.add_argument("--tokens", type=int, default=256)
    parser.add_argument("--system", default=DEFAULT_SYSTEM_PROMPT, help="System prompt")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    config = ChatConfig(
        llama_cli=args.llama_cli,
        model=Path(args.model).expanduser(),
        threads=args.threads,
        context_size=args.context,
        temperature=args.temp,
        max_tokens=args.tokens,
        system_prompt=args.system,
    )
    return run_chat(config)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
