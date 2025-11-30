# Glossary

Definitions of key terms used throughout TEST_AGENTS documentation.

---

## A

### Absolute Path
The complete path to a file from the root directory.
- Example: `/home/user/TEST_AGENTS/MARKETING_TEAM/memory/brand_voice.json`
- Contrast with: Relative path (`memory/brand_voice.json`)
- **See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

### Agent
A specialized AI assistant with specific capabilities and tools.
- Example: `copywriter`, `research-agent`, `visual-designer`, `deal-analyst`, `sdr-agent`
- TEST_AGENTS has 59 agents across 7 teams
- **See:** [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)

### Agent Coordination
When multiple agents work together on a task.
- Example: content-strategist coordinates copywriter, editor, email-specialist
- Agents coordinate automatically based on their definitions
- **See:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)

### Agent Definition
The markdown file (`.md`) that defines an agent's capabilities, tools, and behavior.
- Location: `.claude/agents/{agent-name}.md`
- Contains: YAML frontmatter + instructions + examples
- **See:** Individual agent files in `.claude/agents/`

### Agent Invocation
The act of requesting an agent to perform a task.
- Pattern: `Task(agent-name): Do X`
- Example: `Task(copywriter): Write a blog post about AI`
- **See:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)

### API Key
Authentication credential for external services.
- Examples: OpenAI API key, Google credentials, Perplexity API key
- Storage: `.env` file (never commit to git)
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)

---

## B

### Brand Voice
The consistent tone, style, and messaging used across all content.
- Configuration: `MARKETING_TEAM/memory/brand_voice.json`
- Enforced by: editor agent
- Example: "Dux Machina's Tech Samurai meets McKinsey Strategist voice"
- **See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

### Bright Data
Web scraping service used for lead generation and competitive analysis.
- Used by: lead-gen-agent, analyst, seo-specialist
- APIs: SERP scraping, LinkedIn data, company info
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Bright Data section

---

## C

### Capabilities
The specific functions an agent can perform.
- Declared in: Agent YAML frontmatter
- Example: `- Twitter/X thread creation`, `- LinkedIn long-form posts`
- **See:** Individual agent definitions

### Configuration File
JSON files that store settings agents read.
- Location: `MARKETING_TEAM/memory/`
- Examples: `brand_voice.json`, `email_config.json`, `google_drive_config.json`
- **See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

### Consolidation
Combining multiple redundant agents, tools, or documents into one.
- Example: email-specialist + gmail-agent → email-manager
- Purpose: Reduce duplication, improve maintainability
- **See:** Audit reports in this conversation

### Custom Tool
A team-created tool for specific workflows.
- Examples: `identify_edge_cases`, `analyze_function`
- Priority: Third (after MCP and Skills)
- **See:** [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

---

## D

### Deprecated
No longer maintained or recommended for use.
- Storage: `archive/deprecated/` directory
- Examples: Old workspace enforcement docs
- **See:** `archive/` directory

### Document Generation
Creating formatted documents (PDFs, PowerPoints, Word docs, spreadsheets).
- Skills: pdf, pptx, docx
- Agents: pdf-specialist, presentation-designer
- Note: xlsx not enabled (use Google Sheets MCP instead)
- **See:** [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Document Generation section

---

## E

### Editor Agent
Quality assurance agent that reviews content for brand voice compliance.
- Location: `MARKETING_TEAM/.claude/agents/editor.md`
- Reviews: Blog posts, emails, social media, landing pages, PDFs, presentations
- Scoring: 0-10 scale (target: 7+)
- **See:** `MARKETING_TEAM/.claude/agents/editor.md`

### Editor Review Workflow
Mandatory QA process for brand-facing content.
- Steps: Create → Invoke editor → Revise if needed → Deliver when approved
- Applies to: All external marketing content
- **See:** Agent definitions (copywriter, email-specialist, etc.)

### ENGINEERING_TEAM
Team of 14 agents focused on software development.
- Agents: cto, system-architect, backend-architect, frontend-developer, test-engineer, etc.
- Location: `ENGINEERING_TEAM/`
- **See:** [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md)

### Environment Variable
System variable storing configuration (like API keys).
- Examples: `OPENAI_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`
- Storage: `.env` file or system environment
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)

---

## F

### Frontmatter
YAML metadata at the top of agent definition files.
- Format: Between `---` delimiters
- Contains: name, description, model, tools, skills, capabilities
- Example:
  ```yaml
  ---
  name: copywriter
  description: Creates brand-aligned content
  tools:
    - mcp__google-workspace__create_doc
  skills:
    - pdf
  ---
  ```

---

## G

### Gemini
Google's AI model used for video generation (Veo).
- Used by: video-producer agent
- Purpose: UGC ad video creation
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Gemini section

### Governance
Rules and processes for creating and managing tools, skills, and agents.
- Documents: 7 governance files
- Entry point: [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md)
- Key concept: Prevent duplication, maintain quality
- **See:** [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md)

### Google Workspace
Suite of Google services (Gmail, Drive, Sheets, Docs).
- MCP Server: `mcp__google-workspace__*`
- Used by: MARKETING_TEAM agents
- Setup: Requires service account credentials
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Google Workspace section

---

## H

### Historical
Archived for reference but no longer active.
- Storage: `archive/historical/` directory
- Example: `IMPLEMENTATION_SUMMARY.md`, `VEO_NANO_BANANA_INTEGRATION_COMPLETE.md`
- **See:** `archive/historical/` directory

---

## I

### Integration Test
Testing how multiple components work together.
- Agent: integration-test-agent (QA_TEAM)
- Scope: API endpoints, database connections, service integration
- **See:** `QA_TEAM/.claude/agents/integration-test-agent.md`

### Invocation Pattern
The standardized way to request agent actions.
- Format: `Task(agent-name): Clear instruction`
- ✅ Good: `Task(copywriter): Write a blog post about AI`
- ❌ Bad: `Task(copywriter): {"type": "blog", "topic": "AI"}`
- **See:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)

