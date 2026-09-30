# AI Solution Frameworks

Reusable framework stack for live AI solutioning, agentic workflow design,
consulting delivery conversations, and prototype builds.

Use this order when thinking out loud:

1. Workflow: WISER
2. Tasks: 3Rs
3. Agent design: DBAC plus RAT
4. Output schema: IFDAEC
5. Controls and guardrails: DOAR
6. Metrics: BTAQ
7. Productionization: repeatable, safe, reliable, observable, integrated, measurable

## 1. Workflow: WISER

Use WISER to understand the business workflow before designing the AI system.

| Letter | Meaning | What To Say |
| --- | --- | --- |
| W | Who | Who owns the workflow, uses the tool, reviews output, and is affected by mistakes? |
| I | Input | What information comes in? Emails, tickets, invoices, transcripts, decks, notes, forms, files. |
| S | Steps / Systems | What happens today, step by step, and what systems are touched? CRM, ERP, ticketing, tracker, email, docs. |
| E | Exceptions / Edge Cases | Where does the workflow fail or need human judgment? |
| R | Result | What business outcome are we trying to improve? Time saved, cost saved, quality, throughput, adoption. |

Default workflow wording:

> First I want to understand the current workflow before picking the AI solution. I would identify who owns it, what input comes in, what steps and systems are involved, where the edge cases are, and what result the business actually wants to measure.

## 2. Edge Cases: MUCTA

Use MUCTA inside the WISER edge-case step.

| Letter | Meaning | Default Examples |
| --- | --- | --- |
| M | Missing info | Missing required fields, missing attachment, incomplete transcript, blank document section. |
| U | Unclear info | Ambiguous request, unclear severity, unclear next step, unclear owner, low confidence. |
| C | Conflicting info | Duplicate records, mismatched vendor/PO, conflicting transcripts, stale policy vs current policy. |
| T | Tool failure | API failure, auth failure, timeout, failed CRM/ERP update, vector DB unavailable. |
| A | AI risk | Hallucination, ungrounded answer, false positive, false negative, bad citation, unsupported claim. |

Default wording:

> The main failure points I would watch for are missing information, unclear information, conflicting data, tool failures, and AI-specific risks like hallucination or ungrounded output.

## 3. Tasks: 3Rs

Use 3Rs to decide what the AI should do and what should stay controlled.

| R | Meaning | What To Look For |
| --- | --- | --- |
| Repeatable | Steps that happen over and over | Read, extract, classify, summarize, match, draft, route, update. |
| Rule-bounded | Steps with rules/templates/rubrics | Schemas, approved values, scoring rules, playbooks, SOPs, policies. |
| Risk gates | Steps that require control | Human approval before people-facing, money, legal/security, or system-of-record action. |

Default wording:

> I would automate the repeatable and rule-bounded parts first, then put gates around anything high-risk or ambiguous.

## 4. Risk Gates: PMLS

Use PMLS to know where a human review gate is needed.

| Letter | Meaning | Default Gates |
| --- | --- | --- |
| P | People / customer-facing | Customer email, employee recommendation, sales coaching, executive/partner brief. |
| M | Money | Discounts, payments, invoices, refunds, pricing, compensation, revenue-impacting actions. |
| L | Legal / compliance / security | Contract terms, PHI/PII, HR sensitivity, regulated data, security exceptions. |
| S | System of record | CRM, ERP, HRIS, NetSuite, Salesforce, HubSpot, Zendesk, portfolio tracker. |

Default wording:

> Anything touching people, money, legal/compliance/security, or a system of record should have a human gate unless the rules are extremely clear and the risk is low.

## 5. Agent Design: DBAC

Use DBAC to explain each agent clearly.

| Letter | Meaning | Default Examples |
| --- | --- | --- |
| D | Data | What the agent reads: source docs, transcript, ticket, invoice, CRM record, policy docs. |
| B | Brain | LLM plus rules, templates, rubrics, schemas, SOPs, examples. |
| A | Action | What the agent does: retrieve, extract, classify, score, draft, verify, route, update. |
| C | Check | Validation: required fields, schema, citations, confidence, completeness, tool result, review gate. |

Default agent set for prototypes:

| Agent | Purpose |
| --- | --- |
| Orchestrator | Owns the end-to-end flow and state. |
| Retriever / Context Agent | Pulls the right policies, docs, examples, and source context. |
| Extraction / Reasoning Agent | Extracts facts and makes scenario-specific judgments. |
| Verification Agent | Checks grounding, citations, completeness, schema, and confidence. |
| Human Review / Guardrail Gate | Decides what cannot be auto-approved or auto-sent. |
| Integration / Update Agent | Writes to the mock or real system of record. |

Default wording:

> I would make the orchestrator own the flow, then break the work into specialized agents: context retrieval, extraction/reasoning, verification, human review gate, and system update.

## 6. Agent Behavior: RAT

Use RAT to explain how agents operate.

| Letter | Meaning | What It Means |
| --- | --- | --- |
| R | Reason | Interpret the task using context, rules, and schema. |
| A | Act | Call tools, draft output, update records, or route to review. |
| T | Track | Log decisions, citations, tool calls, errors, cost, latency, and review outcomes. |

Default wording:

> The agent should reason from the source material, act only within its scoped permissions, and track what happened so we can audit and improve it.

## 7. Output Schema: IFDAEC

Use IFDAEC to derive output fields from first principles.

