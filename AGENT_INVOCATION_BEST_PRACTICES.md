# Agent Invocation Best Practices

**For AI Assistants:** Claude Code, Cursor, and other AI development tools

This guide explains how to properly invoke the 37 autonomous agents in this repository to avoid duplicate code and ensure agents use their declared tools.

---

## 🎯 Core Principle: Trust Agent Autonomy

**Agents are fully autonomous.** Each agent:
- Has tools declared in YAML frontmatter (`.claude/agents/*.md`)
- Knows which memory files to read (`memory/*.json`)
- Has explicit workflow instructions in its definition
- Can complete entire workflows from start to finish

**Your role as orchestrator:** Specify WHAT you want, not HOW to do it.

---

## ✅ Correct Invocation Patterns

### Pattern 1: Single Agent Task
**Format:** `"Use [agent-name] to [goal] with [context]"`

**Examples:**
```
✅ "Use copywriter to create 2000-word blog about AI automation"
✅ "Use visual-designer to create LinkedIn header image with brand colors"
✅ "Use pdf-specialist to create whitepaper and upload to Google Drive"
✅ "Use gmail-agent to send Engineering_Team_Partner_Summary.docx"
```

**Key:** Let agent own the ENTIRE workflow. If pdf-specialist creates a PDF, it also uploads it (has `upload_to_drive` tool declared).

### Pattern 2: Multi-Agent Campaign
**Format:** `"Use [coordinator-agent] to [complex-goal]"`

**Examples:**
```
✅ "Use router-agent to coordinate product launch campaign"
✅ "Use content-strategist to plan Q1 content calendar"
✅ "Use cto to design and deploy microservices architecture"
```

**Key:** Coordinator agents (router-agent, content-strategist, cto) will delegate to specialists autonomously.

### Pattern 3: Research Then Create
**Format:** `"Use [research-agent] then [creation-agent]"`

**Examples:**
```
✅ "Use research-agent to analyze AI trends, then use copywriter to write blog"
✅ "Use seo-specialist to research keywords, then use landing-page-specialist to build page"
```

**Key:** Sequential delegation - wait for research results before invoking creation agent.

---

## 🏢 Workspace Context in Invocations

All agents now have **automatic workspace awareness** - you no longer need to specify the team folder in every invocation.

### Before Workspace Enforcement

❌ **Old way (confusing):**
```
"Use the copywriter agent to write a blog and save it to MARKETING_TEAM/outputs/blog_posts/"
"Make sure you're in MARKETING_TEAM folder"
"Read from MARKETING_TEAM/memory/brand_voice.json"
```

### After Workspace Enforcement

✅ **New way (automatic):**
```
"Use copywriter to write a blog about AI trends"
```

**What happens automatically:**
1. Agent validates it's in MARKETING_TEAM workspace
2. Agent reads from MARKETING_TEAM/memory/ automatically
3. Agent saves to MARKETING_TEAM/outputs/blog_posts/ automatically
4. Agent uses absolute paths internally
5. User never needs to specify folders

---

## 🔄 Cross-Team Invocations

**Scenario:** Marketing needs QA to test their tools

✅ **Correct invocation:**
```
"Use test-orchestrator to scan MARKETING_TEAM/tools/ and generate tests"
```

**What happens:**
1. test-orchestrator validates it's in QA_TEAM workspace ✅
2. test-orchestrator READS from MARKETING_TEAM/tools/ ✅ (allowed)
3. test-orchestrator WRITES tests to QA_TEAM/tests/marketing/ ✅ (correct location)
4. Cross-team boundary respected ✅

