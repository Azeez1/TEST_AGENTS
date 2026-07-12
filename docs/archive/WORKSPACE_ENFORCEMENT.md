# Workspace Enforcement

This document defines workspace validation standards and enforcement mechanisms for all TEST_AGENTS.

## Purpose

Workspace enforcement ensures that:
- **Agents always know their working directory** - No ambiguity about file locations
- **File operations use absolute paths** - Prevents errors from relative path assumptions
- **Agent coordination is reliable** - Consistent workspace context across all agents
- **Troubleshooting is easier** - Clear validation errors guide debugging

## Core Concept

Every agent validates its workspace context at startup and uses absolute paths for all file operations.

**Key Principle:** Agents MUST NEVER assume their working directory. They MUST always validate and use absolute paths.

---

## Workspace Validation Standard

### 1. Workspace Context Block (Required)

All agents MUST include a workspace validation block in their agent definition:

```markdown
## 🏢 WORKSPACE CONTEXT & VALIDATION

**CRITICAL: Always validate workspace before operations**

### Workspace Detection
1. Run `pwd` to get current working directory
2. Validate this is the correct project root
3. Use absolute paths for ALL file operations
4. Never assume relative paths

### Required Workspace Structure
```
/absolute/path/to/TEST_AGENTS/
├── MARKETING_TEAM/
├── ENGINEERING_TEAM/
├── QA_TEAM/
├── PROPOSAL_TEAM/
├── .claude/
│   ├── agents/
│   ├── commands/
│   └── skills/
└── memory/
```

### Validation Commands
```bash
# Verify workspace
pwd

# Check directory structure
ls -la

# Validate team directories
ls MARKETING_TEAM ENGINEERING_TEAM QA_TEAM PROPOSAL_TEAM
```
```

### 2. File Operation Standards

**ALWAYS use absolute paths:**

```python
# GOOD - Absolute path
file_path = "/home/user/TEST_AGENTS/MARKETING_TEAM/memory/brand_voice.json"

# BAD - Relative path
file_path = "memory/brand_voice.json"
```

**For all file operations:**
- `read_file(absolute_path)`
- `write_file(absolute_path, content)`
- `edit_file(absolute_path, changes)`

### 3. Workspace Validation on Startup

Every agent MUST validate workspace before performing operations:

```python
# Step 1: Get current working directory
import os
workspace = os.getcwd()

# Step 2: Validate workspace structure
required_dirs = [
    f"{workspace}/MARKETING_TEAM",
    f"{workspace}/ENGINEERING_TEAM",
    f"{workspace}/QA_TEAM",
    f"{workspace}/PROPOSAL_TEAM",
    f"{workspace}/.claude",
    f"{workspace}/memory"
]

for dir_path in required_dirs:
    if not os.path.exists(dir_path):
        raise Exception(f"Invalid workspace: {dir_path} not found")

# Step 3: Proceed with operations using absolute paths
```

---

## Benefits of Workspace Enforcement

### 1. Eliminates Ambiguity
**Before workspace enforcement:**
```
Agent: "Read brand_voice.json"
System: "File not found" (where is it? which directory?)
```

**After workspace enforcement:**
```
Agent: "Read /home/user/TEST_AGENTS/memory/brand_voice.json"
System: "File read successfully"
```

### 2. Enables Multi-Agent Coordination
**Before:**
- Agent A writes to `outputs/report.json` (relative path)
- Agent B looks for `/home/user/outputs/report.json` (wrong location)
- Agent B fails to find file

**After:**
- Agent A writes to `/home/user/TEST_AGENTS/outputs/report.json` (absolute)
- Agent B reads from `/home/user/TEST_AGENTS/outputs/report.json` (absolute)
- Coordination succeeds

### 3. Simplifies Debugging
**Workspace validation errors are clear:**
```
ERROR: Invalid workspace detected
- Expected: /home/user/TEST_AGENTS
- Current: /home/user/
- Resolution: Navigate to correct directory and retry
```

