# The Connection Map — How It All Hangs Together

## Current learning map (September 24, 2026)

This is the short cross-thread index. The sections below remain the first-principles map for system design and agentic engineering.

For the complete frontier-lab target profile, see the [Exceptional AI FDE capability map](elite-tech-mastery/FDE-CAPABILITY-MAP.md).

| Track | Evidence already present | Current practice edge | Home |
|---|---|---|---|
| Business and client solutioning | WISER, MUCTA, IFDAEC, and related frameworks; client-facing AI architecture and API/MCP work | Connect each business decision to a deployable technical artifact | [Elite tech mastery notes](elite-tech-mastery/NOTES.md) |
| System design | Many applied DRAWS/W exercises across feeds, live systems, payments, uploads, search, and dispatch; increasing ability to split durable writes, reads, events, and live delivery | Make R/A classification and W explanations consistent under an unfamiliar prompt; add failure-specific S reps and production artifacts | [System design current state](system-design/CURRENT_STATE.md) · [L2 practice task](codex://threads/01a02648-7248-73a0-af3c-b5838f3c331c) |
| Agentic engineering | Agent workflows and the local multi-agent system, plus the L1–L5 range-of-motion model | Show evals, controls, observability, and deployment in a working implementation | [Agentic engineering plan](agentic-engineering/AE-REP-PLAN.md) |
| Python implementation | CS background, code reading, APIs, and sound problem decomposition; current coding exercises reveal friction translating a plan into unaided Python syntax | Write, run, and debug small Python functions without completion for the upcoming coding screen | [Python practice](python/README.md) |

These are different dimensions of engineering ability. Python typing speed is an immediate interview constraint, not a measure of all prior architecture or delivery experience. The [L4 learning task](codex://threads/01a07e8e-1257-79a2-86ea-2d37efde77b1) records the broader goal: AI production, architecture, and forward-deployed delivery. Treat the task histories as practice evidence, not a formal seniority assessment.

### The antidote to "too many concepts to pick up"

**The panic:** "Agentic Engineering and System Design have SO many concepts. I have to pick them all back up AND see how they connect."
**The cure:** You don't hold the concepts. You hold the **LIMITS**. Every concept is just a *response* to a fundamental limit. Hold ~12 limits and you can re-derive any of the 60 concepts on demand. You store the **generator**, not the answers.

> First Principles here isn't a study method — it's **compression**. ~60 leaves → 2 trunks (one per domain) → 1 root (the limits rhyme).

## The rule for every concept you meet
Don't ask *"do I remember this?"* Ask **"which limit does this solve, and what does it cost?"**
If you know the limit, you can rebuild the concept from scratch. That's why you don't need it pre-loaded — and why "picking them all back up" is the wrong frame. You pick up the *limits*; the concepts grow back.

---

## SYSTEM DESIGN — 6 territories, each with its own compass

Your 9 modules are **different territories** (a real system has different concerns). They group into 6, and each answers its OWN core question. Don't force them all through one lens.

| Territory | Modules | Core question it answers | Its compass (what to derive from) |
|---|---|---|---|
| **The Physics** | M1 Foundations | What are the fundamental limits everything responds to? | *the limits themselves* |
| **The Build** | M2 Software · M3 Cloud · M8 Data | How do we build it so it scales and doesn't fall over? | **the 7 machine limits ↓** |
| **The Ops** | M4 DevOps/SRE | How do we ship safely and know the second it breaks? | feedback loops · automation · error budgets |
| **The Guard** | M5 Security/Compliance | Who do we trust, what's the blast radius if we're wrong? | trust boundaries · least privilege · defense in depth |
| **The Intelligence** | M6 ML · M7 Agents | How do we add ML/agents that actually work? | LLM limits (see Agentic Eng below) |
| **The Proof** | M9 Capstone | Can I design the whole thing end to end? | *integrate all of the above* |

### The Build territory's compass — the ~7 limits of one machine
| Limit (the "why") | Concepts that hang off it (the "what") |
|---|---|
| **Compute** — one CPU does only so much | horizontal scaling · load balancers · async / queues · caching (avoid recompute) |
| **Memory** — RAM is finite | cache tiers · pagination · streaming |
| **Storage** — one disk / DB saturates | sharding · partitioning · replication · data tiering |
| **Failure** — machines die | redundancy · replicas · failover · retries · health checks · multi-AZ |
| **Latency** — work + distance take time | CDN · read replicas · indexing · geo-distribution · caching |
| **Consistency** — copies disagree | CAP · replication lag · consensus · eventual vs strong · idempotency |
| **Cost** — all of it costs money | serverless · autoscaling · right-sizing · the tradeoff axis itself |

> **The unifying habit across ALL 6 territories:** ask *"what fundamental pressure created the need for this?"* The pressure differs by territory (scaling limits / feedback / trust / LLM limits) — the *move* (derive, don't memorize) is always the same. That habit is First Principles. You hold **6 territories + 1 habit**, not 60 concepts.

---

## AGENTIC ENGINEERING — the whole domain hangs off ~6 limits of an LLM

| Limit (the "why") | Concepts that hang off it (the "what") |
|---|---|
| **Finite context window** — can't fit everything | context packing · retrieval · compaction · MECW · memory systems |
| **Imperfect attention** — recall decays over long context | context ordering · tool-count-as-tax · context rot · KV-cache |
| **Non-determinism** — same input, varying output | evals · guardrails · verification · structured output |
| **No ground truth** — the model can't self-certify | LLM-as-judge (+ the Money Rule) · adversarial checks · human-in-loop |
| **Cost / tokens** — intelligence is priced per token | caching · model routing · token budgets |
| **Latency** — inference takes time | streaming · caching · one-shot vs loop tradeoffs |

Every technique in your 73-agent system fits in a row above.

---

## THE BRIDGE — why learning one teaches the other
Agentic engineering **is distributed-systems thinking applied to LLMs.** The limits *rhyme*:

| System Design limit | ↔ | Agentic Engineering limit |
|---|---|---|
| Memory / storage (finite RAM) | ↔ | Finite context window |
| Compute (one machine's ceiling) | ↔ | One agent's context → **multi-agent = horizontal scaling** |
| Failure (machines die) | ↔ | Non-determinism (outputs "fail" unpredictably) |
| Consistency (copies disagree) | ↔ | No ground truth (which output is correct?) |
| Latency & Cost | ↔ | Latency & Cost (identical) |

Your **DBAC** framework already bridges them (Data → Brain → Action → Check; security as a filter across all four). You are not learning two piles — you're learning **one set of limits wearing two costumes.**

---

## What this does to the panic
- You are NOT picking up 60 concepts. You're holding **~12 limits.**
- "How they connect" = concepts connect **through the shared limit**; the domains connect because **the limits rhyme.**
- Every rep = pick a concept → name its limit → re-derive it. The leaves grow back every time, so you never have to store them.

**This file is the trunk. The rep plans (`system-design/REP_PLAN.md`, `agentic-engineering/AE-REP-PLAN.md`) are the leaves. Read this one when the volume feels like too much.**
