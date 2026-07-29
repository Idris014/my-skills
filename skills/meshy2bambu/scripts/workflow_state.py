#!/usr/bin/env python3
"""Persist and enforce Meshy2Bambu user-approved stage gates."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GATES = tuple(f"G{index}" for index in range(10))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_path(job_dir: str) -> Path:
    return Path(job_dir).expanduser().resolve() / "workflow-state.json"


def read_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Workflow state not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "meshy2bambu/v1":
        raise ValueError(f"Unsupported workflow schema in {path}")
    return value


def write_state(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def gate_index(gate: str) -> int:
    if gate not in GATES:
        raise ValueError(f"Unknown gate {gate}; expected one of {', '.join(GATES)}")
    return int(gate[1:])


def init(args: argparse.Namespace) -> int:
    path = state_path(args.job_dir)
    if path.exists() and not args.force:
        raise FileExistsError(f"Workflow already exists: {path}")
    state = {
        "schema": "meshy2bambu/v1",
        "job_name": args.job_name,
        "created_at": now(),
        "updated_at": now(),
        "current_gate": "G0",
        "intake": {
            "source_mode": args.source_mode,
            "multiview": args.multiview,
            "source_note": args.source_note,
        },
        "approvals": {},
        "completions": {
            "G0": {
                "completed_at": now(),
                "note": "Mandatory material intake recorded.",
            }
        },
    }
    write_state(path, state)
    print(path)
    return 0


def approve(args: argparse.Namespace) -> int:
    path = state_path(args.job_dir)
    state = read_state(path)
    target = gate_index(args.gate)
    current = gate_index(state["current_gate"])
    if target != current + 1:
        raise ValueError(
            f"Can only approve the next gate; current={state['current_gate']} requested={args.gate}"
        )
    state["approvals"][args.gate] = {
        "approved_at": now(),
        "user_instruction": args.user_instruction,
    }
    state["updated_at"] = now()
    write_state(path, state)
    print(f"Approved {args.gate}")
    return 0


def assert_approved(args: argparse.Namespace) -> int:
    path = state_path(args.job_dir)
    state = read_state(path)
    target = gate_index(args.gate)
    current = gate_index(state["current_gate"])
    if target != current + 1:
        raise ValueError(
            f"Gate order violation; current={state['current_gate']} requested={args.gate}"
        )
    if args.gate not in state.get("approvals", {}):
        raise PermissionError(f"{args.gate} has no explicit user approval")
    print(f"{args.gate} is approved")
    return 0


def complete(args: argparse.Namespace) -> int:
    path = state_path(args.job_dir)
    state = read_state(path)
    target = gate_index(args.gate)
    current = gate_index(state["current_gate"])
    if target != current + 1:
        raise ValueError(
            f"Gate order violation; current={state['current_gate']} requested={args.gate}"
        )
    if args.gate not in state.get("approvals", {}):
        raise PermissionError(f"{args.gate} has no explicit user approval")
    state["completions"][args.gate] = {
        "completed_at": now(),
        "note": args.note,
        "outputs": args.output,
    }
    state["current_gate"] = args.gate
    state["updated_at"] = now()
    write_state(path, state)
    print(f"Completed {args.gate}; stop and request approval for the next gate.")
    return 0


def show(args: argparse.Namespace) -> int:
    print(json.dumps(read_state(state_path(args.job_dir)), indent=2, ensure_ascii=False))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    command = subparsers.add_parser("init")
    command.add_argument("--job-dir", required=True)
    command.add_argument("--job-name", required=True)
    command.add_argument("--source-mode", choices=("render", "description"), required=True)
    command.add_argument(
        "--multiview",
        choices=("existing", "meshy-generate", "skip"),
        required=True,
    )
    command.add_argument("--source-note", default="")
    command.add_argument("--force", action="store_true")
    command.set_defaults(handler=init)

    command = subparsers.add_parser("approve")
    command.add_argument("--job-dir", required=True)
    command.add_argument("--gate", choices=GATES[1:], required=True)
    command.add_argument("--user-instruction", required=True)
    command.set_defaults(handler=approve)

    command = subparsers.add_parser("assert-approved")
    command.add_argument("--job-dir", required=True)
    command.add_argument("--gate", choices=GATES[1:], required=True)
    command.set_defaults(handler=assert_approved)

    command = subparsers.add_parser("complete")
    command.add_argument("--job-dir", required=True)
    command.add_argument("--gate", choices=GATES[1:], required=True)
    command.add_argument("--note", required=True)
    command.add_argument("--output", action="append", default=[])
    command.set_defaults(handler=complete)

    command = subparsers.add_parser("show")
    command.add_argument("--job-dir", required=True)
    command.set_defaults(handler=show)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.handler(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, FileExistsError, PermissionError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
