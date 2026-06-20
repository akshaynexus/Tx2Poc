#!/usr/bin/env python3
"""Manage twitter-nitter-rss polling checkpoints."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STATE_FILE = Path("./twitter-events/state.json")


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_time(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_state() -> dict[str, Any]:
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_state(data: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def command_window(_: argparse.Namespace) -> None:
    state = load_state()
    check_started_at = utc_now()
    try:
        last_check_time = parse_time(str(state["last_check_time"]))
        source = "state"
    except Exception:
        last_check_time = check_started_at - timedelta(minutes=10)
        source = "default_now_minus_10min"

    print(json.dumps({
        "check_started_at": format_time(check_started_at),
        "last_check_time": format_time(last_check_time),
        "source": source,
    }, indent=2, sort_keys=True))


def command_complete(args: argparse.Namespace) -> None:
    state = load_state()
    state["last_check_time"] = format_time(parse_time(args.checked_at))
    state["last_run_completed_at"] = format_time(utc_now())
    write_state(state)
    print(json.dumps(state, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage twitter-browser-mcp polling state.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("window", help="Print the current polling window.").set_defaults(func=command_window)

    complete = sub.add_parser("complete", help="Advance last_check_time after a successful scan.")
    complete.add_argument("--checked-at", required=True, help="Use check_started_at from window output.")
    complete.set_defaults(func=command_complete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
