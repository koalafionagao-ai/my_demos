# Email Autopilot · 产品设计与使用说明

> 一张画布看懂：多 Agent 邮件自动驾驶

---

## 这是什么

```
客户邮件 ──▶ Autopilot ──▶ 自动回复 / 收材料 / 转人工
                 │
            Admin 画布上配置规则 · 试跑路径 · 看效果
```

**吃掉**：耗时 × 可重复 × 低风险  
**挡掉**：涉及资金 / 责任 → 必须 Human

---

## 界面一览

```
┌─────────────┬──────────────┬─────────────────┐
│   Canvas    │    Email     │  Tickets/Tasks  │
│  工作流画布  │   邮件流      │  Log/Configure  │
└─────────────┴──────────────┴─────────────────┘
```

| 栏 | 看什么 |
|---|---|
| **Canvas** | Agent 泳道 · 节点高亮 · LLM(黄) / API(蓝) |
| **Email** | 往来邮件按序出现（#1 #2 …） |
| **右侧** | Ticket 生命周期 · Task 进度 · 运行日志 · 规则配置 |

---

## 怎么用（30 秒）

```
① 顶部选 Case A 或 Case B
② 点 Run Test
③ 看画布节点依次点亮 · 邮件流出 · Ticket 状态变
④ Case B 停在 Human Handover → 点 Take over 继续
⑤ 右侧切 Tickets / Tasks / Log / Configure
```

---

## 两个 Demo Case

### Case A · Mike · 贷款进度

```
邮件问 why + next
        ▼
Orchestrator → Routing → Query → Close
        ▼
Ticket: Open → In Progress → Resolved → Closed
```

- 全自动 · 只读 SoR · 不碰钱  
- 回复「为什么 pending + 下一步」

### Case B · Emily · 争议单据

```
邮件要退款 $4,800
        ▼
Orchestrator → Routing → Doc → Exception → Human → Close
        ▼
Ticket: Open → In Progress → Waiting → … → Resolved → Closed
```

- Doc 自动催材料 / 验单  
- **退款禁止自动** → 人工接管发 specialist 邮件  
- 争议 Case(SoR) 可继续，Ticket 可先关

---

## Ticket 生命周期

```
Open ──▶ In Progress ──▶ Waiting ──▶ Resolved ──▶ Closed
              ▲               │
              └───── 客户回传 / 人工接管 ────┘
```

| 状态 | 含义 |
|---|---|
| Open | 刚建单 |
| In Progress | Autopilot / Human 在处理 |
| Waiting | 等客户材料 / 等人工 |
| Resolved | 本轮咨询已答完 |
| Closed | Ticket 关闭（底层 Case 可未完） |

> **Ticket ≠ Case(SoR)**  
> Ticket = 这次邮件咨询  
> Case = 贷款 / 争议业务本体

---

## Agent 分工

```
        ┌─ Query ──── 状态问答（Case A）
Routing ┤
        ├─ Doc ────── 收材料 · OCR · 校验（Case B）
        └─ Exception ─ 挡资金 · 转 Human（Case B）
```

| Agent | 一句话 |
|---|---|
| Orchestrator | 能不能上 Autopilot |
| Routing | 意图 → 走哪条泳道 |
| Query | 查 SoR · 生成 · 校验 · 发信 |
| Doc | 要材料 · 提醒 · 质检 · OCR |
| Exception | 禁自动退款 · 组包交接 |
| System | 关 Ticket · 写审计 |

---

## Configure 怎么配

点 Canvas 节点 → 右侧 **Configure**

```
Simple（默认）          Advanced
─────────────          ─────────
业务规则               类型分区
关键参数               · LLM / API / 组合
安全治理               · 模型 · Knowledge · API
```

图例：`●` 暖黄 = LLM　`●` 天蓝 = API　红虚线 = Fail 路径

---

## Bot Summary 读法

```
Ask:       客户要什么
Autopilot: 自动完成了什么
Human:     人做了 / 要做的
Waiting:   还卡在哪
Ticket:    本单状态
Case(SoR): 业务本体状态（可独立）
```

---

## 相关链接

| | |
|---|---|
| 中文 README | https://github.com/koalafionagao-ai/my_demos/blob/main/EmailAutopilot/README-zh.md |
| English README | https://github.com/koalafionagao-ai/my_demos/blob/main/EmailAutopilot/README-en.md |
| Admin Canvas | [`admin-canvas.html`](admin-canvas.html) |
| CLI Demo | [`../cli-demo/`](../cli-demo/) |
