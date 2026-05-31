# TEST_AGENTS Codex Layer

This directory is generated from Claude-first sources plus Codex-native sources without modifying `.claude/`.

- Claude mirrors come from team `.claude/agents/` files.
- Codex-native agents come from `CODEX_TEAM/.codex/agents/`.

## Runtime Rules

- Load agent instructions from `.codex/agents/<team>/<agent>.md`.
- Load exported skills from `.codex/skills-export/<skill>/SKILL.md` when no native Codex skill exists.
- Use Codex-native tools/connectors first when available.
- Do not assume Claude MCP tools are callable from Codex.
- Do not write secrets into generated files. Use `.codex/secrets.local.env` locally.

## Local Slash Commands

- `/codex-sync`: refresh Codex agents, skills, manifest, and docs from Claude and Codex-native sources.
- `/codex-sync-secrets`: refresh Codex agents/skills and update local Codex env values from `.mcp.json`.
- `$codex-sync-mcps`: generate local Codex MCP config from Claude `.mcp.json`.
- `$codex-sync-all`: refresh agents, skills, secrets, and MCP config.

## Agent Index

### CODEX_TEAM
- `codex-agent-editor`: `.codex/agents/CODEX_TEAM/codex-agent-editor.md`
- `codex-layer-architect`: `.codex/agents/CODEX_TEAM/codex-layer-architect.md`
- `codex-leverage-auditor`: `.codex/agents/CODEX_TEAM/codex-leverage-auditor.md`
- `codex-mcp-hooks-engineer`: `.codex/agents/CODEX_TEAM/codex-mcp-hooks-engineer.md`
- `codex-skill-engineer`: `.codex/agents/CODEX_TEAM/codex-skill-engineer.md`
- `codex-team-manager`: `.codex/agents/CODEX_TEAM/codex-team-manager.md`

### ENGINEERING_TEAM
- `ai-engineer`: `.codex/agents/ENGINEERING_TEAM/ai-engineer.md`
- `analytics-dashboard-agent`: `.codex/agents/ENGINEERING_TEAM/analytics-dashboard-agent.md`
- `backend-architect`: `.codex/agents/ENGINEERING_TEAM/backend-architect.md`
- `code-reviewer`: `.codex/agents/ENGINEERING_TEAM/code-reviewer.md`
- `cto`: `.codex/agents/ENGINEERING_TEAM/cto.md`
- `database-architect`: `.codex/agents/ENGINEERING_TEAM/database-architect.md`
- `debugger`: `.codex/agents/ENGINEERING_TEAM/debugger.md`
- `devops-engineer`: `.codex/agents/ENGINEERING_TEAM/devops-engineer.md`
- `frontend-developer`: `.codex/agents/ENGINEERING_TEAM/frontend-developer.md`
- `prompt-engineer`: `.codex/agents/ENGINEERING_TEAM/prompt-engineer.md`
- `security-auditor`: `.codex/agents/ENGINEERING_TEAM/security-auditor.md`
- `system-architect`: `.codex/agents/ENGINEERING_TEAM/system-architect.md`
- `technical-writer`: `.codex/agents/ENGINEERING_TEAM/technical-writer.md`
- `test-engineer`: `.codex/agents/ENGINEERING_TEAM/test-engineer.md`
- `ui-ux-designer`: `.codex/agents/ENGINEERING_TEAM/ui-ux-designer.md`

### FINANCIAL_TEAM
- `accountant`: `.codex/agents/FINANCIAL_TEAM/accountant.md`
- `cfo-agent`: `.codex/agents/FINANCIAL_TEAM/cfo-agent.md`
- `controller`: `.codex/agents/FINANCIAL_TEAM/controller.md`
- `deal-analyst`: `.codex/agents/FINANCIAL_TEAM/deal-analyst.md`
- `financial-analyst`: `.codex/agents/FINANCIAL_TEAM/financial-analyst.md`
- `financial-data-analyst`: `.codex/agents/FINANCIAL_TEAM/financial-data-analyst.md`
- `forecasting-agent`: `.codex/agents/FINANCIAL_TEAM/forecasting-agent.md`
- `fpna-agent`: `.codex/agents/FINANCIAL_TEAM/fpna-agent.md`
- `investor-relations-agent`: `.codex/agents/FINANCIAL_TEAM/investor-relations-agent.md`
- `portfolio-manager`: `.codex/agents/FINANCIAL_TEAM/portfolio-manager.md`
- `tax-advisor`: `.codex/agents/FINANCIAL_TEAM/tax-advisor.md`
- `trading-optimizer`: `.codex/agents/FINANCIAL_TEAM/trading-optimizer.md`
- `treasury-agent`: `.codex/agents/FINANCIAL_TEAM/treasury-agent.md`
- `valuation-agent`: `.codex/agents/FINANCIAL_TEAM/valuation-agent.md`

