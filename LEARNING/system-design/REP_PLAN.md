# System Design — Rep Plan (Anti-Drift Map + Master Checklist)

**Started:** 2026-07-05 · **Mode:** Encoding reps → scenario reps · **Rolls up to:** `../Q3-2026-FOCUS-MAP.md` · **Compass:** `../CONNECTION-MAP.md` · **Method:** `../STUDY-PROTOCOL.md`
**Source spine (in vault):** Elite Architecture Accelerator 9-module course + DDIA + System Design Primer.

## The rep bar (First Principles)
For every concept: name the **fundamental limit** it solves and the **cost/tradeoff** it carries. Derive, don't recite.

## Calibration (2026-07-05)
🟢 Edge: M1, M5, M8 (Data — DDIA-backed) · 🟡 Fuzzy: M2, M3, M4 (tradeoff layer) · 🔴 Thin source: M3 Cloud, M4 DevOps (summary-only — ingest Google SRE Book + AWS Well-Architected when you march there).

## The Arc
Warm-up (M1 + edges) → Build the ladder (M2, M3, M4) → Data + AI (M6, M8) → Integrate (M9 mocks). Interleave with AE reps.

---

## MASTER CHECKLIST — check when repped clean, notes-closed
> **This is a LIVING list.** It's ~95% of the canonical map, not a sealed contract. When a reading or a scenario surfaces a concept that's not here, ADD it. The list can't trap you — it grows.

### Module 1 · Architectural Foundations
- [x] 1. The 5 machine ceilings (compute/memory/storage/network/failure) ✅ *Rep #2, 2026-07-05*
- [x] 2. Latency vs throughput ✅ *Rep #3, 2026-07-05*
- [x] 3. Back-of-envelope estimation (QPS, storage, bandwidth) ✅ *Rep #4, 2026-07-05 — knew the method, fixed unit (÷86,400 sec not 1,440 min); memorize 86,400≈100k*
- [x] 4. Availability & the nines (SLA/SLO/SLI) ✅ *Rep #5, 2026-07-05 — had uptime + acronyms; sharpened the nines ladder + SLI(measure)/SLO(aim)/SLA(promise, looser)*
- [x] 5. CAP theorem ✅ *Rep #6, 2026-07-05 — had C/A/P + tradeoff; sharpened: P not optional, real choice = C vs A DURING a partition (CP=bank, AP=feed); no partition → both*
- [x] 6. PACELC ✅ *Rep #7, 2026-07-05 — recalled both halves; locked "if P→A/C, Else→L/C"; insight: consistency always costs (availability in partition, latency otherwise)*
- [x] 7. Consistency models (strong / eventual / causal) ✅ *Rep #8, 2026-07-05 — strong + eventual solid (got async-replication intuition); sharpened causal = cause-before-effect ordering (comment-thread)*
- [x] 8. Vertical vs horizontal scaling ✅ *Rep #9, 2026-07-05 — nailed w/ EC2 example (bigger box vs more boxes); tradeoff: vertical=simple/ceiling+SPOF, horizontal=no ceiling+fault-tolerant but distributed complexity*
- [x] 9. Statelessness ✅ *Rep #10, 2026-07-05 — strong reasoning (servers interchangeable, no sticky sessions); added state-lives-outside (Redis/DB or JWT in the request)*
- [x] 10. Redundancy / fault tolerance ✅ *Rep #11, 2026-07-05 — redundancy=the duplicates (cause), fault tolerance=system survives failure (effect); redundancy+failover=fault tolerance (spare-tire)* — **🎉 MODULE 1 COMPLETE**

