# Email Workflow - Proper Usage Guide

## Core Principle

**NO HARDCODED EMAIL CONTENT IN TOOLS** ✅

All email composition happens through **gmail-agent**, which reads configuration from `memory/email_config.json` and composes content explicitly for each email.

---

## The Correct Architecture

```
User Request
    ↓
gmail-agent (composes email)
    ↓
Reads memory/email_config.json (gets email addresses)
    ↓
Composes subject + body (clean plaintext)
    ↓
Calls send_email_with_attachment(to, subject, body, path, cc)
    ↓
Email sent with explicit parameters
```

---

## File Roles

### 1. memory/email_config.json (Configuration)

**Purpose:** Single source of truth for email addresses

**Contents:**
```json
{
  "user_google_email": "sabaazeez12@gmail.com",
  "default_to": "sabaazeez12@gmail.com",
  "default_cc": "aoseni@duxvitaecapital.com"
}
```

**Used by:** ALL agents sending emails (gmail-agent, email-specialist, etc.)

### 2. .claude/agents/gmail-agent.md (Agent Definition)

**Purpose:** Email specialist agent that handles all email operations

**Responsibilities:**
- Read `memory/email_config.json` for email addresses
- Compose email content (subject + body)
- Call tools with explicit parameters
- Report message ID to user

**Does NOT:**
- ❌ Hardcode email addresses
- ❌ Hardcode email subjects or bodies
- ❌ Use cached email content

### 3. tools/send_email_with_attachment.py (Pure Utility)

**Purpose:** Technical Gmail API wrapper - NO business logic

**What it does:**
- Authenticates with Gmail API
- Sends email with provided parameters
- Returns message ID

**What it does NOT do:**
- ❌ Compose email content
- ❌ Hardcode any email parameters
- ❌ Read configuration files
- ❌ Make decisions about recipients

**Function signature:**
```python
send_email_with_attachment(
    to_email: str,        # REQUIRED - from memory/email_config.json
    subject: str,         # REQUIRED - composed by gmail-agent
    body: str,            # REQUIRED - composed by gmail-agent
    attachment_path: str, # REQUIRED - file path
    cc: str = None,       # OPTIONAL - from memory/email_config.json
    bcc: str = None       # OPTIONAL
)
```

---

## Correct Usage Example

### Example 1: Send Document to Stakeholders

**User Request:**
```
"Send the stakeholder presentation document to my email"
```

**What gmail-agent should do:**

```python
# Step 1: Read configuration
with open('memory/email_config.json') as f:
    config = json.load(f)
    to_email = config['default_to']      # sabaazeez12@gmail.com
    cc_email = config['default_cc']      # aoseni@duxvitaecapital.com

# Step 2: Compose email (NO HARDCODING!)
subject = "AI Marketing Team Stakeholder Presentation"
body = """Hi,

Attached is the comprehensive stakeholder presentation.

DOCUMENT OVERVIEW

...content specific to this email...

Best regards"""

# Step 3: Verify file exists
attachment_path = "c:\\...\\AI_Marketing_Team_Stakeholder_Presentation.docx"

# Step 4: Call tool with explicit parameters
message_id = send_email_with_attachment(
    to_email=to_email,
    subject=subject,
    body=body,
    attachment_path=attachment_path,
    cc=cc_email
)

# Step 5: Confirm to user
print(f"Email sent! Message ID: {message_id}")
```

---

## What Was Wrong Before

### ❌ OLD (Broken) Approach

**tools/send_email_with_attachment.py had:**
```python
if __name__ == "__main__":
    to_email = "sabaazeez12@gmail.com"
    subject = "AI Investment Platform Landing Page"  # OLD EMAIL!
    body = """Hi, Here's the AI Investment Platform..."""  # OLD CONTENT!
    attachment_path = "outputs/landing_pages/ai_investment_platform.html"
    send_email_with_attachment(to_email, subject, body, attachment_path)
```

**Problem:** When run directly, it sent OLD hardcoded email instead of new parameters!

### ✅ NEW (Fixed) Approach

**tools/send_email_with_attachment.py now has:**
```python
if __name__ == "__main__":
    print("Pure utility - no hardcoded content")
    print("Usage instructions...")
    # NO ACTUAL EMAIL SENDING
```

**Result:** Tool is PURE UTILITY - only works when called with explicit parameters

---

## Email Formatting Rules

When composing email bodies, gmail-agent MUST:

✅ **DO:**
- Use clean plaintext (no markdown symbols)
- Use bullet points with • character
- Section headers in UPPERCASE
- Professional spacing
- Business-appropriate tone

❌ **DON'T:**
- Use markdown symbols (##, **, ---, etc.)
- Use markdown lists (* or - for bullets)
- Use code blocks (```)
- Use emojis (unless requested)

**Example - Good Email Body:**
```
Hi,

Attached is the stakeholder presentation.

DOCUMENT OVERVIEW

This presentation explains our AI Marketing Team system.

KEY HIGHLIGHTS

Performance Metrics:
• 97.8% faster than manual processes
• 99.98% cost reduction
• 46x scalability improvement

Best regards
```

**Example - Bad Email Body:**
```
Hi,

## Document Overview  ← WRONG (markdown)

**This presentation**  ← WRONG (markdown)

- 97.8% faster  ← WRONG (markdown list)

Best regards
```

---

## Testing the Tool

To verify the tool has no hardcoded content:

```bash
python tools/send_email_with_attachment.py
```

**Expected output:**
```
======================================================================
send_email_with_attachment.py - Pure Utility Function
======================================================================

This tool should be called by gmail-agent with explicit parameters.
It contains NO hardcoded email content.
...
```

**If you see actual email sending:** ❌ Tool is broken - has hardcoded content

---

## Common Mistakes to Avoid

### Mistake 1: Running tool directly instead of using gmail-agent
```bash
# ❌ WRONG
python tools/send_email_with_attachment.py
```

```
# ✅ CORRECT
"Use gmail-agent to send the document"
```

### Mistake 2: Hardcoding email addresses in scripts
```python
# ❌ WRONG
to_email = "sabaazeez12@gmail.com"  # Hardcoded!
```

```python
# ✅ CORRECT
config = json.load(open('memory/email_config.json'))
to_email = config['default_to']  # From config
```

### Mistake 3: Reusing old email content
```python
# ❌ WRONG
body = old_email_template  # Cached content!
```

```python
# ✅ CORRECT
body = compose_fresh_email_for_current_task()  # Fresh content
```

---

## Agent Coordination for Emails

**For complex emails, use multi-agent workflow:**

1. **email-specialist** → Composes compelling email copy
2. **gmail-agent** → Reads config, verifies attachment, sends email

**Example:**
```
User: "Send the stakeholder presentation with a professional email"

Flow:
1. Ask email-specialist to write professional email body
2. Use gmail-agent to send with that content + read config + attach file
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Send email with attachment | `"Use gmail-agent to send [file] to [recipient]"` |
| Check email sent successfully | Look for Message ID in response |
| Update default recipients | Edit `memory/email_config.json` |
| Test tool has no hardcoded content | `python tools/send_email_with_attachment.py` |

---

## Summary

✅ **gmail-agent composes ALL emails** - reads config, writes subject/body
✅ **Tools are PURE UTILITIES** - no hardcoded content, no business logic
✅ **Configuration is centralized** - memory/email_config.json is single source of truth
✅ **Each email is fresh** - no cached content, composed explicitly each time

**The Result:** Clean architecture, no surprises, every email is what you expect!

---

**Last Updated:** 2025-10-20
**Applies to:** All MARKETING_TEAM agents sending emails
