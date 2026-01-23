# ENGINEERING_TEAM - 15 Engineering & Infrastructure Agents ⭐ **SUPER TEAM**

## 🎯 Overview

The **ENGINEERING_TEAM** contains **15 specialized agents** (14 specialists + 1 CTO coordinator) for software engineering, infrastructure, security, AI/ML, design, quality, optimization, and analytics. These agents have **full workspace access** and can work with all 58 agents across the 6 teams.

**CTO Coordinator:**
- **cto** ⭐ - Chief Technology Officer for strategic coordination of all 14 specialists

**Core Agents (9 - Custom Built):**
- **devops-engineer** ⭐ - CI/CD, Docker, Kubernetes, Terraform, cloud infrastructure, monitoring (production-ready with 886 lines of code)
- **frontend-developer** - React components, responsive design, state management, performance
- **backend-architect** - RESTful APIs, microservices, database schema, scalability planning
- **security-auditor** ⭐ - Code security analysis, vulnerability scanning, compliance audits (unique comprehensive security)
- **technical-writer** ⭐ - Documentation, PRDs, technical specs, API docs, user guides (broader scope)
- **system-architect** ⭐ **NEW** - System architecture design, professional flow diagrams with Mermaid.js, interactive visualizations
- **ai-engineer** ⭐ - LLM integration, RAG systems, prompt optimization, agent frameworks (perfect for 58 agents!)
- **ui-ux-designer** - User research, wireframes, design systems, accessibility, user flows
- **analytics-dashboard-agent** ⭐ **NEW** - Real-time analytics dashboards, data visualization, multi-source ETL pipelines, client-specific analytics

**Specialist Agents (5 - From aitmpl.com):**
- **code-reviewer** - Quality, security, maintainability reviews (3.2K community downloads)
- **test-engineer** - Test automation, quality assurance, CI/CD testing (1.3K downloads)
- **prompt-engineer** - LLM prompt optimization for all 58 agents (2.4K downloads)
- **database-architect** - Database design, data modeling, scalability (1.2K downloads)
- **debugger** - Root cause analysis, troubleshooting, error investigation (1.7K downloads)

---

## 🚀 Quick Start

### Talk to Claude Code

**Using the CTO Coordinator (Recommended for Complex Tasks):**
```
"Use cto to build an AI-powered analytics dashboard"
"Use cto to deploy all 7 systems to AWS with Kubernetes"
"Use cto to optimize prompts for all 58 agents"
"Use cto to conduct a comprehensive security audit"
"Use cto to troubleshoot the MARKETING_TEAM timeout issues"
```

**Using Individual Specialists Directly:**
```
"Use the devops-engineer to create a complete CI/CD pipeline with GitHub Actions"
"Use the system-architect to create microservices architecture diagram"
"Use the ai-engineer to optimize prompts for the 58 agents in this workspace"
"Use the ui-ux-designer to create wireframes for an agent control dashboard"
"Use the frontend-developer to implement the dashboard in Next.js"
"Use the backend-architect to design an API for managing all 58 agents"
"Use the security-auditor to scan for hardcoded API keys across all systems"
"Use the technical-writer to write a PRD for agent analytics"
```

---

## 🤖 Agent Capabilities

### 0. CTO (Chief Technology Officer) ⭐ **STRATEGIC COORDINATOR**
**Purpose:** Strategic coordination of all 13 ENGINEERING_TEAM specialists

**Capabilities:**
- ✅ **Strategic planning** - Break down complex requests into phased execution plans
- ✅ **Intelligent routing** - Classify requests and delegate to the right specialists
- ✅ **Workflow orchestration** - Coordinate multi-agent workflows with dependency tracking
- ✅ **Quality gates** - Ensure code review, security audit, and testing before deployment
- ✅ **Balanced approach** - Both strategic CTO and hands-on technical lead

**Coordination Tools:**
- `classify_engineering_request` - Intent classification and agent recommendation
- `get_engineer_capabilities` - Agent capability lookup
- `list_engineering_agents` - Complete agent directory
- `create_execution_plan` - Multi-phase workflow planning with dependencies
- `sequential-thinking` MCP - Complex problem decomposition

