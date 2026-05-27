# New Voice Firm — Onboarding

Onboard a new law firm into the VOICE_TEAM factory by generating a complete firm.yml + KB docs.

## What This Does

Invokes the `voice-onboarder` agent to:
1. Conduct a structured discovery interview (firm name, practice area, phone number, voice preference, intake questions, calendar config, etc.)
2. Generate the firm-specific `firm.yml` at `VOICE_TEAM/memory/firms/<slug>.yml`
3. Generate the firm's KB docs (about, faq, practice areas)
4. Hand off to `/deploy-voice-firm <slug>` for deployment

## Usage

```
/new-voice-firm
```

The agent will then ask you a sequence of questions. Answer them conversationally. The agent will fill in sensible defaults for fields you don't have strong opinions on.

## Optional: Provide Discovery Notes Upfront

If you've already had a discovery call with the firm and have notes, paste them after the slash command:

```
/new-voice-firm

Discovery call notes from 2026-05-30:
- Firm: Apex Personal Injury Lawyers
- Location: Houston, TX
- Practice: PI only (no other areas)
- ...
```

The agent will extract what it can from your notes and only ask follow-up questions for gaps.

## Prerequisites

Before running:
- A new phone number MUST be purchased in Retell for this firm (or the firm provides their own number via SIP)
- A Google Calendar (their primary or a dedicated one) MUST be accessible via the `google-workspace` MCP

## Output

When complete, the onboarder writes:
- `VOICE_TEAM/memory/firms/<slug>.yml` — deploy-ready firm config
- `VOICE_TEAM/kb/<slug>/about.md` — firm bio
- `VOICE_TEAM/kb/<slug>/faq.md` — common Qs
- `VOICE_TEAM/kb/<slug>/practice_areas.md` — what they handle

Then it tells you: "Run `/deploy-voice-firm <slug>` to deploy."
