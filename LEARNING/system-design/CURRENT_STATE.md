# System Design Current State

## September 24 update

The September 3 snapshot below is historical. The [L2 system-design task](codex://threads/01a02648-7248-73a0-af3c-b5838f3c331c) shows many subsequent hands-on reps, including live auctions, payment webhooks, job search, uploads, notifications, collaborative editing, feeds, and real-time data. EZ has repeatedly chosen and defended architecture lanes rather than only reviewed terminology. The notes in `NOTES.md` record detailed corrections through September 13.

- **Wiring strength:** Increasing fluency with the durable-write → event → side-effects pattern and with separating read, async, live, file, and reporting paths. Several reps were correct at the intended abstraction level; do not regrade them against unintroduced implementation details.
- **Current DRA work:** After the W-heavy phase, practice shifted back to defining requirements and identifying actors, actions, and assets. Non-functional requirements and the distinction between business assets and components still need short, targeted reps.
- **Next system-design proof:** One unfamiliar end-to-end design done independently, including a small set of failure-specific stress tests and a concrete artifact such as a data model, threat model, runbook, or eval plan. The prior 72/82 count measures concept coverage, not this proof.
- **Cross-track calibration:** The Python interview gap is unaided syntax fluency. Do not infer overall engineering seniority or client-discovery ability from that single gap; see [the cross-track map](../CONNECTION-MAP.md).

---

## September 3 snapshot

**Checked:** 2026-09-03  
**Context:** Calibrated with the Oracle agent plus local `REP_PLAN.md`, `NOTES.md`, and the elite-tech mastery plan. Modules 1-3 were reactivated in-session on 2026-08-22. Module 4 was completed at the concept-checklist level on 2026-08-23. Modules 5 and 8 were completed at the concept-checklist level on 2026-08-24. On 2026-09-01, EZ shifted into W-only architecture drawing reps and practiced appointment booking, food delivery, chat, and document processing patterns. Second-brain check confirmed the vault already contains the system-design source spine.

## Where EZ Is Right Now

You are not starting from scratch.

Current checklist state:

- Completed: 72 concepts
- Primed: 0 concepts
- Remaining: 10 concepts
- Total tracked: 82 concepts

Modules marked complete:

- Module 1: Architectural Foundations
- Module 2: Software Architecture & Design Principles
- Module 3: Cloud Architecture & Infrastructure
- Module 4: DevOps, Automation & SRE
- Module 5: Security Architecture & Compliance
- Module 8: Data Architecture & Data Engineering

Current next module:

- Module 6: AI/ML System Design & MLOps

Current active practice mode:

- W-first reps. Stress testing is paused until EZ can split system lanes and wire them cold. Current focus: identify the product's core lanes, choose the right path for each lane, and explain why each component exists. S will come back after W feels automatic.

Primary W reference:

- `reference/w-primitives-toolbox.html` stores the first-principles wiring primitives, trigger rules, product patterns, and default W template.

Latest W checkpoint:

- Appointment booking: passed core search/read, booking/write, async notification, reporting pattern. Patch: scarce resources need primary DB transactions/constraints before async side effects.
- Food delivery: passed core read/write/async/reporting pattern. Patch: mobile apps are clients before the cloud edge; live tracking needs a separate high-frequency real-time path.
- Chat: identified primary DB, search/read, replica/cache, and audit/report paths. Patch: durable message history and live delivery are separate truths.
- Document processing: correctly used object storage, DB metadata, search index, and report reads. Patch: OCR/AI/search indexing should be triggered after file storage succeeds.

Artifact backlog for proof reps, not blocking concept completion:

- Module 4: DevOps, Automation & SRE scenario rep + mini runbook
- Module 5: security threat model / control matrix for a concrete system
- Module 8: data model / scaling plan / pipeline sketch for a concrete system

Latest checkpoint:

- Modules 1-3 reactivation: **Passed**
- Final mixed rep: **12/12**
- Scenario used: FleetCRM SaaS architecture
- Patched concepts: latency vs throughput, GraphQL vs REST for frontend data shape, CDN vs object storage, and SLI/SLO phrasing
- Teaching preference captured: grade conceptual correctness first; only patch wording when wording changes the meaning.

Module 4 checkpoint:

- Date: Sunday, August 23, 2026
- Status: **Complete at concept-checklist level**
- Mixed rep: **12/12**
- Core mental model: Module 4 = production operations; how systems survive real users after launch.
- Covered: CI/CD, deployment strategies, IaC/Terraform, SLI/SLO/SLA, error budgets, metrics, logging, tracing, incident response, chaos testing, autoscaling.
- Artifact proof still recommended: scenario rep, mini runbook, failure-mode table.
- Under-practiced supporting artifact details: runbooks, alerting, rollback strategy, health checks, smoke tests, dashboards, postmortem structure, ownership/on-call escalation, config/secrets drift, release gates.

Module 5 checkpoint:

- Date: Monday, August 24, 2026
- Status: **Complete at concept-checklist level**
- Mixed rep: **10/10**
- Core mental model: Module 5 = protecting systems, data, users, and proving the controls exist.
- Covered: authentication, authorization, encryption at rest/in transit, secrets management, TLS/certificates, SOC 2/NIST/FedRAMP compliance framing, data classification, DLP, zero trust, threat modeling, OWASP/common vulnerabilities, network security, firewall vs WAF.
- Patched concepts: authentication vs authorization, authentication failure vs broken access control, OWASP/BOLA/IDOR, threat modeling attack path, WAF vs firewall, public vs private exposure.
- Artifact proof still recommended: concrete threat model, security control matrix, and secure architecture walkthrough for a real/synthetic case.

Module 8 checkpoint:

- Date: Monday, August 24, 2026
- Status: **Complete at concept-checklist level**
- Mixed rep: **16/16 concept pass** with terminology patches
- Core mental model: Module 8 = how systems store, query, scale, move, analyze, and keep data correct.
- Covered: OLTP vs OLAP, SQL vs NoSQL, database types, indexing, sharding/partitioning, replication, warehouse/lake/lakehouse, batch vs stream, CDC, data modeling/normalization, ACID vs BASE, consensus, storage engines.
- Patched concepts: partitioning vs sharding, replication lag/stale reads wording, split-brain as the problem consensus prevents.
- Artifact proof still recommended: data model, indexing/sharding rationale, replication/read-model plan, and analytics pipeline sketch for a concrete system.

## What This Means

You have the base layer reactivated:

- Machine limits
- Latency / throughput
- Availability
- CAP / PACELC
- Consistency
- Scaling
- APIs
- Sync vs async
- Queues / pub-sub
- Caching
- Idempotency
- Retries / timeouts / backoff
- Circuit breakers
- Rate limiting
- CQRS / event sourcing
- Containers / serverless
- Load balancing
- Regions / AZs
- CDN / DNS
- VPC / networking
- Storage types
- API gateway
- Cost optimization

The next problem is not vocabulary. The next problem is scenario fluency and production artifacts.

Second-brain source spine confirmed:

- `MEMORY/VAULT/wiki/articles/Architectural Foundations.md`
- `MEMORY/VAULT/wiki/articles/Software Architecture & Design Principles.md`
- `MEMORY/VAULT/wiki/articles/Cloud Architecture & Infrastructure.md`
- `MEMORY/VAULT/wiki/articles/DevOps, Automation & SRE.md`
- `MEMORY/VAULT/wiki/articles/Security Architecture & Compliance.md`
- `MEMORY/VAULT/wiki/articles/AI-ML System Design.md`
- `MEMORY/VAULT/wiki/articles/AI Agent Architecture.md`
- `MEMORY/VAULT/wiki/articles/Data Architecture.md`
- `MEMORY/VAULT/wiki/articles/Capstone Synthesis.md`
- `MEMORY/VAULT/wiki/articles/EZ 8x14x20 System Resilience Framework.md`

## Main Gaps

- DevOps/SRE: concept checklist complete; next gap is production artifact fluency through a runbook, alert/rollback plan, and failure-mode table.
- Security architecture: concept checklist complete; next gap is artifact fluency through a threat model, control matrix, and secure architecture walkthrough.
- Data architecture: concept checklist complete; next gap is artifact fluency through a data model, indexing/sharding rationale, replication plan, and pipeline sketch.
- AI/ML systems: current next block; model serving, evals, drift, A/B testing, training/data pipelines.
- Stress testing: next skill layer after W; identify what breaks under load, failure, bad data, retries, region loss, security abuse, and cost pressure.
- Capstone mocks: URL shortener, news feed, chat, rate limiter, full interview flow.
- Proof discipline: attaching each concept to a real artifact, not just a checked box.

## The Learning Rule

For every system-design concept, ask:

> What limit does this solve, what tradeoff does it create, and where does it fit in the whole system?

Do not memorize components. Derive them from limits.

## Next 7 Days

Use Saturday, August 22 and Sunday, August 23 as setup days. The formal sprint starts Monday, August 24, 2026.

Modules 1-3 were reactivated on Saturday, August 22, 2026. Module 4 was completed at concept-checklist level on Sunday, August 23, 2026. Modules 5 and 8 were completed at concept-checklist level on Monday, August 24, 2026. Next priming block is Module 6 AI/ML System Design & MLOps.

### Saturday, Aug 22

Pick one workflow as the Week 1 artifact.

Best choices:

- PE diagnosis pipeline
- LinkedIn review workflow
- Lead-gen workflow

Output:

- One sentence: "This week I am designing the reliability/runbook layer for ___"

### Sunday, Aug 23

No new content.

Do a 10-minute cold recall of Modules 1-3:

- Single-machine limits
- The components that solve them
- The tradeoffs each component creates

### Monday, Aug 24

Rep CI/CD from first principles.

Plain-English frame:

- CI/CD is the inspector plus the delivery belt.
- CI checks whether the change is safe.
- CD moves the safe change toward users.

Output:

- One Feynman explanation of CI/CD in your own words.

### Tuesday, Aug 25

Connect CI/CD to agentic engineering.

Ask:

- What is the equivalent of CI/CD for an agent workflow?
- What validator runs before an agent output is trusted?
- What retry or escalation rule exists when validation fails?

Output:

- One paragraph connecting CI/CD gates to agent validation gates.

### Wednesday, Aug 26

Draft the artifact.

Output:

- CI/CD + incident-response mini runbook for the chosen workflow.

### Thursday, Aug 27

Run failure-mode drill.

Ask:

- What breaks?
- How would I know?
- What log, metric, trace, or alert catches it?
- What is the fallback?

Output:

- Failure-mode table.

### Friday, Aug 28

Explain it two ways:

- Technical interviewer version
- Buyer / executive version

Target:

- Under 5 minutes each.

## Done For Week 1 When

- One DevOps/SRE concept is repped cold.
- One mini runbook exists.
- One failure-mode table exists.
- One technical explanation and one buyer explanation are practiced out loud.

This artifact work strengthens proof/mastery, but it does not block Module 6 priming.