**Workflow Patterns:**
- **End-to-End Feature Development** - PRD → Design → Build → Test → Deploy → Document
- **Infrastructure Deployment** - Terraform → Security Scan → Testing → Documentation
- **AI Optimization** - Analyze → Optimize → Benchmark → Document
- **Security Audit** - Code Review → Security Scan → Test Coverage → Report
- **Troubleshooting** - Root Cause → Fix → Validate → Review

**Example Tasks:**
```
"Use cto to build an AI-powered analytics dashboard"
→ Coordinates: technical-writer (PRD) → ui-ux-designer (wireframes) →
   database-architect (schema) → backend-architect (API) →
   frontend-developer (UI) → test-engineer (tests) →
   code-reviewer (review) → security-auditor (audit) →
   devops-engineer (deploy) → technical-writer (docs)

"Use cto to deploy MARKETING_TEAM to AWS with Kubernetes"
→ Coordinates: devops-engineer (infra) → security-auditor (scan) →
   test-engineer (validation) → technical-writer (docs)

"Use cto to optimize prompts for all 58 agents"
→ Coordinates: ai-engineer + prompt-engineer (analyze & optimize) →
   technical-writer (document improvements)

"Use cto to create system architecture diagram for microservices"
→ Coordinates: system-architect (diagrams) → technical-writer (documentation)
```

**Special Note:** The CTO agent coordinates **ONLY the 14 ENGINEERING_TEAM specialists**. It does not coordinate other teams (MARKETING_TEAM, QA_TEAM, PROPOSAL_TEAM, FINANCIAL_TEAM, SALES_TEAM) - they have their own coordinators.

---

### 1. DevOps Engineer ⭐ **PRODUCTION-READY**
**Purpose:** Full-stack DevOps automation with production-grade configurations

**Capabilities:**
- ✅ **Complete CI/CD pipelines** - GitHub Actions with test/build/deploy stages
- ✅ **Infrastructure as Code** - Full Terraform configs (VPC, EKS, RDS, Redis, ALB)
- ✅ **Kubernetes deployments** - Helm charts with auto-scaling & health checks
- ✅ **Monitoring stack** - Prometheus, Grafana, Alertmanager with dashboards
- ✅ **Security scanning** - Trivy, kube-bench, gitleaks, dependency checks
- ✅ **Deployment strategies** - Blue-green, canary with Istio, rolling updates

**Example Tasks:**
```
"Use devops-engineer to create a complete GitHub Actions pipeline for MARKETING_TEAM
with unit tests, Docker build, security scanning, and Kubernetes deployment"

"Use devops-engineer to generate Terraform infrastructure for AWS with EKS cluster,
RDS PostgreSQL, Redis cache, and Application Load Balancer"
```

**Outputs:** `outputs/docker/`, `outputs/cicd/`, `outputs/infrastructure/`

**Special Note:** This agent provides **production-ready code** you can use immediately - 886 lines of battle-tested configurations!

---

### 2. Frontend Developer
**Purpose:** Modern React applications and responsive UI components

**Capabilities:**
- ✅ React component architecture (hooks, context, performance)
- ✅ Responsive CSS with Tailwind/CSS-in-JS
- ✅ State management (Redux, Zustand, Context API)
- ✅ Frontend performance (lazy loading, code splitting, memoization)
- ✅ Accessibility (WCAG compliance, ARIA labels, keyboard navigation)

**Approach:**
- Component-first thinking - reusable, composable UI pieces
- Mobile-first responsive design
- Performance budgets - aim for sub-3s load times
- Semantic HTML and proper ARIA attributes

**Example Tasks:**
```
"Use frontend-developer to create a React dashboard component for managing 58 agents
with status indicators, filtering, and responsive design"

"Use frontend-developer to build a marketing content gallery with lazy loading
and infinite scroll"
```

**Outputs:** `outputs/frontend/components/`, `outputs/frontend/apps/`

---

### 3. Backend Architect
**Purpose:** Scalable API design and microservices architecture

**Capabilities:**
- ✅ RESTful API design with proper versioning and error handling
- ✅ Service boundary definition and inter-service communication
- ✅ Database schema design (normalization, indexes, sharding)
- ✅ Caching strategies and performance optimization
- ✅ Security patterns (auth, rate limiting)

