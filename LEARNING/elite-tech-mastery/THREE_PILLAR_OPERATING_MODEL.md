# Three-Pillar Operating Model

## The Thesis

The edge is not being good at three separate things. The edge is being able to move through all three as one motion:

`Business problem -> System architecture -> AI/agent implementation -> measurable outcome`

The three pillars:

1. Business Solutioning
2. System Design
3. Agentic Engineering

## What Each Pillar Answers

| Pillar | Core Question | Your Existing Tools |
| --- | --- | --- |
| Business Solutioning | What workflow matters, who owns it, what can fail, and what outcome improves? | WISER, MUCTA, 3Rs, PMLS, BTAQ |
| System Design | What technical system makes this reliable, scalable, secure, observable, and cost-controlled? | APIs, data, auth, async flows, cloud, DevOps, SRE, security |
| Agentic Engineering | Where should LLMs, tools, RAG, agents, memory, evals, and human gates fit inside the system? | DBAC, RAT, IFDAEC, DOAR, evals, context, tools, orchestration |

## The One Flow To Practice

Use this every time you design an AI solution.

### 1. Workflow Discovery

Ask WISER:

- Who owns, uses, reviews, and is affected?
- What inputs come in?
- What steps and systems exist today?
- What exceptions break the workflow?
- What result should improve?

Output: one workflow map.

### 2. Automation Boundary

Ask 3Rs and PMLS:

- Which steps are repeatable?
- Which steps are rule-bounded?
- Which steps touch people, money, legal/security, or systems of record?

Output: automate / assist / human-review decision.

### 3. System Architecture

Ask system-design questions:

- What services exist?
- What APIs connect them?
- What data is stored?
- What needs async processing?
- What can fail?
- What needs auth, authorization, encryption, rate limits, and audit logs?
- What latency, cost, availability, and scale targets matter?

Output: architecture diagram plus data/API boundaries.

### 4. Agent Architecture

Ask DBAC:

- Data: what does the agent read?
- Brain: what model, prompt, rules, schemas, examples, and retrieval does it use?
- Action: what can it do?
- Check: how do we validate output before it matters?

Output: agent roles, tool permissions, schemas, evals, review gates.

### 5. Production Controls

Ask DOAR and BTAQ:

- Data controls: access, PII, tenant boundaries, approved sources.
- Output controls: schema, citations, confidence, required fields.
- Action controls: human approvals, idempotency, scoped write permissions.
- Runtime controls: logs, retries, fallback queue, alerts, latency, cost.
- Metrics: business value, task quality, reliability, cost, UX.

Output: runbook, eval plan, observability plan, KPI plan.

## The Interview / Buyer Talk Track

Use this when explaining your method:

> I start with the business workflow before picking tools. I identify who owns it, what input comes in, what steps and systems are involved, where it fails, and what outcome we want to improve. Then I turn that into a system design: services, APIs, data, security, async flows, reliability, and observability. Only after that do I place the AI layer: RAG, agents, tools, schemas, evals, guardrails, and human review gates. The goal is not an AI demo. The goal is a measurable production workflow.

## Weekly Rep Format

Each weekly rep should merge all three pillars:

1. Pick one business workflow.
2. Write the WISER map.
3. Draw the system architecture.
4. Define DBAC agent roles.
5. Add IFDAEC output schema.
6. Add DOAR controls.
7. Add BTAQ metrics.
8. Explain the full design out loud in five minutes.

## Elite Bar

You are operating at the target level when you can receive any messy business workflow and produce, from a blank page:

- Workflow map
- Architecture diagram
- Data model
- API/service boundaries
- Agent design
- Output schema
- Evals and validation plan
- Security and human-review gates
- Observability and cost plan
- Business KPI map
- Plain-English explanation for executives
- Technical explanation for engineers

That is the combined role: AI Solutions Architect / Forward Deployed Engineer / agentic systems operator.