### MARKETING_TEAM
- `analyst`: `.codex/agents/MARKETING_TEAM/analyst.md`
- `automation-agent`: `.codex/agents/MARKETING_TEAM/automation-agent.md`
- `content-strategist`: `.codex/agents/MARKETING_TEAM/content-strategist.md`
- `copywriter`: `.codex/agents/MARKETING_TEAM/copywriter.md`
- `editor`: `.codex/agents/MARKETING_TEAM/editor.md`
- `email-specialist`: `.codex/agents/MARKETING_TEAM/email-specialist.md`
- `gmail-agent`: `.codex/agents/MARKETING_TEAM/gmail-agent.md`
- `landing-page-specialist`: `.codex/agents/MARKETING_TEAM/landing-page-specialist.md`
- `lead-gen-agent`: `.codex/agents/MARKETING_TEAM/lead-gen-agent.md`
- `newsletter-agent`: `.codex/agents/MARKETING_TEAM/newsletter-agent.md`
- `pdf-specialist`: `.codex/agents/MARKETING_TEAM/pdf-specialist.md`
- `presentation-designer`: `.codex/agents/MARKETING_TEAM/presentation-designer.md`
- `research-agent`: `.codex/agents/MARKETING_TEAM/research-agent.md`
- `router-agent`: `.codex/agents/MARKETING_TEAM/router-agent.md`
- `seo-specialist`: `.codex/agents/MARKETING_TEAM/seo-specialist.md`
- `social-media-manager`: `.codex/agents/MARKETING_TEAM/social-media-manager.md`
- `video-producer`: `.codex/agents/MARKETING_TEAM/video-producer.md`
- `visual-designer`: `.codex/agents/MARKETING_TEAM/visual-designer.md`

### PROPOSAL_TEAM
- `rfp-agent`: `.codex/agents/PROPOSAL_TEAM/rfp-agent.md`

### QA_TEAM
- `edge-case-agent`: `.codex/agents/QA_TEAM/edge-case-agent.md`
- `fixture-agent`: `.codex/agents/QA_TEAM/fixture-agent.md`
- `integration-test-agent`: `.codex/agents/QA_TEAM/integration-test-agent.md`
- `test-orchestrator`: `.codex/agents/QA_TEAM/test-orchestrator.md`
- `unit-test-agent`: `.codex/agents/QA_TEAM/unit-test-agent.md`

### ROOT
- `linkedin-brand-reviewer`: `.codex/agents/ROOT/linkedin-brand-reviewer.md`
- `oracle`: `.codex/agents/ROOT/oracle.md`
- `pe-diagnosis-validator`: `.codex/agents/ROOT/pe-diagnosis-validator.md`
- `pe-diagnosis-visual-reviewer`: `.codex/agents/ROOT/pe-diagnosis-visual-reviewer.md`
- `supervisor`: `.codex/agents/ROOT/supervisor.md`

### SALES_TEAM
- `account-executive`: `.codex/agents/SALES_TEAM/account-executive.md`
- `customer-success-manager`: `.codex/agents/SALES_TEAM/customer-success-manager.md`
- `outbound-specialist`: `.codex/agents/SALES_TEAM/outbound-specialist.md`
- `pe-outreach-agent`: `.codex/agents/SALES_TEAM/pe-outreach-agent.md`
- `proposal-specialist`: `.codex/agents/SALES_TEAM/proposal-specialist.md`
- `sales-analyst`: `.codex/agents/SALES_TEAM/sales-analyst.md`
- `sales-manager`: `.codex/agents/SALES_TEAM/sales-manager.md`
- `sales-operations`: `.codex/agents/SALES_TEAM/sales-operations.md`
- `sdr-agent`: `.codex/agents/SALES_TEAM/sdr-agent.md`
