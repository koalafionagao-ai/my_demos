"""Terminal rendering helpers for Talkdesk Email Autopilot CLI Demo."""
from __future__ import annotations

import json
import shutil
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence


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


def _fmt_val(v: Any) -> str:
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, separators=(",", ": "))
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def print_email(mail: dict, index: Optional[int] = None) -> None:
    direction = mail.get("dir", "IN")
    tag = "INBOUND" if direction == "IN" else "OUTBOUND"
    tag_col = "cyan" if direction == "IN" else "green"
    title = f"{tag} EMAIL"
    if index is not None:
        title = f"{tag} EMAIL #{index}"
    print()
    print(color(f"  >>> {title}", tag_col))
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
    if mail.get("file"):
        print(color(f"  file: data/{mail['file']}", "gray"))
    print()


def print_data(data: dict) -> None:
    """Render structured {input, tools, output} I/O for a beat."""
    if not data:
        return
    for section in ("input", "tools", "output"):
        block = data.get(section)
        if not block:
            continue
        label = section.capitalize()
        print(color(f"  | {label}", "dim"))
        if isinstance(block, dict):
            max_k = max((len(str(k)) for k in block.keys()), default=8)
            for k, v in block.items():
                print(f"  |   {str(k):<{max_k}}  {_fmt_val(v)}")
        else:
            print(f"  |   {_fmt_val(block)}")


def print_human_badge() -> str:
    return color("[HUMAN]", "magenta")


def print_beat(beat: dict, duration: str) -> None:
    status = beat.get("k", "ok")
    if status == "risk":
        mark = color("FAILED", "red")
    else:
        mark = color("OK", "green")

    agent = beat.get("agent") or ""
    node = beat.get("node") or beat.get("title") or beat.get("s") or beat.get("id")
    if agent and node and not str(node).startswith(agent):
        title = f"{agent} · {node}"
    else:
        title = beat.get("title") or node or beat.get("id")

    human_tag = f"  {print_human_badge()}" if beat.get("human") else ""
    print()
    print(
        color(f"  -- {title} ", "blue")
        + color(f"· {duration}s ", "gray")
        + f"-- {mark}{human_tag}"
    )

    action = beat.get("action")
    if isinstance(action, str) and action:
        print(color(f"  | Action  {action}", "dim"))

    data = beat.get("data")
    if data:
        print_data(data)
    else:
        # Backward-compatible fallback
        think = beat.get("think") or []
        actions = beat.get("action") or []
        if think:
            print(color("  | Think", "dim"))
            max_k = max((len(str(r.get("k", ""))) for r in think), default=8)
            for row in think:
                k = str(row.get("k", ""))
                v = str(row.get("v", ""))
                print(f"  |   {k:<{max_k}}  {v}")
        if isinstance(actions, list) and actions:
            print(color("  | Action", "dim"))
            for a in actions:
                print(f"  |   {a}")
    print()


def print_ticket(
    ticket: dict,
    ticket_id: str,
    prev_status: Optional[str] = None,
) -> None:
    """Render ticket state box with optional status transition."""
    status = ticket.get("status")
    owner = ticket.get("owner")
    note = ticket.get("note")
    files = ticket.get("files") or []

    lines: List[str] = []
    if status:
        if prev_status and prev_status != status:
            lines.append(f"Status: {prev_status} → {status}")
        elif status:
            lines.append(f"Status: → {status}" if not prev_status else f"Status: {status}")
    if owner:
        lines.append(f"Owner:  {owner}")
    if note:
        lines.append(f"Note:   {note}")
    for f in files:
        name = f.get("name", "?") if isinstance(f, dict) else str(f)
        fnote = f.get("note", "") if isinstance(f, dict) else ""
        lines.append(f"File:   {name}" + (f" ({fnote})" if fnote else ""))

    if not lines:
        return

    title = f"TICKET {ticket_id}"
    print()
    print_box(lines, title=title)


def print_summary(summary_text: str) -> None:
    """Render bot summary block (Ask / Autopilot / Human / Waiting / Ticket / Case)."""
    if not summary_text:
        return
    print()
    print(color("  > Summary", "yellow"))
    for line in summary_text.strip().split("\n"):
        print(color(f"  > {line}", "yellow"))
    print()


def print_human_gate(beat: dict) -> None:
    """Print Autopilot pause banner before waiting for human takeover."""
    data = beat.get("data") or {}
    out = data.get("output") or {}
    assignee = out.get("assignee") or "Specialist"
    queue = out.get("queue") or "dispute"

    print()
    bar = "=" * 48
    print(color(f"  {bar}", "yellow"))
    print(color("  ⏸  AUTOPILOT PAUSED — Waiting for human takeover", "yellow"))
    print(color(f"     Specialist: {assignee} · {queue} queue", "yellow"))
    print(color("     Packet: Case memory + docs + context", "yellow"))
    print(color(f"  {bar}", "yellow"))
    print()


