"""Stage-based playback engine for Case A / Case B (aligned with admin-canvas-v2.html)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import render


def run_case(fixture: dict, mails: Dict[str, dict], speed: float = 1.0) -> None:
    render.print_header(fixture.get("label", "Case"))

    inbound_id = fixture.get("inbound")
    mail_index = 0

    # Inbound email first
    if inbound_id and inbound_id in mails:
        mail_index += 1
        render.print_email(mails[inbound_id], index=mail_index)
        render.wait_enter("Press Enter to start Autopilot", auto_delay=0.4 / speed)

    stages: List[dict] = fixture.get("stages") or []
    for stage in stages:
        mode = stage.get("mode") or "stage"

        if mode == "substeps":
            render.print_stage(stage.get("title", stage.get("taskId", "Stage")), data=None)
            mail_index = _run_substeps(stage.get("substeps") or [], mails, mail_index, speed)
        else:
            render.spinner(f"Running · {stage.get('title', '')}…", 0.35 / speed)
            render.print_stage(stage.get("title", stage.get("taskId", "Stage")), stage.get("data"))

            # Mails attached to a simple stage (e.g. Case A T3 → A2)
            for mid in stage.get("mails") or []:
                mail = mails.get(mid)
                if not mail:
                    continue
                mail_index += 1
                render.print_email(mail, index=mail_index)
                render.wait_enter("Press Enter to continue", auto_delay=0.3 / speed)

            # Human takeover gate (Case B T4)
            if stage.get("waitHuman"):
                out = (stage.get("data") or {}).get("output") or {}
                assignee = out.get("handover") or "Priya N."
                queue = out.get("queue") or "dispute"
                render.print_human_pause(assignee=assignee, queue=queue)
                render.wait_enter(
                    'Press Enter to simulate "Take over as specialist"',
                    auto_delay=1.0 / speed,
                )
                print(render.color("  ✓ Specialist took over", "green"))
                print()

                for mid in stage.get("mails_after_takeover") or []:
                    mail = mails.get(mid)
                    if not mail:
                        continue
                    mail_index += 1
                    render.print_email(mail, index=mail_index, specialist=True)
                    render.wait_enter("Press Enter to continue", auto_delay=0.3 / speed)

        if stage.get("pause_after"):
            render.wait_enter("Press Enter to continue", auto_delay=0.25 / speed)

    render.print_result(fixture)
    render.wait_enter("Press Enter to return to menu", auto_delay=0.2 / speed)


def _run_substeps(
    substeps: List[dict],
    mails: Dict[str, dict],
    mail_index: int,
    speed: float,
) -> int:
    """Play Doc Agent substeps with original mail cadence."""
    for step in substeps:
        pause = step.get("pause")
        mail_ids = step.get("mails") or []

        # Customer inbound: prompt first, then show mail
        if pause == "customer":
            prompt = step.get("customer_prompt") or "Press Enter to simulate customer response."
            render.print_prompt(prompt)
            render.wait_enter("Press Enter to continue", auto_delay=0.5 / speed)
            for mid in mail_ids:
                mail = mails.get(mid)
                if not mail:
                    continue
                mail_index += 1
                render.print_email(mail, index=mail_index)
            continue

        # Named decision / action step
        name = step.get("name")
        if name:
            render.spinner(f"Running · {name}…", 0.3 / speed)
            render.print_substep(name, step.get("data"))

        # Outbound / step mails after the JSON
        if mail_ids:
            for mid in mail_ids:
                mail = mails.get(mid)
                if not mail:
                    continue
                mail_index += 1
                render.print_email(mail, index=mail_index)
            if pause == "mail":
                render.wait_enter("Press Enter to continue", auto_delay=0.3 / speed)

    return mail_index


def preview_mail(mail: dict) -> None:
    render.preview_mail(mail)
