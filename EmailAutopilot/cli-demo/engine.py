"""Playback engine for Case A / Case B multi-agent workflows."""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

import render


class RunMemory:
    """Accumulates beat data, ticket timeline, task results, and mail stream."""

    def __init__(self) -> None:
        self.beats: List[Dict[str, Any]] = []
        self.ticket_log: List[Dict[str, Any]] = []
        self.task_results: Dict[str, Any] = {}
        self.mail_log: List[Dict[str, Any]] = []
        self.final_summary: str = ""
        self.final_ticket: Dict[str, Any] = {}

    def as_dict(self) -> Dict[str, Any]:
        return {
            "beats": self.beats,
            "ticket_log": self.ticket_log,
            "task_results": self.task_results,
            "mail_log": self.mail_log,
            "final_summary": self.final_summary,
            "final_ticket": self.final_ticket,
        }


def duration_for(beat: dict) -> str:
    if beat.get("dur"):
        return str(beat["dur"])
    if beat.get("mails"):
        return f"{0.8 + 0.4 * len(beat['mails']):.1f}"
    return f"{0.4 + random.random() * 0.9:.1f}"


def _task_title(fixture: dict, task_id: str) -> str:
    for t in fixture.get("tasks") or []:
        if t.get("id") == task_id:
            return t.get("title") or task_id
    return task_id


def _task_result(fixture: dict, task_id: str, beat: dict) -> Any:
    """Prefer fixture task.result; fall back to beat data.output."""
    for t in fixture.get("tasks") or []:
        if t.get("id") == task_id and t.get("result") is not None:
            return t["result"]
    data = beat.get("data") or {}
    return data.get("output") or {}


