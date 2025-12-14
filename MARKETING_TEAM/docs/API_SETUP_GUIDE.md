# API Setup Guide

This guide provides step-by-step instructions for configuring all API keys and credentials needed across TEST_AGENTS teams.

## Overview

TEST_AGENTS uses several external services via APIs and MCP servers:
- **OpenAI** (GPT-4, DALL-E, image generation)
- **Google Workspace** (Gmail, Drive, Sheets, Docs)
- **Perplexity** (research and web intelligence)
- **Bright Data** (web scraping, SERP analysis)
- **Gemini** (video generation with Veo)
- **Anthropic** (Claude API - optional for testing)
- **n8n** (workflow automation)

**Not all APIs are required.** Configure only the services you plan to use.

---

## Quick Setup Checklist

- [ ] OpenAI API key (MARKETING, ENGINEERING)
- [ ] Google Workspace credentials (MARKETING)
- [ ] Perplexity API key (MARKETING research)
- [ ] Bright Data API key (MARKETING web scraping)
- [ ] Gemini API key (MARKETING video generation)
- [ ] n8n webhook URL (MARKETING automation)
- [ ] Anthropic API key (optional)

---

## 1. OpenAI API Setup

**Used by:** MARKETING_TEAM (visual-designer, copywriter), ENGINEERING_TEAM

**Services:**
- GPT-4o for content generation
- DALL-E for image generation
- Text analysis and embeddings

### Setup Steps:

1. **Get API Key**
   - Visit: https://platform.openai.com/api-keys
   - Sign in or create account
   - Click "Create new secret key"
   - Copy key (starts with `sk-...`)

2. **Configure Environment Variable**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

3. **Add to .env File** (recommended)
   ```bash
   # Create .env in project root
   echo "OPENAI_API_KEY=sk-your-key-here" >> .env

   # Add .env to .gitignore
   echo ".env" >> .gitignore
   ```

4. **Verify Setup**
   ```bash
   # Test OpenAI connection
   python -c "import openai; print('OpenAI configured successfully')"
   ```

### Usage in Agents:
- `visual-designer` - GPT-4o image generation
- `copywriter` - Content creation with GPT-4o
- `email-specialist` - Email generation

### Cost Considerations:
- GPT-4o: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
- DALL-E 3: ~$0.04 per standard quality image
- Set usage limits in OpenAI dashboard to control costs

---

## 2. Google Workspace API Setup

**Used by:** MARKETING_TEAM (gmail-agent, automation-agent, research-agent)

**Services:**
- Gmail (email sending/reading)
- Google Drive (file storage)
- Google Sheets (data management)
- Google Docs (document creation)

### Setup Steps:

1. **Create Google Cloud Project**
   - Visit: https://console.cloud.google.com/
   - Create new project: "TEST_AGENTS"
   - Note Project ID

2. **Enable Required APIs**
   Navigate to "APIs & Services" > "Enable APIs and Services"

   Enable:
   - Gmail API
   - Google Drive API
   - Google Sheets API
   - Google Docs API

3. **Create Service Account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: "test-agents-service"
   - Grant role: "Editor"
   - Create and download JSON key

4. **Configure Credentials**
   ```bash
   # Move credentials to project
   mkdir -p ~/TEST_AGENTS/credentials
   mv ~/Downloads/service-account-key.json ~/TEST_AGENTS/credentials/google_credentials.json

   # Set environment variable
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/TEST_AGENTS/credentials/google_credentials.json"
   ```

5. **Configure OAuth 2.0** (for user-facing operations)
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Download client configuration
   - Save as `credentials/client_secret.json`

6. **Set Up MCP Server** (if using Google Workspace MCP)
   ```bash
   # Install Google Workspace MCP server
   npm install -g @modelcontextprotocol/server-google-workspace

   # Configure in Claude desktop app
   # Add to claude_desktop_config.json:
   {
     "mcpServers": {
       "google-workspace": {
         "command": "npx",
         "args": ["@modelcontextprotocol/server-google-workspace"],
         "env": {
           "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/google_credentials.json"
         }
       }
     }
   }
   ```

7. **Update Memory Configuration**
   Edit `MARKETING_TEAM/memory/email_config.json`:
   ```json
   {
     "user_google_email": "your-email@gmail.com",
     "default_to": ["recipient@example.com"],
     "default_cc": [],
     "signature": "Your Name\\nYour Title"
   }
   ```

   Edit `MARKETING_TEAM/memory/google_drive_config.json`:
   ```json
   {
     "root_folder_id": "your-drive-folder-id",
     "content_folder_id": "content-folder-id",
     "social_media_folder_id": "social-media-folder-id",
     "campaigns_folder_id": "campaigns-folder-id"
   }
   ```

