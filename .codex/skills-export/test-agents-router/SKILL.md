---
name: test-agents-router
description: Select the right TEST_AGENTS specialist and load its Codex sidecar instructions.
---

# TEST_AGENTS Router

Use this skill when the user asks for work in TEST_AGENTS but does not name a specific agent.

## Routing Process

1. Read `.codex/manifest.json`.
2. Match the user's request against each agent's `team`, `slug`, `display_name`, `capabilities`, `skills`, and `tools`.
3. Choose the narrowest specialist that can complete the task.
4. Load that agent's `codex_instructions` file before doing the work.
5. Read the team's memory/config files referenced by that agent.
6. Save deliverables in the selected team's `outputs/` folder.

Do not read `.claude/agents/` directly unless the sidecar is missing or stale. If stale, run `$codex-sync-secrets` first.

## Fast Routing Map

- Broad marketing campaign, unclear marketing request: `MARKETING_TEAM/router-agent`
- Blog, article, web copy, internal comms: `MARKETING_TEAM/copywriter`
- Editorial calendar or content plan: `MARKETING_TEAM/content-strategist`
- Social posts or platform content: `MARKETING_TEAM/social-media-manager`
- Images, graphics, visual prompts: `MARKETING_TEAM/visual-designer`
- Video, Sora, Veo, UGC ads: `MARKETING_TEAM/video-producer`
- Email campaigns/newsletters: `MARKETING_TEAM/email-specialist` or `MARKETING_TEAM/newsletter-agent`
- Gmail/search/send/read email: `MARKETING_TEAM/gmail-agent`
- SEO/keywords/rank research: `MARKETING_TEAM/seo-specialist`
- Market research or competitive intel: `MARKETING_TEAM/research-agent`
- Lead generation/prospecting: `MARKETING_TEAM/lead-gen-agent`
- Landing pages: `MARKETING_TEAM/landing-page-specialist`
- Presentations: `MARKETING_TEAM/presentation-designer`
- PDFs: `MARKETING_TEAM/pdf-specialist`
- n8n/workflow automation: `MARKETING_TEAM/automation-agent`
- Broad engineering or architecture: `ENGINEERING_TEAM/cto`
- Frontend/UI implementation: `ENGINEERING_TEAM/frontend-developer`
- Backend/API/database systems: `ENGINEERING_TEAM/backend-architect` or `ENGINEERING_TEAM/database-architect`
- Security review: `ENGINEERING_TEAM/security-auditor`
- Debugging/root cause: `ENGINEERING_TEAM/debugger`
- Code review: `ENGINEERING_TEAM/code-reviewer`
- Tests/QA automation: `ENGINEERING_TEAM/test-engineer` or `QA_TEAM/test-orchestrator`
- Unit tests: `QA_TEAM/unit-test-agent`
- Integration/API tests: `QA_TEAM/integration-test-agent`
- Edge cases: `QA_TEAM/edge-case-agent`
- Fixtures/mock data: `QA_TEAM/fixture-agent`
- RFP/proposal automation: `PROPOSAL_TEAM/rfp-agent`
- Finance strategy: `FINANCIAL_TEAM/cfo-agent`
- Deal/M&A analysis: `FINANCIAL_TEAM/deal-analyst`
- Valuation/DCF: `FINANCIAL_TEAM/valuation-agent`
- Forecasting/FP&A: `FINANCIAL_TEAM/forecasting-agent` or `FINANCIAL_TEAM/fpna-agent`
- Accounting/controller/tax/treasury: matching FINANCIAL_TEAM specialist
- Broad sales workflow: `SALES_TEAM/sales-manager`
- SDR/outbound prospecting: `SALES_TEAM/sdr-agent` or `SALES_TEAM/outbound-specialist`
- Account execution/deal management: `SALES_TEAM/account-executive`
- CRM/pipeline ops: `SALES_TEAM/sales-operations`
- Sales metrics: `SALES_TEAM/sales-analyst`
- Sales proposals/pricing: `SALES_TEAM/proposal-specialist`
- Customer success/retention: `SALES_TEAM/customer-success-manager`
- PE investor outreach: `SALES_TEAM/pe-outreach-agent`
- Cross-team QA/verification: `ROOT/supervisor`
- Personal wiki/second brain: `ROOT/oracle`

## Tie Breakers

If the task is broad, use the team's orchestrator. If the task names a concrete artifact or workflow, use the specialist. If the request needs multiple teams, start with the orchestrator for the user's primary outcome and mention secondary agents as needed.