### 4. Prevents Silent Failures
**Before:**
```python
# Agent silently creates file in wrong location
with open("config.json", "w") as f:
    f.write(config)
# File written to /home/user/config.json (wrong!)
```

**After:**
```python
# Agent validates workspace first
workspace = "/home/user/TEST_AGENTS"
config_path = f"{workspace}/memory/config.json"
with open(config_path, "w") as f:
    f.write(config)
# File written to /home/user/TEST_AGENTS/memory/config.json (correct!)
```

---

## Implementation Guide

### For Agent Definitions

**Required Sections:**

1. **Workspace Context Block** (see template above)
2. **File Operation Standards** (absolute paths only)
3. **Validation Examples** (show validation commands)

**Template:**
```markdown
## 🏢 WORKSPACE CONTEXT & VALIDATION

[Include standard workspace validation block]

## 🔒 WORKSPACE ENFORCEMENT (CRITICAL)

**ALWAYS use absolute paths for file operations.**

Example:
```bash
# Get workspace
pwd
# Output: /home/user/TEST_AGENTS

# Read file with absolute path
cat /home/user/TEST_AGENTS/memory/brand_voice.json
```

## 📁 File Operations

All file operations MUST use absolute paths:
- `/home/user/TEST_AGENTS/MARKETING_TEAM/outputs/campaign.json`
- `/home/user/TEST_AGENTS/memory/email_config.json`
- `/home/user/TEST_AGENTS/QA_TEAM/test_results/summary.json`
```

### For Python Scripts

```python
import os

# Get workspace
workspace = os.getenv("WORKSPACE", "/home/user/TEST_AGENTS")

# Validate workspace
assert os.path.exists(f"{workspace}/MARKETING_TEAM"), "Invalid workspace"

# Use absolute paths
config_file = f"{workspace}/memory/brand_voice.json"
with open(config_file, "r") as f:
    config = json.load(f)
```

### For Bash Scripts

```bash
# Get workspace
WORKSPACE="${WORKSPACE:-/home/user/TEST_AGENTS}"

# Validate workspace
if [ ! -d "$WORKSPACE/MARKETING_TEAM" ]; then
    echo "ERROR: Invalid workspace"
    exit 1
fi

# Use absolute paths
CONFIG="$WORKSPACE/memory/email_config.json"
cat "$CONFIG"
```

---

## Common Patterns

### Pattern 1: Memory File Access

**Always use absolute paths for memory files:**

```python
workspace = "/home/user/TEST_AGENTS"
memory_files = {
    "brand_voice": f"{workspace}/memory/brand_voice.json",
    "email_config": f"{workspace}/memory/email_config.json",
    "visual_guidelines": f"{workspace}/memory/visual_guidelines.json"
}

# Read brand voice
with open(memory_files["brand_voice"], "r") as f:
    brand_voice = json.load(f)
```

### Pattern 2: Team Output Files

**Use team-specific output directories:**

```python
workspace = "/home/user/TEST_AGENTS"
team = "MARKETING_TEAM"
output_dir = f"{workspace}/{team}/outputs"

# Create output file
output_file = f"{output_dir}/campaign_report.json"
with open(output_file, "w") as f:
    json.dump(report, f, indent=2)
```

### Pattern 3: Multi-Agent Coordination

**Agent A (Producer):**
```python
workspace = "/home/user/TEST_AGENTS"
output_file = f"{workspace}/MARKETING_TEAM/outputs/research_results.json"

# Write results
with open(output_file, "w") as f:
    json.dump(results, f)

print(f"Results written to: {output_file}")
```

**Agent B (Consumer):**
```python
workspace = "/home/user/TEST_AGENTS"
input_file = f"{workspace}/MARKETING_TEAM/outputs/research_results.json"

# Read results
with open(input_file, "r") as f:
    results = json.load(f)

# Process results
```

---

## Troubleshooting

