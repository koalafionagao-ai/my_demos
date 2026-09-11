#!/usr/bin/env python3
"""Talkdesk Email Autopilot · CLI Demo

Interactive Terminal walkthrough of Case A (Loan Status) and Case B (Dispute Doc).
All data is mock — no live APIs or LLM calls.

Usage:
  python3 run.py
  python3 run.py --auto
  python3 run.py --speed 2
  python3 run.py --no-color
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import engine
import render

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def load_json(name: str):
    path = DATA / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Talkdesk Email Autopilot CLI Demo")
    p.add_argument("--auto", action="store_true", help="Auto-play without waiting for Enter")
    p.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (default 1.0)")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    p.add_argument("--case", choices=["A", "B", "a", "b"], help="Jump straight into a case")
    return p.parse_args(argv)


def list_emails(mails: dict, case_filter=None):
    items = []
    for mid, m in mails.items():
        if case_filter and m.get("case") != case_filter:
            continue
        items.append((mid, m))
    return items


def email_menu(mails: dict) -> None:
    while True:
        render.print_header("EMAIL TEMPLATES")
        print("  Pre-stored templates under data/emails/")
        print()
        print("  [A] Case A templates (A1 inbound · A2 outbound)")
        print("  [B] Case B templates (B1 … B5)")
        print("  [1] List all templates")
        print("  [q] Back")
        print()
        try:
            choice = input(render.color("  Select ▸ ", "yellow")).strip().lower()
        except EOFError:
            return
        if choice in ("q", "quit", "back"):
            return
        if choice == "a":
            _pick_and_preview(list_emails(mails, "caseA"), mails)
        elif choice == "b":
            _pick_and_preview(list_emails(mails, "caseB"), mails)
        elif choice == "1":
            _pick_and_preview(list_emails(mails), mails)
        else:
            print(render.color("  Unknown option.", "red"))


def _pick_and_preview(items, mails: dict) -> None:
    if not items:
        print("  No templates.")
        return
    print()
    for i, (mid, m) in enumerate(items, 1):
        path = m.get("file", "")
        print(f"  [{i}] {mid:4}  {m.get('dir', '?'):3}  {m.get('label', m.get('subject'))}")
        print(render.color(f"       data/{path}", "gray"))
    print("  [q] Back")
    print()
    try:
        choice = input(render.color("  Open template ▸ ", "yellow")).strip().lower()
    except EOFError:
        return
    if choice in ("q", ""):
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(items)):
        print(render.color("  Invalid selection.", "red"))
        return
    mid, _ = items[int(choice) - 1]
    engine.preview_mail(mails[mid])


def main_menu(case_a: dict, case_b: dict, mails: dict, speed: float) -> None:
    while True:
        render.print_welcome()
        print("  [1] Run Case A · Mike · Loan Status · #5108")
        print("  [2] Run Case B · Emily · Dispute Doc · #4821")
        print("  [e] Browse / preview email templates")
        print("  [q] Quit")
        print()
        try:
            choice = input(render.color("  Select ▸ ", "yellow")).strip().lower()
        except EOFError:
            print()
            return
        if choice in ("q", "quit", "exit"):
            print(render.color("  Goodbye.", "gray"))
            return
        if choice in ("1", "a", "casea"):
            engine.run_case(case_a, mails, speed=speed)
        elif choice in ("2", "b", "caseb"):
            engine.run_case(case_b, mails, speed=speed)
        elif choice in ("e", "email", "emails"):
            email_menu(mails)
        else:
            print(render.color("  Unknown option. Choose 1, 2, e, or q.", "red"))


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.auto and "--auto" not in sys.argv:
        sys.argv.append("--auto")
    if args.no_color:
        if "--no-color" not in sys.argv:
            sys.argv.append("--no-color")
        render.USE_COLOR = False

    try:
        mails = load_json("mails.json")
        case_a = load_json("case_a.json")
        case_b = load_json("case_b.json")
    except FileNotFoundError as e:
        print(f"Missing data file: {e}", file=sys.stderr)
        return 1

    speed = max(0.25, float(args.speed or 1.0))

    if args.case:
        render.print_welcome()
        if args.case.lower() == "a":
            engine.run_case(case_a, mails, speed=speed)
        else:
            engine.run_case(case_b, mails, speed=speed)
        return 0

    main_menu(case_a, case_b, mails, speed=speed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
