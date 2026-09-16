"""Terminal rendering helpers for Talkdesk Email Autopilot CLI Demo."""
from __future__ import annotations

import json
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Sequence


USE_COLOR = sys.stdout.isatty() and "--no-color" not in sys.argv


def term_width(default: int = 80) -> int:
    try:
        return max(60, min(100, shutil.get_terminal_size((default, 24)).columns))
    except OSError:
        return default


def color(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    codes = {
        "green": "32",
        "red": "31",
        "blue": "34",
        "cyan": "36",
        "yellow": "33",
        "gray": "90",
        "bold": "1",
        "dim": "2",
        "magenta": "35",
    }
    c = codes.get(code, "0")
    return f"\033[{c}m{text}\033[0m"


def print_header(text: str) -> None:
    w = term_width()
    bar = "=" * max(8, w - 4)
    print()
    print(color(f"  {bar}", "dim"))
    print(color(f"  {text}", "bold"))
    print(color(f"  {bar}", "dim"))
    print()


def print_box(lines: Sequence[str], title: Optional[str] = None) -> None:
    w = min(72, term_width() - 4)
    inner = w - 4
    top = "┌" + "─" * (w - 2) + "┐"
    bot = "└" + "─" * (w - 2) + "┘"
    print(f"  {top}")
    if title:
        t = title[:inner]
        print(f"  │ {t:<{inner}} │")
        print(f"  │ {'─' * inner} │")
    for raw in lines:
        for chunk in _wrap(raw, inner):
            print(f"  │ {chunk:<{inner}} │")
    print(f"  {bot}")


def _wrap(text: str, width: int) -> List[str]:
    if not text:
        return [""]
    out: List[str] = []
    for para in text.split("\n"):
        if not para:
            out.append("")
            continue
        words = para.split(" ")
        line = ""
        for word in words:
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= width:
                line += " " + word
            else:
                out.append(line)
                line = word
            while len(line) > width:
                out.append(line[:width])
                line = line[width:]
        if line or para == "":
            out.append(line)
    return out or [""]


def print_json(data: Any) -> None:
    """Pretty-print a JSON object indented like HTML task results."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    for line in text.split("\n"):
        print(f"  {line}")
    print()


def print_stage(title: str, data: Optional[dict] = None) -> None:
    print()
    print(color(f"  ─── {title} ───", "bold"))
    print()
    if data is not None:
        print_json(data)


def print_substep(name: str, data: Optional[dict] = None) -> None:
    print()
    print(color(f"  ── {name} ──", "cyan"))
    print()
    if data is not None:
        print_json(data)


def print_email(mail: dict, index: Optional[int] = None, specialist: bool = False) -> None:
    direction = mail.get("dir", "IN")
    if direction == "IN":
        tag = "INBOUND"
        arrow = "<<<"
        tag_col = "cyan"
    else:
        tag = "OUTBOUND"
        arrow = ">>>"
        tag_col = "green"
    title = f"{tag} EMAIL"
    if index is not None:
        title = f"{tag} EMAIL #{index}"
    if specialist or (direction == "OUT" and "specialist" in (mail.get("from") or "").lower()):
        title += "  [SPECIALIST]"
        tag_col = "magenta"
    print()
    print(color(f"  {arrow} {title}", tag_col))
    lines = [
        f"FROM: {mail.get('from', '—')}",
        f"TIME: {mail.get('time', '—')}",
        f"SUBJ: {mail.get('subject', '—')}",
        "",
    ]
    body = mail.get("body", "")
    lines.extend(body.split("\n"))
    if mail.get("disclosure"):
        lines.append("")
        lines.append("-- AI Disclosure --")
        lines.extend(_wrap(mail["disclosure"], min(68, term_width() - 8)))
    print_box(lines)
    print()


def print_human_pause(assignee: str = "Priya N.", queue: str = "dispute") -> None:
    print()
    bar = "=" * 48
    print(color(f"  {bar}", "yellow"))
    print(color("  ⏸  AUTOPILOT PAUSED — Waiting for human takeover", "yellow"))
    print(color(f"     Specialist: {assignee} · {queue} queue", "yellow"))
    print(color(f"  {bar}", "yellow"))
    print()


def print_welcome() -> None:
    print()
    print_box(
        [
            "Talkdesk Email Autopilot · CLI Demo",
            "Meridian Trust · Multi-Agent Workflow",
            "",
            "Mock data only — no live APIs / LLM calls.",
        ],
        title="EMAIL AUTOPILOT",
    )
    print()


def print_prompt(text: str) -> None:
    print(color(f"  > {text}", "yellow"))


def wait_enter(message: str = "Press Enter to continue", auto_delay: float = 0.35) -> None:
    if "--auto" in sys.argv:
        time.sleep(auto_delay)
        return
    try:
        input(color(f"  > {message} ", "yellow"))
    except EOFError:
        print()


def spinner(text: str, seconds: float = 0.35) -> None:
    if "--auto" in sys.argv:
        seconds = max(0.05, seconds / 3.0)
    frames = "|/-\\"
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r  {color(frame, 'cyan')} {text}   ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 8) + "\r")
    sys.stdout.flush()


def print_result(fixture: dict) -> None:
    print_header("RUN COMPLETE")
    print(f"  {fixture.get('label', 'Case')}")
    print()
    result = fixture.get("result") or ""
    for line in result.strip().split("\n"):
        print(color(f"  {line}", "green"))
    print()


def preview_mail(mail: dict) -> None:
    print_header(mail.get("label") or mail.get("id") or "EMAIL TEMPLATE")
    print_email(mail)
    wait_enter("Press Enter to go back")