def print_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    cols = list(zip(*([headers] + [list(r) for r in rows]))) if rows else [headers]
    widths = [max(len(str(c)) for c in col) for col in cols]

    def fmt(row: Sequence[str]) -> str:
        return " │ ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))

    sep = "-+-".join("-" * w for w in widths)
    print(f"  {fmt(headers)}")
    print(f"  {sep}")
    for row in rows:
        print(f"  {fmt(row)}")


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


def spinner(text: str, seconds: float = 0.55) -> None:
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


def print_result(
    fixture: dict,
    ok_count: int,
    total: int,
    task_ids: Iterable[str],
    final_ticket: Optional[dict] = None,
    final_summary: Optional[str] = None,
) -> None:
    print_header("RUN COMPLETE")
    print(f"  {fixture.get('label', 'Case')}")
    print(color(f"  {fixture.get('result', '')}", "green"))
    print()

    if final_ticket and final_ticket.get("status"):
        tid = (fixture.get("ticket") or {}).get("id", "")
        owner = final_ticket.get("owner", "—")
        print(f"  Ticket {tid}: {final_ticket.get('status')} · Owner: {owner}")
        print()

    if final_summary:
        print_summary(final_summary)

    delta = fixture.get("delta") or []
    if delta:
        print_table(
            ["Metric", "Before", "After"],
            [[d["m"], d["before"], d["after"]] for d in delta],
        )
        print()
    tasks = " · ".join(f"{tid} {color('OK', 'green')}" for tid in task_ids)
    print(f"  Steps: {total} total · {ok_count} {color('OK', 'green')} · {total - ok_count} failed")
    print(f"  Tasks: {tasks}")
    print()


def print_memory_dump(memory: Dict[str, Any], fixture: dict) -> None:
    """Print full memory & context dump after run complete."""
    ticket = fixture.get("ticket") or {}
    ticket_id = ticket.get("id", "")

    print()
    print(color("  ╔══════════════════════════════════════════════╗", "cyan"))
    print(color("  ║  MEMORY & CONTEXT DUMP                       ║", "cyan"))
    print(color("  ╠══════════════════════════════════════════════╣", "cyan"))
    print()

    # 5.1 Working Context
    beats = memory.get("beats") or []
    print(color(f"  ── Working Context ({len(beats)} beats) ──", "bold"))
    print()
    for i, entry in enumerate(beats, 1):
        title = entry.get("title") or entry.get("node") or f"beat-{i}"
        print(f"  [{i}] {title}")
        data = entry.get("data") or {}
        for section in ("input", "tools", "output"):
            block = data.get(section)
            if block is None:
                continue
            print(f"       {section}:  {_fmt_val(block)}")
        print()

    # 5.2 Ticket Timeline
    ticket_log = memory.get("ticket_log") or []
    print(color(f"  ── Ticket {ticket_id} Timeline ──", "bold"))
    print()
    if ticket_log:
        for entry in ticket_log:
            idx = entry.get("beat_index", "?")
            status = entry.get("status") or "—"
            owner = entry.get("owner") or "—"
            note = entry.get("note") or ""
            print(f"  [{idx}]  {status:<14}  {owner:<22}  {note}")
    else:
        print("  (no ticket status changes)")
    print()

    # 5.3 Task Results
    task_results = memory.get("task_results") or {}
    task_defs = {t["id"]: t for t in (fixture.get("tasks") or [])}
    print(color("  ── Task Results ──", "bold"))
    print()
    for tid, result in task_results.items():
        tdef = task_defs.get(tid) or {}
        title = tdef.get("title", tid)
        print(f"  {tid}  {title}")
        print(f"       {_fmt_val(result)}")
        print()
    if not task_results:
        # Fall back to fixture task.result
        for tdef in fixture.get("tasks") or []:
            print(f"  {tdef['id']}  {tdef.get('title', '')}")
            print(f"       {_fmt_val(tdef.get('result') or {})}")
            print()

    # 5.4 Final Bot Summary
    summary = memory.get("final_summary") or ""
    print(color("  ── Bot Summary ──", "bold"))
    print()
    if summary:
        for line in summary.strip().split("\n"):
            print(f"  {line}")
    else:
        print("  (none)")
    print()

    # 5.5 Mail Stream
    mail_log = memory.get("mail_log") or []
    print(color(f"  ── Mail Stream ({len(mail_log)} emails) ──", "bold"))
    print()
    for entry in mail_log:
        idx = entry.get("index", "?")
        direction = entry.get("dir", "?")
        t = entry.get("time", "—")
        subj = entry.get("subject", "—")
        print(f"  #{idx}  {direction:<3}  {t:<18}  {subj}")
    if not mail_log:
        print("  (none)")
    print()
