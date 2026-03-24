"""
Connect Codex-style agents to Central Brain.

This module does not call a Codex API directly. Its job is to:
1. create or reuse a Central Brain session
2. save user messages
3. fetch the shared context block
4. build a system prompt for Codex
5. save the assistant response back to Central Brain

Usage examples:
    python3 codex_integration.py --prompt "ช่วยสรุประบบนี้"
    python3 codex_integration.py --session-id abc123 --prompt "ช่วยวางแผน refactor"
    python3 codex_integration.py --session-id abc123 --reply "นี่คือคำตอบจาก Codex"
"""

import argparse
from typing import Optional

import requests
from requests import RequestException

BASE = "http://localhost:7799"


class CodexBrain:
    """Small helper for connecting any Codex-like agent to Central Brain."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        project: str = "default",
        title: str = "Codex Session",
        base_url: str = BASE,
    ):
        self.base_url = base_url.rstrip("/")
        self.project = project
        self.session_id = session_id or self._create_session(title)

    def _create_session(self, title: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/sessions",
                json={
                    "ai_agent": "codex",
                    "project": self.project,
                    "title": title,
                },
                timeout=10,
            )
            response.raise_for_status()
            session_id = response.json()["session_id"]
            print(f"✅ Codex session created: {session_id}")
            return session_id
        except RequestException as exc:
            raise RuntimeError(connection_error_text(self.base_url)) from exc

    def save_message(self, role: str, content: str) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                json={
                    "session_id": self.session_id,
                    "role": role,
                    "content": content,
                },
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            raise RuntimeError(connection_error_text(self.base_url)) from exc

    def get_context(self) -> str:
        try:
            response = requests.get(
                f"{self.base_url}/context/{self.session_id}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()["context_block"]
        except RequestException as exc:
            raise RuntimeError(connection_error_text(self.base_url)) from exc

    def set_memory(self, key: str, value: str, scope: str = "global") -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/memory",
                json={
                    "key": key,
                    "value": value,
                    "scope": scope,
                    "ai_agent": "all",
                },
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            raise RuntimeError(connection_error_text(self.base_url)) from exc

    def build_system_prompt(self, extra_instruction: Optional[str] = None) -> str:
        context_block = self.get_context()
        prompt = (
            "You are Codex connected to Central Brain.\n\n"
            "Read the memory and conversation history below before answering.\n"
            "When relevant, continue the existing work instead of starting over.\n"
            "If context is missing, say so explicitly.\n\n"
            "=== CENTRAL BRAIN CONTEXT ===\n"
            f"{context_block or '[no context yet]'}"
        )
        if extra_instruction:
            prompt += f"\n\n=== EXTRA INSTRUCTION ===\n{extra_instruction}"
        return prompt

    def prepare_turn(self, user_prompt: str, extra_instruction: Optional[str] = None) -> dict:
        self.save_message("user", user_prompt)
        return {
            "session_id": self.session_id,
            "system_prompt": self.build_system_prompt(extra_instruction=extra_instruction),
            "user_prompt": user_prompt,
        }

    def save_codex_reply(self, reply: str) -> dict:
        return self.save_message("assistant", reply)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare or save a Codex turn with Central Brain.")
    parser.add_argument("--session-id", help="Reuse an existing Central Brain session.")
    parser.add_argument("--project", default="default", help="Project name for new sessions.")
    parser.add_argument("--title", default="Codex Session", help="Title for a new session.")
    parser.add_argument("--prompt", help="User prompt to save and prepare for Codex.")
    parser.add_argument("--reply", help="Codex reply to save back into Central Brain.")
    parser.add_argument(
        "--instruction",
        help="Extra instruction appended to the generated system prompt.",
    )
    parser.add_argument("--memory-key", help="Optional memory key to write before the turn.")
    parser.add_argument("--memory-value", help="Optional memory value to write before the turn.")
    parser.add_argument("--base-url", default=BASE, help="Central Brain base URL.")
    return parser


def connection_error_text(base_url: str) -> str:
    return (
        f"Cannot connect to Central Brain at {base_url}.\n"
        "Make sure the API server is running first:\n"
        "  bash start.sh"
    )


def main() -> None:
    args = build_arg_parser().parse_args()

    try:
        brain = CodexBrain(
            session_id=args.session_id,
            project=args.project,
            title=args.title,
            base_url=args.base_url,
        )

        if args.memory_key and args.memory_value:
            brain.set_memory(args.memory_key, args.memory_value)
            print(f"💾 Memory saved: {args.memory_key}")

        if args.prompt:
            prepared = brain.prepare_turn(args.prompt, extra_instruction=args.instruction)
            print("\n=== COPY INTO CODEX SYSTEM PROMPT ===")
            print(prepared["system_prompt"])
            print("\n=== USER PROMPT ===")
            print(prepared["user_prompt"])
            print(f"\nSESSION_ID={prepared['session_id']}")

        if args.reply:
            brain.save_codex_reply(args.reply)
            print(f"✅ Saved Codex reply to session: {brain.session_id}")

        if not args.prompt and not args.reply:
            print(f"SESSION_ID={brain.session_id}")
            print("Use --prompt to prepare a turn or --reply to save a Codex answer.")
    except RuntimeError as exc:
        print(f"❌ {exc}")


if __name__ == "__main__":
    main()