### Verify Setup:
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'credentials/google_credentials.json'
)
service = build('gmail', 'v1', credentials=credentials)
print("Google Workspace configured successfully")
```

### Usage in Agents:
- `gmail-agent` - Email operations
- `automation-agent` - Drive uploads, Sheets data
- All MARKETING agents - File storage and sharing

---

## 3. Perplexity API Setup

**Used by:** MARKETING_TEAM (research-agent, analyst, seo-specialist)

**Services:**
- Web search and research
- Competitor analysis
- Market intelligence
- Citation-backed answers

### Setup Steps:

1. **Get API Key**
   - Visit: https://www.perplexity.ai/settings/api
   - Sign up for Perplexity account
   - Generate API key
   - Copy key (starts with `pplx-...`)

2. **Configure Environment Variable**
   ```bash
   export PERPLEXITY_API_KEY="pplx-your-key-here"
   ```

3. **Add to .env File**
   ```bash
   echo "PERPLEXITY_API_KEY=pplx-your-key-here" >> .env
   ```

4. **Verify Setup**
   ```bash
   curl --request POST \
     --url https://api.perplexity.ai/chat/completions \
     --header "Authorization: Bearer $PERPLEXITY_API_KEY" \
     --header 'Content-Type: application/json' \
     --data '{
       "model": "llama-3.1-sonar-small-128k-online",
       "messages": [{"role": "user", "content": "test"}]
     }'
   ```

### Usage in Agents:
- `research-agent` - Deep web research with citations
- `analyst` - Competitive intelligence
- `seo-specialist` - SERP analysis and keyword research

### Cost Considerations:
- Sonar Small: ~$0.20 per 1M tokens
- Sonar Large: ~$1 per 1M tokens
- Citations included at no extra cost

---

## 4. Bright Data API Setup

**Used by:** MARKETING_TEAM (lead-gen-agent, analyst, seo-specialist)

**Services:**
- Web scraping
- SERP scraping
- LinkedIn data collection
- Company information gathering

### Setup Steps:

1. **Get API Credentials**
   - Visit: https://brightdata.com/
   - Sign up for account
   - Navigate to "Proxies & Scraping" > "Web Scraper API"
   - Get API token and zone credentials

2. **Configure Environment Variables**
   ```bash
   export BRIGHT_DATA_API_TOKEN="your-api-token"
   export BRIGHT_DATA_ZONE="your-zone"
   export BRIGHT_DATA_USERNAME="your-username"
   export BRIGHT_DATA_PASSWORD="your-password"
   ```

3. **Add to .env File**
   ```bash
   echo "BRIGHT_DATA_API_TOKEN=your-api-token" >> .env
   echo "BRIGHT_DATA_ZONE=your-zone" >> .env
   echo "BRIGHT_DATA_USERNAME=your-username" >> .env
   echo "BRIGHT_DATA_PASSWORD=your-password" >> .env
   ```

4. **Verify Setup**
   ```bash
   curl -u "$BRIGHT_DATA_USERNAME:$BRIGHT_DATA_PASSWORD" \
     "https://brd.superproxy.io:22225" \
     --proxy "brd.superproxy.io:22225"
   ```

### Usage in Agents:
- `lead-gen-agent` - LinkedIn scraping, company data
- `analyst` - Competitor website analysis
- `seo-specialist` - SERP scraping

### Cost Considerations:
- Pay-per-use: ~$5-10 per 1GB
- Set monthly budget limits in Bright Data dashboard

---

## 5. Gemini API Setup (for Video Generation)

**Used by:** MARKETING_TEAM (video-producer)

**Services:**
- Video generation with Veo
- Image-to-video creation
- UGC ad video production

### Setup Steps:

1. **Get API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create API key for Gemini
   - Copy key

2. **Configure Environment Variable**
   ```bash
   export GEMINI_API_KEY="your-gemini-key-here"
   ```

3. **Add to .env File**
   ```bash
   echo "GEMINI_API_KEY=your-gemini-key-here" >> .env
   ```

4. **Verify Setup**
   ```bash
   curl \
     -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
     -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY"
   ```

### Usage in Agents:
- `video-producer` - Veo video generation for UGC ads

### Cost Considerations:
- Veo video generation: Pay-per-use (check current pricing)
- Set usage limits in Google Cloud console

---

## 6. n8n Workflow Automation Setup

**Used by:** MARKETING_TEAM (automation-agent)

**Services:**
- Workflow orchestration
- Multi-tool integration
- Automated campaign execution

### Setup Steps:

1. **Install n8n** (self-hosted)
   ```bash
   npm install -g n8n

   # Or use Docker
   docker run -it --rm \
     --name n8n \
     -p 5678:5678 \
     -v ~/.n8n:/home/node/.n8n \
     n8nio/n8n
   ```

2. **Start n8n**
   ```bash
   n8n start
   # Access at http://localhost:5678
   ```

3. **Configure Webhook URLs**
   - Create workflow in n8n
   - Add Webhook trigger node
   - Copy webhook URL
   - Update `MARKETING_TEAM/memory/n8n_config.json`:
     ```json
     {
       "webhook_base_url": "http://localhost:5678/webhook",
       "campaign_webhook": "http://localhost:5678/webhook/campaign-trigger",
       "email_webhook": "http://localhost:5678/webhook/email-sender"
     }
     ```

4. **Configure n8n Credentials**
   In n8n UI:
   - Add OpenAI credentials
   - Add Google credentials
   - Add Perplexity credentials
   - Add any other service credentials

### Usage in Agents:
- `automation-agent` - Orchestrates multi-tool workflows
- All MARKETING agents can trigger n8n workflows

---

## 7. Anthropic API Setup (Optional)

**Used by:** Testing and development

**Services:**
- Claude API for testing
- Multi-model experimentation

### Setup Steps:

1. **Get API Key**
   - Visit: https://console.anthropic.com/
   - Create account
   - Navigate to API keys
   - Create new key

2. **Configure Environment Variable**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   ```

