# Agentic Engineering — Self-Study Course
## Reverse-engineered from IndyDevDan's Tactical Agentic Coding + adapted to TEST_AGENTS

**Purpose:** Convert your existing 64-agent stack from *scattered components* into a *structured system with feedback*. Pick lessons in any order — dependency map below tells you what blocks what.

**Time budget:** ~12-15 hours total (Dan's course is 6.5h of video; hands-on doubles it). Split across 2-3 weeks at 1h/day.

---

## How to use this doc

Each lesson follows the same shape:

1. **Core concept** — what the idea actually is in plain English
2. **Why it matters for you** — specific to your TEST_AGENTS repo / Dux Machina goals
3. **Free sources** — YouTube, GitHub, Anthropic docs (no paid course needed)
4. **Hands-on** — a concrete exercise inside your repo
5. **Done when** — pass criteria so you know you actually learned it
6. **Time** — realistic estimate

Each lesson is self-contained. Skip lessons whose "Done when" criteria you already meet.

---

## Prerequisites check (what you already have)

You're not starting from zero. Confirmed in your repo:

- 64 agents across 6 teams (lessons 6, 11, 12 partially done)
- 7 MCP servers integrated (lesson 2 partially done)
- Skills system, 28 skills installed (lesson 13 partially done)
- One hook running (`.claude/hooks/pe_validation_gate.ps1`) — proof of concept
- Workspace boundary rules, output routing rules, tool priority rules — but enforced as prose, not gates
- No eval infrastructure
- No closed-loop prompts in production
- No subagent specialization for review/docs

**Two biggest gaps:** hooks (deterministic enforcement) + evals (measurable quality). Lessons 5 and 6 prioritize these.

---

## Dependency map — what blocks what

```
1 (Core Four) ──┬─→ 2 (Leverage) ──┬─→ 3 (Plan) ──→ 4 (PITER) ──→ 5 (Closed Loop)
                │                   │
                └─→ 9 (Context) ────┘                              │
                                                                   ↓
                                              6 (Review agents) ──→ 7 (ZTE) ──→ 8 (Agentic Layer)
                                                                   
                10 (Prompt levels) → 11 (Domain agents) → 12 (Orchestration) → 13 (Skills/Learning) → 14 (Capstone)
```

**Recommended order for you:** 1 → 5 → 6 → 9 → 4 → 10 → 13 → rest. Front-load hooks + evals (5, 6), then context engineering (9), then automation (4), then prompt sophistication (10).

---

## LESSON 1 — The Core Four

**Core concept:** Every AI coding result = function of **Context + Model + Prompt + Tools**. When output is bad, one of these four is the cause. Tune one lever at a time.

- Context = what the model can see (files, prior messages, system prompt, memory)
- Model = which model + which params (Opus vs Sonnet, temperature)
- Prompt = the instruction itself (the *ask*)
- Tools = what the model can do (Read, Write, Bash, MCP tools, subagents)

**Why it matters for you:** You debug agents by tweaking prompts. 80% of the time the real fix is context (wrong files loaded) or tools (missing capability). Wrong lever = hours wasted.

**Free sources:**
- IndyDevDan YouTube — search "Big Three" or "Principled AI Coding"
- Anthropic docs → "Prompt engineering overview" + "Context window"

**Hands-on:** Pick one of your agents that produced bad output recently. Write a one-page diagnosis: which of the four was wrong? File at `LEARNING/diagnoses/01-core-four.md`.

**Done when:** You can name the four levers without thinking, and your next "why did the agent do that?" debug starts with "context or tools?" not "let me rewrite the prompt."

**Time:** 1h

---

## LESSON 2 — The 12 Leverage Points

**Core concept:** Specific places to inject signal into agents. Dan lists 12; the real list (Claude Code specific):

1. `CLAUDE.md` files (project, user, team)
2. System prompt / agent definition YAML
3. Slash commands (`.claude/commands/*.md`)
4. Skills (`.claude/skills/*/SKILL.md`)
5. Subagents (`.claude/agents/*.md`)
6. MCP servers (capability injection)
7. Hooks (deterministic gates)
8. Tool permissions (`settings.json`)
9. Output routing rules (filesystem layout)
10. Type systems / schemas (force structured output)
11. Tests / validators (closed-loop signal)
12. Stdout / logs (what the next turn sees)

**Why it matters for you:** Your repo uses 1-6 and 8-9. You barely use 7 (one hook), 10-12 (no schemas, no validators). The unused leverage points are your highest-ROI work.

**Free sources:**
- Claude Code docs → "Hooks", "Slash commands", "Subagents", "Skills"
- Your own `.claude/` directory — audit what's there

**Hands-on:** Make a table: for each of the 12 points, mark used/unused/partial. File at `LEARNING/audits/12-leverage-audit.md`. For each "unused," write one sentence on what you'd use it for.

**Done when:** You have a prioritized list of which leverage points to add next.

**Time:** 1h

---

## LESSON 3 — Plan First, Execute Second

**Core concept:** Spec-driven development. Before asking an agent to *do*, ask it to *plan*. The plan goes in a file. The agent then executes the plan, ticking off steps.

Pattern:
```
1. agent reads requirements → writes PLAN.md
2. you review PLAN.md (5 min)
3. agent executes PLAN.md step by step
4. agent writes COMPLETED.md with deviations from plan
```

**Why it matters for you:** Your PE diagnosis pipeline, LinkedIn workflow, and lead-gen all do multi-step work. Without explicit plans, deviations are silent. With plans, deviations are visible.

**Free sources:**
- Anthropic docs → "Extended thinking" + "Plan mode"
- IndyDevDan YouTube — "spec prompt" videos
- GitHub spec-kit project

**Hands-on:** Take your `comment-leads` skill. Add a step zero: agent writes `PLAN.md` listing target accounts before running. You approve, then it executes. Time it before/after.

**Done when:** Three of your skills now do plan-then-execute instead of execute-blind.

**Time:** 1.5h

---

## LESSON 4 — PITER / AFK Agents

**Core concept:** Pipeline pattern. Agent runs through fixed phases: **P**lan → **I**mplement → **T**est → **E**valuate → **R**eview. Each phase has a gate. You walk away.

Implementation = bash/Python wrapper that runs `claude -p "phase X prompt"` in sequence, with eval gates between phases.

**Why it matters for you:** Your 17-episode YouTube backlog is the ideal PITER candidate. Each episode goes Plan (script) → Implement (HeyGen render) → Test (preview) → Evaluate (length/quality check) → Review (your final approval). Right now you do it manually.

**Free sources:**
- IndyDevDan YouTube — "AFK agents" / "Agentic Developer Workflow"
- `github.com/disler/indydevtools` — actual PITER implementation in code

**Hands-on:** Write a single PITER script for ONE workflow you do weekly. Bash or Python. Each phase = one Claude call. File at `LEARNING/piter/youtube-episode.sh`.

**Done when:** You can run `./piter/youtube-episode.sh "topic name"` and walk away for 30 min while it produces a script + storyboard.

**Time:** 2-3h

---

## LESSON 5 — Closed Loop Prompts ⭐ (priority)

**Core concept:** Self-correcting loop. Agent runs, reads its own output (test failures, lint errors, validator output), patches, re-runs until green.

Skeleton:
```bash
while ! validator.sh; do
  claude -p "fix what validator.sh just complained about, then exit"
done
```

**Why it matters for you:** You identified this gap. Your PE validation gate hook is half of a closed loop. The other half is auto-fix-and-retry instead of human intervention.

**Free sources:**
- Claude Code docs → "Hooks" (Stop, PostToolUse)
- IndyDevDan YouTube — "closed loop" videos
- Anthropic engineering blog → "Claude Code best practices"

**Hands-on:** Add a closed loop to your PE diagnosis pipeline.
1. Validator already exists (`pe_validation_gate.ps1`)
2. Add a `Stop` hook that runs the validator
3. If validator fails, hook returns "continue with fix" instead of letting agent exit
4. Loop max 3 attempts, then page you via Telegram

**Done when:** A PE diagnosis can fail validation up to 3 times and still produce a valid PDF without your involvement.

**Time:** 2h

---

## LESSON 6 — Specialized Subagents (Review + Docs) ⭐ (priority)

**Core concept:** The agent that *writes* code should not be the agent that *reviews* it. Same model, different context, different prompt, different success criteria. Spawned via the Task tool or subagent definitions.

Three roles every pipeline needs:
- **Implementer** (writes the thing)
- **Reviewer** (reads the thing, finds problems, doesn't touch code)
- **Documenter** (writes how-to-use docs, separate context)

**Why it matters for you:** Your team agents implement. None of them have dedicated reviewer subagents. Cross-team review is the highest-leverage QA play you're missing.

**Free sources:**
- Claude Code docs → "Subagents"
- Your existing `.claude/agents/*.md` files — extend pattern
- Anthropic engineering blog → "Multi-agent research system"

**Hands-on:** Create three new subagents:
1. `linkedin-reviewer` — checks brand voice rules, hashtag count, length
2. `pe-diagnosis-reviewer` — checks 7-rule framework (you have a validator; this adds qualitative review)
3. `code-reviewer` — generic, reviews any code change before commit

Each gets its own `.md` file in `.claude/agents/`. None can call Write or Edit — review only.

**Done when:** Your top-3 most-used pipelines all spawn a reviewer subagent before declaring done.

**Time:** 2-3h

---

## LESSON 7 — ZTE (Zero Touch Engineering)

**Core concept:** Spectrum: in-loop (you babysit) → out-loop (you check in periodically) → ZTE (codebase ships from issue → PR with zero human touches).

ZTE requires: GitHub Actions + Claude Code in CI + closed-loop validators + reviewer subagents + automatic rollback.

**Why it matters for you:** You don't need full ZTE on everything. But your LinkedIn cadence and PE outbound are ripe — they're repeatable, low-risk, daily. ZTE them.

**Free sources:**
- Anthropic docs → "Claude Code GitHub Actions"
- Your repo's `.claude/skills/lead-gen-*` — these are halfway to ZTE

**Hands-on:** Pick ONE workflow to push to ZTE. Recommend `lead-gen-cleaning` since it already runs on a sheet. Add: cron trigger → run skill → reviewer subagent → append to sheet → Telegram summary. No human in the chain.

**Done when:** A lead-gen run happens at 9am Monday without you launching it, and you get a Telegram ping at 9:15am with the result.

**Time:** 3h

---

## LESSON 8 — The Agentic Layer

**Core concept:** Treat agents as a *runtime layer* between intent and execution, not as one-off tools. Build infrastructure around them: logging, observability, fallbacks, retries, cost tracking.

**Why it matters for you:** Once you have 64 agents + hooks + evals + closed loops, you have a distributed system. Distributed systems need observability or they're black boxes.

**Free sources:**
- Anthropic engineering blog → "Building effective agents"
- Concepts: structured logging (JSON), trace IDs, cost-per-task

**Hands-on:** Add a single JSONL log line per agent invocation: `{ts, agent, prompt_tokens, completion_tokens, cost, status, trace_id}`. Dump to `LOGS/agent-runs.jsonl`. Build a tiny script that summarizes: agent X has cost Y this week, fails Z% of runs.

**Done when:** You can answer "which agent costs me the most per week?" in one query.

**Time:** 2h

---

## LESSON 9 — Context Engineering (R&D Framework)

**Core concept:** **R**etrieve only what's needed + **D**iscard aggressively. Big context = slow, expensive, dumber. Engineer context like you engineer memory.

12 techniques (Dan's list, deduplicated):
1. Glob/grep instead of reading whole files
2. Slash-command-injected context (not always-on)
3. CLAUDE.md hierarchy (project > team > user)
4. Ephemeral working files in `tmp/` for agent scratch
5. Summarize-and-discard for long runs
6. Skill files loaded only when invoked
7. Subagent boundary = fresh context (use it on purpose)
8. Tool descriptions trimmed to essentials
9. Output schema forces compact responses
10. Prior turns pruned in long conversations
11. MCP tool list filtered per task
12. Memory files curated, not append-only

**Why it matters for you:** Your CLAUDE.md is already big. Your MEMORY.md is bigger. Every prompt loads all of it. Cost + speed cost compounds.

**Free sources:**
- Anthropic blog → "Effective context engineering for agents" (Sep 2025)
- IndyDevDan YouTube — recent "context" videos

**Hands-on:** Audit your MEMORY.md. Move stale entries (resolved bugs, completed projects) to `MEMORY-archive.md`. Target: cut active memory by 40%. Re-test agent behavior after — should be faster and no worse.

**Done when:** MEMORY.md is under 4KB and you have an archiving rhythm (weekly).

**Time:** 2h

---

## LESSON 10 — The 7 Prompt Levels

**Core concept:** Prompt sophistication is a ladder:

1. **Plain prompt** — "write a function that…"
2. **Structured prompt** — clear role + task + constraints + output format
3. **Few-shot prompt** — includes 2-3 examples
4. **Templated prompt** — variables filled in by code
5. **Chained prompt** — output of A feeds input of B
6. **Meta-prompt** — a prompt that writes prompts
7. **Self-improving meta-prompt** — meta-prompt that updates itself based on results (requires evals)

**Why it matters for you:** Most of your skills are level 2-3. Your slash commands are level 4. Almost nothing is level 5+. The meta-prompt level is where 10x productivity lives.

**Free sources:**
- Anthropic prompt engineering docs
- IndyDevDan YouTube — "meta prompt" videos

**Hands-on:** Pick one skill (e.g., `comment-engine`) and build it at three levels. Compare outputs. Save all three in `LEARNING/prompt-levels/`.

**Done when:** You have one production meta-prompt that generates other prompts you actually use.

**Time:** 2h

---

## LESSON 11 — Domain-Specific Agents

**Core concept:** Specialized agents with deep domain context outperform generalist agents on narrow tasks. You already do this — formalize the pattern.

Domain agent template:
- Strict scope (one domain, one role)
- Domain glossary embedded in prompt
- Domain-specific examples (few-shot)
- Domain validation rules (linked from agent → hook)
- Domain output schema

**Why it matters for you:** Your 6 teams are domain agents at the team level. But within teams, agents overlap. E.g., MARKETING has 18 agents but unclear which owns which type of post.

**Free sources:**
- Your own `.claude/agents/` — already the pattern
- Anthropic → "Agent specialization" examples

**Hands-on:** Audit MARKETING_TEAM agents. For each, write a one-line "owns X, does not do Y." File at `LEARNING/audits/marketing-agent-scope.md`. Eliminate or merge any overlap.

**Done when:** Each MARKETING agent has a non-overlapping domain you can state in one sentence.

**Time:** 2h

---

## LESSON 12 — Multi-Agent Orchestration

**Core concept:** One orchestrator agent receives a complex task, decomposes it, dispatches subtasks to specialists in parallel, aggregates results.

Components:
- Orchestrator (decomposes + dispatches + aggregates)
- Specialist subagents (each does one thing)
- Coordination layer (shared state, often a file or a database row)
- Observability (which subagent is doing what right now)

**Why it matters for you:** Your `router-agent`, `cto`, `cfo-agent`, `sales-manager`, `test-orchestrator` already exist. They're orchestrators in name. Are they orchestrators in behavior? Probably not yet — most of your workflows still run as single-agent.

**Free sources:**
- Anthropic engineering blog → "Building a multi-agent research system"
- Claude Code docs → Task tool + subagents

**Hands-on:** Pick one cross-team workflow (e.g., "produce + publish LinkedIn post including image"). Currently it's probably one agent. Rewrite it as: orchestrator dispatches to (a) copywriter, (b) visual-designer, (c) brand-reviewer, (d) publisher. Run in parallel where possible.

**Done when:** One real workflow runs as ≥3 parallel subagents instead of one sequential agent. Faster wall-clock time + better quality from specialization.

**Time:** 3h

---

## LESSON 13 — Skills as Learned Behavior

**Core concept:** Agents forget. Skills are persistent "memorized procedures" — a markdown file the agent loads when needed. Act-Learn-Reuse loop:

1. Act: agent does a task
2. Learn: if it worked well, capture the pattern as a skill
3. Reuse: next time, agent invokes the skill instead of re-discovering

**Why it matters for you:** You have 28 skills. Most were hand-built. The pattern you're missing: agent writes its own skills after a successful complex task.

**Free sources:**
- Claude Code skills documentation
- Your existing `.claude/skills/*/SKILL.md` — the pattern works

**Hands-on:** Build a meta-skill: `capture-as-skill`. After any successful complex task, run it: agent reflects on what worked, drafts a new SKILL.md, you approve, it goes live. The agent grows its own toolkit.

**Done when:** You've captured at least 2 new skills from real work (not designed in advance) in 30 days.

**Time:** 2h

---

## LESSON 14 — Capstone: Codebase Singularity

**Core concept:** Combine everything. Codebase that maintains and extends itself with minimal touch.

**Why it matters for you:** This is Dux Machina's delivery moat. Anyone can sell agentic consulting. Almost nobody can demo a codebase that ships features while the founder sleeps.

**Free sources:** Everything above. No new material.

**Hands-on — the real capstone:** Pick ONE end-to-end Dux Machina workflow and make it fully ZTE for 30 days. Recommended: **PE Outreach pipeline**.

End state:
- Cron-triggered weekly
- Pulls new PE firms from SAM.gov / public sources
- Researches each via Perplexity MCP
- Drafts 7-touch sequence per firm
- Reviewer subagent QAs
- Logs everything (lesson 8)
- Runs evals (lesson 6 logic)
- Pages you on Telegram if anything fails
- Updates Google Sheet conditional formatting (your green-row pattern)

If this runs untouched for 30 days and you book one meeting from it, you have ZTE proof. That's the Dux Machina pitch deck slide.

**Done when:** You can show a prospect a live screen recording of the pipeline running with zero human input.

**Time:** Open-ended (4-8h to build, 30 days to validate)

---

## What to do this week

If you do nothing else: **Lesson 5 (closed loop) + Lesson 6 (reviewer subagent) + Lesson 9 (context audit)**. These three together = the structural upgrade from "scattered" to "system." Everything else compounds off these.

## How to know you actually learned this

Three external proofs:

1. **Repo proof** — `LEARNING/` directory full of completed exercises
2. **Behavior proof** — three of your pipelines now run closed-loop with reviewer subagents
3. **Business proof** — one ZTE pipeline shipping real outputs (LinkedIn posts, PE diagnoses, leads) without your daily touch for ≥2 weeks

When all three are true, you've extracted ~90% of what the $599 course teaches, on your own repo, with code you understand because you wrote it.
