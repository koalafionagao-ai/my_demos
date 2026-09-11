# Talkdesk Email Autopilot · CLI Demo

Interactive Terminal walkthrough of the Meridian Trust multi-agent email workflow.

Mock data only — **no live APIs, LLM calls, or file lookups**.

Aligned with `../product-canvas/admin-canvas.html` and `../product-canvas/workflow-extract.md`.

## Requirements

- Python 3.9+ (stdlib only)
- macOS Terminal / iTerm2 recommended

## Quick start

```bash
cd Talkdesk-case-email/deliverables/cli-demo
python3 run.py
```

### Options

| Flag | Meaning |
|---|---|
| `--auto` | Auto-play (no Enter pauses) |
| `--speed 2` | Faster playback |
| `--no-color` | Disable ANSI colors |
| `--case A` / `--case B` | Jump straight into a case |

```bash
python3 run.py --auto --speed 3 --case A
python3 run.py --case B
```

## Menu

1. **Run Case A** — Mike · Loan Status · #5108 (Query path)
2. **Run Case B** — Emily · Dispute Doc · #4821 (Doc + Exception + Human)
3. **Browse email templates** — preview pre-stored `.txt` files before running

## Cases

### Case A · Mike · #5108

| Task | Agent | Steps |
|---|---|---|
| T1 Orchestrator · Lane gate | Orchestrator | Email Intake → Orchestrator |
| T2 Routing · Understand & route | Routing Agent | Read & Extract → Understand → Validate → Route |
| T3 Query · Answer loan status | Query Agent | Retrieve → Grounding → Generation → Verify → Output |
| T4 Close the loop | System | Close Loop |

Ticket lifecycle: **Open → In Progress → Resolved → Closed**

### Case B · Emily · #4821

| Task | Agent | Steps |
|---|---|---|
| T1 Orchestrator · Lane gate | Orchestrator | Email Intake → Orchestrator |
| T2 Routing · Multi-intent split | Routing Agent | Read & Extract → Understand → Validate → Route |
| T3 Doc · Collect & validate | Doc Agent | Check → Secure Collection → Detection → OCR → Output |
| T4 Exception · Refund block + Human | Exception Agent | Classify → Human Handover → Specialist reply |
| T5 Close the loop | System | Close Loop |

Ticket lifecycle: **Open → In Progress → Waiting → In Progress → Waiting → In Progress (human) → Resolved → Closed**

At Human Handover the CLI **pauses** until you press Enter to simulate specialist takeover.

## What you will see

- Structured step I/O: **Input / Tools / Output** (matches HTML beat `data`)
- Email stream with sequential numbering (#1, #2, …)
- Ticket lifecycle boxes with status transitions
- Bot summary at ticket status milestones (Ask / Autopilot / Human / Waiting / Ticket / Case)
- Case B: Autopilot pause gate + `[HUMAN]` badges
- Before/after time-delta summary
- **Memory & Context dump** at the end:
  - Working Context (all beats)
  - Ticket Timeline
  - Task Results
  - Bot Summary
  - Mail Stream

## Email templates

All templates live under `data/emails/`:

| File | ID | Dir | Case |
|---|---|---|---|
| `A1_inbound_mike.txt` | A1 | IN | Case A |
| `A2_outbound_reply.txt` | A2 | OUT | Case A |
| `B1_inbound_emily.txt` | B1 | IN | Case B |
| `B2_outbound_docs_needed.txt` | B2 | OUT | Case B |
| `B2r_outbound_reminder.txt` | B2r | OUT | Case B |
| `B2in_inbound_upload_blurry.txt` | B2in | IN | Case B |
| `B3_outbound_clearer_doc.txt` | B3 | OUT | Case B |
| `B3in_inbound_resubmit_clear.txt` | B3in | IN | Case B |
| `B4_outbound_under_review.txt` | B4 | OUT | Case B |
| `B5_outbound_specialist.txt` | B5 | OUT | Case B |

Catalog: `data/mails.json`  
Fixtures: `data/case_a.json`, `data/case_b.json`

## Layout

```
cli-demo/
├── run.py          # entry + menus
├── engine.py       # playback engine + RunMemory
├── render.py       # terminal cards / colors / spinner / memory dump
├── README.md
└── data/
    ├── mails.json
    ├── case_a.json
    ├── case_b.json
    └── emails/     # selectable email templates
```

## Source

Workflow beats, ticket lifecycle, and email copy are aligned with  
`../product-canvas/admin-canvas.html`, `../product-canvas/workflow-extract.md`,  
and `../product-canvas/cli-refactor-plan.md`.