**Approach:**
- Start with clear service boundaries
- Design APIs contract-first
- Consider data consistency requirements
- Plan for horizontal scaling from day one

**Example Tasks:**
```
"Use backend-architect to design a microservices architecture for managing 58 agents
with API gateway, service mesh, and database per service"

"Use backend-architect to create an API specification for agent task execution
with request/response examples and OpenAPI documentation"
```

**Outputs:** `outputs/backend/architecture/`, `outputs/backend/api-specs/`

---

### 4. Security Auditor
**Purpose:** Application security, code review, vulnerability assessment

**Capabilities:**
- ✅ Scan for hardcoded secrets (API keys, passwords)
- ✅ Identify security vulnerabilities (OWASP Top 10)
- ✅ Review authentication and authorization logic
- ✅ Dependency vulnerability scanning
- ✅ Container security analysis
- ✅ Compliance audits (GDPR, HIPAA, SOC2)

**Example Tasks:**
```
"Use security-auditor to scan all Python files for hardcoded credentials
and create a security audit report with severity ratings"

"Use security-auditor to review MARKETING_TEAM email security for injection
vulnerabilities and OAuth token security"
```

**Outputs:** `outputs/security/audits/`, `outputs/security/scans/`

**Special Focus:**
- API key management across 58 agents
- Email security (MARKETING_TEAM Gmail integration)
- OAuth token security (Google Workspace)

---

### 5. Technical Writer
**Purpose:** Documentation, PRDs, technical specs, API docs

**Capabilities:**
- ✅ **Product Requirements Documents (PRDs)** with user stories and success metrics
- ✅ Technical specifications with architecture diagrams
- ✅ API documentation (OpenAPI/Swagger)
- ✅ System architecture diagrams (Mermaid, PlantUML)
- ✅ User guides and tutorials
- ✅ Release notes and changelogs

**Example Tasks:**
```
"Use technical-writer to write a comprehensive PRD for an 'Agent Scheduling System'
with user stories, acceptance criteria, technical requirements, and success metrics"

"Use technical-writer to create API documentation for MARKETING_TEAM tools
with endpoint descriptions, request/response examples, and authentication details"
```

**Outputs:** `docs/prds/`, `docs/specs/`, `docs/api/`, `docs/guides/`

**Documentation Types:**
- PRDs: Product vision, requirements, user stories, KPIs
- Technical Specs: Architecture, data models, integrations
- API Docs: Endpoints, parameters, responses, authentication
- User Guides: Step-by-step instructions, screenshots, examples

---

### 6. System Architect ⭐ **NEW - PROFESSIONAL FLOW DIAGRAMS**
**Purpose:** System architecture design and professional flow diagram creation

**Capabilities:**
- ✅ **System architecture design** - Microservices, cloud infrastructure, distributed systems
- ✅ **Flow diagrams** - Mermaid.js with 9+ diagram types (flowcharts, sequence, ER, state, CI/CD)
- ✅ **Interactive visualizations** - HTML output with pan/zoom navigation
- ✅ **Data flow diagrams** - How data moves through systems and components
- ✅ **Technical documentation** - Architecture decision records, system design docs
- ✅ **Integration specifications** - API architectures, event-driven systems

**Diagram Types:**
- System architecture diagrams (components, services, infrastructure)
- Sequence diagrams (API interactions, authentication flows)
- ER diagrams (database schemas, relationships)
- State diagrams (lifecycle, workflow states)
- Flowcharts (business logic, decision trees)
- CI/CD pipeline visualizations
- User journey and UX flows

**Example Tasks:**
```
"Use system-architect to create a microservices architecture diagram for the
MARKETING_TEAM system with API gateway, service mesh, and database interactions"

"Use system-architect to visualize the CI/CD pipeline for deploying all 58 agents
to AWS with Kubernetes, including security scanning and automated testing"

"Use system-architect to create an ER diagram for the agent analytics database
showing relationships between agents, executions, and performance metrics"
```

**Outputs:** `outputs/diagrams/` (Mermaid code + interactive HTML)

**Uses:** flow-diagram skill for professional Mermaid diagram generation

---

### 7. AI Engineer ⭐ **PERFECT FOR THIS WORKSPACE**
**Purpose:** LLM applications, RAG systems, agent frameworks

