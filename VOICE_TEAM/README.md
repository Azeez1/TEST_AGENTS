# VOICE_TEAM — AI Voice Agent Factory

Production voice AI agent factory for law firms (and other professional services). Deploys customized Retell AI agents per firm from a single `firm.yml` config in under 60 seconds.

## Quick Start — Deploy A New Firm

```bash
# 1. Onboard a new firm (interactive — generates firm.yml + KB docs)
/new-voice-firm

# 2. Deploy the agent to Retell
/deploy-voice-firm <firm-slug>

# 3. Test by calling the phone number printed at the end of deploy

# 4. Process pending booking intents (post-call calendar bookings)
python VOICE_TEAM/tools/book_pending_consults.py --firm <firm-slug>
```

## Architecture

```
                    ┌────────────────────────────────────────┐
                    │ VOICE_TEAM/memory/firms/<slug>.yml    │
                    │   ─ firm identity, practice area      │
                    │   ─ phone, voice, intake questions    │
                    │   ─ post-call analysis schema         │
                    └────────────────┬───────────────────────┘
                                     │
                                     ▼
         ┌──────────────────────────────────────────────────────┐
         │  deploy_retell_agent.py                              │
         │  1. Render global_prompt_template.md (Jinja)         │
         │  2. Build conversation flow nodes from               │
         │     intake_flow_template.yml                         │
         │  3. POST /create-conversation-flow → flow_id         │
         │  4. POST /create-agent → agent_id                    │
         │  5. PATCH /update-phone-number/<phone>               │
         │  6. Write deployment artifact                        │
         └────────────────┬─────────────────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  Retell platform        │
              │  ┌────────────────┐    │
              │  │ Agent          │    │
              │  │ Conv flow      │    │
              │  │ Phone binding  │◀───┼──── Callers dial in
              │  │ Post-call data │    │
              │  └────────────────┘    │
              └────────────┬───────────┘
                           │ (after each call)
                           ▼
            ┌──────────────────────────────┐
            │  book_pending_consults.py    │
            │  1. List recent calls        │
            │  2. Parse Preferred Day/Time │
            │  3. Write booking intent     │
            │     to outputs/bookings/     │
            └──────────────┬───────────────┘
                           ▼
            ┌──────────────────────────────┐
            │  voice-deployer agent        │
            │  Reads booking intents       │
            │  Calls google-workspace MCP  │
            │  manage_event → Calendar     │
            └──────────────────────────────┘
```

## Directory Layout

```
VOICE_TEAM/
├── memory/
│   ├── voice_config.json       Factory-wide defaults (Retell API, models, voice, compliance)
│   ├── output_paths.json       Canonical output routing
│   ├── firm_template.yml       The schema all firm.yml files follow
│   └── firms/
│       └── sterling_legal.yml  Demo firm config (Personal Injury, NC)
├── prompts/
│   ├── global_prompt_template.md   Jinja template for the agent's system prompt
│   └── intake_flow_template.yml    Declarative node graph for conversation flow
├── kb/
│   └── sterling_legal/         Demo firm's knowledge base (about, faq, practice areas)
├── tools/
│   ├── deploy_retell_agent.py  THE FACTORY — deploys a firm config to Retell
│   ├── book_pending_consults.py  Post-call booking intent writer
│   └── web_call_demo.html      Browser-based voice call backup demo
├── outputs/
│   ├── deployments/            One JSON per deployed firm (agent_id, flow_id, phone)
│   ├── call_logs/              Cached call logs pulled from Retell
│   ├── summaries/              Post-call analysis snapshots
│   └── bookings/               Booking intent files (consumed by voice-deployer)
└── .claude/
    ├── agents/
    │   ├── voice-onboarder.md  Interviews → firm.yml + KB docs
    │   └── voice-deployer.md   Deploys firms + processes booking intents
    └── commands/
        ├── new-voice-firm.md     Slash command for onboarder
        └── deploy-voice-firm.md  Slash command for deployer
```

## The Demo Firm — Sterling Legal Services

- **Practice:** Personal Injury (North Carolina)
- **Phone:** +1 (336) 323-8344
- **Voice:** ElevenLabs Adrian (professional female)
- **Hours:** Mon–Fri 9am–6pm ET
- **AI receptionist:** 24/7 intake with AI disclosure, recording disclosure, escalation rules

Call the number to hear the agent live.

## Day 1 Gotchas (Lessons Learned)

These tripped us up during the initial build — documenting so the next firm onboarding doesn't:

### 1. Retell API schema is stricter than docs imply

The `/create-conversation-flow` endpoint requires:
- `start_speaker` at the flow body root (not just per-node)
- `model_choice` object with `type: "cascading" | "openai-realtime"`, `model`, `high_priority`
- `start_node_id` pointing at the first node's id
- `tool_call_strict_mode: true` (optional but recommended)

The `tools[]` array uses `oneOf` schema with specific shapes per tool type (custom, cal_com, end_call, etc.) — get the shape wrong and the error message is misleading.

### 2. Windows cp1252 stdout chokes on Unicode

