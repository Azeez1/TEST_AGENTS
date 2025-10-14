# API Setup Guide for Marketing Team

This guide walks you through setting up all API connections for your marketing agents.

---

## ✅ Already Configured

- **OpenAI API** - For GPT-4o image generation and Sora video generation
- **Perplexity API** - For advanced web research with real-time data and citations
- **Microsoft Office MCP** - For Word, Excel, and PowerPoint automation

---

## 📋 Quick Status

| API | Status | Required For | Setup Time |
|-----|--------|--------------|------------|
| OpenAI | ✅ Configured | visual-designer, video-producer | Done |
| Perplexity | ✅ Configured | research-agent, advanced web research | Done |
| Office MCP | ✅ Configured | Word, Excel, PowerPoint automation | Done |
| Gmail | ⚠️ Needs Setup | gmail-agent, email campaigns | 10 min |
| Google Drive | ⚠️ Needs Setup | File uploads and sharing | 5 min |
| Playwright MCP | ✅ Auto | seo-specialist, web research | Auto |

---

## 🔑 API Setup Instructions

### 1. OpenAI API (✅ Already Done!)

Your OpenAI API key is configured in [.env](.env)

**What this enables:**
- GPT-4o image generation (gpt-image-1 model)
- Sora video generation
- visual-designer agent
- video-producer agent

**Test it:**
```
"Use the visual-designer subagent to create an image of a modern tech startup office"
```

---

### 2. Perplexity API (✅ Already Done!)

Your Perplexity API key is configured in [.env](.env)

**What this enables:**
- Real-time web search with citations
- Advanced research capabilities
- Up-to-date information from the web
- research-agent specialist
- Market research and competitor analysis

**Official MCP Server:**
The official `@perplexity-ai/mcp-server` is configured in [.claude/mcp_config.json](.claude/mcp_config.json)

**Test it:**
```
"Use the research-agent to find the latest AI marketing trends for 2025"
```

---

### 3. Microsoft Office MCP (✅ Already Done!)

**Required for:** Word, Excel, PowerPoint automation

**What you get:**
- Create and edit Word documents programmatically
- Generate Excel spreadsheets with data
- Create PowerPoint presentations
- Full Microsoft Office automation capabilities

**How it works:**
Uses the `officemcp` Python package (configured in [.claude/mcp_config.json](.claude/mcp_config.json))

**Note:** This requires Microsoft Office to be installed on your system (Windows/Mac)

**Test it:**
```
"Create a Word document with a marketing campaign summary"
```

---

### 4. Gmail API (⚠️ Needs Setup)

**Required for:** email-specialist, gmail-agent

**What you get:**
- Send emails programmatically
- Create email drafts
- Send email campaigns (rate limited: 500/day)
- Attach files (up to 25MB)

#### Setup Steps:

**Step 1: Enable Gmail API**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable "Gmail API"
   - Go to "APIs & Services" → "Library"
   - Search "Gmail API"
   - Click "Enable"

**Step 2: Create OAuth Credentials**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop app"
4. Name it "Marketing Team Gmail"
5. Click "Create"
6. Download credentials JSON file
7. Rename to `gmail_credentials.json`
8. Place in `MARKETING_TEAM/` folder

**Step 3: First Authentication**
```bash
cd MARKETING_TEAM
python -c "from tools.gmail_api import GmailManager; GmailManager()"
```

This will:
- Open browser for Google OAuth
- Ask you to sign in
- Grant permissions
- Save `gmail_token.pickle` (reusable)

**Step 4: Verify**
```
"Use the gmail-agent to send a test email to myself"
```

---

### 5. Google Drive API (⚠️ Needs Setup)

**Required for:** All agents that upload files (visual-designer, video-producer, pdf-specialist, etc.)

**What you get:**
- Upload generated images to Drive
- Upload videos, PDFs, presentations
- Get shareable links
- Organize in folders

#### Setup Steps:

**Step 1: Enable Google Drive API**
1. Same Google Cloud project as Gmail
2. Go to "APIs & Services" → "Library"
3. Search "Google Drive API"
4. Click "Enable"

**Step 2: Add Drive Scope to OAuth**
1. The same `gmail_credentials.json` works for Drive
2. Just need to add Drive scope (already in code)
3. Delete `gmail_token.pickle` to re-authenticate with new scopes

**Step 3: Re-authenticate**
```bash
cd MARKETING_TEAM
python -c "from tools.google_drive import DriveManager; DriveManager()"
```

**Step 4: Optional - Specify Upload Folder**
1. Create a folder in Google Drive
2. Copy the folder ID from URL: `drive.google.com/drive/folders/FOLDER_ID_HERE`
3. Add to [.env](.env):
   ```
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   ```

**Step 5: Verify**
```
"Use the visual-designer to create an image and upload to Google Drive"
```

---

### 6. Playwright MCP Server (✅ Auto-Configured)

**Required for:** seo-specialist, web research, competitor analysis

**What you get:**
- Browser automation
- Web scraping
- Keyword research
- Competitor analysis
- Screenshot capture

#### Already Configured!

MCP config at [.claude/mcp_config.json](.claude/mcp_config.json) auto-starts Playwright.

**First-time setup:**
```bash
npx playwright install
```

**Test it:**
```
"Use the seo-specialist to research AI marketing trends"
```

---

## 🔒 Security Best Practices

### Protect Your Credentials

**Never commit these files to git:**
- `.env` (contains API keys)
- `gmail_credentials.json` (OAuth secrets)
- `gmail_token.pickle` (access tokens)

**Add to .gitignore:**
```
.env
gmail_credentials.json
gmail_token.pickle
memory/
outputs/
```