**Capabilities:**
- ✅ **LLM integration** - OpenAI, Anthropic, open source/local models
- ✅ **RAG systems** - Vector databases (Qdrant, Pinecone, Weaviate)
- ✅ **Prompt engineering** - Optimization and structured outputs
- ✅ **Agent frameworks** - LangChain, LangGraph, CrewAI patterns
- ✅ **Embedding strategies** - Semantic search and similarity
- ✅ **Token optimization** - Cost management and monitoring

**Why Perfect for Your Workspace:**
- You have **59 AI agents** - ai-engineer can help improve them!
- You use **Anthropic Claude** - ai-engineer knows prompt optimization
- You could build **RAG systems** for agent knowledge
- Can help with **agent orchestration** frameworks

**Example Tasks:**
```
"Use ai-engineer to optimize the prompts for MARKETING_TEAM copywriter agent
to reduce token usage by 30% while maintaining quality"

"Use ai-engineer to build a RAG system that stores all marketing content
in a vector database for semantic search and content recommendations"

"Use ai-engineer to create a multi-agent orchestration framework using LangGraph
that coordinates workflow between copywriter, visual-designer, and email-specialist"
```

**Outputs:** `outputs/ai/prompts/`, `outputs/ai/rag-systems/`, `outputs/ai/orchestration/`

---

### 8. UI/UX Designer ⭐ **COMPLEMENTS FRONTEND**
**Purpose:** User-centered design and interface systems

**Capabilities:**
- ✅ **User research** - Persona development and journey mapping
- ✅ **Wireframing** - Low and high-fidelity prototypes
- ✅ **Design systems** - Component libraries and guidelines
- ✅ **Accessibility** - Inclusive design principles (WCAG)
- ✅ **Information architecture** - User flows and navigation
- ✅ **Usability testing** - Iteration strategies and metrics

**Approach:**
- User needs first - design with empathy and data
- Progressive disclosure for complex interfaces
- Consistent design patterns and components
- Mobile-first responsive design thinking

**Works with frontend-developer:**
1. ui-ux-designer → Creates wireframes & design systems
2. frontend-developer → Implements designs in React/Next.js

**Example Tasks:**
```
"Use ui-ux-designer to create user journey maps and wireframes for an agent
control dashboard with filtering, search, and real-time status updates"

"Use ui-ux-designer to design a design system for the workspace with
color palette, typography, spacing, and component patterns"
```

**Outputs:** `outputs/design/wireframes/`, `outputs/design/systems/`, `outputs/design/user-flows/`

---

### 9. Code Reviewer ⭐ **QUALITY LAYER**
**Purpose:** Expert code review for quality, security, and maintainability

**Capabilities:**
- ✅ Code quality analysis (readability, naming, duplication)
- ✅ Security review (exposed secrets, API keys, input validation)
- ✅ Error handling verification
- ✅ Test coverage assessment
- ✅ Performance considerations
- ✅ Automatic git diff analysis on invocation

**Approach:**
- Proactively reviews after code writing/modification
- Organizes feedback by priority (Critical/Warnings/Suggestions)
- Provides specific fix examples for all issues
- Works alongside security-auditor for comprehensive coverage

**Example Tasks:**
```
"Use code-reviewer to review the new MARKETING_TEAM email tool for quality and security"
"Use code-reviewer after modifying devops-engineer templates to ensure best practices"
```

**Outputs:** `outputs/quality/reviews/`

---

### 10. Test Engineer ⭐ **TEST AUTOMATION**
**Purpose:** Comprehensive test automation and quality assurance

**Capabilities:**
- ✅ Test pyramid strategy (70% unit, 20% integration, 10% E2E)
- ✅ Automation frameworks (Jest, Playwright, pytest, Cypress)
- ✅ Performance testing (load, stress, benchmark)
- ✅ Test suite management and CI/CD integration
- ✅ Coverage analysis and quality gates
- ✅ Test data management

**Approach:**
- Focuses on engineering test automation (different from TEST_AGENT)
- Creates comprehensive test strategies
- Implements full testing pipelines
- Provides test configuration templates

**Example Tasks:**
```
"Use test-engineer to create a complete test strategy for the 58-agent workspace"
"Use test-engineer to build E2E tests for MARKETING_TEAM agent workflows"
```

