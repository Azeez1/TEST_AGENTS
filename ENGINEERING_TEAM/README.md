# ENGINEERING_TEAM - 5 Engineering & Infrastructure Agents

## 🎯 Overview

The **ENGINEERING_TEAM** contains 5 specialized agents for software engineering, infrastructure, security, and documentation. These agents have **full workspace access** and can work with all 28 agents across the 4 systems.

**Agents:**
- **devops-engineer** - Deployment, CI/CD, Docker, Kubernetes, cloud infrastructure
- **security-auditor** - Code security analysis, vulnerability scanning, compliance audits
- **frontend-developer** - React, Next.js, TypeScript, UI/UX, responsive web apps
- **backend-developer** - Python, FastAPI, REST APIs, databases, microservices
- **technical-writer** - Documentation, PRDs, technical specs, API docs, user guides

---

## 🚀 Quick Start

### Talk to Claude Code

```
"Use the devops-engineer to containerize the MARKETING_TEAM agents"
"Use the security-auditor to scan the workspace for hardcoded API keys"
"Use the frontend-developer to build a dashboard for the 28 agents"
"Use the backend-developer to create an API for agent management"
"Use the technical-writer to write a PRD for an agent control panel"
```

---

## 🤖 Agent Capabilities

### 1. DevOps Engineer
**Purpose:** Cloud deployment, containerization, CI/CD pipelines

**Capabilities:**
- ✅ Dockerize Python applications (Streamlit, FastAPI)
- ✅ Create docker-compose configurations
- ✅ Build CI/CD pipelines (GitHub Actions, GitLab CI)
- ✅ Infrastructure as Code (Terraform, CloudFormation)
- ✅ Kubernetes deployments and services
- ✅ Cloud deployment (AWS, GCP, Azure)

**Example Tasks:**
```
"Use devops-engineer to create a Dockerfile for USER_STORY_AGENT"
"Use devops-engineer to build a GitHub Actions pipeline for testing"
"Use devops-engineer to deploy MARKETING_TEAM to AWS ECS"
```

**Outputs:** `outputs/docker/`, `outputs/cicd/`, `outputs/infrastructure/`

---

