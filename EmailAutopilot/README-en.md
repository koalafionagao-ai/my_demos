# Email Autopilot · Product Design & How to Use

> One canvas: multi-agent email automation you can see

---

## What it is

```
Customer email ──▶ Autopilot ──▶ Reply / Collect docs / Hand to human
                       │
                  Admin configures rules · runs paths · sees outcomes
```

**Automate**: time-consuming × repeatable × low-risk  
**Block**: money / liability → must go Human

---

## Layout at a glance

```
┌─────────────┬──────────────┬─────────────────┐
│   Canvas    │    Email     │  Tickets/Tasks  │
│  workflow   │   thread     │  Log/Configure  │
└─────────────┴──────────────┴─────────────────┘
```

| Column | What you see |
|---|---|
| **Canvas** | Agent lanes · node glow · LLM (yellow) / API (blue) |
| **Email** | Thread in stream order (#1 #2 …) |
| **Right** | Ticket lifecycle · Task progress · Run log · Rules |

---

## How to use (30 seconds)

```
① Pick Case A or Case B in the top bar
② Click Run Test
③ Watch nodes light up · emails appear · ticket status change
④ Case B pauses at Human Handover → click Take over
⑤ Switch right tabs: Tickets / Tasks / Log / Configure
```

---

## Two demo cases

### Case A · Mike · Loan status

```
Ask: why pending + next step
        ▼
Orchestrator → Routing → Query → Close
        ▼
Ticket: Open → In Progress → Resolved → Closed
```

- Fully automated · read-only SoR · no money movement  
- Answers “why pending” and “what’s next”

### Case B · Emily · Dispute docs

```
Ask: refund $4,800
        ▼
Orchestrator → Routing → Doc → Exception → Human → Close
        ▼
Ticket: Open → In Progress → Waiting → … → Resolved → Closed
```

- Doc Autopilot collects / validates receipts  
- **No auto-refund** → human takeover → specialist email  
- Dispute Case (SoR) may continue after Ticket closes

---

## Ticket lifecycle

```
Open ──▶ In Progress ──▶ Waiting ──▶ Resolved ──▶ Closed
              ▲               │
              └── customer upload / human takeover ──┘
```

| State | Meaning |
|---|---|
| Open | Just created |
| In Progress | Autopilot or Human actively working |
| Waiting | Blocked on customer or specialist |
| Resolved | This consultation is answered |
| Closed | Ticket closed (underlying Case may continue) |

> **Ticket ≠ Case (SoR)**  
> Ticket = this email consultation  
> Case = the loan / dispute business object

---

## Agent roles

```
        ┌─ Query ──── status Q&A (Case A)
Routing ┤
        ├─ Doc ────── collect · OCR · validate (Case B)
        └─ Exception ─ block money · hand to Human (Case B)
```

| Agent | One line |
|---|---|
| Orchestrator | Is Autopilot allowed? |
| Routing | Intent → which lane |
| Query | SoR lookup · draft · verify · send |
| Doc | Request docs · remind · quality · OCR |
| Exception | Block auto refund · build handover |
| System | Close ticket · write audit |

---

## Configure

Click a canvas node → right rail **Configure**

```
Simple (default)         Advanced
────────────────         ────────
Business rules           Typed sections
Key parameters           · LLM / API / Composite
Safety / governance      · Model · Knowledge · API
```

Legend: `●` warm yellow = LLM　`●` sky blue = API　red dashed = fail path

---

## How to read Bot Summary

```
Ask:       What the customer wants
Autopilot: What automation completed
Human:     What a person did / must do
Waiting:   What’s still blocked
Ticket:    Status of this consultation
Case(SoR): Status of the business object (may differ)
```

---

## Links

| | |
|---|---|
| 中文 README | https://github.com/koalafionagao-ai/my_demos/blob/main/EmailAutopilot/README-zh.md |
| English README | https://github.com/koalafionagao-ai/my_demos/blob/main/EmailAutopilot/README-en.md |
| Admin Canvas | https://koalafionagao-ai.github.io/my_demos/EmailAutopilot/ |
| CLI Demo | https://github.com/koalafionagao-ai/my_demos/tree/main/EmailAutopilot/cli-demo |
