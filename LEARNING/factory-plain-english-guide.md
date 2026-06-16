# Your Software Factory, in Plain English

*A Feynman-style guide to what you built on June 13, 2026, and every tool you used.*

---

## The whole thing in one breath

You built a **factory that makes custom software**. The secret is what you did not standardize. Every client's app is different, so you cannot standardize the product. Instead you standardized the **process** and the **starting kit**. Like a kitchen that cooks a different dish every night but never changes its stations: prep, cook, plate, check, serve. You proved the kitchen works by cooking one real meal (FleetCRM) and serving it live at https://fleetcrm-staging.onrender.com.

---

## Part 1: What a web app actually is (the scaffold)

Forget code for a second. Every web app is six parts. Hold these in your head and everything else hangs off them:

1. **The face** - what the user sees and clicks (pages, buttons, forms).
2. **The rules** - what happens when they click ("save this", "only admins can delete").
3. **The memory** - where the records live, permanently.
4. **The bouncer** - who is allowed in, and what each person may do.
5. **The building** - the computer on the internet that runs it all, 24/7.
6. **The alarm** - the thing that tells you when something breaks at 2am.

A CRM, a dashboard, a booking site: all just different arrangements of those six parts.

---

## Part 2: The tools, each in its slot

**The face + the rules -> Next.js.**
The building material for both what the user sees and the logic behind the buttons, in one kit. Instead of gluing a separate front end and back end together, Next.js does both in one language: faster to build, easier for agents to get right. Analogy: a pre-fab home kit with the walls and the wiring included.

**The language -> TypeScript.**
JavaScript (the language web apps speak) with a built-in spell-checker that catches mistakes before they ship. The difference between finding a typo while writing versus your customer finding it live. The "typecheck" gate is that spell-checker.

**The memory -> PostgreSQL, spoken to through Prisma.**
PostgreSQL is the actual filing cabinet where records live forever. Prisma is the translator between your code and that cabinet, so agents write a clean sentence ("create this company") instead of raw database commands. Postgres is boring, proven, and runs anywhere (no lock-in); Prisma makes the database one readable file agents can edit safely. The "migration" on deploy was Prisma building the cabinet's drawers from that file.

**The bouncer -> Clerk.**
Handles login, identity, passwords, and roles, so you never build that yourself. This matters most because login is where security bugs hide and where weeks of work disappear. Renting Clerk gives you professional-grade locks for free. Analogy: hire a bonded security company instead of whittling your own locks.

**The building -> Render.**
The computer on the internet that runs your app around the clock, and hosts the Postgres cabinet. You already had experience with it, and a known boring host beats a fancy unknown one. This is the only part that costs real money, and it is the client's bill, not yours.

**The alarm -> Sentry + Resend.**
Sentry is the black-box flight recorder: when something breaks it captures what and why. Resend is the messenger that emails you "go look." Sentry answers "what happened" for debugging; Resend answers "you need to know now." Together: the difference between a client telling you they are down versus you knowing first.

**The save-history and vault -> git + GitHub.**
git records every change so you can rewind; GitHub is the shared online vault where the code lives and syncs between your machines. The undo button for an entire codebase.

**The inspector -> GitHub Actions.**
The robot that automatically checks every change (spell-checker, tests, secret-scan) before it can ship. A gate that never gets tired or skips a step. "CI/CD" is just the name for this inspector plus the auto-delivery belt behind it.

**The smaller specialists (each fills a corner):**
- **Zod** - the form-checker at the door; rejects bad data ("not a valid email") before it reaches the memory.
- **Tailwind + shadcn** - the paint and the pre-made furniture; how the app looks without designing every button.
- **TanStack Table** - the sortable, paged spreadsheet widget for lists of records.
- **Vitest + Playwright** - the test crew. Vitest checks the small pieces; Playwright clicks through the app like a fake user. "85 tests passed" was this crew signing off.

> The pattern: for every slot you rented the boring, proven specialist (Clerk for locks, Render for hosting, Sentry for alarms) and only hand-built the part that is the client's unique value (their rules and their data). That is the whole philosophy in one line: **assemble proven parts, build only what is unique.** It is why a client app is a 3-day job instead of 4 months.

---

## Part 3: The factory layer (the tools above the app)

Everything in Part 2 builds the app. These are how you operated the kitchen itself; they do not ship to the client, they are your means of production:

- **The agents + workflows** - the workers and the assembly-line choreography. One agent is one worker; a workflow is the conveyor belt that runs many workers in parallel and checks their output. The "3-lens review" that caught your security bugs was a workflow running three independent inspectors.
- **The guardrails (hooks)** - the safety interlocks bolted to the machinery. They physically stopped the deploy and the delete until you approved. The part most people fake and you actually built.
- **The memory files** - the factory's notebook that survives between sessions, so the plan and the deploy state do not evaporate when you close the laptop.
- **MCP servers (Render MCP, Chrome MCP)** - the hands. An MCP is a socket that lets an agent reach into a real system. Render MCP created your database and services; Chrome MCP read your dashboard through your real browser. Without these an agent can only write code; with them it can operate the world.
- **The template + the runbook** - the mold and the instruction sheet, the two things the whole build existed to produce.

---

## Part 4: Three clever tricks worth understanding

1. **The fake-placeholder trick.** We built and tested the entire app before you had a single real account, by feeding it harmless fake keys (a fake database address, a fake login key) that let the code compile but connect to nothing. Real keys slot in only at deploy. It let the whole thing be verified green on day one with zero secrets: your "build everything, set credentials last" instinct made real.

2. **Just-in-time provisioning.** Instead of a fragile separate system to copy users into your database, the app creates your record the first time you log in, and crowns the very first user as admin. We switched to it because it removed a manual setup step that needed a Clerk dashboard login, and it is sturdier (it cannot get out of sync). That is the change that unblocked your sign-up.

3. **Migrate-on-build.** The app builds its own database drawers automatically the first time it deploys. It means "stamp a new repo, push, done": the database sets itself up. That is what makes the next client genuinely a 3-day job.

---

## The three repos (so you never get them confused)

| Repo | What it is | Analogy |
|------|-----------|---------|
| **dux-factory** | The paperwork: runbook, spec templates, checklists, pricing, deploy lessons. No app code. | The recipe book + operating manual |
| **dux-template-webapp** | The reusable starter code. You stamp a fresh copy of this per client. | The cake mold |
| **fleetcrm** | The test app we built and deployed live to prove the mold works. | The test cake |

A real client never touches these three. You run one command that stamps a brand-new 4th repo from the template, and build their app there. Each client gets their own repo; the template stays pristine.

Stamp command:
```
gh repo create Azeez1/client-NAME --template Azeez1/dux-template-webapp --private --clone
```

---

## One-line summary

Six slots, a proven tool in each, a factory layer above it, and three tricks that let it all be built before a single credential existed. The machine is built and proven live. The next milestone is not more tools. It is a paying client.