### 2. Security Auditor
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
"Use security-auditor to scan all Python files for hardcoded credentials"
"Use security-auditor to audit MARKETING_TEAM email security"
"Use security-auditor to check for SQL injection vulnerabilities"
```

**Outputs:** `outputs/security/audits/`, `outputs/security/scans/`

**Special Focus:**
- API key management across 28 agents
- Email security (MARKETING_TEAM Gmail integration)
- File upload security (USER_STORY_AGENT)
- OAuth token security (Google Workspace)

---

### 3. Frontend Developer
**Purpose:** Modern web applications, UI/UX design, dashboards

**Capabilities:**
- ✅ React 18+ applications with TypeScript
- ✅ Next.js 14+ with App Router
- ✅ Responsive design (Tailwind CSS, shadcn/ui)
- ✅ Data visualization (charts, graphs)
- ✅ Admin dashboards and control panels
- ✅ Component libraries and design systems

**Example Tasks:**
```
"Use frontend-developer to build a dashboard to manage all 28 agents"
"Use frontend-developer to create a marketing content gallery"
"Use frontend-developer to build a test results viewer for TEST_AGENT"
```

**Outputs:** `outputs/frontend/nextjs/`, `outputs/frontend/react/`, `outputs/frontend/components/`

**Technologies:**
- React, Next.js, TypeScript
- Tailwind CSS, shadcn/ui
- Chart.js, Recharts
- React Hook Form, Zod

---

### 4. Backend Developer
**Purpose:** APIs, databases, microservices, async programming

**Capabilities:**
- ✅ FastAPI REST APIs with automatic docs
- ✅ Database design (PostgreSQL, MongoDB, Redis)
- ✅ GraphQL APIs (Strawberry)
- ✅ WebSocket real-time communication
- ✅ Microservices architecture
- ✅ Background task queues (Celery, Redis)

**Example Tasks:**
```
"Use backend-developer to create an API for agent management"
"Use backend-developer to build a database schema for tracking agent executions"
"Use backend-developer to create a task queue for async agent operations"
```

**Outputs:** `outputs/backend/apis/`, `outputs/backend/models/`, `outputs/backend/services/`

**Technologies:**
- FastAPI, Flask, Django
- PostgreSQL, Redis, MongoDB
- SQLAlchemy, Celery
- JWT, OAuth 2.0

---

### 5. Technical Writer
**Purpose:** Documentation, PRDs, technical specs, API docs

**Capabilities:**
- ✅ Product Requirements Documents (PRDs)
- ✅ Technical specifications
- ✅ API documentation (OpenAPI/Swagger)
- ✅ System architecture diagrams (Mermaid, PlantUML)
- ✅ User guides and tutorials
- ✅ Release notes and changelogs

**Example Tasks:**
```
"Use technical-writer to write a PRD for an agent control dashboard"
"Use technical-writer to document the MARKETING_TEAM API"
"Use technical-writer to create a system architecture diagram for the workspace"
```

**Outputs:** `docs/prds/`, `docs/specs/`, `docs/api/`, `docs/guides/`, `docs/architecture/`

**Documentation Types:**
- PRDs: Product vision, requirements, success metrics
- Technical Specs: Architecture, data models, integrations
- API Docs: Endpoints, parameters, responses
- User Guides: Step-by-step instructions, screenshots

---

## 🌐 Workspace-Wide Access

All ENGINEERING_TEAM agents can access and work with:

| System | Agents | What Engineering Agents Can Do |
|--------|--------|--------------------------------|
| **MARKETING_TEAM/** | 17 agents | Deploy agents, audit security, build dashboards, document APIs |
| **TEST_AGENT/** | 5 agents | Review test code, containerize, build CI/CD, document testing strategy |
| **USER_STORY_AGENT/** | 1 app | Dockerize Streamlit app, security audit, create web alternative |
| **ENGINEERING_TEAM/** | 5 agents | Self-improvement, documentation, deployment |

**Cross-Team Collaboration:**
- DevOps can deploy any of the 28 agents
- Security Auditor can scan all 4 systems
- Frontend Developer can build UIs for any system
- Backend Developer can create APIs for all agents
- Technical Writer can document all 28 agents

---

## 📂 Folder Structure

```
ENGINEERING_TEAM/
├── .claude/
│   ├── agents/                  ← 5 agent definitions
│   │   ├── devops-engineer.md
│   │   ├── security-auditor.md
│   │   ├── frontend-developer.md
│   │   ├── backend-developer.md
│   │   └── technical-writer.md
│   └── settings.json            ← Workspace-wide access config
│
├── tools/                       ← Shared engineering tools
├── scripts/                     ← Utility scripts
├── memory/                      ← Configuration and memory
│   └── config.json              ← Workspace info, deployment defaults
│
├── outputs/                     ← Generated deliverables (gitignored)
│   ├── docker/
│   ├── cicd/
│   ├── infrastructure/
│   ├── security/
│   │   ├── audits/
│   │   └── scans/
│   ├── frontend/
│   │   ├── nextjs/
│   │   ├── react/
│   │   └── components/
│   └── backend/
│       ├── apis/
│       ├── models/
│       └── services/
│
├── docs/                        ← Documentation
│   ├── prds/                    ← Product Requirements Documents
│   ├── specs/                   ← Technical specifications
│   ├── api/                     ← API documentation
│   ├── guides/                  ← User guides
│   ├── architecture/            ← Architecture diagrams
│   └── deployments/             ← Deployment documentation
│
├── requirements.txt             ← Python dependencies
└── README.md                    ← This file
```

---

## 🛠️ Setup

### Install Dependencies

```bash
cd ENGINEERING_TEAM
pip install -r requirements.txt
```

**Key Dependencies:**
- FastAPI, uvicorn - API development
- Docker, Kubernetes - Containerization
- SQLAlchemy, Redis - Databases
- Celery - Task queues
- Bandit, Safety - Security scanning
- Pytest - Testing
- MkDocs - Documentation

---

## 💡 Common Use Cases

### 1. Containerize an Agent System
```
"Use devops-engineer to create a Docker configuration for MARKETING_TEAM
that includes all 17 agents, their Python dependencies, and environment variables"
```

**Result:** Dockerfile, docker-compose.yml, .dockerignore

---

### 2. Security Audit the Workspace
```
"Use security-auditor to scan the entire workspace for:
- Hardcoded API keys
- SQL injection vulnerabilities
- Insecure file uploads
- Missing input validation"
```

**Result:** Security audit report with severity ratings and remediation steps

---

### 3. Build an Agent Control Dashboard
```
"Use frontend-developer to build a Next.js dashboard with:
- List of all 28 agents with status indicators
- Ability to trigger agent tasks
- Real-time task execution monitoring
- Marketing content gallery"
```

**Result:** Production-ready Next.js application

---

### 4. Create an Agent Management API
```
"Use backend-developer to build a FastAPI service that:
- Lists all available agents
- Executes agent tasks
- Tracks task history
- Provides authentication with JWT"
```

**Result:** FastAPI application with OpenAPI docs

---

### 5. Write a PRD for New Feature
```
"Use technical-writer to write a PRD for an 'Agent Scheduling System'
that allows users to schedule recurring agent tasks with cron-like syntax"
```

**Result:** Complete PRD with user stories, technical requirements, and success metrics

---

## 🎯 Example Workflows

### Complete Deployment Pipeline
```
1. "Use security-auditor to scan MARKETING_TEAM for vulnerabilities"
2. "Use devops-engineer to create Docker containers for all 17 agents"
3. "Use devops-engineer to build a GitHub Actions CI/CD pipeline"
4. "Use technical-writer to document the deployment process"
```

### Build Full-Stack Agent Dashboard
```
1. "Use backend-developer to create a FastAPI agent management API"
2. "Use frontend-developer to build a Next.js dashboard UI"
3. "Use devops-engineer to containerize both frontend and backend"
4. "Use security-auditor to audit the dashboard for security issues"
5. "Use technical-writer to write user documentation"
```

---

## 🔐 Security Best Practices

All ENGINEERING_TEAM agents follow these security standards:

1. ✅ **Never hardcode secrets** - Use environment variables
2. ✅ **Scan before deploy** - Security audit all code
3. ✅ **Least privilege** - Minimal permissions
4. ✅ **Input validation** - Validate all user inputs
5. ✅ **Audit logging** - Track all sensitive operations

**Security Scanning:**
```bash
# Run security scans
bandit -r . -ll          # Python code scanning
safety check             # Dependency vulnerabilities
pip-audit                # Dependency auditing
```

---

## 📊 Agent Statistics

**Total Workspace:**
- 28 AI agents across 4 teams
- 23 existing + 5 new engineering agents
- 4 systems (MARKETING_TEAM, TEST_AGENT, USER_STORY_AGENT, ENGINEERING_TEAM)

**ENGINEERING_TEAM Agents:**
- 5 specialized engineering agents
- Full workspace access
- Cross-team collaboration enabled
- 17 skills available (inherited from workspace)
- 7 MCP servers (playwright, google-workspace, perplexity, bright-data, n8n-mcp, sequential-thinking, fetch)

---

## 📖 Documentation

- **Main Workspace Docs:** `../claude.md` - Complete repository guide
- **Multi-Agent Guide:** `../MULTI_AGENT_GUIDE.md` - How to use all 28 agents
- **Agent Definitions:** `.claude/agents/` - Individual agent instructions

---

## 🚦 Next Steps

1. **Deploy an Agent System**
   ```
   "Use devops-engineer to containerize USER_STORY_AGENT"
   ```

2. **Run Security Audit**
   ```
   "Use security-auditor to scan for hardcoded API keys"
   ```

3. **Build a Dashboard**
   ```
   "Use frontend-developer to create an agent control panel"
   ```

4. **Create API Documentation**
   ```
   "Use technical-writer to document MARKETING_TEAM tools API"
   ```

5. **Write a PRD**
   ```
   "Use technical-writer to write a PRD for agent analytics"
   ```

---

**Last Updated:** 2025-10-21
**Version:** 1.0
**Repository:** https://github.com/Azeez1/TEST_AGENTS
