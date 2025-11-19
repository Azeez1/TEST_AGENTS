# Agent Suggest

Intelligent agent recommendation system to find the best agent(s) for your task.

## What This Does

Analyzes your task description and recommends:
1. Most appropriate agent(s) to use
2. Relevant slash commands for the workflow
3. Estimated time and cost
4. Alternative approaches
5. Team coordination requirements
6. Related documentation and examples

## Usage

```
/agent-suggest [your task description]
```

## Examples

```
/agent-suggest "I need to create a landing page for our new AI product"
/agent-suggest "Debug why our API is returning 500 errors"
/agent-suggest "Create a comprehensive quarterly business review"
/agent-suggest "Build a customer onboarding email sequence"
/agent-suggest "Design a scalable microservices architecture"
```

## How It Works

The suggestion engine analyzes your task using keyword matching, context understanding, and agent capability mapping to provide intelligent recommendations.

### Analysis Process

1. **Task Classification**
   - Identifies task type (development, marketing, sales, finance, QA)
   - Detects complexity level (simple, moderate, complex)
   - Determines scope (single-agent, multi-agent, cross-team)

2. **Agent Mapping**
   - Matches task keywords to agent specializations
   - Considers agent tools and capabilities
   - Reviews similar past invocations (if available)

3. **Recommendation Generation**
   - Primary agent recommendation (best fit)
   - Secondary agents (supporting specialists)
   - Relevant slash commands
   - Expected workflow

4. **Context Enrichment**
   - Time estimate for completion
   - Estimated token usage and cost
   - Prerequisites and dependencies
   - Example usage and documentation links

---

## Example Output

### Example 1: Landing Page Request

**Input:**
```
/agent-suggest "Create a landing page for our new AI analytics product"
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AGENT RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: "Create a landing page for our new AI analytics product"
Classification: Marketing + Engineering | Complexity: Moderate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Best Fit: landing-page-specialist (MARKETING_TEAM)

Why this agent?
  • Specialized in high-converting landing pages
  • Combines UX design with code implementation
  • Integrates competitor analysis
  • Focuses on conversion optimization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPPORTING AGENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Consider involving:
  1. copywriter - For compelling headlines and copy
  2. visual-designer - For hero images and graphics
  3. seo-specialist - For search optimization
  4. frontend-developer - If complex interactions needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1: Single Agent (Fastest)
  → "Use landing-page-specialist to create a landing page for our AI analytics product"

  Time: 30-45 minutes
  Cost: ~$0.20-0.40

Option 2: Comprehensive Campaign (Recommended)
  → /launch-campaign "AI Analytics Product" "B2B SaaS" "Lead generation"

  Includes:
    • Landing page (landing-page-specialist)
    • Supporting content (copywriter, editor)
    • SEO optimization (seo-specialist)
    • Visual assets (visual-designer)
    • Email sequences (email-specialist)

  Time: 2-4 hours
  Cost: ~$2.00-5.00

Option 3: Full Product Launch (Most Comprehensive)
  → /product-launch "AI Analytics Product" "next-month" "B2B SaaS companies"

  Cross-team coordination: Engineering + Marketing + Sales
  Time: 4-6 weeks
  Cost: ~$20-50 (agent coordination only)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREREQUISITES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before starting:
  ✓ Product positioning and value proposition defined
  ✓ Target audience identified
  ✓ Key messaging and USPs documented
  ✓ Brand assets available (logo, colors, fonts)
  ✓ Call-to-action decision (demo, trial, contact)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RELATED DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📄 Agent: MARKETING_TEAM/.claude/agents/landing-page-specialist.md
  📄 Command: .claude/commands/launch-campaign.md
  📄 Guide: MULTI_AGENT_GUIDE.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Example 2: Debugging Request

**Input:**
```
/agent-suggest "Debug why our API is returning 500 errors"
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AGENT RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: "Debug why our API is returning 500 errors"
Classification: Engineering | Complexity: Moderate-High | Urgency: High

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Best Fit: debugger (ENGINEERING_TEAM)