3. **Add to .env File**
   ```bash
   echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
   ```

---

## Environment Variables Summary

Create a `.env` file in your project root with all API keys:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Google Workspace
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google_credentials.json

# Perplexity
PERPLEXITY_API_KEY=pplx-your-key-here

# Bright Data
BRIGHT_DATA_API_TOKEN=your-api-token
BRIGHT_DATA_ZONE=your-zone
BRIGHT_DATA_USERNAME=your-username
BRIGHT_DATA_PASSWORD=your-password

# Gemini
GEMINI_API_KEY=your-gemini-key-here

# n8n
N8N_WEBHOOK_BASE_URL=http://localhost:5678/webhook

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Load environment variables:**
```bash
# In your shell
source .env

# Or use python-dotenv
pip install python-dotenv
```

---

## Security Best Practices

1. **Never commit API keys to git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "credentials/" >> .gitignore
   ```

2. **Use environment variables or secret managers**
   - Development: `.env` files
   - Production: AWS Secrets Manager, Google Secret Manager, etc.

3. **Rotate keys regularly**
   - OpenAI: Every 90 days
   - Google: Every 90 days
   - Other services: According to security policy

4. **Set usage limits**
   - OpenAI: Set monthly budget cap
   - Google Cloud: Set billing alerts
   - Bright Data: Set monthly spend limit

5. **Restrict API key permissions**
   - Only enable required scopes
   - Use separate keys for dev/staging/prod
   - Monitor usage logs

---

## Troubleshooting

### Issue: "Authentication failed"
**Solution:**
1. Verify API key is correct
2. Check environment variable is loaded: `echo $API_KEY_NAME`
3. Ensure key has required permissions

### Issue: "Google credentials not found"
**Solution:**
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Check JSON file exists: `ls -la $GOOGLE_APPLICATION_CREDENTIALS`
3. Ensure file has correct permissions: `chmod 600 credentials/google_credentials.json`

### Issue: "Rate limit exceeded"
**Solution:**
1. Check API usage in provider dashboard
2. Implement exponential backoff
3. Upgrade to higher tier if needed

### Issue: "n8n webhook not responding"
**Solution:**
1. Verify n8n is running: `curl http://localhost:5678`
2. Check webhook URL is correct
3. Activate workflow in n8n UI

---

## By Team: Required APIs

### MARKETING_TEAM
- **Required:**
  - OpenAI (visual content, copywriting)
  - Google Workspace (email, drive, docs)
- **Recommended:**
  - Perplexity (research)
  - Bright Data (lead generation)
- **Optional:**
  - Gemini (video generation)
  - n8n (automation)

### ENGINEERING_TEAM
- **Required:**
  - OpenAI (code generation, analysis)
- **Optional:**
  - Anthropic (testing)

### QA_TEAM
- **Required:**
  - None (uses built-in tools)
- **Optional:**
  - OpenAI (test generation)

### PROPOSAL_TEAM
- **Required:**
  - Google Workspace (docs generation)
- **Optional:**
  - OpenAI (content generation)

---

## Related Documentation

- [GETTING_STARTED.md](GETTING_STARTED.md) - Overall setup guide
- [MCP_SETUP.md](MCP_SETUP.md) - MCP server configuration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Debugging issues
- [MARKETING_TEAM/docs/getting-started/api-setup.md](MARKETING_TEAM/docs/getting-started/api-setup.md) - Team-specific setup

---

## Next Steps

After configuring APIs:
1. Test each agent that requires API access
2. Verify memory configuration files are updated
3. Run integration tests
4. Set up monitoring and usage alerts

**Questions?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [FAQ.md](FAQ.md)