If a Python script prints Unicode (checkmarks, em-dashes, smart quotes), it crashes on Windows with `UnicodeEncodeError`. Add at the top of every script:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
```

### 3. ElevenLabs API key is NOT bring-your-own in Retell

Retell uses managed ElevenLabs — you cannot pass your own ElevenLabs API key. Voice selection happens in the Retell dashboard's voice library, not via your ElevenLabs account.

### 4. GPT Realtime requires different `model_choice.type`

The cascading deploy works out of the box. To upgrade to Realtime (lower latency, ~320ms vs ~500ms), the schema needs `model_choice.type: "openai-realtime"` plus likely additional fields. Investigate in v2.

### 5. Post-call analysis > custom functions for slot capture

For Day 1, the agent doesn't need a custom function to "book the slot mid-call." Instead, define structured `post_call_analysis_data` fields (Preferred Callback Day, Time, Urgency) — Retell extracts them from the transcript automatically after the call ends, and `book_pending_consults.py` does the actual calendar booking. Simpler architecture, no public endpoint needed.

### 6. Phone number attach uses PATCH, not POST

To bind a number to an agent: `PATCH /update-phone-number/<phone>` with `{"inbound_agent_id": "<agent_id>"}`. Common mistake: trying POST or PUT.

## Cost Model

Per-call cost with current Sterling Legal config (cascading GPT-4.1 + ElevenLabs voice + Retell telephony):
- LLM: ~$0.05/min
- TTS (ElevenLabs): ~$0.04/min
- Telephony: ~$0.015/min
- Retell platform: ~$0.055/min
- **Total: ~$0.16/min**

Premium tier (GPT Realtime + Fast Tier, v2 upgrade): ~$0.40/min — buys you sub-400ms latency.

## Pricing (Charged To Law Firms)

Flat-rate tiers (NOT per-minute, lawyers hate variable bills):

- **Starter — $497/mo** — 500 included min, $1/min overage. For solo / small firms.
- **Growth — $997/mo** — 1,500 included min, $0.75/min overage. **Sweet spot for mid-market PI firms.**
- **Pro — $1,997/mo** — 4,000 included min, $0.50/min overage. For high-volume practices.
- **Setup fee — $1,500–$3,000 one-time per firm.** Covers onboarding, voice tuning, KB ingestion, training.

Gross margin at Growth tier: ~76%. At 20 firms across the mix: ~$15k–$25k/mo MRR.

## Adding A New Firm

```bash
# Step 1: Buy a new phone number in Retell dashboard for the firm
# Step 2: Run /new-voice-firm and answer interview questions
# Step 3: Run /deploy-voice-firm <new-slug>
# Step 4: Test by calling the number
# Step 5: Hand off to client
```

A complete new-firm cycle should take 30–45 minutes including the onboarding interview.

## Compliance Defaults (Per voice_config.json)

- **AI disclosure:** ON (agent announces "I'm the AI assistant" in opening)
- **Recording disclosure:** ON (agent mentions calls may be recorded)
- **PII redaction:** Post-call (transcripts redact SSN, DOB, addresses)
- **Data retention:** 90 days default (configurable per firm in firm.yml)
- **Scope boundaries:** ON (agent refuses to give legal advice)

For HIPAA / SOC 2 / GDPR specifics, see Retell's compliance page. Sterling Legal (and all VOICE_TEAM-deployed agents) inherits Retell's certifications.

## What's NOT Yet Built

- ❌ White-label client dashboard (Next.js, planned v2)
- ❌ Real-time mid-call calendar booking (custom function with public endpoint, planned v2)
- ❌ GPT Realtime 1.5 deployment path (schema work needed, planned v2)
- ❌ Outbound calling / batch campaigns
- ❌ SMS reminders (Retell SMS agents, planned v3)
- ❌ Multi-language voice cloning per firm
- ❌ TCPA / DNC scrubbing service integration
- ❌ Automated billing per-firm

## Maintainer Notes

- The factory was built 2026-05-27 against Retell API ~v2025-Q4 schema. If endpoints change, smoke-test with `tools/` scripts before bulk-redeploying.
- The Codex-reviewed plan that drove this build lives at `~/.claude/plans/wobbly-plotting-thunder.md`.
- The phone number `+13363238344` is currently bound to `agent_046ea303e87fa84eb156c48ff4` (Sterling Legal demo).

## Demo To Steven Checklist

- [ ] Place 3 test calls from your phone, ideally with different scenarios (car accident, slip & fall, dog bite)
- [ ] Verify all 3 land in Retell dashboard with populated `post_call_analysis_data`
- [ ] Run `python tools/book_pending_consults.py --firm sterling_legal` and check `outputs/bookings/`
- [ ] Record a 3-minute Loom: dial the number, walk through dashboard, show the booking intent file
- [ ] Build a second firm (`/new-voice-firm` for a fictional dentist or family lawyer) to prove the factory ships firm #2 in <1 hour
- [ ] Pitch frame: "We deploy a custom AI receptionist for your firm in under 60 minutes. Here's what it sounds like. Here's how leads come in. Here's how we add your firm next week."
