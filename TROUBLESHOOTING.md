# Troubleshooting Guide

**Comprehensive debugging guide for the TEST_AGENTS multi-agent system**

This guide helps you diagnose and fix common issues when working with the 39 agents across MARKETING_TEAM, ENGINEERING_TEAM, QA_TEAM, PROPOSAL_TEAM, and the ROOT supervisor.

---

## Table of Contents

1. [Agent Invocation Issues](#agent-invocation-issues)
2. [Workspace Validation Errors](#workspace-validation-errors)
3. [API Configuration Problems](#api-configuration-problems)
4. [File Operation Errors](#file-operation-errors)
5. [Multi-Agent Coordination Failures](#multi-agent-coordination-failures)
6. [Memory File Issues](#memory-file-issues)
7. [Tool/Skill/MCP Problems](#toolskillmcp-problems)
8. [Editor Review Workflow Issues](#editor-review-workflow-issues)
9. [Supervisor Verification Issues](#supervisor-verification-issues)
10. [Common Error Messages](#common-error-messages)
11. [Debug Workflows](#debug-workflows)

---

## Agent Invocation Issues

### Problem 1: Agent Not Found

**Symptom:**
```
Error: Agent 'copywritter' not found
Agent definition does not exist
```

**Cause:**
- Typo in agent name
- Agent doesn't exist in the system
- Looking in wrong team folder

**Solution:**

**Step 1:** Verify agent name spelling
```bash
# List all agents by team
ls MARKETING_TEAM/.claude/agents/
ls ENGINEERING_TEAM/.claude/agents/
ls QA_TEAM/.claude/agents/
ls PROPOSAL_TEAM/.claude/agents/
ls .claude/agents/  # Root (supervisor)
```

**Step 2:** Check complete agent list
```bash
# See MULTI_AGENT_GUIDE.md for full list
cat MULTI_AGENT_GUIDE.md | grep "^-"
```

**Step 3:** Use correct invocation format
```
# Correct spelling
Task(copywriter): Write a blog post

# NOT: copywritter, copy-writer, or Copywriter
```

**Common Typos:**
- `copywritter` → `copywriter`
- `router` → `router-agent`
- `test-orchestrater` → `test-orchestrator`
- `gmail` → `gmail-agent`

---

### Problem 2: Agent Doesn't Use Declared Tools

**Symptom:**
```
Agent creates new script instead of using existing tool
Agent says "I don't have access to that tool"
Duplicate code created in outputs/ folder
```

**Cause:**
- Tool not declared in agent's YAML frontmatter
- Over-specified invocation (tells agent HOW instead of WHAT)
- Agent definition doesn't mention the tool

**Solution:**

**Step 1:** Check agent's tool declarations
```bash
# Read agent definition
cat MARKETING_TEAM/.claude/agents/pdf-specialist.md

# Look for YAML frontmatter:
# ---
# tools:
#   - upload_to_drive
#   - generate_pdf
# ---
```

**Step 2:** Update agent definition if tool missing
```yaml
# Add missing tool to YAML frontmatter
---
name: PDF Specialist
tools:
  - upload_to_drive  # Add this if missing
  - generate_pdf
skills:
  - pdf
  - pdf-filler
---
```

**Step 3:** Use minimal invocation (WHAT not HOW)
```
# ❌ WRONG - Over-specified
Task(pdf-specialist): Read brand_voice.json, import reportlab, create PDF, upload to Drive

# ✅ CORRECT - Minimal
Task(pdf-specialist): Create whitepaper and upload to Google Drive
```

**See:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) for detailed patterns

---

### Problem 3: Orchestrator Creates Duplicate Scripts

**Symptom:**
```
Files like temp_send_email.py, upload_final_ebook.py appear
Agent functionality duplicated in standalone scripts
Existing tools in tools/ folder ignored
```

**Cause:**
- Invocation too detailed (triggers "script creation mode")
- Agent's complete workflow not specified in invocation
- Orchestrator takes over mid-workflow

**Solution:**

**Step 1:** Use complete workflow specification
```
# ❌ WRONG - Incomplete workflow
Task(pdf-specialist): Create ebook
# Result: Agent creates PDF → Orchestrator creates upload script

# ✅ CORRECT - Complete workflow
Task(pdf-specialist): Create ebook and upload to Google Drive
# Result: Agent creates PDF AND uploads using declared tool
```

**Step 2:** Trust agent autonomy
```
# Let agent own ENTIRE workflow from start to finish
# Agent will:
# 1. Read configuration files
# 2. Use declared tools
# 3. Complete all steps
# 4. Return results
```

**Step 3:** Review agent YAML for complete tool set
```yaml
# If agent should upload, ensure it has the tool
---
tools:
  - generate_pdf
  - upload_to_drive  # ✅ Both tools declared
---
```

---

## Workspace Validation Errors

### Problem 4: Workspace Validation Failed

**Symptom:**
```
❌ Workspace validation failed for copywriter in MARKETING_TEAM
Error: Invalid workspace detected
Expected: /home/user/TEST_AGENTS
Current: /home/user/
```

**Cause:**
- Working directory not in TEST_AGENTS
- Team folder doesn't exist
- Required folders missing

**Solution:**

**Step 1:** Check current directory
```bash
pwd
# Should output: /home/user/TEST_AGENTS or similar
```

**Step 2:** Navigate to correct directory
```bash
cd /home/user/TEST_AGENTS
pwd  # Verify
```

**Step 3:** Verify team folders exist
```bash
ls -la
# Should show:
# MARKETING_TEAM/
# ENGINEERING_TEAM/
# QA_TEAM/
# PROPOSAL_TEAM/
# .claude/
# memory/
```

**Step 4:** Verify team structure
```bash
# For MARKETING_TEAM
ls MARKETING_TEAM/
# Should show: memory/ outputs/ tools/ .claude/

# For QA_TEAM
ls QA_TEAM/
# Should show: memory/ tests/ tools/ .claude/
```

**Step 5:** Create missing folders if needed
```bash
# Example: Create missing outputs folder
mkdir -p MARKETING_TEAM/outputs
mkdir -p MARKETING_TEAM/outputs/blog_posts
mkdir -p MARKETING_TEAM/outputs/images
mkdir -p MARKETING_TEAM/outputs/videos
```

---

### Problem 5: Agent Using Wrong Directory

**Symptom:**
```
Files created in /home/user/outputs/ instead of /home/user/TEST_AGENTS/MARKETING_TEAM/outputs/
Agent can't find configuration files
FileNotFoundError: No such file or directory: 'memory/brand_voice.json'
```

**Cause:**
- Agent using relative paths instead of absolute paths
- Agent not validating workspace before operations
- Workspace enforcer tool not being used

**Solution:**

**Step 1:** Verify agent uses workspace enforcer
```bash
# Check agent definition includes workspace validation
cat MARKETING_TEAM/.claude/agents/copywriter.md | grep -A 10 "WORKSPACE"
```

**Step 2:** Ensure agent definition has workspace context block
```markdown
## 🏢 WORKSPACE CONTEXT & VALIDATION

**CRITICAL: Always validate workspace before operations**

### Workspace Detection
1. Run `pwd` to get current working directory
2. Validate this is the correct project root
3. Use absolute paths for ALL file operations
4. Never assume relative paths
```

**Step 3:** Test workspace enforcer
```bash
# Run workspace enforcer test
python tools/workspace_enforcer.py

# Or test in Python
python -c "
from tools.workspace_enforcer import validate_workspace
result = validate_workspace('copywriter', 'MARKETING_TEAM')
print(result)
"
```

**Step 4:** Update agent to use absolute paths
```python
# ✅ CORRECT - Absolute path
from tools.workspace_enforcer import get_absolute_paths

paths = get_absolute_paths("MARKETING_TEAM")
config_path = f"{paths['memory']}/brand_voice.json"

# ❌ WRONG - Relative path
config_path = "memory/brand_voice.json"
```

**See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) for complete guide

---

### Problem 6: Cross-Team Boundary Violations

**Symptom:**
```
Error: QA agent trying to write to MARKETING_TEAM folder
Workspace enforcer blocks operation
Permission denied
```

**Cause:**
- Agent trying to save files outside its team folder
- Cross-team operation not properly structured

**Solution:**

**Step 1:** Understand team boundaries
```
✅ ALLOWED:
- QA agents READ from any team (for testing)
- QA agents WRITE to QA_TEAM/tests/

❌ BLOCKED:
- QA agents WRITE to MARKETING_TEAM/
- MARKETING agents WRITE to QA_TEAM/
```

**Step 2:** Use correct invocation for cross-team work
```
# ✅ CORRECT
Task(test-orchestrator): Scan MARKETING_TEAM/tools/ and generate tests in QA_TEAM/tests/marketing/

# ❌ WRONG
Task(test-orchestrator): Save tests to MARKETING_TEAM/tests/
```

**Step 3:** Verify team-specific output paths
```bash
# QA tests always go to QA_TEAM/tests/
ls QA_TEAM/tests/

# Marketing tests should be in subdirectory
ls QA_TEAM/tests/marketing/
```

---

## API Configuration Problems

### Problem 7: OpenAI API Key Not Found

**Symptom:**
```
Error: OpenAI API key not configured
openai.error.AuthenticationError: No API key provided
Image generation failed
```

**Cause:**
- OPENAI_API_KEY environment variable not set
- API key not in .env file
- API key expired or invalid

**Solution:**

**Step 1:** Check if API key is set
```bash
echo $OPENAI_API_KEY
# Should output: sk-... (your key)
```

**Step 2:** Set environment variable
```bash
# Temporary (current session only)
export OPENAI_API_KEY="sk-your-key-here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Step 3:** Create .env file
```bash
# Create .env in project root
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-anthropic-key
EOF

# Ensure .env is gitignored
echo ".env" >> .gitignore
```

**Step 4:** Verify API key works
```bash
# Test OpenAI connection
python MARKETING_TEAM/scripts/test_openai_connection.py

# Or test directly
python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
print('OpenAI API key configured successfully')
"
```

**Step 5:** Get new API key if needed
```
1. Visit: https://platform.openai.com/api-keys
2. Sign in
3. Click "Create new secret key"
4. Copy and save key (you won't see it again)
5. Update OPENAI_API_KEY environment variable
```

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) for complete setup

---

### Problem 8: Google Workspace MCP Not Connected

**Symptom:**
```
Error: MCP server 'google-workspace' not found
Gmail agent can't send emails
Drive uploads fail
```

**Cause:**
- Google Workspace MCP server not installed
- MCP server not configured in .mcp.json
- Authentication credentials missing

**Solution:**

**Step 1:** Check MCP server status
```bash
# List active MCP servers
claude mcp list
# Should show: google-workspace: ✓ Connected
```

**Step 2:** Install Google Workspace MCP server
```bash
npm install -g @modelcontextprotocol/server-google-workspace
```

**Step 3:** Configure MCP server
```bash
# Check .mcp.json configuration
cat .mcp.json

# Should contain:
# {
#   "mcpServers": {
#     "google-workspace": {
#       "command": "npx",
#       "args": ["@modelcontextprotocol/server-google-workspace"],
#       "env": {
#         "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json"
#       }
#     }
#   }
# }
```

**Step 4:** Set up Google credentials
```bash
# Create credentials directory
mkdir -p credentials

# Download credentials from Google Cloud Console
# https://console.cloud.google.com/

# Move credentials file
mv ~/Downloads/credentials.json credentials/google_credentials.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/credentials/google_credentials.json"
```

**Step 5:** Restart Claude Code
```bash
# Restart to reload MCP servers
# Then verify:
claude mcp list
```

**See:** [MCP_SETUP.md](MCP_SETUP.md) for detailed configuration

---

### Problem 9: Perplexity API Rate Limit

**Symptom:**
```
Error: Rate limit exceeded
Perplexity API returned 429 Too Many Requests
Research failed
```

**Cause:**
- Too many API requests in short time
- Free tier monthly limit reached
- No API key configured (using free tier)

**Solution:**

**Step 1:** Check API usage
```bash
# Visit Perplexity dashboard
# https://www.perplexity.ai/settings/api

# Check:
# - Current usage
# - Monthly limit
# - Rate limits
```

**Step 2:** Implement rate limiting
```python
# Use research tools with delays
from tools.perplexity_research_tool import conduct_research
import time

# Add delay between requests
results = conduct_research(query)
time.sleep(2)  # Wait 2 seconds before next request
```

**Step 3:** Use hybrid research strategy
```python
# Fallback to MCP if tool fails
try:
    # Try custom Perplexity tool first
    results = conduct_research(query)
except RateLimitError:
    # Fallback to Perplexity MCP
    results = mcp__perplexity__ask(query)
```

**Step 4:** Upgrade to paid tier if needed
```
1. Visit: https://www.perplexity.ai/settings/api
2. Upgrade to Pro ($20/month for higher limits)
3. Update PERPLEXITY_API_KEY in environment
```

---

### Problem 10: Missing API Key Environment Variable

**Symptom:**
```
KeyError: 'OPENAI_API_KEY'
NameError: name 'PERPLEXITY_API_KEY' is not defined
Environment variable not found
```

**Cause:**
- Environment variable not set in current shell
- .env file not loaded
- Typo in variable name

**Solution:**

**Step 1:** Create comprehensive .env file
```bash
cat > .env << 'EOF'
# OpenAI (MARKETING, ENGINEERING)
OPENAI_API_KEY=sk-your-openai-key

# Anthropic (All teams)
ANTHROPIC_API_KEY=your-anthropic-key

# Google Workspace (MARKETING)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Perplexity (MARKETING research)
PERPLEXITY_API_KEY=your-perplexity-key

# Bright Data (MARKETING web scraping)
BRIGHT_DATA_API_KEY=your-brightdata-key

# Gemini (MARKETING video)
GEMINI_API_KEY=your-gemini-key

# n8n (MARKETING automation)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/
EOF
```

**Step 2:** Load environment variables
```bash
# Install python-dotenv
pip install python-dotenv

# In Python scripts, load .env
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are available
import os
api_key = os.getenv('OPENAI_API_KEY')
```

**Step 3:** Verify all required keys are set
```bash
# Check required environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'PERPLEXITY_API_KEY']
missing = [k for k in required if not os.getenv(k)]

if missing:
    print(f'❌ Missing: {missing}')
else:
    print('✅ All required API keys configured')
"
```

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) sections 1-7

---

## File Operation Errors

### Problem 11: File Not Found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'memory/brand_voice.json'
Agent can't read configuration files
Config file missing
```

**Cause:**
- Using relative path instead of absolute path
- File actually missing
- Working directory incorrect

**Solution:**

**Step 1:** Verify file exists
```bash
# Check if file exists
ls -la MARKETING_TEAM/memory/brand_voice.json

# If missing, list what's in memory/
ls -la MARKETING_TEAM/memory/
```

**Step 2:** Use absolute paths
```python
# ✅ CORRECT - Absolute path
from tools.workspace_enforcer import get_absolute_paths

paths = get_absolute_paths("MARKETING_TEAM")
brand_voice_path = f"{paths['memory']}/brand_voice.json"

with open(brand_voice_path, 'r') as f:
    brand_voice = json.load(f)

# ❌ WRONG - Relative path
brand_voice_path = "memory/brand_voice.json"  # May fail
```

**Step 3:** Create missing memory files
```bash
# Create brand_voice.json template
cat > MARKETING_TEAM/memory/brand_voice.json << 'EOF'
{
  "tone": "Professional yet approachable",
  "voice_principles": [
    "Clear and concise",
    "Action-oriented",
    "Data-driven"
  ],
  "target_audience": "Tech-savvy professionals",
  "avoid_words": ["utilize", "leverage", "synergy"]
}
EOF

# Create email_config.json template
cat > MARKETING_TEAM/memory/email_config.json << 'EOF'
{
  "user_google_email": "your-email@gmail.com",
  "default_to": "recipient@example.com",
  "default_cc": ""
}
EOF
```

**Step 4:** Verify workspace paths
```bash
# Test path validator
python -c "
from tools.path_validator import validate_read_path

# This will show correct absolute path
path = validate_read_path('brand_voice.json', 'MARKETING_TEAM')
print(f'Correct path: {path}')
"
```

---

### Problem 12: Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/file'
Can't write to directory
Access denied
```

**Cause:**
- Insufficient file permissions
- Directory doesn't exist
- File is read-only

**Solution:**

**Step 1:** Check file permissions
```bash
ls -la MARKETING_TEAM/outputs/

# Look for permissions like:
# drwxr-xr-x  (directory, readable/writable)
# -rw-r--r--  (file, readable/writable by owner)
```

**Step 2:** Fix directory permissions
```bash
# Make directory writable
chmod 755 MARKETING_TEAM/outputs/

# Make all subdirectories writable
chmod -R 755 MARKETING_TEAM/outputs/
```

**Step 3:** Create directory if missing
```bash
# Create with proper permissions
mkdir -p MARKETING_TEAM/outputs/blog_posts
chmod 755 MARKETING_TEAM/outputs/blog_posts
```

**Step 4:** Check file ownership
```bash
# Check who owns the file
ls -l MARKETING_TEAM/outputs/file.txt

# Change ownership if needed (Linux/Mac)
chown $USER:$USER MARKETING_TEAM/outputs/file.txt
```

---

### Problem 13: File Already Exists

**Symptom:**
```
FileExistsError: [Errno 17] File exists: 'output.json'
Can't overwrite file
Duplicate file error
```

**Cause:**
- File already exists and script doesn't handle overwrite
- No backup or versioning logic
- Attempting to create existing directory

**Solution:**

**Step 1:** Check if file exists before writing
```python
import os

output_path = "MARKETING_TEAM/outputs/report.json"

# Check if file exists
if os.path.exists(output_path):
    # Option 1: Backup existing file
    import shutil
    backup_path = f"{output_path}.backup"
    shutil.copy2(output_path, backup_path)
    print(f"Backed up to: {backup_path}")

# Now safe to write
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)
```

**Step 2:** Use versioned filenames
```python
from datetime import datetime

# Add timestamp to filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"MARKETING_TEAM/outputs/report_{timestamp}.json"

# Now each file is unique
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)
```

**Step 3:** Use safe directory creation
```python
# Create directory only if it doesn't exist
os.makedirs("MARKETING_TEAM/outputs/blog_posts", exist_ok=True)
```

---

## Multi-Agent Coordination Failures

### Problem 14: Agent B Can't Find File Created by Agent A

**Symptom:**
```
Agent A creates file successfully
Agent B reports "File not found"
Multi-agent workflow breaks
```

**Cause:**
- Agent A used relative path
- Agent B looking in wrong location
- Inconsistent path formats

**Solution:**

**Step 1:** Both agents use absolute paths
```python
# Agent A (Producer) - Use absolute path
from tools.workspace_enforcer import get_absolute_paths

paths = get_absolute_paths("MARKETING_TEAM")
output_file = f"{paths['outputs']}/research_results.json"

with open(output_file, 'w') as f:
    json.dump(results, f)

print(f"✅ Results written to: {output_file}")
# Output: /home/user/TEST_AGENTS/MARKETING_TEAM/outputs/research_results.json

# Agent B (Consumer) - Use same absolute path
with open(output_file, 'r') as f:
    results = json.load(f)
```

**Step 2:** Pass full paths between agents
```
# ✅ CORRECT - Pass absolute path
Task(copywriter): Use research from /home/user/TEST_AGENTS/MARKETING_TEAM/outputs/research_results.json

# ❌ WRONG - Pass relative path
Task(copywriter): Use research from outputs/research_results.json
```

**Step 3:** Verify file exists after creation
```python
# Agent A - Verify before passing to next agent
import os

output_file = f"{paths['outputs']}/research_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f)

# Verify file exists and has content
assert os.path.exists(output_file), f"File not created: {output_file}"
assert os.path.getsize(output_file) > 0, f"File is empty: {output_file}"

print(f"✅ File verified: {output_file} ({os.path.getsize(output_file)} bytes)")
```

---

### Problem 15: Circular Agent Dependencies

**Symptom:**
```
Agent A delegates to Agent B
Agent B delegates to Agent A
Infinite loop
Maximum recursion depth exceeded
```

**Cause:**
- Poor task decomposition
- Agents don't know their responsibilities
- Missing workflow coordination

**Solution:**

**Step 1:** Use coordinator pattern
```
# ✅ CORRECT - Coordinator delegates to specialists
User → router-agent → [copywriter, visual-designer, email-specialist]
                       ↓
                    Results aggregated by router-agent
                       ↓
                    Return to user

# ❌ WRONG - Circular delegation
copywriter → social-media-manager → copywriter → ...
```

**Step 2:** Define clear agent responsibilities
```markdown
## Agent: copywriter
**Responsibilities:**
- Write blog posts
- Create article content
- Draft copy for campaigns

**Does NOT:**
- Create images (delegates to visual-designer)
- Send emails (delegates to gmail-agent)
- Research (delegates to research-agent)

**Delegation Rules:**
- NEVER delegate to agents that might delegate back
- Use router-agent for complex multi-step workflows
```

**Step 3:** Implement depth limits
```python
# In coordinator agent
MAX_DELEGATION_DEPTH = 3

def delegate_task(task, depth=0):
    if depth >= MAX_DELEGATION_DEPTH:
        raise Exception("Maximum delegation depth exceeded")

    # Delegate to specialist
    result = invoke_agent(task, depth=depth+1)
    return result
```

---

### Problem 16: Agent Doesn't Wait for Delegated Task

**Symptom:**
```
Coordinator delegates task to specialist
Coordinator returns before specialist finishes
Incomplete results
```

**Cause:**
- Asynchronous delegation without waiting
- No result verification
- Missing coordination logic

**Solution:**

**Step 1:** Ensure synchronous delegation
```python
# ✅ CORRECT - Wait for result
def coordinate_campaign():
    # Delegate and WAIT for completion
    blog_post = invoke_agent("copywriter", "Write blog about AI")
    # Wait until blog_post is complete

    # Then delegate next task
    image = invoke_agent("visual-designer", "Create header image")
    # Wait until image is complete

    return {"blog": blog_post, "image": image}

# ❌ WRONG - Fire and forget
def coordinate_campaign():
    invoke_agent("copywriter", "Write blog")  # Don't wait
    invoke_agent("visual-designer", "Create image")  # Don't wait
    return  # Nothing to return!
```

**Step 2:** Verify results before proceeding
```python
def coordinate_campaign():
    # Delegate task
    blog_post = invoke_agent("copywriter", "Write blog about AI")

    # Verify result
    assert blog_post is not None, "Blog post not created"
    assert len(blog_post) > 100, "Blog post too short"

    # Now safe to proceed
    return blog_post
```

---

## Memory File Issues

### Problem 17: Brand Voice Not Applied

**Symptom:**
```
Content doesn't match brand voice guidelines
Generic tone instead of Dux Machina voice
Agent ignores brand_voice.json
```

**Cause:**
- Agent didn't read brand_voice.json
- Agent definition missing configuration section
- Memory file path incorrect

**Solution:**

**Step 1:** Verify brand_voice.json exists
```bash
cat MARKETING_TEAM/memory/brand_voice.json

# Should show brand voice configuration
# If missing, create it
```

**Step 2:** Check agent definition has configuration section
```bash
cat MARKETING_TEAM/.claude/agents/copywriter.md | grep -A 10 "Configuration Files"

# Should show:
# ## ⚙️ Configuration Files (READ FIRST)
# 1. **memory/brand_voice.json** - Brand voice guidelines
```

**Step 3:** Verify agent reads memory file
```markdown
## Your Process

1. **Read memory/brand_voice.json** ← CRITICAL
2. Follow brand voice principles in ALL content
3. Use tone: "Tech Samurai meets McKinsey Strategist"
4. Avoid generic marketing speak
```

**Step 4:** Test brand voice application
```bash
# Invoke agent and check output
Task(copywriter): Write a 200-word product description

# Verify output includes:
# - Brand voice principles
# - Signature phrases
# - Avoids forbidden words
```

---

### Problem 18: Email Config Not Found

**Symptom:**
```
Error: user_google_email not configured
Gmail agent can't send emails
Email config missing
```

**Cause:**
- email_config.json doesn't exist
- File has incorrect structure
- Agent looking in wrong location

**Solution:**

**Step 1:** Create email_config.json
```bash
cat > MARKETING_TEAM/memory/email_config.json << 'EOF'
{
  "user_google_email": "your-email@gmail.com",
  "default_to": "recipient@example.com",
  "default_cc": ""
}
EOF
```

**Step 2:** Verify file structure
```bash
# Check JSON is valid
python -c "
import json
with open('MARKETING_TEAM/memory/email_config.json') as f:
    config = json.load(f)
    print('✅ Email config valid')
    print(f'Email: {config[\"user_google_email\"]}')
"
```

**Step 3:** Update with your email
```bash
# Edit email_config.json
nano MARKETING_TEAM/memory/email_config.json

# Update:
# - user_google_email: Your Gmail address
# - default_to: Default recipient
# - default_cc: Default CC (optional)
```

**Step 4:** Verify agent reads config
```python
# Test email config reading
import json

with open('MARKETING_TEAM/memory/email_config.json') as f:
    config = json.load(f)

print(f"✅ Email: {config['user_google_email']}")
print(f"✅ Default To: {config['default_to']}")
```

---

### Problem 19: Drive Folder IDs Incorrect

**Symptom:**
```
Error: Folder not found
Drive upload fails with 404
Invalid folder ID
```

**Cause:**
- google_drive_config.json has wrong folder IDs
- Folder doesn't exist in Google Drive
- Insufficient permissions

**Solution:**

**Step 1:** Get correct folder IDs from Google Drive
```bash
# 1. Open Google Drive in browser
# 2. Navigate to folder
# 3. Copy folder ID from URL
#    https://drive.google.com/drive/folders/1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv
#                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                                            This is the folder ID
```

**Step 2:** Update google_drive_config.json
```bash
cat > MARKETING_TEAM/memory/google_drive_config.json << 'EOF'
{
  "user_google_email": "your-email@gmail.com",
  "folders": {
    "ai_marketing_team": "YOUR_FOLDER_ID_HERE",
    "videos": "YOUR_VIDEOS_FOLDER_ID",
    "images": "YOUR_IMAGES_FOLDER_ID"
  },
  "upload_defaults": {
    "presentations": "YOUR_FOLDER_ID_HERE",
    "documents": "YOUR_FOLDER_ID_HERE",
    "images": "YOUR_IMAGES_FOLDER_ID",
    "videos": "YOUR_VIDEOS_FOLDER_ID"
  }
}
EOF
```

**Step 3:** Test folder access
```bash
# Test Drive upload
python MARKETING_TEAM/scripts/simple_upload.py
```

**Step 4:** Verify folder permissions
```
1. Open folder in Google Drive
2. Right-click → Share
3. Ensure your service account email has Editor access
4. Service account email format: xxx@xxx.iam.gserviceaccount.com
```

---

## Tool/Skill/MCP Problems

### Problem 20: MCP vs Skill vs Tool Confusion

**Symptom:**
```
Agent doesn't know which to use
Duplicate functionality created
Wrong tool/skill selected
```

**Cause:**
- Not following priority hierarchy
- Agent definition unclear about priorities
- Missing from TOOL_REGISTRY.md

**Solution:**

**Step 1:** Follow canonical priority hierarchy
```
1️⃣ MCP SERVERS (HIGHEST PRIORITY)
   ↓ (if MCP unavailable)
2️⃣ SKILLS (SECOND PRIORITY)
   ↓ (if skill unavailable)
3️⃣ CUSTOM TOOLS (THIRD PRIORITY)
   ↓ (if nothing exists)
4️⃣ CREATE NEW (LAST RESORT)
```

**Step 2:** Check TOOL_REGISTRY.md
```bash
# Before creating anything, check registry
cat TOOL_REGISTRY.md | grep -i "email"

# Shows:
# - MCP: google-workspace (send_email)
# - Tool: send_email_with_attachment.py
# - Use MCP for text emails, Tool for attachments
```

**Step 3:** Use decision tree
```
Need to send email?
├─ Has attachment?
│  ├─ YES → Use send_email_with_attachment.py (MCP can't handle)
│  └─ NO → Use mcp__google-workspace__send_email (preferred)
└─ Done
```

**See:** [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) for complete hierarchy

---

### Problem 21: Skill Not Enabled

**Symptom:**
```
Error: Skill 'xlsx' is not available
Skill declared in agent YAML but doesn't work
SkillNotEnabled exception
```

**Cause:**
- Skill not enabled in .claude/settings.json
- Skill doesn't exist in .claude/skills/
- Typo in skill name

**Solution:**

**Step 1:** Check skill is enabled
```bash
# Check settings.json
cat MARKETING_TEAM/.claude/settings.json | grep -A 20 "skills"

# Should show:
# "skills": {
#   "pdf": true,
#   "pptx": true,
#   "xlsx": false  ← NOT enabled!
# }
```

**Step 2:** Enable skill if needed
```bash
# Edit settings.json
nano MARKETING_TEAM/.claude/settings.json

# Change:
# "xlsx": false
# to:
# "xlsx": true
```

**Step 3:** Use MCP alternative if skill unavailable
```python
# Instead of xlsx skill (not enabled)
# Use Google Sheets MCP
mcp__google-workspace__create_spreadsheet(
    title="Campaign Data",
    data=[[1, 2, 3], [4, 5, 6]]
)
```

**Step 4:** Verify skill declaration matches enabled skills
```yaml
# Agent YAML frontmatter
---
skills:
  - pdf        # ✅ Enabled
  - pptx       # ✅ Enabled
  # NOT: xlsx  # ❌ Not enabled in settings.json
---
```

**Current Enabled Skills (MARKETING_TEAM):**
- ✅ pdf, pptx, pdf-filler
- ✅ canvas-design, flow-diagram, slack-gif-creator
- ✅ algorithmic-art, artifacts-builder, theme-factory
- ❌ xlsx, docx (use Google Workspace MCP instead)

---

### Problem 22: MCP Server Not Found

**Symptom:**
```
Error: MCP server 'perplexity' not found
MCP tool unavailable
Connection refused
```

**Cause:**
- MCP server not installed
- Not configured in .mcp.json
- Server not running

**Solution:**

**Step 1:** List active MCP servers
```bash
claude mcp list

# Shows all connected servers:
# google-workspace: ✓ Connected
# perplexity: ✗ Not connected
# playwright: ✓ Connected
```

**Step 2:** Install missing MCP server
```bash
# For Perplexity
npm install -g @modelcontextprotocol/server-perplexity

# For Google Workspace
npm install -g @modelcontextprotocol/server-google-workspace

# For Playwright
npm install -g @executeautomation/playwright-mcp-server
```

**Step 3:** Configure in .mcp.json
```bash
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-perplexity"],
      "env": {
        "PERPLEXITY_API_KEY": "your-key-here"
      }
    }
  }
}
EOF
```

**Step 4:** Restart Claude Code
```bash
# Restart to reload MCP configuration
# Then verify:
claude mcp list
```

**See:** [MCP_SETUP.md](MCP_SETUP.md) for all servers

---

### Problem 23: Custom Tool Import Fails

**Symptom:**
```
ModuleNotFoundError: No module named 'tools.upload_to_drive'
ImportError: cannot import name 'send_email_with_attachment'
Tool import error
```

**Cause:**
- Python path not configured
- Tool file doesn't exist
- Typo in import statement

**Solution:**

**Step 1:** Verify tool file exists
```bash
ls -la MARKETING_TEAM/tools/upload_to_drive.py
ls -la MARKETING_TEAM/tools/send_email_with_attachment.py

# If missing, check TOOL_REGISTRY.md for correct location
```

**Step 2:** Fix Python path
```python
# Add team tools to Python path
import sys
import os

# Get absolute path to tools folder
tools_path = os.path.join(os.getcwd(), "MARKETING_TEAM", "tools")
if tools_path not in sys.path:
    sys.path.insert(0, tools_path)

# Now imports work
from upload_to_drive import upload_to_drive
```

**Step 3:** Use correct import syntax
```python
# ✅ CORRECT - Import from tools module
from tools.upload_to_drive import upload_to_drive

# ❌ WRONG - Import from MARKETING_TEAM.tools
from MARKETING_TEAM.tools.upload_to_drive import upload_to_drive
```

**Step 4:** Verify tool has correct structure
```bash
# Tool must be in tools/ folder
# Tool must have .py extension
# Tool must define functions/classes to import

# Check file structure:
python -c "
import ast
with open('MARKETING_TEAM/tools/upload_to_drive.py') as f:
    tree = ast.parse(f.read())
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    print(f'Functions: {functions}')
"
```

---

## Editor Review Workflow Issues

### Problem 24: Editor Not Reviewing Content

**Symptom:**
```
Content created but not reviewed by editor
Brand voice not enforced
No tone score provided
```

**Cause:**
- Editor agent not invoked
- Editor review step skipped
- Agent doesn't know to delegate to editor

**Solution:**

**Step 1:** Ensure coordinator agents invoke editor
```markdown
## Process (router-agent, content-strategist)

1. Delegate to copywriter for content creation
2. **Delegate to editor for brand voice review** ← CRITICAL
3. Editor provides tone score (7+ required)
4. If score < 7, revise content
5. Deliver final approved content
```

**Step 2:** Explicitly invoke editor
```
# ✅ CORRECT - Include editor review
Task(router-agent): Create blog post and ensure editor approves with tone score 7+

# ❌ WRONG - Skip editor review
Task(copywriter): Create blog post
```

**Step 3:** Verify editor agent definition
```bash
cat MARKETING_TEAM/.claude/agents/editor.md | grep -A 5 "Your Process"

# Should show:
# 1. Read brand_voice.json
# 2. Analyze content for brand voice alignment
# 3. Provide tone score (1-10)
# 4. Suggest revisions if score < 7
```

**Step 4:** Test editor review
```
Task(editor): Review this content and provide tone score:

"[Your content here]"

# Editor should return:
# - Tone Score: X/10
# - Brand Voice Alignment: [analysis]
# - Suggestions: [if score < 7]
```

---

### Problem 25: Editor Score Always Too Low

**Symptom:**
```
Editor consistently gives scores of 5-6
Content keeps getting rejected
Can't achieve tone score 7+
```

**Cause:**
- Content doesn't follow brand voice principles
- Missing key brand voice elements
- Generic marketing language

**Solution:**

**Step 1:** Review brand voice principles
```bash
cat MARKETING_TEAM/memory/brand_voice.json | grep -A 10 "voice_principles"

# Key principles:
# - Tech Samurai meets McKinsey Strategist
# - Data-driven decision making
# - Clear, actionable insights
# - No generic marketing speak
```

**Step 2:** Check for forbidden words
```bash
# Avoid these words (from brand_voice.json):
# - "utilize" (use "use")
# - "leverage" (use specific verb)
# - "synergy" (be specific)
# - "paradigm shift"
# - "best-in-class"
```

**Step 3:** Include brand voice elements
```markdown
✅ GOOD - Dux Machina voice:
"Our AI agents execute with precision, delivering measurable ROI
through data-driven automation. No guesswork—just results."

❌ BAD - Generic marketing:
"We leverage cutting-edge AI solutions to synergize your marketing
efforts and drive paradigm-shifting results."
```

**Step 4:** Request specific feedback
```
Task(editor): Review this content and provide:
1. Tone score with detailed reasoning
2. Specific examples of violations
3. Suggested replacements for problem phrases
```

---

## Supervisor Verification Issues

### Problem 26: Supervisor Not Verifying Tasks

**Symptom:**
```
Work completed but not verified
No quality report generated
Supervisor not invoked
```

**Cause:**
- Coordinator doesn't auto-trigger supervisor
- User forgot to invoke supervisor
- Supervisor not configured

**Solution:**

**Step 1:** Manually invoke supervisor
```
# After task completion, verify:
Task(supervisor): Verify that [task description] is complete and ready for deployment

# Example:
Task(supervisor): Verify that the authentication feature is complete with tests, docs, and commits
```

**Step 2:** Configure auto-trigger (for coordinators)
```markdown
## Process (cto, router-agent, test-orchestrator)

[... complete work ...]

**CRITICAL: Auto-verify significant work**

If work is significant (3+ files, 100+ lines, production code):
1. Invoke supervisor for verification
2. Wait for verification report
3. Address any issues found
4. Re-verify if changes made
```

**Step 3:** Verify supervisor agent exists
```bash
# Check supervisor definition
ls -la .claude/agents/supervisor.md

# Should exist at root level (not in team folder)
```

**See:** [SUPERVISOR_ARCHITECTURE.md](SUPERVISOR_ARCHITECTURE.md) and [SUPERVISOR_AUTO_TRIGGER_SETUP.md](SUPERVISOR_AUTO_TRIGGER_SETUP.md)

---

### Problem 27: Supervisor Verification Fails

**Symptom:**
```
Verification Status: FAILED
Quality Score: 3/10
Multiple issues found
```

**Cause:**
- Code quality issues
- Tests not passing
- Documentation missing
- Security vulnerabilities

**Solution:**

**Step 1:** Review verification report
```
Supervisor returns:
- Status: FAILED
- Quality Score: 3/10
- Issues Found:
  1. Tests not passing (2/5 failed)
  2. Missing docstrings (15 functions)
  3. Hardcoded API key in config.py
  4. No API documentation
- Recommendations:
  1. Fix failing tests
  2. Add docstrings
  3. Move API key to environment variable
  4. Create API documentation
```

**Step 2:** Address each issue systematically
```bash
# Fix failing tests
pytest tests/test_auth.py -v

# Add docstrings
# (Edit each function to add docstring)

# Remove hardcoded secrets
# Move to .env file

# Create documentation
# Add to docs/api.md
```

**Step 3:** Re-verify after fixes
```
Task(supervisor): Re-verify authentication feature after fixes
```

**Step 4:** Achieve PASSED status
```
Verification Report:
- Status: PASSED ✅
- Quality Score: 9/10
- Issues Found: 0
- Deployment Ready: YES
```

---

### Problem 28: Supervisor Can't Find Deliverables

**Symptom:**
```
Error: Expected file not found
Deliverable validation failed
Missing: src/auth/routes.py
```

**Cause:**
- Files created in wrong location
- Incorrect file paths in verification
- Workspace context mismatch

**Solution:**

**Step 1:** Verify files exist in expected locations
```bash
# Check expected deliverables
ls -la src/auth/routes.py
ls -la tests/test_auth.py
ls -la docs/api.md
```

**Step 2:** Use absolute paths in verification
```
Task(supervisor): Verify deliverables at:
- /home/user/TEST_AGENTS/src/auth/routes.py
- /home/user/TEST_AGENTS/tests/test_auth.py
- /home/user/TEST_AGENTS/docs/api.md
```

**Step 3:** Check git commits
```bash
# Supervisor checks git for changes
git status
git log --oneline -5

# Ensure files are committed
git add src/auth/routes.py tests/test_auth.py docs/api.md
git commit -m "Add authentication feature"
```

**Step 4:** Provide clear verification criteria
```
Task(supervisor): Verify authentication feature with criteria:

Expected Deliverables:
1. Code: src/auth/routes.py (login, logout endpoints)
2. Tests: tests/test_auth.py (5+ test cases, all passing)
3. Docs: docs/api.md (API endpoints documented)
4. Git: Committed with message "Add authentication feature"

Quality Gates:
- All tests pass
- Code has docstrings
- No hardcoded secrets
- Documentation complete
```

---

## Common Error Messages

### Error: "Task invocation pattern not recognized"

**Full Error:**
```
Error: Task invocation pattern not recognized
Expected: Task(agent-name): instruction
Received: Use the agent to do something
```

**Fix:**
```
# ❌ WRONG
Use the copywriter to write a blog post

# ✅ CORRECT
Task(copywriter): Write a blog post about AI automation
```

---

### Error: "Agent not authorized for this team"

**Full Error:**
```
Error: Agent 'copywriter' not authorized for team 'QA_TEAM'
Workspace validation failed
```

**Fix:**
```
# ❌ WRONG - Copywriter is in MARKETING_TEAM
Task(copywriter) in QA_TEAM context

# ✅ CORRECT - Use QA_TEAM agent
Task(test-orchestrator): Generate tests

# OR invoke from MARKETING_TEAM context
cd MARKETING_TEAM
Task(copywriter): Write blog post
```

---

### Error: "Memory file not configured"

**Full Error:**
```
Error: Required memory file not found
Missing: MARKETING_TEAM/memory/brand_voice.json
Agent cannot proceed
```

**Fix:**
```bash
# Create missing memory file
cat > MARKETING_TEAM/memory/brand_voice.json << 'EOF'
{
  "tone": "Professional yet approachable",
  "voice_principles": ["Clear", "Concise", "Data-driven"]
}
EOF
```

**See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) section 4

---

### Error: "MCP tool not available"

**Full Error:**
```
Error: MCP tool 'mcp__google-workspace__send_email' not available
MCP server not connected
```

**Fix:**
```bash
# Check MCP status
claude mcp list

# Install if missing
npm install -g @modelcontextprotocol/server-google-workspace

# Restart Claude Code
```

**See:** [MCP_SETUP.md](MCP_SETUP.md)

---

### Error: "Priority hierarchy violation"

**Full Error:**
```
Error: Creating custom tool when MCP server exists
Violation: MCP servers have priority over custom tools
```

**Fix:**
```
# Use MCP instead of creating new tool
# Check TOOL_REGISTRY.md for available MCP servers
# Follow priority: MCP → Skill → Custom Tool → Create New
```

**See:** [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

---

## Debug Workflows

### Workflow 1: Agent Invocation Not Working

```
STEP 1: Verify agent exists
├─ ls MARKETING_TEAM/.claude/agents/
├─ Check spelling
└─ Confirm team membership

STEP 2: Check invocation syntax
├─ Use: Task(agent-name): instruction
├─ Not: "Use the agent to..."
└─ Not: JSON format

STEP 3: Verify workspace context
├─ pwd (should be in TEST_AGENTS)
├─ Check team folders exist
└─ Validate with workspace_enforcer

STEP 4: Check agent definition
├─ cat MARKETING_TEAM/.claude/agents/agent-name.md
├─ Verify YAML frontmatter
└─ Check tools/skills declared

STEP 5: Test with simple task
└─ Task(agent-name): Simple test task
```

---

### Workflow 2: File Operations Failing

```
STEP 1: Verify workspace
├─ pwd
├─ ls MARKETING_TEAM/
└─ Check folder structure

STEP 2: Check file paths
├─ Use absolute paths
├─ Get from workspace_enforcer.get_absolute_paths()
└─ Never use relative paths

STEP 3: Verify permissions
├─ ls -la MARKETING_TEAM/outputs/
├─ chmod 755 if needed
└─ Check ownership

STEP 4: Test file operations
├─ Create test file
├─ Read test file
└─ Delete test file

STEP 5: Check memory files
└─ Verify all required memory/*.json exist
```

---

### Workflow 3: API Configuration Issues

```
STEP 1: Check environment variables
├─ echo $OPENAI_API_KEY
├─ echo $PERPLEXITY_API_KEY
└─ echo $GOOGLE_APPLICATION_CREDENTIALS

STEP 2: Verify .env file
├─ cat .env
├─ Check all required keys
└─ Load with python-dotenv

STEP 3: Test API connections
├─ python MARKETING_TEAM/scripts/test_openai_connection.py
├─ python MARKETING_TEAM/scripts/test_perplexity_research.py
└─ python MARKETING_TEAM/scripts/test_google_workspace_mcp.py

STEP 4: Check MCP servers
├─ claude mcp list
├─ Verify all servers connected
└─ Restart if needed

STEP 5: Review API_SETUP_GUIDE.md
└─ Follow setup for missing APIs
```

---

### Workflow 4: Multi-Agent Coordination Debug

```
STEP 1: Verify agent A completes successfully
├─ Check output files created
├─ Verify file content
└─ Note absolute path

STEP 2: Pass absolute path to agent B
├─ Use: Task(agent-b): Use file at /absolute/path
└─ Not: Use file at relative/path

STEP 3: Check agent B can read file
├─ Verify file exists (ls -la /absolute/path)
├─ Check permissions
└─ Test with cat /absolute/path

STEP 4: Verify both agents use workspace enforcer
├─ Both call validate_workspace()
├─ Both use get_absolute_paths()
└─ Both use consistent path format

STEP 5: Test coordination pattern
└─ Simple producer → consumer test
```

---

### Workflow 5: Tool/Skill/MCP Selection

```
STEP 1: Check TOOL_REGISTRY.md
└─ Search for functionality

STEP 2: Apply priority hierarchy
├─ 1️⃣ MCP server exists? → Use MCP
├─ 2️⃣ Skill exists? → Use Skill
├─ 3️⃣ Custom tool exists? → Use Tool
└─ 4️⃣ Nothing exists? → Create (with approval)

STEP 3: Verify availability
├─ MCP: claude mcp list
├─ Skill: Check .claude/settings.json
└─ Tool: Check TOOL_REGISTRY.md

STEP 4: Test selected option
├─ MCP: Invoke MCP tool
├─ Skill: Use skill in agent
└─ Tool: Import and call function

STEP 5: Document decision
└─ Update TOOL_REGISTRY.md if creating new tool
```

---

## Quick Reference: Most Common Issues

| Issue | Quick Fix | Documentation |
|-------|-----------|---------------|
| Agent not found | Check spelling, verify team | [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) |
| Workspace validation failed | `cd TEST_AGENTS`, verify folders | [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) |
| File not found | Use absolute paths | [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) |
| API key missing | Set environment variable, create .env | [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) |
| MCP not connected | `claude mcp list`, install server | [MCP_SETUP.md](MCP_SETUP.md) |
| Memory file missing | Create in team/memory/ folder | [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) |
| Skill not enabled | Check .claude/settings.json | [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) |
| Duplicate scripts created | Use minimal invocation, trust agent | [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) |
| Brand voice not applied | Verify agent reads brand_voice.json | [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) |
| Supervisor not verifying | Explicitly invoke or configure auto-trigger | [SUPERVISOR_ARCHITECTURE.md](SUPERVISOR_ARCHITECTURE.md) |

---

## Related Documentation

**Core Guides:**
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start guide
- [FAQ.md](FAQ.md) - Frequently asked questions
- [GLOSSARY.md](GLOSSARY.md) - Terms and definitions
- [claude.md](claude.md) - Repository navigation

**Technical Documentation:**
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All 39 agents
- [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) - Workspace validation
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - Configuration files
- [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - Invocation patterns

**Governance:**
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - Governance map
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Priority hierarchy
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Complete tool inventory

**Setup:**
- [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - API configuration
- [MCP_SETUP.md](MCP_SETUP.md) - MCP server setup

---

## Need More Help?

1. **Check FAQ.md** for common questions
2. **Review relevant documentation** listed above
3. **Test with simple examples** from GETTING_STARTED.md
4. **Verify system structure** with ls commands
5. **Run debug workflows** from this guide

**Still stuck?** Review the complete documentation at [claude.md](claude.md) for navigation to all resources.

---

**Last Updated:** 2025-11-17