### Module 2 · Software Architecture & Design Principles
- [x] 11. Monolith vs microservices vs modular monolith ✅ *Rep #12, 2026-07-06 — got all 3; killed monolith=spaghetti myth (axis = one deployable vs many, not clean vs messy); "costly"=distributed-systems tax; rule: don't start w/ microservices, extract when a part needs independence*
- [x] 12. API: REST ✅ *Rep #13, 2026-07-06 — REST=simple universal default (HTTP verbs+JSON), over/under-fetch weakness*
- [x] 13. API: gRPC ✅ *Rep #13 — binary/Protobuf over HTTP/2, fast, internal service-to-service (nailed the use case)*
- [x] 14. API: GraphQL ✅ *Rep #13 — client asks exact fields, one endpoint, mobile/varied clients (nailed use case). One-liner: REST=simple default, gRPC=internal speed, GraphQL=client flexibility*
- [x] 15. Sync vs async communication ✅ *Rep #14, 2026-07-06 — nailed (phone=sync/blocking, text=async/queued); why async = don't halt everything for one service. Sharpened: async = DECOUPLING (resilience + load-smoothing + responsiveness), cost = eventual consistency (linked to M1 himself)*
- [x] 16. Message queues / event-driven ✅ *Rep #15, 2026-07-06 — queue = one message → ONE consumer (ticket line, work distribution); event-driven = services emit/react to events instead of direct calls*
- [x] 17. Pub/sub ✅ *Rep #15 — described publish+subscribe correctly; sharpened vs queue: pub/sub = one event → MANY subscribers each get a copy (newsletter/fan-out). Order-placed example: queue=1 payment worker, pub/sub=email+inventory+analytics all get it*
- [x] 18. Coupling & cohesion ✅ *Rep #16, 2026-07-06 — coupling=dependence BETWEEN modules (want low) nailed; fixed cohesion = focus WITHIN one module on one job (want high), not "working together". Low coupling + high cohesion = clean module/service boundary*
- [x] 19. Caching strategies (cache-aside, write-through, write-back) ✅ *Rep #17, 2026-07-06 — NEW material, taught: cache=fast close copy (M1 latency fix), sits many layers (Redis in front of DB). cache-aside=load when asked, write-through=both at once, write-back=cache now/DB later. Feynman-closed cache-aside flow (cache→db→cache)*
- [x] 20. Cache invalidation ✅ *Rep #17 — taught: stale-data problem (DB updated, cache old); the famous joke; fixes = TTL / invalidate-on-write / write-through*
- [x] 21. Idempotency ✅ *Rep #18, 2026-07-06 — got the WHY (no double-charge); sharpened WHAT = same result done once or N times (set-balance vs add contrast); HOW = idempotency key (Stripe). Needed b/c unreliable networks → retries (M1)*
- [x] 22. Retries / timeouts / backoff ✅ *Rep #19, 2026-07-06 — retry (count) + backoff (spacing) nailed; FIXED timeout = TIME limit on ONE attempt (not a count). Added exponential backoff + jitter, and why: don't hammer a struggling service (retry storm)*
- [x] 23. Circuit breakers ✅ *Rep #20, 2026-07-06 — got core (shuts it off); added WHY (prevent cascading failure, fail fast, let it recover) + 3 states (closed/open/half-open) + fallback = graceful degradation (M1)*
- [x] 24. Rate limiting ✅ *Rep #21, 2026-07-06 — got it (stop clients flooding us); added per-client/window cap → 429, token-bucket algorithm, fair-use + cost + DDoS protection*
- [x] 25. CQRS ✅ *Rep #22, 2026-07-06 — NEW, taught: separates WRITES from READS (scale/optimize independently; restaurant analogy); cost = sync between models (eventual consistency)*
- [x] 26. Event sourcing ✅ *Rep #22 — NEW, taught: stores EVENTS not current STATE, replay to rebuild (git / bank-ledger analogy); audit trail + time-travel; snapshots for speed. Pairs w/ CQRS* — **🎉 MODULE 2 COMPLETE**