def run_case(fixture: dict, mails: Dict[str, dict], speed: float = 1.0) -> None:
    render.print_header(fixture.get("label", "Case"))
    ticket_meta = fixture.get("ticket") or {}
    ticket_id = ticket_meta.get("id", "—")
    render.print_box(
        [
            f"Ticket: {ticket_id}",
            f"Title:  {ticket_meta.get('title', '—')}",
            f"Customer: {ticket_meta.get('customer', '—')}",
            f"Inbound template: {fixture.get('inbound', '—')}",
        ],
        title="CASE CONTEXT",
    )

    memory = RunMemory()
    done_tasks: List[str] = []
    mail_index = 0
    ok_count = 0
    beats = fixture.get("run") or []
    prev_ticket_status: Optional[str] = None
    current_ticket: Dict[str, Any] = {}

    for beat_i, beat in enumerate(beats, 1):
        pause = beat.get("pause")
        mail_ids = beat.get("mails") or []

        # Customer-response pause before showing inbound follow-up mail
        if pause == "customer" and mail_ids:
            mid = mail_ids[0]
            mail = mails.get(mid, {})
            render.print_header("WAITING FOR CUSTOMER")
            prompt = mail.get("prompt") or "Press Enter to simulate customer response."
            render.print_prompt(prompt)
            render.wait_enter("Press Enter to continue")

        # Send inbound starter (prompt only — numbered card shown after beat)
        if pause == "send" and mail_ids:
            mid = mail_ids[0]
            mail = mails.get(mid, {})
            render.print_header("STEP · SEND INBOUND EMAIL")
            render.print_prompt(f"Ready to send template: data/{mail.get('file', mid)}")
            render.wait_enter("Press Enter to send this email (or type Enter to proceed)")
            render.spinner("Sending inbound email…", 0.7 / speed)

        # Agent step animation
        dur = duration_for(beat)
        render.spinner(f"Running · {beat.get('title', beat.get('id'))}…", float(dur) * 0.55 / speed)
        render.print_beat(beat, dur)
        ok_count += 1 if beat.get("k") != "risk" else 0

        # Accumulate beat into memory
        memory.beats.append(
            {
                "title": beat.get("title") or beat.get("node") or beat.get("id"),
                "node": beat.get("node"),
                "agent": beat.get("agent"),
                "data": beat.get("data") or {},
                "action": beat.get("action"),
                "result": beat.get("result") or beat.get("k"),
            }
        )

        # Mail stream — always numbered, after the beat (matches HTML email stream order)
        if mail_ids:
            for mid in mail_ids:
                mail = mails.get(mid)
                if not mail:
                    continue
                mail_index += 1
                if pause == "customer":
                    render.print_email(mail, index=mail_index)
                elif pause in ("mail", "send") or mail.get("dir") == "OUT":
                    if mail.get("dir") == "OUT":
                        render.print_header("OUTBOUND EMAIL")
                    elif pause == "send":
                        render.print_header("INBOUND EMAIL")
                    else:
                        render.print_header("EMAIL")
                    render.print_email(mail, index=mail_index)
                    if pause != "send":
                        render.wait_enter("Press Enter to continue")
                else:
                    render.print_email(mail, index=mail_index)

                memory.mail_log.append(
                    {
                        "index": mail_index,
                        "id": mid,
                        "dir": mail.get("dir", "?"),
                        "time": mail.get("time", "—"),
                        "subject": mail.get("subject", "—"),
                        "from": mail.get("from", "—"),
                    }
                )

        # Ticket lifecycle
        ticket_patch = beat.get("ticket")
        if ticket_patch:
            status_changed = (
                "status" in ticket_patch
                and ticket_patch.get("status") != prev_ticket_status
            )
            # Merge patch into current ticket state
            current_ticket = {**current_ticket, **ticket_patch}

            if status_changed or ticket_patch.get("note") or ticket_patch.get("owner"):
                render.print_ticket(
                    ticket_patch,
                    ticket_id=ticket_id,
                    prev_status=prev_ticket_status if status_changed else None,
                )

            # Bot summary at ticket status milestones only
            if status_changed and ticket_patch.get("summary"):
                render.print_summary(ticket_patch["summary"])

            if ticket_patch.get("status"):
                memory.ticket_log.append(
                    {
                        "beat_index": beat_i,
                        "status": ticket_patch.get("status"),
                        "owner": ticket_patch.get("owner")
                        or current_ticket.get("owner", "—"),
                        "note": ticket_patch.get("note") or "",
                    }
                )
                prev_ticket_status = ticket_patch["status"]

            if ticket_patch.get("summary"):
                memory.final_summary = ticket_patch["summary"]

            memory.final_ticket = dict(current_ticket)

        # Human gate — Autopilot pause
        if beat.get("waitHuman"):
            render.print_human_gate(beat)
            # Longer delay in auto mode so the pause is visible
            render.wait_enter(
                'Press Enter to simulate "Take over as specialist"',
                auto_delay=1.2,
            )
            print(render.color("  ✓ Specialist took over", "green"))
            print()
            # After takeover, ticket moves to In Progress (human) — mirror HTML
            if prev_ticket_status == "Waiting":
                takeover_patch = {
                    "status": "In Progress",
                    "owner": current_ticket.get("owner") or "Priya N. · Dispute",
                    "note": "Specialist took over · Autopilot resumed for human steps.",
                }
                render.print_ticket(
                    takeover_patch,
                    ticket_id=ticket_id,
                    prev_status=prev_ticket_status,
                )
                current_ticket = {**current_ticket, **takeover_patch}
                memory.ticket_log.append(
                    {
                        "beat_index": f"{beat_i}+",
                        "status": "In Progress",
                        "owner": takeover_patch["owner"],
                        "note": takeover_patch["note"],
                    }
                )
                prev_ticket_status = "In Progress"
                memory.final_ticket = dict(current_ticket)

        # Task completion
        if beat.get("doneTask") and beat.get("taskId"):
            tid = beat["taskId"]
            if tid not in done_tasks:
                done_tasks.append(tid)
            memory.task_results[tid] = _task_result(fixture, tid, beat)
            title = _task_title(fixture, tid)
            render.print_prompt(f"✓ Task {tid} complete ({title})")
            print()

    render.print_result(
        fixture,
        ok_count,
        len(beats),
        done_tasks,
        final_ticket=memory.final_ticket,
        final_summary=None,  # Bot Summary lives in memory dump below
    )
    render.print_memory_dump(memory.as_dict(), fixture)
    render.wait_enter("Press Enter to return to menu")


def preview_mail(mail: dict) -> None:
    render.print_header(mail.get("label") or mail.get("id") or "EMAIL TEMPLATE")
    render.print_email(mail)
    render.wait_enter("Press Enter to go back")
