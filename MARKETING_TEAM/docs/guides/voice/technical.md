# 🎤 Voice Interface for Marketing Agents

**Real-time voice interaction with all 17 marketing agents via ElevenLabs Conversational AI**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Voice Commands](#voice-commands)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Voice Interface allows you to talk to all 17 MARKETING_TEAM agents using natural speech. Simply speak your request, and the appropriate agent will respond with voice output.

**Example Conversation:**
```
You: "Hey copywriter, write a blog about AI marketing trends"
Agent (copywriter voice): "I'll create a comprehensive blog about AI marketing trends. Let me start with the introduction..."

You: "Now create a LinkedIn post about that blog"
Agent (social-media-manager voice): "I'll create an engaging LinkedIn post highlighting the key insights from the blog..."
```

---

## ✨ Features

### Core Capabilities
- ✅ **Real-time voice interaction** - Speak to agents and hear responses instantly
- ✅ **Natural language routing** - No need to memorize commands; just talk naturally
- ✅ **All 17 agents supported** - Full access to entire marketing team
- ✅ **Multi-context management** - Handle up to 5 concurrent conversations
- ✅ **Conversation memory** - Sessions saved to `memory/voice_sessions.json`
- ✅ **Interruption handling** - Stop agent mid-response if needed
- ✅ **Automatic response formatting** - Markdown converted to natural speech
- ✅ **Latency monitoring** - Real-time ping/pong tracking
- ✅ **Audio level visualization** - See input/output levels in real-time

### Agent-Specific Voices
Each agent has a unique voice for personality:
- **copywriter, router-agent, content-strategist** - Professional narrator voice
- **social-media-manager, email-specialist, editor, gmail-agent** - Friendly communicator voice
- **visual-designer, presentation-designer** - Creative designer voice
- **video-producer, landing-page-specialist** - Dynamic producer voice
- **seo-specialist, analyst, pdf-specialist, automation-agent** - Technical expert voice
- **research-agent, lead-gen-agent** - Investigative researcher voice

---

## 🏗️ Architecture

### System Components

```
voice_app.py (Streamlit UI)
    ├── websocket_client.py     - WebSocket connection to ElevenLabs
    ├── audio_handler.py         - Microphone input & speaker output
    ├── voice_agent_router.py    - Agent detection & response formatting
    ├── context_manager.py       - Multi-context lifecycle management
    ├── conversation_memory.py   - Session persistence
    └── config.py                - Configuration loader
```

### Data Flow

```
1. User speaks → Microphone (PyAudio)
2. Audio → WebSocket → ElevenLabs STT
3. Transcript → Agent Router → Detect agent
4. Prompt → Claude Agent SDK → Generate response
5. Response → Format for speech
6. Text → ElevenLabs TTS → Audio
7. Audio → Speaker (PyAudio)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- ElevenLabs API key
- Microphone and speakers
- All MARKETING_TEAM dependencies installed

### Installation

```bash
# Navigate to MARKETING_TEAM folder
cd MARKETING_TEAM

# Install voice dependencies
pip install -r requirements_voice.txt

# Verify installation
python test_websocket_connection.py
```

**Expected output:**
```
✅ ALL TESTS PASSED! Ready to build voice interface.
```

### Launch Voice Interface

```bash
streamlit run voice_app.py
```

The interface will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### Basic Workflow

1. **Connect**
   - Click "🔌 Connect" in the sidebar
   - Wait for "🟢 Connected" status

2. **Start Recording**
   - Click "▶️ Start Recording"
   - A session ID will be generated

3. **Talk to Agents**
   - Say the agent name + your request
   - Example: "Talk to copywriter and write a blog about AI"

4. **Hear Response**
   - Agent responds with voice
   - Transcript appears in the UI

5. **Switch Agents**
   - Just mention a different agent name
   - Example: "Now talk to social media manager"

6. **Stop Recording**
   - Click "⏹️ Stop Recording"
   - Session is saved to memory

### Natural Language Examples

**Content Creation:**
```
"Copywriter, write a 2000-word blog about AI automation"
"Email specialist, create a welcome email sequence"
"Create a LinkedIn post about our new product"
```

**Visual Content:**
```
"Visual designer, make a header image for the blog"
"Video producer, create a 15-second product demo"
"Design a landing page for our webinar"
```

**Research & Strategy:**
```
"Research agent, find competitor pricing"
"SEO specialist, research keywords for AI marketing"
"Analyst, analyze our campaign performance"
```

**Special Commands:**
```
"List all available agents"
"Stop"
"Help"
"Switch to the email specialist"
```

---

## ⚙️ Configuration

### Voice Configuration (`memory/voice_config.json`)

```json
{
  "default_voice_id": "JBFqnCBsd6RMkjVDRZzb",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.8,
    "similarity_boost": 0.8,
    "use_speaker_boost": true
  },
  "conversation_settings": {
    "max_contexts": 5,
    "context_timeout_seconds": 20,
    "keep_alive_interval_seconds": 18,
    "default_language": "en"
  },
  "agent_voices": {
    "copywriter": "JBFqnCBsd6RMkjVDRZzb",
    "social-media-manager": "21m00Tcm4TlvDq8ikWAM",
    ...
  }
}
```

### Environment Variables (`.env`)

```bash
# ElevenLabs API Key
ELEVENLABS_API_KEY=sk_your_api_key_here