### Issue 1: "File not found" errors

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'
```

**Solution:**
1. Verify workspace: `pwd`
2. Use absolute path: `/home/user/TEST_AGENTS/memory/config.json`
3. Check file exists: `ls /home/user/TEST_AGENTS/memory/config.json`

### Issue 2: Agent using wrong directory

**Symptom:**
```
Agent writes file to /home/user/outputs/ instead of /home/user/TEST_AGENTS/outputs/
```

**Solution:**
1. Add workspace validation to agent definition
2. Update all file paths to absolute paths
3. Test with `pwd` to confirm workspace

### Issue 3: Multi-agent coordination fails

**Symptom:**
```
Agent B cannot find file created by Agent A
```

**Solution:**
1. Both agents use absolute paths
2. Verify both agents validate workspace on startup
3. Use consistent path format: `/home/user/TEST_AGENTS/{TEAM}/outputs/{file}`

### Issue 4: Invalid workspace detected

**Symptom:**
```
ERROR: Invalid workspace detected
Expected: /home/user/TEST_AGENTS
Current: /home/user/
```

**Solution:**
```bash
# Navigate to correct workspace
cd /home/user/TEST_AGENTS

# Verify workspace
pwd
ls MARKETING_TEAM ENGINEERING_TEAM QA_TEAM PROPOSAL_TEAM

# Retry operation
```

---

## Validation Checklist

Use this checklist to validate workspace enforcement in agent definitions:

- [ ] Workspace context block included in agent definition
- [ ] File operations use absolute paths only
- [ ] Workspace validation on startup (pwd, ls verification)
- [ ] Memory file access uses absolute paths
- [ ] Output file paths are absolute
- [ ] Multi-agent coordination uses absolute paths
- [ ] Error messages include full paths for debugging
- [ ] Examples demonstrate absolute path usage

---

## Standards by Team

### MARKETING_TEAM

**Standard Paths:**
```
/home/user/TEST_AGENTS/MARKETING_TEAM/
├── memory/
│   ├── brand_voice.json
│   ├── email_config.json
│   └── visual_guidelines.json
├── outputs/
│   ├── campaigns/
│   ├── content/
│   └── reports/
└── .claude/agents/
```

**Validation:**
```bash
pwd
ls /home/user/TEST_AGENTS/MARKETING_TEAM/memory
```

### ENGINEERING_TEAM

**Standard Paths:**
```
/home/user/TEST_AGENTS/ENGINEERING_TEAM/
├── components/
├── docs/
├── outputs/
└── .claude/agents/
```

**Validation:**
```bash
pwd
ls /home/user/TEST_AGENTS/ENGINEERING_TEAM/components
```

### QA_TEAM

**Standard Paths:**
```
/home/user/TEST_AGENTS/QA_TEAM/
├── test_results/
├── fixtures/
├── outputs/
└── .claude/agents/
```

**Validation:**
```bash
pwd
ls /home/user/TEST_AGENTS/QA_TEAM/test_results
```

### PROPOSAL_TEAM

**Standard Paths:**
```
/home/user/TEST_AGENTS/PROPOSAL_TEAM/
├── knowledge_base/
├── outputs/
└── .claude/agents/
```

**Validation:**
```bash
pwd
ls /home/user/TEST_AGENTS/PROPOSAL_TEAM/knowledge_base
```

---

## Related Documentation

- [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - Workspace troubleshooting section
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - Workspace enforcement overview
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Debugging workspace issues
- [GLOSSARY.md](GLOSSARY.md) - Workspace terminology

---

## Summary

**Core Principles:**
1. ✅ Always validate workspace on startup (`pwd`, `ls`)
2. ✅ Always use absolute paths for file operations
3. ✅ Never assume relative paths or working directory
4. ✅ Include workspace validation in all agent definitions
5. ✅ Use consistent path format across all agents

**Quick Validation:**
```bash
# Am I in the right workspace?
pwd
# Expected: /home/user/TEST_AGENTS

# Does the workspace structure exist?
ls MARKETING_TEAM ENGINEERING_TEAM QA_TEAM PROPOSAL_TEAM .claude memory
# All directories should exist
```

**Remember:** Workspace enforcement prevents 90% of file operation errors in multi-agent systems.
