# 🎤 Voice Interface - Quick Start Guide

**Talk to your 17 marketing agents with voice responses!**

---

## ⚡ 60-Second Setup

### 1. Install Dependencies

```bash
cd MARKETING_TEAM
pip install -r requirements_voice.txt
```

### 2. Add API Key

Edit `.env` file and add:
```bash
ELEVENLABS_API_KEY=your_api_key_here
```

### 3. Launch

**Windows:**
```bash
start_voice_cli.bat
```

**Mac/Linux:**
```bash
python voice_cli_simple.py
```

---

## 🎯 How to Use

### Basic Conversation

```
You: copywriter, write a blog about AI marketing trends

copywriter: I'm the copywriter. You said: write a blog about AI marketing trends.
           Let me help you with that!
   💾 Audio saved: outputs/voice_response_160802.mp3
   ▶️  Play this file to hear the response
```

### Switch Agents

```
You: social media manager, create a LinkedIn post

social-media-manager: I'm the social-media-manager. You said: create a LinkedIn post.
                     Let me help you with that!
   💾 Audio saved: outputs/voice_response_160845.mp3
   ▶️  Play this file to hear the response
```

### Exit

```
You: quit

📊 Session Summary
Duration: 125.3s
Messages: 4
Agent switches: 1

👋 Goodbye!
```

---

## 🤖 Available Agents

Just mention the agent name in your message:

| Agent | Keywords | Example |
|-------|----------|---------|
| **copywriter** | copywriter, writer, write, blog | "copywriter, write a blog about AI" |
| **social-media-manager** | social, linkedin, twitter, post | "social media manager, create a LinkedIn post" |
| **visual-designer** | image, visual, designer, picture | "visual designer, create a header image" |
| **video-producer** | video, producer, sora | "video producer, create a 15-second ad" |
| **research-agent** | research, find, search | "research agent, find competitor pricing" |
| **seo-specialist** | seo, keywords, optimize | "seo specialist, research keywords" |
| **email-specialist** | email, newsletter | "email specialist, write a welcome email" |

...and 10 more! See [../guides/voice/user-guide.md](../guides/voice/user-guide.md) for complete list.

---

## 📁 Where Are Files Saved?

**Audio Files:**
- Location: `outputs/voice_response_HHMMSS.mp3`
- Format: MP3, 44100 Hz
- Play with: VLC, Windows Media Player, or any MP3 player

**Session History:**
- Location: `memory/voice_sessions.json`
- View with: Streamlit UI (`streamlit run voice_app.py`)

---

## ✅ What Works

- ✅ Type messages to any of 18 agents
- ✅ Agent responds with text
- ✅ Audio file saved automatically
- ✅ Natural language agent detection
- ✅ Agent switching in same session
- ✅ Session persistence and memory
- ✅ Unique voice per agent

---

## ❌ What Doesn't Work (Yet)

- ❌ Real-time microphone input (threading issues)
- ❌ Live speaker output during conversation
- ❌ Voice-activated agent switching

**Why?** PyAudio callbacks run in separate threads and can't call async functions.

**Future solutions:**
- FastAPI backend with proper async handling
- Pipecat framework integration (COMING NEXT!)
- WebRTC for browser-based real-time audio

See [../guides/voice/user-guide.md](../guides/voice/user-guide.md) for technical details.

---

## 🎓 Example Workflows

### Create Blog Post

```
You: copywriter, write a 2000-word blog about AI marketing automation trends in 2025

[Agent generates blog post]
💾 Audio saved: outputs/voice_response_120345.mp3

You: editor, review the blog post

[Agent reviews and provides feedback]
💾 Audio saved: outputs/voice_response_120412.mp3

You: quit
```

### Social Media Campaign

```
You: social media manager, create a LinkedIn post about AI productivity tools

[Agent creates post]
💾 Audio saved: outputs/voice_response_143022.mp3

You: visual designer, create an image for the LinkedIn post

[Agent generates image]
💾 Audio saved: outputs/voice_response_143145.mp3

You: quit
```

### Lead Generation

```
You: lead gen agent, find 50 B2B SaaS companies in San Francisco with 50-200 employees

[Agent scrapes and generates leads]
💾 Audio saved: outputs/voice_response_151230.mp3

You: quit
```

---

## 📊 View Session History

**Launch Streamlit UI:**
```bash
streamlit run voice_app.py
```

**What you can see:**
- All past conversations
- Message history
- Agent switches
- Session duration
- Statistics

**Note:** The Streamlit UI is for viewing only. Actual voice interaction happens via CLI.

---

## 🐛 Troubleshooting

### "ELEVENLABS_API_KEY not found"
- Add API key to `.env` file
- Make sure `.env` is in MARKETING_TEAM folder

### "Failed to load voice configuration"
- Check `memory/voice_config.json` exists
- Re-run `python voice_cli_simple.py` to regenerate

### "Audio file not playing"
- Check `outputs/` folder exists
- Verify file was created (should be ~50-200 KB)
- Try different media player (VLC recommended)

### "Agent not responding"
- Make sure you mentioned agent name in message
- Try exact agent name: "copywriter" not "writer"
- See agent keywords table above

---

## 📖 More Documentation

- **[../guides/voice/user-guide.md](../guides/voice/user-guide.md)** - Comprehensive guide explaining what works and why
- **[../guides/voice/technical.md](../guides/voice/technical.md)** - Technical documentation for all modules
- **[../../README.md](../../README.md)** - MARKETING_TEAM overview

---

## 🚀 Get Started Now

```bash
cd MARKETING_TEAM
python voice_cli_simple.py
```

Type "copywriter, write a blog about AI" and experience voice-enabled agents!

---

**Last Updated:** 2025-10-21
**Status:** ✅ Working (text input + audio output)
**Coming Next:** 🎙️ Real-time microphone/speaker with Pipecat framework