Why this agent?
  • Specializes in root cause analysis
  • Systematic troubleshooting approach
  • Log analysis and error tracing
  • Performance profiling capabilities

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPPORTING AGENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Consider involving:
  1. backend-architect - For API architecture review
  2. security-auditor - If security-related errors
  3. test-engineer - For regression testing after fix
  4. devops-engineer - If infrastructure/deployment related

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1: Quick Debug (Fastest)
  → "Use debugger to find why our API is returning 500 errors"

  Time: 15-30 minutes
  Cost: ~$0.10-0.30

Option 2: Comprehensive Debug (Recommended)
  → /debug-issue "API 500 errors" "production"

  Includes:
    • Root cause analysis (debugger)
    • Fix implementation (appropriate engineer)
    • Test creation (test-engineer)
    • Deployment verification (devops-engineer)

  Time: 1-2 hours
  Cost: ~$0.50-1.50

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMATION NEEDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide to the agent:
  • Error logs or stack traces
  • When the error started occurring
  • Affected endpoints/routes
  • Recent deployments or changes
  • Environment (production, staging, dev)
  • Request/response examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RELATED DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📄 Agent: ENGINEERING_TEAM/.claude/agents/debugger.md
  📄 Command: .claude/commands/debug-issue.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Agent Selection Matrix

The suggestion engine uses this decision tree:

### By Domain

**Engineering Tasks:**
- Feature development → cto, frontend-developer, backend-architect
- Debugging → debugger, test-engineer
- Architecture → system-architect, backend-architect
- Security → security-auditor
- DevOps → devops-engineer
- Documentation → technical-writer
- AI/ML → ai-engineer
- Database → database-architect

**Marketing Tasks:**
- Campaign → router-agent (coordinates team)
- Content → copywriter, content-strategist
- SEO → seo-specialist
- Social media → social-media-manager
- Email → email-specialist
- Design → visual-designer, ui-ux-designer
- Video → video-producer
- Landing pages → landing-page-specialist
- Research → research-agent

**Sales Tasks:**
- Proposals → proposal-specialist, sales-manager
- Outbound → outbound-specialist, sdr-agent
- Account management → account-executive
- Customer success → customer-success-manager
- Sales ops → sales-operations
- Analytics → sales-analyst

**QA Tasks:**
- Testing strategy → test-orchestrator
- Unit tests → unit-test-agent
- Integration tests → integration-test-agent
- Edge cases → edge-case-agent
- Fixtures → fixture-agent

**Finance Tasks:**
- Analysis → cfo-agent, financial-analyst
- Forecasting → forecasting-agent, fpna-agent
- Accounting → accountant, controller
- Valuation → valuation-agent
- M&A → deal-analyst
- Tax → tax-advisor
- Investments → portfolio-manager

### By Complexity

**Simple (single agent):**
- Clear, well-defined task
- Single domain/specialty
- < 1 hour of work

**Moderate (2-3 agents):**
- Requires multiple perspectives
- Cross-specialty within one team
- 1-3 hours of work

**Complex (multi-agent/cross-team):**
- Multiple domains involved
- Requires coordination
- Strategic or high-impact
- > 3 hours of work

---

## Smart Recommendations

The agent suggest system learns from:
- Task keyword analysis
- Agent capability matching
- Historical performance data (if available)
- User feedback and corrections
- Similar task patterns

## Time Estimate

This command runs instantly (< 5 seconds) and provides recommendations without invoking agents.

## Related Commands

- `/agent-health` - Check agent status and performance
- `/explain-agent [name]` - Detailed agent capabilities
- `/compare-approaches` - Compare multiple solution approaches

## Notes

- Suggestions are recommendations, not requirements
- You can always directly invoke any agent
- Consider starting with simpler approaches first
- Cross-team coordination requires more time
- Costs are estimates based on typical usage
- Actual performance may vary based on task complexity

## Pro Tips

1. **Be specific in your task description** - More details = better recommendations
2. **Mention urgency** - "urgent", "quick" triggers faster approaches
3. **Specify constraints** - "low-cost", "comprehensive", "minimal" adjust recommendations
4. **Include context** - Project type, environment, audience improves suggestions
5. **Try suggested workflows** - Slash commands often provide better coordination