**Outputs:** `outputs/testing/strategies/`, `outputs/testing/automation/`

---

### 11. Prompt Engineer ⭐ **AI OPTIMIZATION**
**Purpose:** Expert LLM prompt optimization for AI systems

**Capabilities:**
- ✅ Prompt techniques (few-shot, chain-of-thought, role-playing)
- ✅ Model-specific optimization (Claude, GPT, open models)
- ✅ Structured output formatting
- ✅ Constitutional AI principles
- ✅ Prompt chaining and pipelines
- ✅ Performance benchmarking

**Why Perfect for This Workspace:**
- You have **59 AI agents** that all use prompts!
- Can optimize every agent definition for better performance
- Reduce token usage across all agents
- Improve output quality and consistency

**Example Tasks:**
```
"Use prompt-engineer to optimize the copywriter agent prompt to reduce tokens by 30%"
"Use prompt-engineer to create a prompt pipeline for multi-agent campaigns"
```

**Outputs:** `outputs/optimization/prompts/`, `outputs/optimization/benchmarks/`

---

### 12. Database Architect ⭐ **DATA LAYER**
**Purpose:** Database architecture and data modeling specialist

**Capabilities:**
- ✅ Data modeling (ER design, normalization, dimensional modeling)
- ✅ Scalability planning (sharding, replication, partitioning)
- ✅ Polyglot persistence (SQL, NoSQL, cache, search, time-series)
- ✅ Microservices data patterns (database per service, CQRS, event sourcing)
- ✅ Migration strategies with rollback support
- ✅ Performance monitoring and optimization

**Why Needed:**
- Design unified analytics database for 58 agents
- Optimize MARKETING_TEAM content storage
- Track agent performance metrics
- Store test results and coverage data

**Example Tasks:**
```
"Use database-architect to design an analytics database tracking all 59 agent metrics"
"Use database-architect to create a content management schema for MARKETING_TEAM"
```

**Outputs:** `outputs/database/schemas/`, `outputs/database/migrations/`

---

### 13. Debugger ⭐ **TROUBLESHOOTING**
**Purpose:** Root cause analysis and debugging specialist

**Capabilities:**
- ✅ Error message and stack trace analysis
- ✅ Reproduction step identification
- ✅ Failure location isolation
- ✅ Hypothesis formation and testing
- ✅ Strategic debug logging
- ✅ Variable state inspection

**Common Debugging Scenarios:**
- Agent coordination failures
- API integration issues
- MCP server problems
- Tool execution errors
- Workflow orchestration bugs

**Example Tasks:**
```
"Use debugger to investigate why the MARKETING_TEAM copywriter agent is timing out"
"Use debugger to fix the MCP connection issues in the workspace"
```

**Outputs:** `outputs/debugging/reports/`, `outputs/debugging/fixes/`

---

### 14. Analytics Dashboard Agent ⭐ **NEW - CLIENT ANALYTICS**
**Purpose:** Real-time analytics dashboards and data visualization for client data

**Capabilities:**
- ✅ **Real-time dashboards** - Interactive React dashboards with WebSocket/SSE updates
- ✅ **Multi-source data integration** - ETL pipelines for APIs, databases, and files
- ✅ **Data visualization** - Charts (Chart.js, D3.js), KPIs, tables, interactive widgets
- ✅ **Data cleaning and transformation** - Pandas-based ETL with outlier detection
- ✅ **Client customization** - Branded dashboards with custom themes and widgets
- ✅ **Real-time streaming** - WebSocket and Server-Sent Events for live updates
- ✅ **Deployment** - Docker, Kubernetes, Vercel-ready configurations

**Tech Stack:**
- Frontend: React, Chart.js, D3.js, TailwindCSS
- Backend: FastAPI, WebSocket, Redis, PostgreSQL
- ETL: Pandas, asyncio, aiohttp
- Deployment: Docker, Vercel, AWS

**Why Perfect for Your Workspace:**
- Transforms siloed client data into actionable insights
- Creates beautiful, fast real-time dashboards
- Handles multiple data sources (APIs, databases, CSV/Excel/JSON)
- Client-specific branding and customization
- Production-ready deployment solutions