---

## M

### MARKETING_TEAM
Team of 17 agents focused on marketing and content.
- Agents: copywriter, editor, research-agent, visual-designer, video-producer, etc.
- Location: `MARKETING_TEAM/`
- **See:** [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md)

### MCP (Model Context Protocol)
Protocol for integrating external services with Claude.
- Examples: Google Workspace, Gmail, Drive, Sheets
- Priority: Highest (use MCP before skills or custom tools)
- Format: `mcp__service__tool-name`
- **See:** [MCP_SETUP.md](MCP_SETUP.md), [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

### MCP Server
A server implementing the Model Context Protocol.
- Examples: `mcp__google-drive`, `mcp__gmail`, `mcp__perplexity`
- Installation: Via npm or other package managers
- Configuration: In Claude desktop config
- **See:** [MCP_SETUP.md](MCP_SETUP.md)

### Memory File
JSON configuration file that agents read.
- Location: `{TEAM}/memory/`
- Examples: `brand_voice.json`, `email_config.json`
- Purpose: Maintain consistency across agents
- **See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

### Memory System
The configuration management system for agents.
- Storage: Team-specific memory folders
- Access: Agents read at startup and during operations
- Files: JSON format with specific schemas
- **See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

### Multi-Agent Coordination
See: Agent Coordination

---

## N

### n8n
Workflow automation platform used by automation-agent.
- Purpose: Orchestrate multi-tool workflows
- Used by: automation-agent (MARKETING_TEAM)
- Setup: Self-hosted or cloud
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - n8n section

---

## O

### OpenAI
AI company providing GPT-4 and DALL-E APIs.
- Used by: Multiple agents for content and image generation
- APIs: GPT-4o (text), DALL-E (images)
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - OpenAI section

### Output Directory
Location where agents save generated content.
- Pattern: `{TEAM}/outputs/`
- Examples: `MARKETING_TEAM/outputs/`, `QA_TEAM/outputs/`
- Best practice: Always use absolute paths
- **See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

---

## P

### Perplexity
AI-powered search and research service.
- Used by: research-agent, analyst, seo-specialist
- Features: Web search, citations, SERP analysis
- **See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Perplexity section

### Pre-Flight Checks
Checklist to complete before creating new tools.
- Purpose: Prevent duplication
- Steps: Check TOOL_REGISTRY, verify priority hierarchy, validate need
- **See:** [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)

### Priority Hierarchy
Order of preference for tool selection.
- Order: MCP → Skill → Custom Tool → Create New
- Purpose: Use existing solutions before creating new ones
- **See:** [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

### PROPOSAL_TEAM
Team with 1 agent focused on RFP parsing and proposal generation.
- Agent: rfp-agent
- Location: `PROPOSAL_TEAM/`
- **See:** [PROPOSAL_TEAM/README.md](PROPOSAL_TEAM/README.md)

---

## Q

### QA_TEAM
Team of 5 agents focused on quality assurance and testing.
- Agents: unit-test-agent, integration-test-agent, edge-case-agent, fixture-agent, test-orchestrator
- Location: `QA_TEAM/`
- **See:** [QA_TEAM/README.md](QA_TEAM/README.md)

### Quality Score
Numerical rating (0-100) from supervisor or editor.
- Editor: 0-10 scale for brand voice compliance (target: 7+)
- Supervisor: 0-100 scale for overall quality (target: 70+)
- **See:** [SUPERVISOR_ARCHITECTURE.md](SUPERVISOR_ARCHITECTURE.md)

---

## R

### Redundancy
Duplication of tools, skills, agents, or documentation.
- Problem: Increases maintenance burden, causes confusion
- Solution: Consolidation
- Detection: Regular audits via TOOL_AUDITOR_CHECKLIST.md
- **See:** [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md)

### Relative Path
Path from current directory (not recommended).
- Example: `memory/brand_voice.json` (where is memory?)
- Issue: Ambiguous, causes "file not found" errors
- Solution: Use absolute paths instead
- **See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

---

## S

### Session ID
Unique identifier for a git branch/session.
- Format: Long alphanumeric string
- Example: `01694mTUfmUevsSwYpgbUTQY`
- Usage: Branch name must end with session ID
- **See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Git Issues

### Skill
Official Claude skill for specific functionality.
- Location: `.claude/skills/`
- Examples: pdf, pptx, docx, algorithmic-art, slack-gif-creator
- Priority: Second (after MCP, before custom tools)
- **See:** [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)

### Supervisor
Root-level agent that performs cross-team quality verification.
- Location: `.claude/agents/supervisor.md`
- Purpose: Verify deliverables meet quality standards
- Output: Verification status, quality score, issues, recommendations
- **See:** [SUPERVISOR_ARCHITECTURE.md](SUPERVISOR_ARCHITECTURE.md)

---

## T

### Team
A group of related agents.
- Teams: MARKETING_TEAM, ENGINEERING_TEAM, QA_TEAM, PROPOSAL_TEAM, USER_STORY_AGENT
- Structure: Each team has own directory with agents, memory, outputs
- **See:** Team-specific README files

### Tool
A function or capability that agents can use.
- Types: MCP servers, skills, custom tools
- Registry: [TOOL_REGISTRY.md](TOOL_REGISTRY.md)
- Governance: [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

### Tool Registry
Master inventory of all tools, skills, and MCPs.
- File: [TOOL_REGISTRY.md](TOOL_REGISTRY.md)
- Purpose: Prevent duplication, document capabilities
- Maintenance: Update when adding new tools
- **See:** [TOOL_REGISTRY.md](TOOL_REGISTRY.md)

---

## U

### UGC (User-Generated Content)
Content that appears to be created by users, often used in ads.
- Agent: video-producer
- Technology: Image-to-video (Veo, Sora)
- Use case: Social media ad videos
- **See:** [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - UGC Video Workflow

### Unit Test
Testing individual functions or components in isolation.
- Agent: unit-test-agent (QA_TEAM)
- Framework: pytest (Python)
- **See:** `QA_TEAM/.claude/agents/unit-test-agent.md`

---

## V

### Verification
Quality assurance check performed by supervisor agent.
- Types: Requirement verification, brand voice check, technical validation
- Output: PASS/FAIL status + detailed feedback
- **See:** [SUPERVISOR_VERIFICATION_CRITERIA.md](SUPERVISOR_VERIFICATION_CRITERIA.md)

### Veo
Google's video generation model (part of Gemini).
- Used by: video-producer agent
- Purpose: Create UGC ad videos from text or images
- **See:** [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - UGC Video Workflow

---

## W

### Workspace
The root directory of TEST_AGENTS project.
- Path: `/home/user/TEST_AGENTS`
- Validation: Required before file operations
- **See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

### Workspace Enforcement
System ensuring agents use correct file paths.
- Requirements: Absolute paths, workspace validation
- Benefits: Prevents file errors, enables coordination
- **See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

### Workspace Validation
Checking that agents are in correct working directory.
- Commands: `pwd`, `ls`, directory structure check
- Required: Before all file operations
- **See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

---

## Y

### YAML Frontmatter
Metadata section at top of agent definition files.
- Format: Between `---` delimiters
- Contains: Agent configuration (name, tools, skills, capabilities)
- **See:** Agent definition files in `.claude/agents/`

---

## Related Documentation

- [GETTING_STARTED.md](GETTING_STARTED.md) - Setup guide
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All agents
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - Governance system
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Tool inventory
- [FAQ.md](FAQ.md) - Common questions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Debugging guide
