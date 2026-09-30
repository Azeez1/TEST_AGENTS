# Agentic Engineering — Rep Plan (Master Checklist, by Module)

**Started:** 2026-07-05 · **Mode:** Recall + articulation reps (this is your EDGE) · **Rolls up to:** `../Q3-2026-FOCUS-MAP.md` · **Compass:** `../CONNECTION-MAP.md` · **Method:** `../STUDY-PROTOCOL.md`
**Built on:** the 6 LLM limits + your 12 Leverage Points framework + gap-checked against *AI Engineering* (Chip Huyen, in vault, 2026-07-06).

## The rep bar (First Principles)
For each concept: name the **LLM limit** it addresses + **where you've used it in your own 73-agent system.** Derive + point, don't recite.

## The shape: BUILD path + TRUST path
- **Build path** (make an agent work): Modules 1–5.
- **Trust path** (know it works, keep it safe, make it improve): Modules 6–8. *(Huyen spends ~40% of the book here — it's what turns a demo into a product.)*

## Your 4 pillars → where they live
Prompt engineering → **M1** · Context engineering → **M2** · Loop engineering → **M3 (Reasoning)** · Harness engineering → **M3 (Tools)**.

## Rule: stop at a MODULE boundary (finish the unit, map it, bank it).

**Related source:** [Operating-level video notes](Operating-Level-Video-Notes.md) — a decision rule for when to inspect code/data versus turn verified work into agent workflows. Practice it alongside M3–M6.

---

## Module 1 · Foundations & Prompting   ✅ core done · +4 new to rep
**The 6 LLM limits (the root — mirror of SD's 5 machine ceilings)**
- [x] 1. The 6 LLM limits: context window · attention/recall · non-determinism · no ground truth · cost · latency ✅ *AE Rep #1, 2026-07-05 — named all 6 (context/groundedness from experience; nudged non-determinism/cost/latency/attention); locked fit(window) vs use(attention)*

**Prompt Engineering**
- [x] 2. System-prompt design ✅ *AE Rep #2 — standing role/rules layer; CLAUDE.md = concrete example*
- [x] 3. Few-shot / in-context learning ✅ *AE Rep #3 — CORRECTED: few-shot = few EXAMPLES in the prompt (not multi-turn chat); zero/one/few-shot; in-context learning*
- [x] 4. Structured / constrained output ✅ *AE Rep #4 — nailed it: JSON schema forcing exact parseable format (addresses non-determinism)*
- [x] 5. Steering & refusal handling ✅ *AE Rep #5 — steering=softly guide, refusal handling=manage wrong refusals; guardrails BLOCK, steering GUIDES*

**Model behavior (NEW — folded from AI Engineering book, Ch. 2)**
- [ ] 6. Sampling & decoding: temperature, top-k, top-p, min-p *(the knobs under "structured output")*
- [ ] 7. Test-time compute: best-of-N, self-consistency, beam search
- [ ] 8. Post-training: SFT vs RLHF / DPO / RLAIF *(why the model behaves the way it does — the layer under the 6 limits)*
- [ ] 9. Hallucination: the two hypotheses (why models make things up)

## Module 2 · Context Engineering *(your deep edge)*   ✅ COMPLETE
- [x] 10. MECW (minimal effective context window) ✅ *AE Rep #6, 2026-07-06 — extra context DILUTES attention = tax on window+attention+cost. Curation problem.*
- [x] 11. KV-cache ✅ *AE Rep #7 — caches already-computed work for seen tokens; reused when prefix identical. LEVER: stable stuff front, changing end.*
- [x] 12. Context packing / selection ✅ *AE Rep #8 — ORDER (edges, "lost in the middle") + SELECT (relevance + retrieval + budget)*
- [x] 13. Retrieval (RAG) ✅ *AE Rep #9 — pipeline nailed; 3 wins: window + knowledge it lacks + grounding/anti-hallucination*
- [x] 14. Chunking / embeddings / vector DBs ✅ *AE Rep #10 — embedding=coords of MEANING; chunk tradeoff (too small loses context/too big blurs, use overlap)*
- [x] 15. Tiered compaction / summarization ✅ *AE Rep #11 — tiered by recency+relevance; lossy; tension: rewriting prefix busts KV-cache*
- [x] 16. Context rot / attention decay ✅ *AE Rep #12 — the DISEASE; all of context-eng is the treatment. Synthesized the module himself.*

## Module 3 · Reasoning, Tools & Memory
**Reasoning & Control = LOOP ENGINEERING**
- [x] 17. ReAct (reason + act loop) ✅ *AE Rep #13, 2026-07-07 — got the loop (think→act→repeat until outcome). Made OBSERVATION explicit: Thought→Action→Observation→repeat; observation feeds next thought = adaptive. Interleaves reason+act. Tradeoff: decides next step each turn (flexible but can wander) → sets up plan-execute*
- [x] 18. Plan-and-execute ✅ *AE Rep #14, 2026-07-07 — nailed tradeoff (plan upfront, no wander, good for long defined tasks; weakness=constrained). Sharpened: rigidity = charges ahead when reality diverges; fix = plan+RE-PLAN hybrid. ReAct=adaptive/exploratory, plan=coherent/defined. Cost: plan w/ smart model, execute w/ cheap*
- [x] 19. Reflection / self-critique ✅ *AE Rep #15, 2026-07-07 — got the cross-attempt form (Reflexion: learn from failures, do better next try). Added within-task self-critique (generate→critique→revise before finishing). Works like proofreading. Catches: costs tokens, can be wrong about own critique, can't reflect past a knowledge gap*
- [x] 20. Chain-of-thought ✅ *AE Rep #16, 2026-07-07 — nailed it + connected to attention/recall limit himself (sharp). Affirmed: reasoning tokens = external scratchpad (working memory it can attend to) + more tokens = more COMPUTE. Base primitive under ReAct & reflection; = test-time compute*
- [ ] 21. Loop design & termination
**Tools & Harness = HARNESS ENGINEERING**
- [x] 22. Tool schema design ✅ *AE Rep #17, 2026-07-07 — got description half (what it does, when to use / NOT use). Added: schema = name + description + PARAMETERS (typed inputs). Principle: schema is the model's ONLY window into the tool — picks+fills purely from it. Write like docs for a smart intern who can't see the code*
- [x] 23. Tool-count-as-tax ✅ *AE Rep #18, 2026-07-07 — nailed it (lost-in-the-middle/attention, keep tools minimal ~3-4). Named both taxes: context (schema burns tokens even unused) + decision (more options = noise/wrong-tool). = MECW for tools. Fix for many: dynamic tool selection (RAG for tools)*
- [ ] 24. Action-space design
**Memory**
- [ ] 25. Short-term vs long-term memory
- [ ] 26. Episodic / semantic / file-based memory
- [x] 27. Memory retrieval & decay ✅ *AE Rep #23, 2026-07-07 — retrieval=semantic search (+ recency + importance); decay=context window pressure. Deepened decay = forgetting is a FEATURE (signal/high-quality, staleness, cost) = curation for long-term memory (same as MECW/context rot). His MEMORY.md pruning in action* — **🎉 AE MODULE 3 COMPLETE**

## Module 4 · Multi-Agent & Cost / Reliability  *(eval carved out → M6)*
**Multi-Agent**
- [ ] 28. Orchestrator / router patterns
- [ ] 29. Fan-out / fan-in (parallel vs serial)
- [ ] 30. Handoffs / delegation
- [ ] 31. When multi-agent beats single
**Cost, Latency & Reliability**
- [ ] 32. Token budgets
- [ ] 33. Model routing (Haiku / Sonnet / Opus)
- [ ] 34. Prompt caching
- [ ] 35. Streaming / latency
- [ ] 36. Fine-tune vs RAG vs prompt (the decision rule: finetune for form, RAG for facts)
- [ ] 37. Retries / fallbacks / error recovery

## Module 5 · The 12 Leverage Points (Claude Code control surfaces — your framework)
*(calibration from your 2026-05-11 audit; scores stale, framework timeless)*
- [ ] 38. CLAUDE.md 🟢 · 39. Agent YAML 🟢 · 40. Slash commands 🟢 · 41. Skills 🟢
- [ ] 42. Subagents 🔴 (defined ≠ dispatched) · 43. MCP servers 🟢 · 44. Tool permissions (allow+deny) 🟡
- [ ] 45. Hooks 🟡→⬆️ · 46. Output routing 🟡→⬆️ · 47. Schemas 🔴 · 48. Validators 🟡 · 49. Structured logs 🟡

---
## ⭐ TRUST PATH (added 2026-07-06 from AI Engineering gap-check — the demo→product half)

## Module 6 · Evaluation & Model Selection  *(the #1 add — book gives it 2 of 10 chapters)*
- [ ] 50. Evals / benchmarks *(moved from M4)*
- [ ] 51. LLM-as-judge (+ the Money Rule) *(moved from M4)*
- [ ] 52. Adversarial verification *(moved from M4)*
- [ ] 53. Cost-ordered eval portfolio: functional correctness > similarity-to-reference > AI judge > human
- [ ] 54. Language-modeling metrics (perplexity / cross-entropy) + contamination detection
- [ ] 55. Comparative eval (Elo, Bradley-Terry, Chatbot Arena)
- [ ] 56. Model selection (criteria buckets + build-vs-buy 7-axis)
- [ ] 57. Eval-pipeline design (per-component + end-to-end; rubrics tied to business metrics)
- [ ] 58. Sample sizing (~100 / ~1,000 / ~10,000 for 10% / 3% / 1% gaps)

## Module 7 · LLM Security  *(justified: you ship write-capable agents with tools + hooks)*
- [ ] 59. Guardrails / filtering *(moved from M4)*
- [ ] 60. Prompt injection (direct + indirect)
- [ ] 61. Jailbreak taxonomy (direct / automated / indirect)
- [ ] 62. Prompt extraction (reverse prompt engineering)
- [ ] 63. The 3-layer defense (model / prompt / system)
- [ ] 64. PII handling / data exfiltration
- [ ] 65. Tool-use safety (agent with write actions + injection = the real danger)

## Module 8 · Feedback Loops & AI Product  *(the "data flywheel" — book's biggest under-investment area)*
- [ ] 66. Implicit / conversational feedback (early termination, error correction, regeneration, edits as preference data)
- [ ] 67. Explicit feedback
- [ ] 68. Degenerate feedback loops (sycophancy, popularity bias, filter bubbles)
- [ ] 69. Feedback UX design
- [ ] 70. Latency budgets (TTFT / TPOT at p50 / p90 / p99)
- [ ] 71. Human-in-the-loop for write actions *(your DBAC Money Rule, formalized)*
- [ ] 72. Uncertainty-triggered feedback (collect when the model is low-confidence)

---

**~72 concepts across 8 modules** (5 build-path + 3 trust-path). Done: M1 core + M2 = 12. Diagnosis to carry: *"knowledge-heavy, enforcement/quality-light — capability grew faster than controls"* — the trust path (M6-8) is literally the fix.

**Rejected as a gap:** multimodality (book's thin on it — not core in 2026). **Already beyond the book:** your context engineering (M2) and memory model (M3).

> **LIVING list** — surface a new concept? Add it. Ask "which LLM limit / trust-gap?" and it slots in.

## How to use
Say **"rep me — agentic"** → one concept, notes closed: *which LLM limit? which technique/lever? where did I use it in my own system?* Log below.

## Rep Log
| # | Date | Module / Concept | Scenario | Finding |
|---|------|------------------|----------|---------|
| 1 | 2026-07-05 | M1 · The 6 LLM limits | **Encoding rep** — find the LLM's limits (mirror of SD's 5 machine ceilings) | ✅ Named all 6 (2 from experience, 4 nudged). Feynman-closed cold. AE foundation locked. |