# Anthropic API Key (for agents)
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Audio Settings

Configure in Streamlit sidebar:
- **Microphone** - Select input device
- **Speaker** - Select output device
- **Sample Rate** - Default: 44100 Hz
- **Channels** - Default: Mono (1)

---

## 🗣️ Voice Commands

### Agent Selection

| Command | Agent | Aliases |
|---------|-------|---------|
| "Talk to copywriter" | copywriter | "writer", "blog writer" |
| "Social media manager" | social-media-manager | "twitter", "linkedin" |
| "Visual designer" | visual-designer | "image creator", "designer" |
| "Video producer" | video-producer | "video creator", "sora" |
| "Research agent" | research-agent | "researcher", "research" |
| "SEO specialist" | seo-specialist | "seo", "keywords" |
| "Email specialist" | email-specialist | "email writer" |
| "Landing page specialist" | landing-page-specialist | "landing page" |

**Full list:** See `voice_interface/voice_agent_router.py`

### System Commands

- **"Stop"** - Cancel current task
- **"List agents"** - Hear all available agents
- **"Help"** - Get usage instructions
- **"Switch agent"** - Change to different agent

---

## 🔧 Technical Details

### WebSocket Protocol

**Endpoint:** `wss://api.elevenlabs.io/v1/convai/conversation`

**Authentication:**
```
Headers: {
  "xi-api-key": "your_api_key"
}
```

**Message Types:**
- `user_audio_chunk` - Audio from user (base64)
- `audio` - Audio from agent (base64)
- `user_transcript` - User's speech transcribed
- `conversation_initiation_metadata` - Session started
- `ping` / `pong` - Latency monitoring
- `keep_alive` - Prevent 20s timeout

### Audio Format

**Input (Microphone):**
- Format: PCM 16-bit
- Sample Rate: 44100 Hz
- Channels: Mono (1)
- Chunk Size: 1024 frames

**Output (Speaker):**
- Format: MP3 44100 128kbps
- Sample Rate: 44100 Hz
- Channels: Mono (1)

### Latency Optimization

**Strategies:**
1. **Streaming Latency** - Level 3 optimization (0-4 scale)
2. **Chunk Buffering** - 120/160/250/290 character thresholds
3. **Keep-Alive** - Every 18s (must be < 20s timeout)
4. **Ping/Pong** - Every 5s for monitoring
5. **Adaptive Buffering** - Adjust based on network conditions

**Typical Latencies:**
- Speech-to-Text: 100-300ms
- Agent Response: 1-3s (depends on complexity)
- Text-to-Speech: 200-500ms
- **Total Round-Trip:** 1.5-4s

### Multi-Context Management

**Limits:**
- Max concurrent contexts: 5
- Context timeout: 20 seconds inactivity
- Auto-cleanup: Every 10 seconds

**Context Lifecycle:**
1. Create context for agent
2. Track activity (messages, audio chunks)
3. Timeout after 20s inactivity
4. Auto-cleanup on timeout
5. Close manually on agent switch

### Conversation Memory

**Storage:** `memory/voice_sessions.json`

**Session Data:**
```json
{
  "session_id": "session_20250121_123456",
  "started_at": "2025-01-21T12:34:56",
  "ended_at": "2025-01-21T12:45:30",
  "total_duration_seconds": 634.5,
  "agent_switches": 3,
  "total_messages": 12,
  "messages": [...]
}
```

**Query Capabilities:**
- Get all sessions
- Get session by ID
- Get recent sessions (limit N)
- Get conversation stats
- Export to text

---

## 🐛 Troubleshooting

### Connection Issues

**Problem:** "Failed to connect to ElevenLabs"

**Solutions:**
1. Check API key in `.env`:
   ```bash
   ELEVENLABS_API_KEY=sk_your_key_here
   ```
2. Verify internet connection
3. Check ElevenLabs API status
4. Run test script: `python test_websocket_connection.py`

---

### Audio Issues

**Problem:** "No audio detected" or "Cannot hear agent"

