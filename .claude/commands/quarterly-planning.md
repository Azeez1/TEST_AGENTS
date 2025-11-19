# Quarterly Planning

Comprehensive cross-team strategic planning for OKRs, roadmaps, budgets, and goals.

## What This Does

Orchestrates all teams for strategic quarterly planning including:
1. **Strategy:** OKRs, goals, and key initiatives
2. **Engineering:** Technical roadmap and sprint planning
3. **Marketing:** Campaign calendar and growth strategy
4. **Sales:** Pipeline goals and sales strategy
5. **Finance:** Budgets, forecasts, and resource allocation
6. **QA:** Quality goals and testing strategy
7. **Operations:** Cross-team alignment and dependencies

## Usage

```
/quarterly-planning [quarter] [year] [focus areas]
```

## Examples

```
/quarterly-planning "Q1" "2026" "product-market-fit, revenue-growth"
/quarterly-planning "Q2 2026" "all-teams" "comprehensive"
/quarterly-planning "next-quarter" "engineering+marketing" "product-launch-focused"
```

## Process

This is a **comprehensive, multi-phase strategic planning workflow**:

---

## **PHASE 1: REVIEW & RETROSPECTIVE** (Week 1)

### 1.1 Previous Quarter Review
**Teams:** All coordinators (cto, router-agent, sales-manager, cfo-agent, test-orchestrator)

**Deliverables:**
- Last quarter achievements vs. goals
- Key wins and successes
- Misses and learnings
- Metrics and KPI performance
- Customer feedback and insights
- Team capacity and velocity analysis

**Questions to answer:**
- What did we accomplish?
- What didn't we achieve and why?
- What surprised us (good or bad)?
- What should we stop/start/continue doing?

### 1.2 Market & Competitive Analysis
**Teams:** Marketing (research-agent, analyst) + Sales (sales-analyst)

**Deliverables:**
- Market trends and shifts
- Competitive landscape changes
- Customer needs evolution
- Industry benchmarks
- Opportunity assessment
- Threat identification

### 1.3 Financial Performance Review
**Teams:** Finance (cfo-agent, financial-analyst, controller)

**Deliverables:**
- Revenue vs. forecast analysis
- Expense breakdown and trends
- Profitability analysis
- Cash flow review
- Budget variance analysis
- Financial health scorecard

---

## **PHASE 2: STRATEGIC PLANNING** (Week 2)

### 2.1 Company-Level OKRs
**Teams:** All department leads + Finance (cfo-agent)

**Define top 3-5 company objectives with measurable key results:**

**Example Objectives:**
1. Achieve product-market fit
2. Scale revenue to $X
3. Build world-class team
4. Establish category leadership
5. Achieve operational excellence

**Each objective should have 3-5 key results (measurable)**

**Deliverables:**
- Company OKR document
- Priority rankings
- Success metrics
- Timeline and milestones
- Resource requirements

### 2.2 Department-Level Planning

#### Engineering Planning
**Team:** Engineering (cto coordinates all specialists)

**Deliverables:**
- Technical roadmap (3-month view)
- Feature prioritization (MoSCoW method)
- Technical debt allocation (20% capacity)
- Architecture improvements
- Infrastructure and scaling plans
- Sprint planning framework
- Hiring and team growth needs
- Tool and technology decisions

**Use command:** `/design-architecture` for system planning

#### Marketing Planning
**Team:** Marketing (router-agent coordinates team)

**Deliverables:**
- Marketing strategy and positioning
- Campaign calendar (month-by-month)
- Content calendar (weekly themes)
- Channel strategy and budget allocation
- Lead generation goals
- Brand awareness metrics
- SEO and organic growth strategy
- Paid advertising plans
- Event and webinar schedule

**Use command:** `/launch-campaign` for individual campaigns

#### Sales Planning
**Team:** Sales (sales-manager coordinates team)

**Deliverables:**
- Sales targets and quotas
- Pipeline goals (by stage)
- Sales process improvements
- Territory and account planning
- Pricing and packaging strategy
- Partner and channel strategy
- Sales enablement needs
- CRM and tools optimization
- Team hiring and training plans

**Use command:** `/proposal-package` for sales materials

#### Finance Planning
**Team:** Finance (cfo-agent coordinates team)

**Deliverables:**
- Quarterly budget by department
- Revenue forecast (conservative, base, optimistic)
- Expense forecast and controls
- Cash flow projections
- Capital allocation priorities
- Financial goals and metrics
- Risk assessment and mitigation
- Compliance and audit planning

**Use command:** `/financial-analysis` for detailed analysis

