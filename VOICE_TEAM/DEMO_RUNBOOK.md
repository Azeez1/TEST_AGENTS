# Steven Demo Runbook

The complete step-by-step playbook for the Sterling Legal Services voice agent demo. Follow in order. Total demo runtime: ~12–15 minutes.

## Before The Demo (One-Time Prep)

- [ ] Confirm phone `+13363238344` is bound to the latest agent (run `python tools/deploy_retell_agent_s2s.py memory/firms/sterling_legal.yml` once if you've made changes)
- [ ] Confirm Retell account has $20+ credit
- [ ] Have these 4 tabs/windows open and ready:
  1. **Retell dashboard** → https://dashboard.retellai.com/agents/agent_217a2928ec8d2c9b383a218a31
  2. **Google Calendar** (today's view, near 5pm ET — to show the booking)
  3. **Gmail inbox** (to show the email summary)
  4. **Your terminal** in the VOICE_TEAM directory (for showing the factory deploy command)
- [ ] Record a 3-min Loom that includes everything below (optional — if Steven is asking for a recording instead of live demo)

---

## Part 1 — The Setup (1 min)

**What you say:**
> "Steven, you told me your clients are bleeding after-hours leads. Most miss 60–70% of calls outside business hours. I built a voice AI receptionist factory that captures those leads 24/7. Let me show you what your client would actually deploy."

**What you show:** Just talk — no screen share yet.

---

## Part 2 — Live Call (3 min)

**What you say:**
> "I'm going to dial Sterling Legal's number right now. Sterling is the demo firm I built first — Personal Injury, North Carolina. Listen for: the AI disclosure in the opening, how it handles intake questions, and notice the response speed."

**What you do:** 
- Put your phone on speaker
- Dial **+1 (336) 323-8344**
- Walk through this script as the "caller":
  > "Hi, I was rear-ended at a red light yesterday on Route 40. The other driver was on their phone. I went to the ER last night for whiplash and back pain. My name is Azeez Saba, that's A-Z-E-E-Z S-A-B-A. Best number to reach me is 301-448-9941. Can someone call me tomorrow afternoon, like 2pm?"

**What to listen for during the call (point these out to Steven as they happen):**
- Opening: "I'm the AI assistant — your call may be recorded" (compliance built in)
- Sub-400ms response latency (sounds like a real receptionist)
- Asks about injuries, fault, police report, insurance (qualifying questions)
- Spells your name back letter-by-letter (accuracy)
- Confirms phone number digit-by-digit (accuracy)
- Confirms callback time before ending

---

## Part 3 — The Retell Dashboard (2 min)

**What you say:**
> "Every call is captured with full transcript + structured intake data. This is what your client's intake queue looks like in real-time."

**What you show (screen share Retell dashboard):**
1. Click **Calls** in the sidebar
2. Click on the call you just made
3. Point to:
   - **Transcript** (right side) — agent + caller turns
   - **Post-call analysis** (structured fields): Caller Full Name, Callback Phone Number, Incident Type, Currently Injured, Fault Assessment, Police Report Filed, Insurance Contact, Preferred Callback Day/Time, Urgency Level, Case Quality
   - **Latency metrics** — show p50 / p95 numbers
   - **Recording** — play 5 seconds to demo audio quality

---

## Part 4 — The Calendar + Email Automation (2 min)

**What you say:**
> "Capturing the data is half the job. The other half is making sure your attorney never misses the callback. Watch what happens automatically after the call ends."

**What you do:**
1. **In terminal**, run:
   ```
   python tools/book_pending_consults.py --firm sterling_legal --since-hours 1
   ```
   Show the output: "Found 1 call... booking intent → outputs/bookings/...json, email intent → outputs/emails/...json"

2. **In the Claude Code window**, type:
   > "Process the pending intents from VOICE_TEAM/outputs/bookings/ and VOICE_TEAM/outputs/emails/ — create the calendar events and send the email summaries via the google-workspace MCP."

   Claude will process them in front of Steven.

3. **Switch to Google Calendar** — show the consultation event with full intake details in the description.

4. **Switch to Gmail** — show the formatted email summary that just landed.

---

## Part 5 — The Factory Reveal (3 min)

**This is the close.**

**What you say:**
> "Everything I just showed you is for ONE firm. But the real product isn't this one agent — it's the system that builds these agents. Watch."

**What you do:**
1. **In your editor**, show `VOICE_TEAM/memory/firms/sterling_legal.yml`. Scroll through it. Point out: name, practice area, phone number, intake questions, post-call analysis schema. Say:
   > "This is the entire config for Sterling Legal. About 100 lines of YAML. Everything that makes this agent unique is in this file."

2. Copy the file and rename it. In terminal:
   ```
   copy memory\firms\sterling_legal.yml memory\firms\demo_firm_2.yml
   ```

3. Open `demo_firm_2.yml` and change 4-5 lines in front of Steven:
   - `slug:` → `"demo_firm_2"`
   - `name:` → "Apex Family Law" (or any other firm name)
   - `practice_area:` → `"family"`
   - `practice_area_display:` → "Family Law"
   - `phone_number:` → (skip this for demo — you'd buy a new Retell number for real)

4. **Pause and say:**
   > "That's it. That's the entire customization for a new client. Let me deploy this."

5. **In terminal:** `python tools/deploy_retell_agent_s2s.py memory/firms/demo_firm_2.yml`

6. Wait ~30 seconds. Show the output:
   - "✓ LLM created"
   - "✓ Agent created"
   - "DEPLOY COMPLETE"

7. **Say:**
   > "New voice agent, deployed and ready, in 30 seconds. Your client has 50 firms? I can onboard the entire book in a week. Most agencies do this manually in the Retell dashboard — 2–4 hours per firm. I do it in 60 seconds because everything I just showed you is one YAML config and one Python command."

---

## Part 6 — Pricing & Close (3 min)

**What you say:**
> "Three tiers, no per-minute billing — lawyers hate variable invoices."

**Show this table on screen (have it in a Google Doc or just say it):**

| Tier | Monthly | Included min | Best for |
|---|---|---|---|
| Starter | $497 | 500 min | Solo / 2-attorney shops |
| Growth | $997 | 1,500 min | Mid-market PI firms |
| Pro | $1,997 | 4,000 min | High-volume practices |

Plus a **$1,500–$3,000 one-time setup fee** per firm (covers onboarding interview + custom voice + KB ingestion + 5 test scenarios).

**The math:**
- Your cost at Growth tier: ~$240/mo
- Gross margin: ~76%
- 20 firms in the mix: ~$15–25k/mo MRR

**The close:**
> "Steven — what would it take for us to onboard your first client this week? I need three things from you: (1) a target firm, (2) intro to their decision maker, (3) sign-off on a revenue split or referral fee structure between us. The deploy is already done — we just need the green light."

---

## If Something Breaks Mid-Demo

| Failure | Backup plan |
|---|---|
| Agent doesn't answer the call | Use the **web call demo** at `VOICE_TEAM/tools/web_call_demo.html` — open in browser, click "Start Call" |
| Booking script fails | Skip it — point at the Retell dashboard's post-call analysis fields and say "this data flows into the calendar via API" |
| Email doesn't send | Show the email intent JSON file in `outputs/emails/` and say "the email payload is generated; production deploys this to SendGrid or Postmark" |
| Live deploy fails | Pre-record the deploy command output and screen-share that |
| Audio quality is bad on phone | Switch to web call demo for the rest of the demo |

---

## Post-Demo Follow-Up (Within 24h)

Send Steven this email template:

> Subject: Sterling Legal demo recap + next steps
>
> Steven,
>
> Quick recap of what we covered:
> - Live voice agent: +1 (336) 323-8344 (try it again any time)
> - Factory model: ~30 seconds from firm.yml to deployed agent
> - Pricing tiers: $497 / $997 / $1,997 monthly + setup fee
> - Capacity: I can onboard a new firm end-to-end in under an hour
>
> Three next steps if we're moving forward:
> 1. Name the target firm + decision maker
> 2. Lock our revenue split or referral structure
> 3. I'll have their custom agent deployed within 48 hours of go-ahead
>
> Let me know.
>
> Azeez

---

## Common Steven Questions + Answers

**Q: "How is this different from Smith.ai or Ruby Receptionists?"**
A: They use human agents and charge per-call. We use AI, 24/7 availability, sub-400ms response, structured intake schema custom-built per firm, and integrate directly into the firm's existing CRM/calendar. Half the price, twice the capability.

**Q: "What about compliance? Lawyers are paranoid about this."**
A: Retell is SOC 2 Type II + HIPAA + GDPR. AI disclosure is in every call opening. PII redaction is on. Recording disclosure is built into the script. State bar-compliant.

**Q: "What if it makes a mistake mid-call?"**
A: Hard rules baked into the prompt: never give legal advice, never quote fees, never promise outcomes. State machine architecture prevents looping. We test 5 standard scenarios before every firm goes live.

**Q: "Can the firm's existing receptionist still take calls during business hours?"**
A: Yes. Multiple agents can be assigned to one number with weighted routing. Human-first during business hours, AI fallback for overflow + after-hours.

**Q: "What's your cut per firm?"**
A: (Your call — depends on what you and Steven negotiate. Stay flexible here.)

**Q: "Can we white-label this?"**
A: Currently Retell shows in the dashboard URL. Production white-label dashboard is on the roadmap — clients only see your brand. ~$5k–$10k engineering cost to build. Build it once they're paying.

---

## Demo Success Criteria

You nail the demo if Steven says any of these:
- "How fast can we onboard my first client?"
- "What's the revenue split look like?"
- "Send me a one-pager I can show them."
- "Can I see another practice area, like family law?"
- "Let's get on a call with my client this week."

If he says "interesting, let me think about it" — that's a soft pass. Follow up in 48h with a specific next step (named target firm).