**Solutions:**
1. Check microphone permissions
2. Select correct devices in Settings
3. Test audio:
   ```bash
   python voice_interface/audio_handler.py
   ```
4. Verify PyAudio installation:
   ```bash
   pip install --force-reinstall pyaudio
   ```

---

### Agent Not Responding

**Problem:** "Agent doesn't understand command"

**Solutions:**
1. Speak clearly and mention agent name explicitly
2. Use full agent names (e.g., "copywriter" not "writer")
3. Check available aliases in `voice_agent_router.py`
4. Try rephrasing the command

---

### Latency Too High

**Problem:** "Responses are slow (>5 seconds)"

**Solutions:**
1. Check latency in sidebar (should be <100ms)
2. Reduce network congestion
3. Switch to wired internet connection
4. Lower `optimize_streaming_latency` in config
5. Check agent complexity (complex tasks take longer)

---

### Session Not Saving

**Problem:** "Conversation history empty"

**Solutions:**
1. Ensure `memory/` folder exists
2. Check write permissions
3. Verify `conversation_memory.py` is imported
4. Check for errors in console logs

---

## 📊 Performance Metrics

### Expected Performance

**Audio Quality:**
- Input Level: 0.02-0.8 (speaking normally)
- Output Level: 0.3-0.9 (clear playback)
- Background Noise: <0.02

**Network:**
- WebSocket Latency: <100ms (good), 100-300ms (acceptable), >300ms (slow)
- Packet Loss: <1%
- Bandwidth: ~50-100 KB/s per stream

**Memory:**
- Session File: ~1-5 KB per session
- Audio Buffers: ~100-500 KB
- Total RAM: ~200-500 MB

---

## 📚 API Documentation

### Voice Interface Modules

**websocket_client.py:**
```python
client = ElevenLabsWebSocketClient(config)
await client.connect()
await client.send_audio(audio_bytes)
await client.disconnect()
```

**audio_handler.py:**
```python
handler = AudioHandler(config)
handler.start_recording()
handler.start_playback()
handler.queue_audio(audio_bytes)
handler.cleanup()
```

**voice_agent_router.py:**
```python
router = VoiceAgentRouter(voice_config)
agent, prompt = router.route_message(user_input)
formatted = router.format_response_for_speech(response)
```

**context_manager.py:**
```python
manager = ContextManager(max_contexts=5)
ctx_id = manager.create_context(agent_name, voice_id)
manager.update_activity(ctx_id)
manager.close_context(ctx_id)
```

**conversation_memory.py:**
```python
memory = ConversationMemory()
memory.start_session(session_id)
memory.add_message(role, agent_name, content)
memory.end_session()
```

---

## 🎓 Best Practices

### For Best Voice Recognition

1. **Speak clearly** - Enunciate agent names
2. **Use pauses** - Brief pause after agent name
3. **Reduce background noise** - Quiet environment
4. **Good microphone** - Use quality mic if possible
5. **Consistent volume** - Speak at normal volume

### For Best Agent Responses

1. **Be specific** - Clear, detailed requests
2. **One task at a time** - Avoid multiple requests
3. **Natural language** - Speak normally, not robotically
4. **Context** - Provide necessary details
5. **Confirm agent** - Verify correct agent responded

### For Session Management

1. **End sessions** - Click "Stop Recording" when done
2. **Review history** - Check past conversations
3. **Export important sessions** - Save to text files
4. **Clear old sessions** - Periodically clean up memory
5. **Monitor stats** - Track agent usage patterns

---

## 🔐 Security & Privacy

### API Key Security
- API keys stored in `.env` (gitignored)
- Never commit `.env` to version control
- Rotate keys periodically
- Use separate keys for dev/prod

### Audio Privacy
- Audio NOT stored locally (only transcripts)
- Sessions saved as text only
- ElevenLabs privacy policy applies
- Can clear sessions anytime

### Network Security
- WebSocket uses TLS encryption (wss://)
- API key transmitted via headers (not URL)
- No audio data logged or cached

---

## 📝 License & Credits

**Built with:**
- ElevenLabs Conversational AI API
- Claude Agent SDK (Anthropic)
- PyAudio
- Streamlit
- websockets
- Pipecat Framework

**Developed for:** MARKETING_TEAM multi-agent system

**Version:** 1.0.0

**Last Updated:** 2025-10-21

---

## 🆘 Support

**For issues:**
1. Check [Troubleshooting](#troubleshooting) section
2. Run diagnostic test: `python test_websocket_connection.py`
3. Review logs in console
4. Check ElevenLabs API status
5. Verify all dependencies installed

**For feature requests:**
- See MARKETING_TEAM/README.md for contact info

---

**🎉 Enjoy talking to your marketing agents!**