❌ **Incorrect (would fail):**
```
"Use test-orchestrator to save tests to MARKETING_TEAM/tests/"
```
→ Workspace enforcer blocks this (QA agents can't write to MARKETING_TEAM)

---

## 🛠️ Workspace Troubleshooting

**If agent says "Workspace validation failed":**

1. Check current directory: `pwd`
2. Expected directory: `TEST_AGENTS` or `TEST_AGENTS/{TEAM_NAME}/`
3. Navigate if needed: `cd TEST_AGENTS/`
4. Re-invoke agent

**If files end up in wrong location:**
- Check agent used workspace_enforcer tool
- Verify agent used absolute paths
- Run: `pytest tests/test_workspace_enforcement.py`

---

## ❌ Anti-Patterns (What NOT To Do)

### Anti-Pattern 1: Over-Specification
```
❌ BAD: "Use gmail-agent. Read memory/email_config.json. Import send_email_with_attachment.py. Call send_email()..."

Why bad: Triggers script creation mode instead of agent invocation
Result: Creates temp_send_email.py (duplicate code)

✅ GOOD: "Use gmail-agent to send whitepaper.pdf"

Why good: Agent reads its definition → sees tools declared → uses them
Result: Agent imports send_email_with_attachment tool and sends email
```

### Anti-Pattern 2: Orchestrator Taking Over Mid-Workflow
```
❌ BAD:
User: "Create ebook and upload to Drive"
Orchestrator: Invokes pdf-specialist
pdf-specialist: Creates PDF
Orchestrator: Takes over, creates upload_final_ebook.py script

Why bad: Ignores pdf-specialist's declared upload_to_drive tool
Result: Duplicate upload script created

✅ GOOD:
User: "Create ebook and upload to Drive"
Orchestrator: "Use pdf-specialist to create ebook and upload to Drive"
pdf-specialist:
  1. Creates PDF using reportlab (pdf skill)
  2. Uploads using tools.upload_to_drive (declared tool)
  3. Returns Drive link

Why good: Agent completes entire workflow with its declared tools
Result: No duplicate code, uses battle-tested tool
```

### Anti-Pattern 3: Specifying Implementation Details
```
❌ BAD: "Use visual-designer to create image with GPT-4o using openai_gpt4o_image.py"

Why bad: Tells agent HOW to do it, not WHAT to create
Result: Agent may create new script instead of using existing tool

✅ GOOD: "Use visual-designer to create LinkedIn header with Dux Machina brand colors"

Why good: Agent knows it has openai_gpt4o_image tool declared
Result: Agent uses existing tool automatically
```

### Anti-Pattern 4: Mentioning Files/Imports
```
❌ BAD: "Use pdf-specialist. Import reportlab. Create SimpleDocTemplate..."

Why bad: Sounds like script instructions, not agent invocation
Result: May create standalone script with reportlab code

✅ GOOD: "Use pdf-specialist to create 5-chapter ebook about Dux Machina"

Why good: Agent knows it has pdf skill (which includes reportlab)
Result: Agent uses pdf skill's reportlab capabilities
```

---

## 🔍 Decision Tree: When to Invoke Agents

```
Task requested by user
│
├─ Is there a specialized agent for this task?
│  │
│  ├─ YES: Check agent's YAML frontmatter
│  │  │
│  │  ├─ Agent has required tools/skills declared?
│  │  │  │
│  │  │  ├─ YES → Invoke agent with minimal spec ✅
│  │  │  │        "Use [agent] to [goal] with [context]"
│  │  │  │
│  │  │  └─ NO → Add tool to agent definition, then invoke
│  │  │
│  │  └─ Unsure? → Read agent definition (.claude/agents/*.md)
│  │
│  └─ NO: Is this a common task worth creating an agent for?
│     │
│     ├─ YES → Create new agent with tools declared
│     └─ NO → Use direct tools/commands (non-agent task)
│
└─ Simple utility task (ls, grep, etc.)?
   └─ Use direct commands (no agent needed)
```

---

## 🧠 What Agents Already Know

### From Agent Definitions (`.claude/agents/*.md`)

**1. YAML Frontmatter:**
```yaml
---
name: PDF Specialist
tools:
  - upload_to_drive
  - generate_pdf
skills:
  - pdf
  - pdf-filler
  - canvas-design
---
```

**What this means:**
- Agent will use `tools.upload_to_drive` for uploads
- Agent will use `tools.generate_pdf` for PDF creation
- Agent can invoke pdf, pdf-filler, or canvas-design skills
- **You don't need to tell the agent to use these** - it already knows

**2. Configuration Files Section:**
```markdown
## ⚙️ Configuration Files (READ FIRST)

1. **memory/email_config.json** - Email defaults
2. **memory/google_drive_config.json** - Drive folder IDs
3. **memory/brand_voice.json** - Brand voice guidelines
```

**What this means:**
- Agent will read these files at task start
- **You don't need to tell the agent to read them** - it already knows
- Configuration is centralized, never hardcoded

**3. Workflow Instructions:**
```markdown
## Your Process

1. Read brand voice guidelines
2. Create content following guidelines
3. Upload to Google Drive
4. Deliver shareable link
```

**What this means:**
- Agent has step-by-step workflow defined
- **You don't need to specify steps** - agent follows its definition
- Agent owns entire workflow from start to finish

---

## 🔧 Troubleshooting Guide

### Problem 1: Duplicate Scripts Keep Getting Created

**Symptoms:**
- `temp_*.py`, `create_*.py`, `upload_*.py` scripts appear in outputs/
- Agent functionality duplicated in standalone scripts
- Existing tools in `tools/` folder ignored

**Root Cause:**
- Over-specified invocation → Orchestrator enters "script creation mode"
- Example: "Use agent. Read X. Import Y. Call Z..." → Creates script with those steps

**Solution:**
1. Use minimal invocation: `"Use [agent] to [goal]"`
2. Check agent's YAML frontmatter for declared tools
3. Trust agent to use its declared tools
4. Never mention file paths, imports, or function calls

**Example Fix:**
```
❌ Before: "Use gmail-agent. Read email_config.json. Import send_email_with_attachment..."
   Result: Created temp_send_email.py

✅ After: "Use gmail-agent to send whitepaper.pdf"
   Result: Agent used its declared send_email_with_attachment tool
```

### Problem 2: Agent Doesn't Use Its Declared Tools

**Symptoms:**
- Agent creates new implementation instead of using tool from YAML
- Agent claims "I don't have access to that tool"
- Tool exists in `tools/` but agent doesn't import it

**Root Cause:**
- Tool not declared in agent's YAML frontmatter
- Agent definition doesn't mention the tool in instructions

**Solution:**
1. Open agent definition: `.claude/agents/[agent-name].md`
2. Check YAML frontmatter - is tool listed under `tools:`?
3. If not listed → Add tool to YAML frontmatter
4. Update agent instructions to mention when to use the tool

**Example Fix:**
```yaml
# Before (missing upload_to_drive)
---
name: PDF Specialist
tools:
  - generate_pdf
---

# After (tool added)
---
name: PDF Specialist
tools:
  - generate_pdf
  - upload_to_drive  ✅
---
```

### Problem 3: Orchestrator Takes Over Mid-Workflow

**Symptoms:**
- Agent completes part of task (e.g., creates PDF)
- Orchestrator creates script for remaining steps (e.g., upload)
- Agent's workflow incomplete

**Root Cause:**
- Invocation doesn't include full workflow goal
- Example: "Use pdf-specialist to create ebook" → Missing "and upload"

**Solution:**
1. Specify complete workflow in invocation
2. Include upload/delivery in goal statement
3. Let agent own entire workflow

**Example Fix:**
```
❌ Before: "Use pdf-specialist to create ebook"
   Result: Agent creates PDF → Orchestrator creates upload script

✅ After: "Use pdf-specialist to create ebook and upload to Google Drive"
   Result: Agent creates PDF AND uploads using declared tool
```

### Problem 4: Agent Creates Files in Wrong Location

**Symptoms:**
- Files created in root directory instead of `outputs/`
- Drive uploads to wrong folder
- Email sent to wrong address

**Root Cause:**
- Agent didn't read memory configuration files
- Hardcoded paths/values used instead of config

**Solution:**
- This shouldn't happen if agent definition has "Configuration Files" section
- Check agent definition has instructions to read `memory/*.json`
- If missing, add configuration section to agent definition

**Example Agent Definition Section:**
```markdown
## ⚙️ Configuration Files (READ FIRST)

**ALWAYS read these memory files before starting work:**

1. **memory/google_drive_config.json** - Drive folder IDs
   - Used when: Uploading files
   - Required for: ALL Drive uploads
```

---

## 📚 Real-World Examples from Repository

### Example 1: Ebook Creation (pdf-specialist)

**❌ What Happened (Incorrect):**
```
User: "Create ebook and upload to Drive"
Orchestrator: Invokes pdf-specialist
pdf-specialist: Creates ebook PDF using reportlab
Orchestrator: Creates upload_final_ebook.py script to upload
```

**Why This Is Wrong:**
- pdf-specialist has `upload_to_drive` tool declared in YAML (line 15)
- Agent definition shows exact upload code (lines 206-215)
- Orchestrator ignored agent's capabilities and created duplicate script

**✅ What Should Happen (Correct):**
```
User: "Create ebook and upload to Drive"
Orchestrator: "Use pdf-specialist to create ebook and upload to Google Drive"
pdf-specialist:
  1. Reads agent definition → sees upload_to_drive tool
  2. Creates PDF using reportlab (pdf skill)
  3. Imports tools.upload_to_drive (declared tool)
  4. Uploads PDF to Drive
  5. Returns Drive link to orchestrator
```

**Lesson:** When agent's YAML declares a tool, orchestrator should NEVER create a script for that functionality.

### Example 2: Email with Attachment (gmail-agent)

**✅ Correct Invocation:**
```
"Use gmail-agent to send Engineering_Team_Partner_Summary.docx with professional message"
```

**What Happens:**
1. gmail-agent reads `memory/email_config.json` (knows to do this from definition)
2. Uses `send_email_with_attachment` tool (declared in YAML)
3. Sends email with proper formatting
4. Returns confirmation

**Why It Works:**
- Minimal invocation (WHAT not HOW)
- Agent owns entire workflow
- Uses declared tools and config files

### Example 3: Social Media Campaign (router-agent)

**✅ Correct Invocation:**
```
"Use router-agent to coordinate product launch campaign"
```

**What Happens:**
1. router-agent analyzes request → needs multiple deliverables
2. Delegates to copywriter → blog post
3. Delegates to social-media-manager → LinkedIn/Twitter posts
4. Delegates to visual-designer → header images
5. Delegates to email-specialist → launch email
6. Coordinates timeline and delivery
7. Returns complete campaign package

**Why It Works:**
- High-level goal only
- router-agent has coordination logic in its definition
- Each specialist uses their declared tools
- No duplicate scripts created

---

## 📊 Quick Reference: Invocation Checklist

Before invoking an agent, ask yourself:

- [ ] **Did I specify WHAT I want (not HOW to do it)?**
- [ ] **Did I check agent's YAML frontmatter for declared tools?**
- [ ] **Did I include the complete workflow goal (create + upload + deliver)?**
- [ ] **Did I avoid mentioning file paths, imports, or function calls?**
- [ ] **Am I letting the agent own the entire workflow?**
- [ ] **Did I trust the agent's definition instead of over-specifying?**

If you answered YES to all → Your invocation will work correctly ✅

If you answered NO to any → Revise your invocation to be more minimal ⚠️

---

## 🎯 Key Takeaways

1. **Agents are autonomous** - They know which tools to use from YAML frontmatter
2. **Specify WHAT, not HOW** - High-level goals only, no implementation details
3. **Trust agent definitions** - They have complete workflow instructions
4. **Let agents own workflows** - From creation to upload to delivery
5. **Orchestrator routes, agents execute** - Clear separation of responsibilities
6. **Check YAML before creating scripts** - If tool is declared, agent will use it
7. **Memory files are automatic** - Agents read them, you don't need to specify

---

## 📖 See Also

- **[claude.md](claude.md)** - Complete repository navigation guide
- **[MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)** - Master guide for all 37 agents
- **Agent Definitions:** `.claude/agents/*.md` files in each system folder
- **Memory Configuration:** `memory/*.json` files in MARKETING_TEAM folder

---

**Last Updated:** 2025-11-02
