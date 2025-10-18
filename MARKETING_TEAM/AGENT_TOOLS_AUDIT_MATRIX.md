# Agent Tools & Skills Audit Matrix

**Generated:** 2025-10-18
**Status:** ❌ **CRITICAL ISSUES FOUND**

---

## Summary of Issues

### Critical Problems Found:
1. **❌ Non-existent tools referenced** - Many agents reference tools that don't exist
2. **❌ Wrong tool names** - Tools using MCP prefix when they shouldn't
3. **❌ Missing `@tool` decorators** - Some referenced "tools" are just Python functions
4. **❌ Inconsistent naming** - MCP tools have inconsistent prefixes

### Tools That DON'T EXIST (but are referenced):
- `mcp__marketing__get_brand_voice` - Referenced by 6+ agents, DOESN'T EXIST
- `mcp__marketing__save_content` - Referenced by email-specialist, DOESN'T EXIST
- `mcp__marketing__get_visual_guidelines` - Referenced by visual-designer and landing-page, DOESN'T EXIST
- `perplexity_research` - WRONG NAME (should be `mcp__perplexity__perplexity_research`)
- `perplexity_compare` - DOESN'T EXIST
- `generate_image` - WRONG NAME (should be `generate_gpt4o_image`)
- `create_presentation` - NOT a @tool (it's just a Python function)
- `mcp__openai__generate_gpt4o_image` - WRONG (should be `generate_gpt4o_image`)

---

## Agent-by-Agent Audit

### 1. **analyst** ⚠️ NEEDS FIXES
**Current Tools:**
- ✅ `mcp__bright-data__*` - OK (wildcard MCP)
- ✅ `WebSearch` - OK (built-in)
- ✅ `WebFetch` - OK (built-in)
- ✅ `mcp__google_workspace__create_sheet` - OK
- ✅ `mcp__google_workspace__update_sheet` - OK
- ✅ `mcp__google_workspace__read_sheet` - OK

**Status:** ✅ Good - All tools exist

---

### 2. **content-strategist** ✅ OK
**Current Tools:**
- ✅ `mcp__google_workspace__create_calendar_event` - OK
- ✅ `mcp__google_workspace__create_sheet` - OK
- ✅ `mcp__google_workspace__create_doc` - OK

**Status:** ✅ Good - All tools exist

---

### 3. **copywriter** ❌ CRITICAL
**Current Tools:**
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ✅ `mcp__google_workspace__create_doc` - OK
- ✅ `mcp__google_workspace__update_doc` - OK

**Current Skills:**
- ✅ `internal-comms` - OK

**Recommendations:**
- ❌ REMOVE: `mcp__marketing__get_brand_voice` (doesn't exist)
- ✅ ADD: Access to brand guidelines via filesystem skill or documentation

---

### 4. **editor** ❌ CRITICAL
**Current Tools:**
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ✅ `mcp__google_workspace__get_doc_content` - OK
- ✅ `mcp__google_workspace__modify_doc_text` - OK
- ✅ `mcp__google_workspace__create_doc` - OK
- ✅ `Read` - OK (built-in)

**Recommendations:**
- ❌ REMOVE: `mcp__marketing__get_brand_voice`

---

### 5. **email-specialist** ❌ CRITICAL
**Current Tools:**
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ❌ `mcp__marketing__save_content` - DOESN'T EXIST
- ✅ `mcp__google_workspace__create_doc` - OK

**Recommendations:**
- ❌ REMOVE: Both `mcp__marketing__*` tools (don't exist)
- ✅ ADD: `send_gmail` for email drafting
- ✅ ADD: `create_gmail_draft` for email creation

---

### 6. **gmail-agent** ✅ MOSTLY OK
**Current Tools:**
- ✅ `send_gmail` - OK
- ✅ `create_gmail_draft` - OK
- ✅ `send_email_campaign` - OK
- ✅ `mcp__google_workspace__send_email` - OK (but redundant with send_gmail)
- ✅ `mcp__google_workspace__create_draft` - OK (but redundant with create_gmail_draft)

**Recommendations:**
- ⚠️ REDUNDANCY: Has both local tools AND MCP versions (decide which to keep)

---

### 7. **landing-page-specialist** ❌ CRITICAL
**Current Tools:**
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ❌ `mcp__marketing__get_visual_guidelines` - DOESN'T EXIST
- ✅ `mcp__perplexity__*` - OK (wildcard)
- ✅ `mcp__bright-data__*` - OK (wildcard)
- ✅ `mcp__google_workspace__create_doc` - OK
- ✅ `mcp__google_workspace__upload_to_drive` - OK

**Current Skills:**
- ✅ `artifacts-builder` - OK
- ✅ `theme-factory` - OK

**Recommendations:**
- ❌ REMOVE: Both `mcp__marketing__*` tools

---

### 8. **lead-gen-agent** ✅ GOOD
**Current Tools:**
- ✅ `mcp__bright-data__*` - OK
- ✅ `mcp__perplexity__*` - OK
- ✅ `mcp__google_workspace__create_sheet` - OK
- ✅ `mcp__google_workspace__upload_to_drive` - OK

**Status:** ✅ Perfect - All tools exist

---

### 9. **pdf-specialist** ✅ GOOD
**Current Tools:**
- ✅ `generate_pdf` - OK
- ✅ `mcp__google_workspace__upload_to_drive` - OK

**Current Skills:**
- ✅ `pdf-filler` - OK
- ✅ `canvas-design` - OK

**Status:** ✅ Perfect

---

### 10. **presentation-designer** ❌ CRITICAL
**Current Tools:**
- ❌ `create_presentation` - NOT A @tool (just a Python function)
- ❌ `generate_image` - WRONG NAME (should be `generate_gpt4o_image`)
- ⚠️ `Task` - Built-in, but unusual for agent tool
- ✅ `mcp__google_workspace__create_drive_file` - OK

**Current Skills:**
- ✅ `theme-factory` - OK
- ✅ `artifacts-builder` - OK

**Recommendations:**
- ❌ REMOVE: `create_presentation` (not a tool)
- ❌ FIX: `generate_image` → `generate_gpt4o_image`
- ✅ ADD: `generate_powerpoint` (actual @tool)
- ✅ ADD: `create_pitch_deck` (actual @tool)

---

### 11. **research-agent** ❌ CRITICAL
**Current Tools:**
- ❌ `perplexity_research` - WRONG (should be `mcp__perplexity__perplexity_research`)
- ❌ `perplexity_compare` - DOESN'T EXIST
- ✅ `mcp__bright-data__*` - OK
- ✅ `WebSearch` - OK
- ✅ `WebFetch` - OK
- ✅ `mcp__playwright__*` - OK
- ✅ `mcp__google_workspace__create_doc` - OK

**Recommendations:**
- ❌ FIX: `perplexity_research` → `mcp__perplexity__perplexity_research`
- ❌ REMOVE: `perplexity_compare` (doesn't exist)
- ✅ ADD: `mcp__perplexity__perplexity_ask`
- ✅ ADD: `mcp__perplexity__perplexity_reason`

---

### 12. **router-agent** ✅ PERFECT
**Current Tools:**
- ✅ `classify_intent` - OK
- ✅ `get_agent_capabilities` - OK
- ✅ `list_available_agents` - OK
- ✅ `format_agent_response` - OK

**Status:** ✅ Perfect - All tools exist

---

### 13. **seo-specialist** ❌ CRITICAL
**Current Tools:**
- ✅ `mcp__perplexity__*` - OK
- ✅ `mcp__bright-data__*` - OK
- ✅ `mcp__playwright__*` - OK
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ✅ `mcp__google_workspace__create_doc` - OK

**Recommendations:**
- ❌ REMOVE: `mcp__marketing__get_brand_voice`

---

### 14. **social-media-manager** ❌ CRITICAL
**Current Tools:**
- ✅ `format_twitter_post` - OK
- ✅ `format_linkedin_post` - OK
- ✅ `extract_hashtags` - OK
- ✅ `optimize_post_for_engagement` - OK
- ✅ `create_post_variations` - OK
- ❌ `mcp__openai__generate_image` - DOESN'T EXIST
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ❌ `mcp__marketing__save_content` - DOESN'T EXIST
- ✅ `mcp__google_workspace__create_doc` - OK

**Current Skills:**
- ✅ `algorithmic-art` - OK
- ✅ `slack-gif-creator` - OK

**Recommendations:**
- ❌ REMOVE: All `mcp__marketing__*` and `mcp__openai__*` tools
- ✅ ADD: `generate_gpt4o_image`

---

### 15. **video-producer** ❌ CRITICAL
**Current Tools:**
- ✅ `generate_sora_video` - OK
- ✅ `create_video_storyboard` - OK
- ❌ `mcp__openai__create_video` - DOESN'T EXIST
- ❌ `mcp__marketing__get_brand_voice` - DOESN'T EXIST
- ✅ `mcp__google_workspace__upload_to_drive` - OK

**Recommendations:**
- ❌ REMOVE: Both `mcp__openai__*` and `mcp__marketing__*` tools

---

### 16. **visual-designer** ❌ CRITICAL - **PRIORITY FIX**
**Current Tools:**
- ❌ `mcp__openai__generate_gpt4o_image` - WRONG NAME
- ❌ `mcp__marketing__get_visual_guidelines` - DOESN'T EXIST
- ✅ `mcp__google_workspace__upload_to_drive` - OK

**Current Skills:**
- ✅ `algorithmic-art` - OK
- ✅ `canvas-design` - OK
- ✅ `theme-factory` - OK
- ✅ `figma` - OK

**Recommendations:**
- ❌ FIX: `mcp__openai__generate_gpt4o_image` → `generate_gpt4o_image` (**THIS IS THE DOG IMAGE BUG**)
- ❌ REMOVE: `mcp__marketing__get_visual_guidelines`

---

## Summary Statistics

**Total Agents:** 16

**Agents with Issues:**
- ❌ **Critical Issues:** 11 agents
- ⚠️ **Minor Issues:** 1 agent
- ✅ **No Issues:** 4 agents

**Non-Existent Tools Referenced:**
- `mcp__marketing__get_brand_voice` - 6 agents
- `mcp__marketing__save_content` - 2 agents
- `mcp__marketing__get_visual_guidelines` - 2 agents
- `mcp__openai__generate_gpt4o_image` - 1 agent (**visual-designer**)
- `mcp__openai__generate_image` - 1 agent
- `mcp__openai__create_video` - 1 agent
- `perplexity_research` - 1 agent (wrong name)
- `perplexity_compare` - 1 agent (doesn't exist)
- `generate_image` - 1 agent (wrong name)
- `create_presentation` - 1 agent (not a @tool)

---

## Priority Fixes (Ordered)

### 🔥 URGENT (Blocking Functionality):
1. **visual-designer** - Fix `mcp__openai__generate_gpt4o_image` → `generate_gpt4o_image`
2. **presentation-designer** - Fix `generate_image` → `generate_gpt4o_image`
3. **research-agent** - Fix perplexity tool names

### ⚠️ HIGH (Remove non-existent tools):
4. **All agents** - Remove all `mcp__marketing__*` references (6+ agents)
5. **social-media-manager** - Fix image generation tool
6. **video-producer** - Remove `mcp__openai__create_video`

### ✅ MEDIUM (Improvements):
7. **gmail-agent** - Decide on local vs MCP email tools (redundancy)
8. **presentation-designer** - Add proper PowerPoint tools

---

## Next Actions

1. ✅ Fix **visual-designer** first (for dog image test)
2. Fix all agents with non-existent `mcp__marketing__*` tools
3. Fix all agents with wrong MCP tool names
4. Test all fixed agents
5. Generate final report

---

*End of Audit Matrix*
