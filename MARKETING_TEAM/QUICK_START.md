# 🚀 Quick Start Guide - Autonomous Marketing Agents

## ⚡ 3-Step Setup

### Step 1: Restart Claude Code
Close and reopen Claude Code to load the new MCP server.

### Step 2: Verify MCP Server
```
Ask Claude: "What MCP tools are available from marketing-tools?"
```

You should see 15 tools listed.

### Step 3: Test Your First Agent
```
Ask Claude: "Use the copywriter subagent to write a 200-word blog intro about AI marketing"
```

---

## 📝 Example Commands

### **Write Content**
```
"Use copywriter to write a 2000-word blog about marketing automation"
```

### **Create Social Posts**
```
"Use social-media-manager to create a LinkedIn post about our new feature"
"Use social-media-manager to create a Twitter thread about productivity"
```

### **Generate Images**
```
"Use visual-designer to create a LinkedIn header showing AI collaboration"
"Use visual-designer to create 3 images for a product launch campaign"
```

### **Generate Videos**
```
"Use video-producer to create a 12-second product demo video in landscape"
"Use video-producer to create a 4-second Instagram story video in portrait"
```

### **Send Emails**
```
"Use gmail-agent to send this email to john@example.com"
"Use email-specialist to write a 3-email welcome sequence"
```

### **Complete Campaigns**
```
"Use router-agent to create a social media campaign for our product launch"
"Use content-strategist to plan a complete Q1 marketing campaign"
```

---

## 🛠️ Available Tools (Auto-Invoked by Agents)

Your agents will automatically use these tools when needed:

| Agent | Tools They Use |
|-------|----------------|
| **copywriter** | Read brand_voice.json |
| **social-media-manager** | format_twitter_post, format_linkedin_post, extract_hashtags, optimize_post_for_engagement, generate_gpt4o_image |
| **visual-designer** | generate_gpt4o_image, upload_file_to_drive |
| **video-producer** | generate_sora_video, upload_file_to_drive |
| **email-specialist** | send_gmail, create_gmail_draft |
| **gmail-agent** | send_gmail, create_gmail_draft, send_email_campaign |
| **router-agent** | classify_intent, get_agent_capabilities, list_available_agents, format_agent_response |
| **presentation-designer** | generate_gpt4o_image |

---

## 💰 Cost Reference

| Service | Cost | Usage |
|---------|------|-------|
| **GPT-4o Images** | $0.04 (1024x1024), $0.06 (1024x1536) | Per image |
| **Sora-2 Videos** | $0.10/second | 4s = $0.40, 8s = $0.80, 12s = $1.20 |
| **Gmail** | Free | 500 emails/day limit |
| **Google Drive** | Free | 15GB free storage |

---

## ⚠️ Rate Limits

- **Gmail:** 500 emails/day
- **Email Campaigns:** 7-second delay between sends
- **OpenAI:** Project-level rate limits apply
- **Google Drive:** API quota limits apply

---

## 🎯 Testing Checklist

- [ ] Restart Claude Code
- [ ] Verify MCP server loaded
- [ ] Test copywriter (simplest)
- [ ] Test social-media-manager with formatting
- [ ] Test visual-designer with image generation
- [ ] Test gmail-agent (send to yourself first!)
- [ ] Test router-agent multi-agent coordination

---

## 🔧 Troubleshooting

**"MCP server not found"**
→ Restart Claude Code

**"Tool not found"**
→ Check `.claude.json` has marketing-tools entry
→ Restart Claude Code

**"OpenAI API error"**
→ Check `MARKETING_TEAM/.env` has valid `OPENAI_API_KEY`

**"Gmail authentication failed"**
→ Need `gmail_credentials.json` in MARKETING_TEAM/
→ First run will open browser for OAuth

---

## 📚 Full Documentation

- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Complete setup guide
- [README.md](README.md) - System overview
- [docs/guides/usage-guide.md](docs/guides/usage-guide.md) - Detailed usage examples

---

## 🎊 You're Ready!

Your autonomous marketing agents are live and ready to use.

**Just start talking to Claude Code and invoke your agents!** 🚀
