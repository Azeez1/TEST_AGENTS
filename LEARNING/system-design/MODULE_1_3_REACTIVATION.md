# Modules 1-3 Reactivation Plan

**Created:** 2026-08-22  
**Purpose:** Reactivate the 37 completed System Design concepts without relearning them from scratch.
**Status:** Completed in-session on 2026-08-22. Final mixed rep scored 12/12.

## The Rule

Do not reread the whole curriculum.

Use this loop:

1. Blank-page recall first.
2. Explain from the limit.
3. Name the tradeoff.
4. Apply it to a scenario.
5. Patch only the miss.

If a concept comes back clean, leave it alone. If it is fuzzy, rep it once.

## Pass / Patch / Relearn

For each concept, grade yourself:

- **Pass:** I can explain it plainly, name the limit, name the tradeoff, and use it in a scenario.
- **Patch:** I know it but stumble on the mechanism, tradeoff, or when to use it.
- **Relearn:** I cannot explain it without rereading.

Only `Relearn` gets a full lesson. Most rusty concepts should be `Patch`.

## Day 1: Module 1 - Foundations

Cold prompt:

> A customer-facing app is slowing down and reliability is dropping. From first principles, what physical/system limits could be causing it, and what tradeoffs appear when we fix them?

Concepts to reactivate:

- Machine ceilings: compute, memory, storage, network, failure
- Latency vs throughput
- Back-of-envelope estimation
- Availability and the nines
- SLI / SLO / SLA
- CAP theorem
- PACELC
- Consistency models
- Vertical vs horizontal scaling
- Statelessness
- Redundancy and fault tolerance

Pass condition:

- You can explain why each concept exists without using "best practice" language.

## Day 2: Module 2 - Software Architecture

Cold prompt:

> Design the service communication layer for a growing SaaS app. When do you use direct APIs, queues, pub/sub, caching, retries, rate limits, or event sourcing?

Concepts to reactivate:

- Monolith vs microservices vs modular monolith
- REST
- gRPC
- GraphQL
- Sync vs async communication
- Message queues
- Event-driven systems
- Pub/sub
- Coupling and cohesion
- Cache-aside
- Write-through
- Write-back
- Cache invalidation
- Idempotency
- Retries
- Timeouts
- Backoff
- Circuit breakers
- Rate limiting
- CQRS
- Event sourcing

Pass condition:

- You can choose between patterns based on limit + tradeoff, not memorized definitions.

## Day 3: Module 3 - Cloud Architecture

Cold prompt:

> Design the baseline cloud architecture for a customer-facing AI workflow. Include public/private networking, app execution, storage, traffic routing, scaling, and cost controls.

Concepts to reactivate:

- VMs vs containers vs serverless
- Containers and Kubernetes/orchestration
- Load balancing: L4 vs L7
- Regions and Availability Zones
- Multi-region failover and disaster recovery
- RPO and RTO
- CDN and edge
- DNS
- VPC
- Public/private subnets
- Block storage
- Object storage
- File storage
- API gateway
- Cost optimization / FinOps

Pass condition:

- You can draw a baseline cloud diagram and justify each component from reliability, latency, security, scale, or cost.

## Day 4: Integrated Scenario

Scenario:

> FleetCRM goes from 50 users to 50,000 users. Pages are timing out. Some users report stale data. Support says failures spike during batch imports. Leadership wants it fixed without overbuilding.

Answer format:

1. Clarify requirements and symptoms.
2. Estimate rough traffic and data pressure.
3. Identify likely bottlenecks.
4. Propose minimum correct fixes.
5. Name tradeoffs.
6. Explain what you would monitor.

Pass condition:

- You diagnose before prescribing.
- You do not jump straight to read replicas, sharding, Kubernetes, or microservices without evidence.

## Day 5: Three-Pillar Merge

Use one real workflow:

- PE diagnosis
- LinkedIn review
- Lead-gen

Produce:

- WISER map
- System architecture sketch
- DBAC agent design
- One output schema
- One failure-mode table
- One metric

Pass condition:

- Business, system design, and agentic engineering appear in one artifact.

## 10-Minute Daily Reactivation Loop

Use this when short on time:

1. Pick one concept.
2. Ask: what limit does it solve?
3. Ask: what does it cost?
4. Explain it to a smart 12-year-old.
5. Apply it to one real workflow.

## Completion Bar

Modules 1-3 are reactivated when:

- 80 percent of concepts are `Pass`.
- No concept is `Relearn`.
- The integrated FleetCRM scenario is coherent.
- One three-pillar artifact exists.

Then move to Module 4: DevOps, Automation & SRE.

## Completion Checkpoint - 2026-08-22

Result: **Pass**

What was tested:

- Module 1: machine limits, latency/throughput, availability, SLI/SLO/SLA, CAP/PACELC, consistency, scaling, statelessness, redundancy
- Module 2: modular monolith, REST/gRPC/GraphQL, sync/async, queues, pub/sub, coupling/cohesion, caching, idempotency, retries/timeouts/backoff, circuit breakers, rate limiting, CQRS/event sourcing
- Module 3: containers, Kubernetes, load balancing, regions/AZs, DR, RPO/RTO, CDN, DNS, VPC/subnets, storage types, API gateway, FinOps

Patches to remember:

- Latency = one user/job feels slow; throughput = system volume per time.
- GraphQL fits frontend screens that need a custom data shape across resources.
- Object storage stores files; CDN delivers cached files closer to users.
- SLI is the measurement; SLO is the target; SLA is the external agreement.

Resume point:

- Start Module 4 with CI/CD from first principles.
