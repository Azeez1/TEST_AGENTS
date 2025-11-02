# 🧠 Memory System - Complete Guide

**For AI Assistants and Developers**

This guide explains how the memory system works across all 37 agents in the repository, ensuring consistent configuration without hardcoding values.

---

## Overview

All agents are instructed in their definitions to read memory configuration files at task start. This ensures:
- ✅ Consistent email addresses across all email operations
- ✅ Consistent Drive folder structure for uploads
- ✅ Consistent brand voice and visual guidelines
- ✅ Single source of truth (update once, affects all agents)

---

## How Agents Access Memory

### 1. Agent Definition Includes Configuration Section
Each agent's `.claude/agents/*.md` file contains a "⚙️ Configuration Files (READ FIRST)" section.

### 2. Explicit Instructions to Read Files
The section lists which memory files to read and when to use them.

### 3. Agent Reads Files at Task Start
Agent uses Read tool or filesystem skill to load configuration.

### 4. Agent Uses Configuration Throughout Task
Configuration values used instead of hardcoded defaults.

---

## Memory Files Reference

### MARKETING_TEAM/memory/

All memory files are in the `MARKETING_TEAM/memory/` directory:

#### 1. email_config.json
**Purpose:** Email defaults for ALL email operations

```json
{
  "user_google_email": "sabaazeez12@gmail.com",
  "default_to": "sabaazeez12@gmail.com",
  "default_cc": "aoseni@duxvitaecapital.com"
}
```

**Used by:** gmail-agent, email-specialist, any agent sending emails
**Used when:** Sending emails, creating drafts, searching messages
**Required for:** ALL Google Workspace MCP email tools

---

#### 2. google_drive_config.json
**Purpose:** Drive folder structure and upload locations

```json
{
  "user_google_email": "sabaazeez12@gmail.com",
  "folders": {
    "ai_marketing_team": "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv",
    "videos": "1EMk6waLu87DmLaI4LrxoBvpYSdFzy42q",
    "images": "12DaX0JJ5K6_os1ANj6FgovF72ymdson1",
    "social_media": "1mFHE1aKOIzhxL3BmIC593WfNt5G1GBxi",
    "lead_gen": "1G5AQYEcKv_kKUMfr8QgPVAlkcMjvhEB_"
  },
  "upload_defaults": {
    "presentations": "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv",
    "documents": "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv",
    "images": "12DaX0JJ5K6_os1ANj6FgovF72ymdson1",
    "videos": "1EMk6waLu87DmLaI4LrxoBvpYSdFzy42q",
    "leads": "1G5AQYEcKv_kKUMfr8QgPVAlkcMjvhEB_"
  }
}
```

**Used by:** pdf-specialist, presentation-designer, visual-designer, video-producer
**Used when:** Uploading files to Google Drive
**Required for:** ALL Drive uploads via `upload_to_drive.py`

---

#### 3. brand_voice.json
**Purpose:** Dux Machina brand voice guidelines

**Contains:**
- Tone and style guidelines
- Voice principles ("Tech Samurai meets McKinsey Strategist")
- Keywords and signature phrases
- Avoid-words list
- Writing guidelines

**Used by:** copywriter, social-media-manager, email-specialist, editor
**Used when:** Creating ALL content (blogs, posts, emails, PDFs, presentations)
**Why:** Ensures consistent brand voice across all marketing materials

---

#### 4. visual_guidelines.json
**Purpose:** Dux Machina visual identity standards