#### QA Planning
**Team:** QA (test-orchestrator coordinates team)

**Deliverables:**
- Quality goals and metrics
- Testing strategy and coverage targets
- Automation roadmap
- Performance testing plans
- Security testing approach
- Tool and process improvements
- Team capacity planning

---

## **PHASE 3: CROSS-TEAM ALIGNMENT** (Week 3)

### 3.1 Dependency Mapping
**Teams:** All teams

**Identify and document:**
- Cross-team dependencies
- Shared resources
- Blocking risks
- Handoff points
- Communication protocols
- Escalation paths

**Create dependency matrix:**
```
Engineering depends on:
  - Marketing: Product requirements, user feedback
  - Sales: Customer needs, feature requests
  - Finance: Budget approval for tools/infrastructure

Marketing depends on:
  - Engineering: Feature releases, product updates
  - Sales: Customer stories, case studies
  - Finance: Campaign budgets

Sales depends on:
  - Engineering: Product demos, technical resources
  - Marketing: Leads, content, collateral
  - Finance: Pricing approvals, deal structures

Finance depends on:
  - All teams: Budget requests, forecast inputs
```

### 3.2 Initiative Prioritization
**Teams:** All department leads

**Prioritization framework:**
1. Impact (1-5): Business value delivered
2. Effort (1-5): Resources required
3. Risk (1-5): Execution risk
4. Strategic fit (1-5): Alignment with company OKRs

**Prioritization matrix:**
- **High Impact, Low Effort** → DO FIRST (Quick wins)
- **High Impact, High Effort** → PLAN & EXECUTE (Strategic bets)
- **Low Impact, Low Effort** → FILL-IN WORK (If capacity)
- **Low Impact, High Effort** → AVOID (Not worth it)

### 3.3 Resource Allocation
**Teams:** Finance (cfo-agent, fpna-agent) + All teams

**Allocate resources:**
- Budget by department
- Headcount and hiring priorities
- Tool and software spend
- Marketing and sales budgets
- Infrastructure and hosting
- Contractor and agency support

### 3.4 Timeline & Milestones
**Teams:** All teams

**Create integrated timeline:**
- Month 1 (Weeks 1-4): Key deliverables
- Month 2 (Weeks 5-8): Key deliverables
- Month 3 (Weeks 9-12): Key deliverables
- Key milestones and checkpoints
- Review and adjustment cadence

---

## **PHASE 4: EXECUTION PLANNING** (Week 4)

### 4.1 Detailed Planning

**Engineering:**
- Sprint breakdown (2-week sprints)
- Story pointing and capacity
- Technical spikes and research
- Code review and quality gates
- Release schedule

**Marketing:**
- Weekly content calendar
- Campaign execution plans
- Social media schedule
- Email sequences and nurture flows
- Metrics and tracking setup

**Sales:**
- Weekly/monthly targets
- Account assignments
- Demo and call scripts
- Proposal templates
- Commission and incentives

**Finance:**
- Monthly budget tracking
- Forecast update schedule
- Financial review meetings
- Variance analysis process
- Reporting dashboards

**QA:**
- Test sprint alignment
- Automation priorities
- Performance test schedule
- Release testing checklist

### 4.2 Communication & Reporting

**Establish cadences:**
- **Daily:** Team standups (per team)
- **Weekly:** Department syncs, metrics review
- **Bi-weekly:** Cross-team sync, blocker resolution
- **Monthly:** OKR progress review, budget review
- **Quarterly:** Full retrospective and planning

**Reporting structure:**
- Weekly: Progress updates (each team)
- Monthly: OKR scorecard (company-wide)
- Quarterly: Comprehensive business review

### 4.3 Risk Management

**Identify and plan for:**
- Technical risks (scalability, performance, security)
- Market risks (competition, demand changes)
- Execution risks (capacity, dependencies)
- Financial risks (budget overruns, revenue misses)
- Team risks (hiring, retention, skill gaps)

**Mitigation strategies:**
- Contingency plans
- Buffer allocations (time, budget)
- Alternative approaches
- Early warning indicators

---

## **DELIVERABLES**

### Executive Summary (5-10 pages)
- Company OKRs and strategic priorities
- Key initiatives by department
- Resource allocation and budget
- Timeline and major milestones
- Success metrics and targets
- Risk assessment and mitigation

### Department Plans (per team)
- Department OKRs (aligned to company)
- Detailed roadmap and initiatives
- Resource needs and budget
- Timeline and deliverables
- Metrics and KPIs
- Dependencies and risks

### Cross-Team Artifacts
- Dependency matrix
- Integrated timeline (Gantt chart)
- Resource allocation matrix
- Budget summary by department
- Communication and reporting calendar
- Risk register