| Letter | Meaning | Field Defaults |
| --- | --- | --- |
| I | Identity | record_id, customer_id, company_id, invoice_id, ticket_id, transcript_id, user_id, owner. |
| F | Facts | extracted fields, summary, issue, risks, objections, invoice amount, vendor, themes, notes. |
| D | Decisions | risk_level, severity, priority, category, match_status, score, qualified_status, route_decision. |
| A | Actions | draft_response, update_crm, update_tracker, route_to_team, flag_exception, next_step. |
| E | Evidence | source_id, source_quote, citation, timestamp, page/section, attachment_reference. |
| C | Controls | confidence_score, needs_human_review, reason_for_review, missing_fields, blocked_actions. |

Default wording:

> For the output, I want structured fields: identity so we know the record, facts from the source, decisions the AI made, actions it recommends or takes, evidence showing where it came from, and controls for review.

## 8. Controls / Guardrails: DOAR

Use DOAR to cover safety and production controls.

| Letter | Meaning | Default Controls |
| --- | --- | --- |
| D | Data controls | RBAC, tenant isolation, approved sources, PII masking, sensitivity labels, scoped folder/email access. |
| O | Output controls | Pydantic/JSON schema, required fields, approved values, confidence thresholds, citation required. |
| A | Action controls | Human approval, scoped write permissions, idempotency, audit logs, no auto-send/no auto-approve. |
| R | Runtime controls | JSONL logs, retries, fallback queue, alerts, timeout handling, error monitoring, LangSmith traces. |

Default wording:

> I think about controls in four layers: what data the AI can access, what shape the output must follow, what actions it is allowed to take, and what we monitor at runtime.

## 9. Metrics: BTAQ

Use BTAQ when asked how to measure success.

| Bucket | Default Metrics |
| --- | --- |
| Business | Adoption rate, ROI, time saved, cost saved, throughput, cycle time. |
| Task quality | Accuracy, completeness, groundedness, citation accuracy, hallucination rate, precision, draft quality. |
| Agent reliability | Workflow success rate, tool success/failure rate, retry rate, error rate, exception rate. |
| Quality / Cost / UX | Cost per run, token usage, latency, override rate, edit rate, user satisfaction. |

Default wording:

> I would measure this in four buckets: business value, task quality, agent reliability, and cost/user experience.

Quick definitions:

| Metric | Simple Meaning |
| --- | --- |
| Cycle time | Time from workflow start to workflow finish. |
| Throughput | Number of items processed in a period. |
| Override rate | How often a human changes or rejects the AI decision. |
| Edit rate | How much humans edit drafts before approving. |
| Retry rate | How often a tool call or workflow step has to retry. |
| Exception rate | How often the workflow cannot complete normally and needs fallback/manual review. |
| Groundedness | Whether the answer is supported by source material. |
| Citation accuracy | Whether cited sources actually support the claim. |
| Hallucination rate | Share of claims that are unsupported or contradicted by source truth. |

## 10. Productionization

Use this when asked, "How would you productionize this?"

| Principle | What To Mention |
| --- | --- |
| Repeatable | Reusable schemas, prompts, skills/playbooks, templates, agent modules. |
| Safe | RBAC, scoped data access, human review gates, PII masking, approved actions only. |
| Reliable | Validation, tests, idempotency, retries, fallback queue, deterministic checks. |
| Observable | Logs, audit logs, alerts, traces, latency, error rate, token/cost tracking. |
| Integrated | Real APIs, CRM/ERP/ticketing/file/email systems, system-of-record writes. |
| Measurable / improving | KPIs, evals, override reasons, edit reasons, feedback loop, regression tests. |

Default wording:

> To productionize it, I would make it repeatable, safe, reliable, observable, integrated, and measurable. That means reusable schemas and prompts, scoped permissions and review gates, validation and retries, logs and traces, real system integrations, and a feedback loop from metrics and human overrides.

## 11. Live Build Prompt Skeleton

Use this when splitting work across AI coding sessions.

```text
Case:
We are building a local prototype for [workflow/use case].
Current process: [who] receives [input], does [steps], handles [edge cases].
Goal: reduce [time/cost/error], improve [quality/throughput/adoption].

Plan:
Before writing files, propose:
- output schema using Identity, Facts, Decisions, Actions, Evidence, Controls
- agent roles and orchestration
- RAG/docs/vector DB plan
- memory/logging plan
- guardrails/human review gates
- metrics

Build:
- create sample inputs
- create knowledge base docs for RAG
- implement backend API
- implement frontend reviewer UI
- implement structured JSON outputs
- write runtime logs, audit logs, and run DB records
- include idempotency and human review flags

Connect:
- mock integration target: [CRM/ERP/ticketing/tracker]
- update mock system only when safe
- store runs and updates

Verify:
- backend health
- end-to-end API call
- frontend works
- SQLite tables/fields/data
- vector DB chunks and relevant retrieval
- source IDs/citations
- logs/traces/evals

Reuse:
- README
- runbook
- reusable prompts/skills/playbook
- optional subagent recommendations

Keep it local, simple, and runnable.
```

## 12. Solutioning Talk Track

Use this if you need a short, natural way to open.

> I am going to start with the workflow before jumping into tools. I want to understand who uses it, what comes in, what steps happen, where it can fail, and what result we want. Then I will turn that into tasks, agents, outputs, controls, metrics, and a local prototype we can verify end to end.

Use this if asked why the framework matters.

> The framework keeps me from just building a demo. It makes sure the AI system maps to the business workflow, has clear output fields, has human controls where risk is high, and has metrics so we know whether it is working.