**Contains:**
- Brand colors (Void Black #0A0E14, Precision Gold #B8860B, Tactical Cyan #4A90A4)
- Typography (fonts, sizes, weights)
- Image styles and design preferences
- Design principles

**Used by:** visual-designer, presentation-designer, pdf-specialist
**Used when:** Designing ANY visual assets (images, PDFs, presentations)
**Why:** Ensures consistent visual identity

---

#### 5. docs_folder_structure.json
**Purpose:** Documentation organization rules

**Contains:**
- Folder structure guidelines
- File naming conventions
- Organization patterns

**Used by:** AI assistants (Claude Code, Cursor, etc.) when creating documentation
**NOT used by:** Marketing agents (codebase maintenance only)

---

#### 6. learned_patterns.json (QA_TEAM)
**Purpose:** Test generation patterns learned from feedback

**Location:** `QA_TEAM/memory/learned_patterns.json`
**Used by:** test-orchestrator, unit-test-agent, edge-case-agent
**Why:** Improves test quality over time

---

#### 7. preferences_store.json (USER_STORY_AGENT)
**Purpose:** User preferences for story generation

**Location:** `USER_STORY_AGENT/memory/preferences_store.json`
**Used by:** USER_STORY_AGENT Streamlit app
**Why:** Remembers user preferences across sessions

---

## How Agents Use Memory

### Email Operations
**All agents sending emails:**
- ✅ Read `memory/email_config.json` for user_google_email, default_to, default_cc
- ✅ Use values from config (never hardcode)
- ✅ Pass user_google_email to all Google Workspace MCP tools

### Drive Uploads
**All agents uploading to Drive:**
- ✅ Read `memory/google_drive_config.json` for folder IDs
- ✅ Use upload_defaults for file type mapping
- ✅ Pass folder_id to `tools/upload_to_drive.py`

### Content Creation
**Content agents (copywriter, email-specialist, social-media-manager):**
- ✅ Read `memory/brand_voice.json` for tone and style
- ✅ Follow voice principles in ALL content
- ✅ Avoid anti-patterns from guidelines

### Visual Design
**Visual agents (visual-designer, presentation-designer, pdf-specialist):**
- ✅ Read `memory/visual_guidelines.json` for brand colors
- ✅ Use Dux Machina color palette
- ✅ Follow design principles

---

## Google Drive Upload Strategy

### ⚠️ CRITICAL: MCP is BROKEN for Binary Files

Google Workspace MCP's `create_drive_file` has a critical bug:
- Creates 116-byte placeholder files instead of uploading actual content
- Test confirmed: PPTX file (26 KB) → uploaded as only 116 bytes
- Fails silently - returns "success" but file is unusable

### PRIMARY METHOD: Use Python Tool ✅

**For ALL File Types:**

```python
from tools.upload_to_drive import upload_to_drive

# Read folder ID from memory
import json
with open('MARKETING_TEAM/memory/google_drive_config.json') as f:
    drive_config = json.load(f)

folder_id = drive_config['upload_defaults']['presentations']  # or 'images', 'videos', etc.

result = upload_to_drive(
    file_path="outputs/presentations/deck.pptx",
    file_name="My Presentation.pptx",
    folder_id=folder_id  # From google_drive_config.json
)

# Returns: {'file_id': '...', 'file_name': '...', 'web_view_link': '...'}
```

**Features:**
- ✅ Uses `token_drive.pickle` (separate auth from Gmail)
- ✅ Handles all file types: PPTX, PDF, XLSX, PNG, MP4, HTML, DOCX, etc.
- ✅ Auto-detects MIME types from file extensions
- ✅ Verified working with full file content
- ✅ **PRIMARY METHOD** for all uploads

### ❌ AVOID: MCP for Binary Files

```python
# ❌ DO NOT USE for binary files
mcp__google-workspace__create_drive_file(...)
```

**Why:**
- Creates placeholder files (116 bytes) instead of uploading content
- Fails silently - returns "success" but file unusable
- Only safe for Google Workspace text documents (Docs, Sheets, Forms created from text)

---

## Email Sending Strategy

### Two Approaches Based on Attachment Needs

#### Without Attachments (Text-Only)

**Use:** Google Workspace MCP tool

```python
mcp__google-workspace__send_gmail_message(
    user_google_email="from_email_config.json",
    to="recipient@example.com",
    subject="Email Subject",
    body="Email body content",
    body_format='html'  # CRITICAL for proper rendering
)
```

**Features:**
- ✅ Fast and simple
- ✅ Already authenticated through MCP
- ✅ Perfect for text-only emails
- ✅ No file size limitations for body content

**Requirements:**
- Must use `user_google_email` from `email_config.json`
- Must set `body_format='html'` for proper line breaks
- Convert plaintext to HTML before sending (see gmail-agent.md)

---

#### With Attachments

**Use:** Python Gmail API tool

```python
from tools.send_email_with_attachment import send_email_with_attachment

send_email_with_attachment(
    to="recipient@example.com",
    subject="Email Subject",
    body="Email body content",
    attachment_path="outputs/pdfs/whitepaper.pdf"
)
```

**Features:**
- ✅ Supports file attachments via MIME multipart messages
- ✅ Handles base64 encoding automatically
- ✅ Automatically converts plaintext to HTML for proper formatting
- ✅ Recommended for files under 25 MB

**Requirements:**
- Requires full Gmail API scope authentication
- Uses `token.pickle` for auth

---

### Email Formatting Rules (ALL EMAILS)

**Clean Plaintext Body:**
- ❌ No markdown symbols (no ##, **, ---, etc.)
- ✅ Professional formatting with proper spacing
- ✅ Clear hierarchy with section headers
- ✅ Use bullet points with • character
- ✅ Section headers in UPPERCASE for emphasis
- ✅ Business-appropriate tone
- ✅ Greeting and closing

**HTML Rendering (Automatic):**
- Both MCP and Python tools send HTML emails
- **UPPERCASE headers automatically bolded** (e.g., "DOCUMENT OVERVIEW" → **DOCUMENT OVERVIEW**)
- Line breaks (`\n`) → `<br>` tags
- Double line breaks (`\n\n`) → `<br><br>` (paragraph breaks)
- Professional styling: Arial/Calibri, 11pt, line-height 1.5
- No more "wall of text" formatting issues

**Example Clean Email Body:**
```
Hi,

Here's the landing page we created today.

LANDING PAGE OVERVIEW

Platform: AI InvestIQ
Purpose: Investment intelligence platform

KEY FEATURES

The page includes:

• Hero section with compelling stats
• 6 feature cards explaining benefits
• Social proof with testimonials

File is attached and ready to deploy.

Best regards
```

---

## Agent Definition Example

**Example from gmail-agent.md:**

```markdown
## ⚙️ Configuration Files (READ FIRST)

**ALWAYS read these memory files before starting work:**

1. **memory/email_config.json** - Email defaults (CRITICAL for ALL email operations)
   - Contains: `user_google_email`, `default_to`, `default_cc`
   - Used when: Sending emails, creating drafts, searching messages
   - Required for: ALL Google Workspace MCP email tools

2. **memory/google_drive_config.json** - Drive folder IDs (if uploading attachments)
   - Contains: Folder IDs for organized file storage
   - Used when: Uploading email attachments to Drive first
   - Required for: Drive file uploads
```

**Why this matters:** Agents know exactly which files to read and when to use them. No hardcoding, ever.

---

## Best Practices

### For Agents
1. ✅ Read memory files at task start
2. ✅ Use values from config files
3. ❌ Never hardcode email addresses
4. ❌ Never hardcode Drive folder IDs
5. ✅ Trust memory system for consistency

### For Developers
1. ✅ Update config once, affects all agents
2. ✅ Add new config files to agent definitions
3. ✅ Document which agents use which files
4. ❌ Don't duplicate config values across agents
5. ✅ Keep memory files gitignored (local-only)

---

## Security Notes

**All memory files are gitignored:**
- `memory/` folder excluded from version control
- Contains user-specific configuration (emails, folder IDs)
- Never committed to repository
- Local-only configuration

**Authentication files also gitignored:**
- `token.pickle` (Gmail auth)
- `token_drive.pickle` (Drive auth)
- `credentials.json` (OAuth credentials)
- `.env` files (API keys)

---

## See Also

- **[claude.md](claude.md)** - Repository navigation guide
- **[MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)** - Master guide for all 37 agents
- **Agent Definitions:** `.claude/agents/*.md` files in each system folder

---

**Last Updated:** 2025-11-02