**Example Tasks:**
```
"Use analytics-dashboard-agent to create a real-time analytics dashboard for Client X
showing revenue, users, and conversions from their Salesforce API and PostgreSQL database"

"Use analytics-dashboard-agent to build an ETL pipeline that integrates Google Analytics API,
MySQL sales database, and CSV files from S3, with real-time dashboard updates"

"Use analytics-dashboard-agent to deploy a custom branded dashboard for ACME Corp with
their logo, colors, and KPIs (MRR, churn rate, LTV) to production using Docker"
```

**Outputs:** `outputs/dashboards/`, `outputs/pipelines/`, `outputs/deployment/`

**Works with:**
- **frontend-developer** - Complex React components and UI optimization
- **backend-architect** - API design and microservices architecture
- **database-architect** - Database schema and query optimization
- **devops-engineer** - Deployment, CI/CD, and infrastructure
- **ui-ux-designer** - Dashboard design and user experience

---

## 🌐 Workspace-Wide Access

All ENGINEERING_TEAM agents can access and work with:

| System | Agents | What Engineering Agents Can Do |
|--------|--------|--------------------------------|
| **MARKETING_TEAM/** | 18 agents | Deploy, audit security, build dashboards, document APIs, optimize prompts, review code, test workflows, design databases, create analytics dashboards |
| **QA_TEAM/** | 5 agents | Review test code, containerize, build CI/CD, document testing, debug failures |
| **PROPOSAL_TEAM/** | 1 agent | RFP automation, compliance matrix, proposal generation |
| **FINANCIAL_TEAM/** | 10 agents | PE/M&A, valuations, FP&A, accounting, tax planning |
| **SALES_TEAM/** | 8 agents | SDR, AE, sales ops, proposals, customer success |
| **ENGINEERING_TEAM/** | 15 agents | Self-improvement, documentation, deployment, AI optimization, quality assurance, database design, analytics dashboards |

**Cross-Team Collaboration:**
- **DevOps** can deploy ANY of the 58 agents
- **AI Engineer** can optimize prompts for ALL agents
- **Prompt Engineer** can refine all 58 agent definitions
- **Security Auditor** can scan ALL 6 teams
- **Code Reviewer** ensures quality across ALL codebases
- **UI/UX Designer** can design dashboards for ALL teams
- **Frontend Developer** can build UIs for ANY system
- **Backend Architect** can create APIs for ALL agents
- **Database Architect** can design unified data layer
- **Technical Writer** can document ALL 58 agents
- **Test Engineer** can create test strategies for ALL teams
- **Debugger** can troubleshoot ANY agent or workflow
- **Analytics Dashboard Agent** can create dashboards for ANY team's data

---

## 📂 Folder Structure

```
ENGINEERING_TEAM/
├── .claude/
│   ├── agents/                  ← 15 agent definitions (1 coordinator + 14 specialists)
│   │   ├── cto.md                   ⭐ (30K - CTO coordinator for all 14 specialists)
│   │   ├── devops-engineer.md       (24K - production CI/CD, Terraform, Helm)
│   │   ├── frontend-developer.md    (1.3K - React, responsive design)
│   │   ├── backend-architect.md     (1.3K - API design, microservices)
│   │   ├── security-auditor.md      (8.1K - code security, vulnerability scanning)
│   │   ├── technical-writer.md      (16K - PRDs, specs, API docs)
│   │   ├── ai-engineer.md           (1.3K - LLM, RAG, prompt optimization)
│   │   ├── ui-ux-designer.md        (1.2K - UX design, wireframes, accessibility)
│   │   ├── analytics-dashboard-agent.md ⭐ NEW (real-time dashboards, ETL, data viz)
│   │   ├── code-reviewer.md         (quality & security reviews)
│   │   ├── test-engineer.md         (test automation & QA)
│   │   ├── prompt-engineer.md       (LLM prompt optimization)
│   │   ├── database-architect.md    (database design & modeling)
│   │   └── debugger.md              (troubleshooting & debugging)
│   └── settings.json            ← Workspace-wide access config
│
├── tools/                       ← Shared engineering tools
│   ├── engineering_coordinator_tools.py  ⭐ NEW (CTO coordination tools)
│   └── validate_agents.py       ← Agent definition validator
├── scripts/                     ← Utility scripts
├── memory/                      ← Configuration and memory
│   └── config.json              ← Workspace info, deployment defaults
│
├── outputs/                     ← Generated deliverables (gitignored)
│   ├── docker/
│   ├── cicd/
│   ├── infrastructure/
│   ├── security/
│   ├── frontend/
│   ├── backend/
│   ├── design/
│   ├── ai/
│   ├── quality/                 ⭐ NEW (code reviews)
│   ├── testing/                 ⭐ NEW (test strategies, automation)
│   ├── optimization/            ⭐ NEW (prompt optimization, benchmarks)
│   ├── database/                ⭐ NEW (schemas, migrations)
│   ├── debugging/               ⭐ NEW (debugging reports, fixes)
│   ├── dashboards/              ⭐ NEW (analytics dashboards, visualizations)
│   └── pipelines/               ⭐ NEW (ETL pipelines, data integration)
│
├── docs/                        ← Documentation
│   ├── prds/
│   ├── specs/
│   ├── api/
│   ├── guides/
│   └── architecture/
│
├── requirements.txt             ← Python dependencies
└── README.md                    ← This file
```

---

## 💡 Common Use Cases

### 1. Full-Stack Agent Dashboard (CTO Coordinates All 12 Specialists)

**Without CTO (Manual Coordination - 12 Steps):**
```
Step 1: "Use technical-writer to write a PRD for an agent control dashboard"
Step 2: "Use ui-ux-designer to create wireframes and user flows for the dashboard"
Step 3: "Use database-architect to design the analytics database schema"
Step 4: "Use backend-architect to design the API for agent management"
Step 5: "Use frontend-developer to implement the dashboard in Next.js"
Step 6: "Use code-reviewer to review the implementation for quality"
Step 7: "Use test-engineer to create comprehensive test strategy"
Step 8: "Use security-auditor to audit the dashboard for vulnerabilities"
Step 9: "Use devops-engineer to containerize and deploy to Kubernetes"
Step 10: "Use ai-engineer to add intelligent agent recommendations"
Step 11: "Use prompt-engineer to optimize all AI prompts in the dashboard"
Step 12: "Use debugger to troubleshoot any deployment issues"
```

**With CTO (Single Command - Automated Coordination):**
```
"Use cto to build an AI-powered analytics dashboard for tracking all 58 agents"

→ CTO automatically:
  1. Classifies request as "build_feature"
  2. Creates execution plan with 6 phases
  3. Delegates to all 13 specialists in proper sequence
  4. Ensures quality gates (review + security + testing)
  5. Coordinates deployment
  6. Generates complete documentation
```

### 2. Optimize All 59 Agents (AI Engineer + Prompt Engineer Collaboration)
```
"Use ai-engineer and prompt-engineer together to:
1. Analyze prompts for all 58 agents
2. Optimize for token reduction (30% target)
3. Improve structured outputs with JSON mode
4. Add fallback strategies for API failures
5. Create a prompt versioning system
6. Implement A/B testing for prompt variants
7. Build RAG system for agent knowledge base
8. Track performance metrics across all agents"
```

### 3. Production Deployment Pipeline
```
"Use devops-engineer to create a complete deployment pipeline:
1. GitHub Actions CI/CD with test/build/deploy stages
2. Terraform infrastructure for AWS EKS cluster
3. Helm charts for all agent systems
4. Prometheus/Grafana monitoring
5. Blue-green deployment strategy
6. Security scanning with Trivy and gitleaks"
```

### 4. Build RAG System for Marketing Content
```
"Use ai-engineer to build a RAG system:
1. Extract all marketing content from MARKETING_TEAM outputs
2. Chunk documents with optimal size (512 tokens)
3. Generate embeddings with OpenAI text-embedding-3-large
4. Store in Qdrant vector database
5. Implement semantic search API
6. Add retrieval-augmented generation for content recommendations"
```

---

## 🎯 Agent Combinations

### Design → Develop → Deploy
```
1. ui-ux-designer: Create wireframes
2. frontend-developer: Build React components
3. backend-architect: Design API
4. devops-engineer: Deploy to production
```

### AI Optimization Workflow
```
1. ai-engineer: Analyze agent prompts
2. technical-writer: Document optimizations
3. security-auditor: Audit prompt injection risks
```

### Complete Feature Development
```
1. technical-writer: Write PRD
2. backend-architect: Design architecture
3. frontend-developer: Build UI
4. ui-ux-designer: Design UX
5. security-auditor: Security review
6. devops-engineer: Deploy
7. ai-engineer: Add AI features
```

---

## 📊 Agent Statistics ⭐ **SUPER TEAM**

**Total Workspace:**
- **58 AI agents** across 6 teams
- 18 marketing + 5 QA + 1 proposal + 10 financial + 8 sales + **15 engineering** + 1 supervisor
- 6 teams working together

**ENGINEERING_TEAM Agents (15 Total):**

**CTO Coordinator (1 - Custom Built):**
- ⭐ **cto** - Strategic coordinator for all 14 specialists (~850 lines)
  - Tools: classify_engineering_request, get_engineer_capabilities, list_engineering_agents, create_execution_plan
  - Workflow patterns: End-to-end feature, infrastructure deployment, AI optimization, security audit, troubleshooting

**Core 9 Specialists (Custom Built):**
- 3 official templates (devops, frontend, ui-ux) ← Production-ready
- 3 new additions (ai-engineer, system-architect, analytics-dashboard-agent) ← Perfect for this workspace
- 1 architecture-focused (backend-architect)
- 2 custom comprehensive (security-auditor, technical-writer) ← Unique capabilities

**Specialist 5 (aitmpl.com Community):**
- code-reviewer (3.2K downloads) ← Quality layer
- test-engineer (1.3K downloads) ← QA automation
- prompt-engineer (2.4K downloads) ← AI optimization
- database-architect (1.2K downloads) ← Data layer
- debugger (1.7K downloads) ← Troubleshooting

**Resources:**
- Full workspace access to all 58 agents
- 17 skills available (inherited from workspace)
- 7 MCP servers (playwright, google-workspace, perplexity, bright-data, n8n-mcp, sequential-thinking, marketing-tools)

---

## 🔐 Security Best Practices

All ENGINEERING_TEAM agents follow these security standards:

1. ✅ **Never hardcode secrets** - Use environment variables
2. ✅ **Scan before deploy** - Security audit all code
3. ✅ **Least privilege** - Minimal permissions
4. ✅ **Input validation** - Validate all user inputs
5. ✅ **Audit logging** - Track all sensitive operations

---

## 📖 Documentation

- **Main Workspace Docs:** `../claude.md` - Complete repository guide
- **Multi-Agent Guide:** `../MULTI_AGENT_GUIDE.md` - How to use all 58 agents
- **Agent Definitions:** `.claude/agents/` - Individual agent instructions

---

## 🚦 Next Steps

1. **Deploy an Agent System**
   ```
   "Use devops-engineer to create a complete Kubernetes deployment for MARKETING_TEAM"
   ```

2. **Optimize All AI Agents**
   ```
   "Use ai-engineer and prompt-engineer to optimize prompts for all 58 agents"
   ```

3. **Build Agent Dashboard**
   ```
   "Use ui-ux-designer, frontend-developer, and database-architect to build a control panel"
   ```

4. **Create Documentation**
   ```
   "Use technical-writer to document all 58 agents with PRDs and API specs"
   ```

5. **Security & Quality Audit**
   ```
   "Use security-auditor and code-reviewer to scan and review all 7 teams"
   ```

6. **Comprehensive Testing**
   ```
   "Use test-engineer to create test strategies for all systems"
   ```

7. **Build Client Analytics Dashboard**
   ```
   "Use analytics-dashboard-agent to create real-time analytics dashboard for client data"
   ```

---

**Last Updated:** 2025-11-18
**Version:** 5.0 - ANALYTICS DASHBOARD AGENT ADDED ⭐ (15 agents: 1 coordinator + 14 specialists)
**Total Workspace Agents:** 58 (18 marketing + 5 QA + 1 proposal + 10 financial + 8 sales + **15 engineering** + 1 supervisor)
**Latest Addition:** analytics-dashboard-agent - Real-time analytics dashboards, ETL pipelines, multi-source data integration
**Repository:** https://github.com/Azeez1/TEST_AGENTS