### Module 3 · Cloud Architecture & Infrastructure
- [x] 27. VMs vs containers vs serverless ✅ *Rep #23, 2026-07-07 — nailed all 3 + management ladder (VM>container>serverless). Sharpened: container SHARES host OS kernel (why it's light/fast/portable) vs VM=full OS; serverless=function on-demand, cold-start catch. Trade: less mgmt/faster start = less control*
- [x] 28. Containers & orchestration (Kubernetes) ✅ *Rep #24, 2026-07-07 — got self-healing (replace failed container) + rolling updates. Added scheduling, auto-scaling, load balancing. Crowned with the unifying idea: declarative DESIRED STATE + reconciliation loop (make reality match the wish)*
- [x] 29. Load balancing (L4 vs L7, algorithms) ✅ *Rep #25, 2026-07-07 — got distribute-traffic + L4/L7=OSI layers. Sharpened practical: L4=routes by IP/port (fast/dumb), L7=reads HTTP content (smart, path/cookie routing). Algorithms: round-robin, least-connections, IP-hash*
- [x] 30. Regions / Availability Zones ✅ *Rep #26, 2026-07-07 — got region=location/bigger, AZ=within, multi-AZ for redundancy. Sharpened: AZ = ISOLATED data center (own power/cooling/net, fails independently); multi-AZ = survive a data-center death w/o cross-region latency = default HA. M1 failure ceiling at DC scale*
- [x] 31. Multi-region / failover / DR ✅ *Rep #27, 2026-07-07 — got latency + disaster benefits, failover=auto-switch. TAUGHT RPO (data you can lose / last-save) vs RTO (time to recover / reboot); smaller=pricier. Cost: cross-region replication = CAP/consistency pain*
- [x] 32. CDN & edge ✅ *Rep #28, 2026-07-07 — nailed it (cache at the edge, short distance = faster), linked to caching+latency himself. Added: caches STATIC content; also OFFLOADS origin (throughput relief, not just latency). CDN = M2 caching, geographic*
- [x] 33. DNS ✅ *Rep #29, 2026-07-07 — got domain→IP (+ caching instinct). Added system-design angle: DNS = global traffic director (geo-routing to nearest region, health-based failover); TTL tradeoff (low=fast failover/more lookups, high=cheaper/slower)*
- [x] 34. Networking (VPC, subnets, public/private) ✅ *Rep #30, 2026-07-07 — VPC=isolated private network; DB in private subnet (right reason). Sharpened: public/private = internet REACHABILITY (routing/gateway), not just authz; pattern = public (LB only) → private (app+DB), defense in depth*
- [x] 35. Storage types (block / object / file) ✅ *Rep #31, 2026-07-07 — GAP fixed (thought S3=block; corrected S3=object). Locked w/ own analogies: Block=DB's fast private disk (one server), Object=media/backup locker via key (S3), File=shared SharePoint drive (EFS). Deeper: DB needs block b/c object replaces whole objects+higher latency; storage tiers (hot/Glacier) = cost lever*
- [x] 36. API gateway ✅ *Rep #32, 2026-07-07 — got routing to right service. Added the rest: single front door does auth + rate limiting + SSL + logging ONCE (vs every service reimplementing). Security-desk analogy. Pairs w/ microservices = one door for many services*
- [x] 37. Cost optimization / FinOps ✅ *Rep #33, 2026-07-07 — named auto-scaling + storage tiering + rate limiting (pulled from earlier reps!). Added right-sizing, reserved vs spot, serverless scale-to-zero, visibility/tagging. Mindset: cost = first-class design dimension (M1 cost limit operationalized)* — **🎉 MODULE 3 COMPLETE**

### Module 4 · DevOps, Automation & SRE
- [x] 38. CI/CD pipelines ✅ *2026-08-23 — concept primed and mixed-check passed*
- [x] 39. Deployment strategies (blue-green, canary, rolling) ✅ *2026-08-23*
- [x] 40. Infrastructure as Code (Terraform) ✅ *2026-08-23*
- [x] 41. SLI / SLO / SLA ✅ *2026-08-23*
- [x] 42. Error budgets ✅ *2026-08-23*
- [x] 43. Metrics ✅ *2026-08-23*
- [x] 44. Logging ✅ *2026-08-23*
- [x] 45. Tracing ✅ *2026-08-23*
- [x] 46. Incident response / on-call / postmortems ✅ *2026-08-23*
- [x] 47. Chaos / resilience testing ✅ *2026-08-23*
- [x] 48. Autoscaling ✅ *2026-08-23* — **MODULE 4 COMPLETE**

