# Email Autopilot · CLI Demo

Interactive terminal walkthrough of the Meridian Trust multi-agent email workflow.

Mock data only — **no live APIs, LLM calls, or network lookups**.

> **Repo path:** [`EmailAutopilot/cli-demo`](.)  
> Visual Admin Canvas: see sibling docs under `EmailAutopilot/` (README·中文 / README·EN).

---

## Requirements

- Python **3.9+** (stdlib only — nothing to `pip install`)
- Terminal with UTF-8 (macOS Terminal / iTerm2 / Windows Terminal)

---

## Quick start

Clone the repo, then:

```bash
cd EmailAutopilot/cli-demo
python3 run.py
```

### Flags

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

---

## Menu

1. **Case A** — Mike · Loan Status · `#5108` (Query path)
2. **Case B** — Emily · Dispute Doc · `#4821` (Doc + Exception + Human)
3. **Email templates** — preview files under `data/emails/`

---

## Cases at a glance

### Case A · Mike · `#5108`

```
Orchestrator → Routing → Query → Close
Ticket: Open → In Progress → Resolved → Closed
```

| Task | Agent |
|---|---|
| T1 Lane gate | Orchestrator |
| T2 Understand & route | Routing Agent |
| T3 Answer loan status | Query Agent |
| T4 Close the loop | System |

### Case B · Emily · `#4821`

```
Orchestrator → Routing → Doc → Exception → Human → Close
Ticket: Open → In Progress → Waiting → … → Resolved → Closed
```

| Task | Agent |
|---|---|
| T1 Lane gate | Orchestrator |
| T2 Multi-intent split | Routing Agent |
| T3 Collect & validate | Doc Agent |
| T4 Refund block + Human | Exception Agent |
| T5 Close the loop | System |

At **Human Handover** the CLI pauses — press Enter to simulate specialist takeover.

---

## What you will see

- Step I/O: **Input / Tools / Output**
- Numbered email stream (`#1`, `#2`, …)
- Ticket status boxes with transitions
- Bot summary: Ask / Autopilot / Human / Waiting / Ticket / Case(SoR)
- Case B: `[HUMAN]` badge + Autopilot pause gate
- Before → after time deltas
- **Memory & Context dump** at the end (working context, ticket timeline, task results, mail stream)

---

## Layout

```
cli-demo/
├── run.py
├── engine.py
├── render.py
├── README.md
├── README-github.md   ← this file (GitHub-oriented)
└── data/
    ├── mails.json
    ├── case_a.json
    ├── case_b.json
    └── emails/
```

---

## Note for GitHub visitors

Browsing this folder on GitHub **does not run the demo**.  
To try it: clone → `cd EmailAutopilot/cli-demo` → `python3 run.py`.

For a **zero-install** visual walkthrough, open the Admin Canvas HTML (hosted separately under this project’s README links).