### Operational Documents
- Sprint planning framework (Engineering)
- Campaign calendar (Marketing)
- Sales playbook updates (Sales)
- Budget tracking template (Finance)
- Test strategy (QA)
- Meeting cadence calendar

### Dashboards & Tracking
- OKR tracking dashboard (real-time)
- Financial dashboard (budget vs. actual)
- Marketing metrics dashboard
- Sales pipeline dashboard
- Engineering velocity dashboard
- QA quality dashboard

---

## **SUCCESS METRICS**

Track throughout the quarter:

**Company-Level:**
- OKR completion rate (target: 70%+)
- Revenue vs. target
- Customer acquisition and growth
- Product-market fit indicators
- Team satisfaction and engagement

**Engineering:**
- Feature delivery vs. roadmap (target: 80%+)
- Sprint velocity and predictability
- Code quality metrics
- Production incidents (target: <X)
- Technical debt reduction

**Marketing:**
- Lead generation (MQLs, SQLs)
- Content engagement metrics
- Campaign ROI
- Website traffic and conversions
- Brand awareness metrics

**Sales:**
- Revenue vs. quota
- Pipeline generation and health
- Win rate and deal velocity
- Customer acquisition cost (CAC)
- Customer lifetime value (LTV)

**Finance:**
- Budget variance (target: <10%)
- Burn rate and runway
- Gross margins
- Operating leverage
- Cash flow positive (if applicable)

**QA:**
- Test coverage (target: 80%+)
- Defect escape rate (target: <5%)
- Automation coverage
- Release quality scores
- Testing efficiency

---

## **TIME ESTIMATE**

- **Planning phase:** 4 weeks (with all teams)
- **Total agent coordination time:** 15-25 hours
- **Ongoing execution:** 12 weeks (full quarter)
- **Mid-quarter review:** 2-4 hours
- **End-quarter review:** 4-6 hours

---

## **RELATED COMMANDS**

- `/product-launch` - For major product initiatives
- `/financial-analysis` - For detailed financial planning
- `/design-architecture` - For technical roadmap planning
- `/launch-campaign` - For marketing campaigns
- `/proposal-package` - For sales enablement

---

## **BEST PRACTICES**

1. **Start planning 3-4 weeks before quarter starts**
2. **Involve all stakeholders early**
3. **Be realistic about capacity** (plan for 70% utilization)
4. **Build in buffer time** (20% for unexpected work)
5. **Align on priorities** (say no to non-strategic work)
6. **Track weekly** (don't wait until end of quarter)
7. **Adjust monthly** (plans are living documents)
8. **Celebrate wins** (team morale and motivation)
9. **Learn from misses** (continuous improvement)
10. **Use supervisor verification** (ensure quality and completeness)

---

## **NOTES**

- This is the most strategic and comprehensive planning workflow
- Requires executive alignment and commitment
- Should involve all department leaders
- May require facilitation for first-time planning
- Consider using external facilitator for offsites
- Document everything for future reference
- Update and refine process each quarter
- Use tools like Asana, Linear, or Notion for tracking
- Consider OKR software (Lattice, 15Five, Gtmhub) for scaling

---

## **QUARTERLY PLANNING CHECKLIST**

**4 Weeks Before Quarter:**
- [ ] Schedule planning sessions
- [ ] Gather previous quarter data
- [ ] Conduct retrospective
- [ ] Collect team feedback

**3 Weeks Before Quarter:**
- [ ] Define company OKRs
- [ ] Department planning sessions
- [ ] Budget proposals submitted
- [ ] Resource needs identified

**2 Weeks Before Quarter:**
- [ ] Cross-team alignment meetings
- [ ] Dependency mapping complete
- [ ] Initiative prioritization done
- [ ] Budget finalized

**1 Week Before Quarter:**
- [ ] Detailed execution plans ready
- [ ] Communication cadence set
- [ ] Dashboards and tracking configured
- [ ] Team kickoff prepared

**Quarter Start:**
- [ ] All-hands kickoff meeting
- [ ] OKRs communicated company-wide
- [ ] Individual goals set (aligned to OKRs)
- [ ] First sprint/cycle started

**Mid-Quarter (Week 6):**
- [ ] OKR progress review
- [ ] Adjust plans as needed
- [ ] Address blockers
- [ ] Forecast updates

**End of Quarter (Week 12):**
- [ ] Final OKR scoring
- [ ] Retrospective meetings
- [ ] Results communication
- [ ] Recognition and celebration
- [ ] Start next quarter planning