### Module 5 · Security Architecture & Compliance
- [x] 49. Authentication (OAuth, JWT, sessions) ✅ *2026-08-24 — concept primed and mixed-check passed*
- [x] 50. Authorization (RBAC, ABAC) ✅ *2026-08-24*
- [x] 51. Encryption at rest / in transit ✅ *2026-08-24*
- [x] 52. Key & secrets management ✅ *2026-08-24*
- [x] 53. TLS / certificates ✅ *2026-08-24*
- [x] 54. Compliance frameworks (NIST, FedRAMP, SOC2) ✅ *2026-08-24*
- [x] 55. Data classification / DLP ✅ *2026-08-24*
- [x] 56. Zero trust ✅ *2026-08-24*
- [x] 57. Threat modeling ✅ *2026-08-24*
- [x] 58. OWASP / common vulnerabilities ✅ *2026-08-24*
- [x] 59. Network security (firewall, WAF) ✅ *2026-08-24* — **MODULE 5 COMPLETE**

### Module 6 · AI/ML System Design & MLOps
- [ ] 60. ML lifecycle (training vs inference)
- [ ] 61. Feature stores
- [ ] 62. Model registry / versioning
- [ ] 63. Model serving (batch vs real-time)
- [ ] 64. Offline vs online evaluation
- [ ] 65. Drift detection & retraining
- [ ] 66. A/B testing models
- [ ] 67. Training / data pipelines

### Module 7 · AI Agent Architecture
- [ ] → Covered in `../agentic-engineering/AE-REP-PLAN.md` (shared seam between the two domains)

### Module 8 · Data Architecture & Data Engineering
- [x] 68. OLTP vs OLAP ✅ *2026-08-24 — concept primed and mixed-check passed*
- [x] 69. SQL vs NoSQL ✅ *2026-08-24*
- [x] 70. DB types (relational, document, key-value, graph, columnar, time-series) ✅ *2026-08-24*
- [x] 71. Indexing ✅ *2026-08-24*
- [x] 72. Sharding / partitioning ✅ *2026-08-24 — patched: partitioning splits data; sharding spreads partitions across machines*
- [x] 73. Replication (leader-follower, multi-leader, leaderless) ✅ *2026-08-24 — patched: stale reads come from replication lag*
- [x] 74. Warehouse vs lake vs lakehouse ✅ *2026-08-24*
- [x] 75. Batch vs stream (Kafka, Spark) ✅ *2026-08-24*
- [x] 76. Change data capture (CDC) ✅ *2026-08-24*
- [x] 77. Data modeling / normalization ✅ *2026-08-24*
- [x] 78. ACID vs BASE ✅ *2026-08-24*
- [x] 79. Consensus (Paxos, Raft) ✅ *2026-08-24 — patched: split-brain is the problem; consensus is the solution*
- [x] 80. Storage engines (LSM-tree vs B-tree) ✅ *2026-08-24* — **MODULE 8 COMPLETE**

### Module 9 · Capstone (scenario reps, not new concepts)
- [ ] Full mock: URL shortener · news feed · chat · rate limiter · the interview flow (requirements → estimation → high-level → deep dive → bottlenecks → tradeoffs)

**~80 concepts + capstone mocks.**

---

## How to use
Say **"rep me"** (SD) → Sol throws one concept (encoding rep) or scenario. Notes closed. Reason from the limit up. Log below. Check the box only when it comes out clean and cold.

## Rep Log
| # | Date | Module(s) | Scenario | Finding |
|---|------|-----------|----------|---------|
| 1 | 2026-07-05 | M8 + M1 scaling | FleetCRM 50→50k, screen timing out — what first, what not yet? | (diagnostic) Jumped to read replica, skipped diagnose-first + cheap fixes, didn't name replication lag. Ladder needs reps. |
| 2 | 2026-07-05 | M1 Foundations | **Encoding rep** — the 5 ceilings of a single machine, via one-worker-restaurant analogy | ✅ Encoded. Generated all 5 himself; caught "ceiling ≠ component"; fixed memory(head)/storage(pantry) blur; Feynman-closed cold. Foundation locked. |
| 3 | 2026-07-05 | M1 Foundations | **Encoding rep** — latency vs throughput, via highway analogy | ✅ Encoded from memory (didn't read). Sharpened latency=time/"how long", throughput=rate/"per second". Reasoned the add-lanes→throughput-not-latency tradeoff himself; linked to Rep #2 (lanes=machines=horizontal scaling). Feynman-closed all 5 blanks cold. |