### API Key Safety
- ✅ Store in `.env` file
- ✅ Use environment variables
- ❌ Never hardcode in code
- ❌ Never commit to version control
- ❌ Never share publicly

### OAuth Token Refresh
- `gmail_token.pickle` auto-refreshes
- Re-authenticate if expired (rare)
- Revoke access at: [Google Account Permissions](https://myaccount.google.com/permissions)

---

## 📊 Rate Limits & Costs

### OpenAI API

**GPT-4o Image Generation (gpt-image-1):**
- 1024x1024: $0.04/image
- 1024x1536: $0.06/image
- 1536x1024: $0.06/image

**Sora Video Generation:**
- Pricing varies by video length and resolution
- Check [OpenAI Pricing](https://openai.com/api/pricing/)

### Gmail API

**Free Tier Limits:**
- 500 emails/day (standard Gmail account)
- 2000 emails/day (Google Workspace)
- Rate limited: 5-10 seconds between emails (built-in)

**Attachments:**
- Max 25MB per email
- Larger files → use Google Drive links

### Google Drive API

**Free Tier:**
- 15GB storage (shared with Gmail, Photos)
- Unlimited API requests (reasonable use)
- No upload limits beyond storage

---

## 🧪 Testing Your Setup

### Test OpenAI (Image Generation)
```
"Use the visual-designer subagent to create a minimalist logo for a tech startup"
```

Expected output:
- Image generated
- Saved to `outputs/images/final/`
- Uploaded to Google Drive (if configured)
- Shareable link provided

### Test OpenAI (Video Generation)
```
"Use the video-producer subagent to create a 5-second product demo video"
```

Expected output:
- Video generated via Sora
- Saved to `outputs/videos/`
- Uploaded to Google Drive (if configured)

### Test Gmail
```
"Use the gmail-agent to send me a test email with subject 'Test from Marketing Team'"
```

Expected output:
- Email sent
- Confirmation message
- Check your inbox

### Test Google Drive
```
"Use the visual-designer to create an image and upload to Drive"
```

Expected output:
- Image created
- Uploaded to Drive
- Shareable link: `https://drive.google.com/file/d/...`

### Test Web Research
```
"Use the seo-specialist to research 'AI content marketing trends 2025'"
```

Expected output:
- Playwright browser launched
- Web pages visited
- Data extracted
- Report with findings

---

## 🐛 Troubleshooting

### OpenAI API Errors

**"Invalid API key"**
- Check `.env` file has correct key
- Verify no extra spaces or quotes
- Key starts with `sk-proj-` or `sk-`

**"Insufficient quota"**
- Add payment method: [OpenAI Billing](https://platform.openai.com/account/billing)
- Check usage: [OpenAI Usage](https://platform.openai.com/usage)

**"Model not available"**
- Sora may require waitlist access
- GPT-4o images (gpt-image-1) available to all paid accounts

### Gmail API Errors

**"Credentials not found"**
- Ensure `gmail_credentials.json` exists in MARKETING_TEAM/
- Check file name is exactly `gmail_credentials.json`

**"Token expired"**
- Delete `gmail_token.pickle`
- Re-run authentication

**"Permission denied"**
- Check OAuth scopes include Gmail
- Re-create credentials with correct scopes

**"Daily send limit exceeded"**
- Wait 24 hours
- Or upgrade to Google Workspace (2000/day)

### Google Drive Errors

**"Drive API not enabled"**
- Enable in Google Cloud Console
- Wait 1-2 minutes for activation

**"Insufficient permissions"**
- Re-authenticate with Drive scope
- Delete `gmail_token.pickle` and re-auth

### Playwright Errors

**"Playwright not installed"**
```bash
npx playwright install
```

**"Browser not found"**
```bash
npx playwright install chromium
```

---

## 📚 Additional Resources

### Official Documentation
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Google Drive API Python Quickstart](https://developers.google.com/drive/api/quickstart/python)
- [Playwright Documentation](https://playwright.dev/python/)

### Pricing & Limits
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Gmail API Quotas](https://developers.google.com/gmail/api/reference/quota)
- [Google Drive API Quotas](https://developers.google.com/drive/api/guides/limits)

### Support
- OpenAI: [help.openai.com](https://help.openai.com)
- Google APIs: [Google Cloud Support](https://cloud.google.com/support)

---

## ✅ Setup Checklist

Use this to track your setup progress:

- [x] OpenAI API key added to `.env`
- [x] Perplexity API key added to `.env`
- [x] Official Perplexity MCP server configured
- [x] Microsoft Office MCP configured
- [x] `.env.example` created for reference
- [ ] Gmail API enabled in Google Cloud Console
- [ ] OAuth credentials downloaded (`gmail_credentials.json`)
- [ ] First Gmail authentication completed
- [ ] Google Drive API enabled
- [ ] Drive authentication completed (or use same as Gmail)
- [ ] Playwright browsers installed
- [ ] Tested image generation
- [ ] Tested web research with Perplexity
- [ ] Tested email sending
- [ ] Tested file upload to Drive
- [ ] Added `.env` to `.gitignore`

---

## 🎯 Next Steps

Once setup is complete:

1. **Read [usage-guide.md](../guides/usage-guide.md)** - Learn to use all 13 agents
2. **Try your first agent** - Start with visual-designer (already working!)
3. **Set up Gmail** - Enable email campaigns
4. **Set up Drive** - Enable file sharing
5. **Create your first campaign** - Use content-strategist to orchestrate

---

**Your OpenAI API is already configured!** Try creating an image right now:

```
"Use the visual-designer subagent to create a modern, minimalist banner image for a SaaS product"
```
