# Simple Agent Tests - Copy and Paste These Commands

**IMPORTANT:** Restart Claude Code first, then test these agents one at a time.

---

## ✅ Test 1: pdf-specialist

```
Use the pdf-specialist subagent to create a 3-page test PDF whitepaper about "AI Marketing Trends 2025" with sections on market growth, key benefits, and implementation strategies. Save it as test_whitepaper.pdf
```

**Expected:** PDF created in outputs/pdfs/ folder

---

## ✅ Test 2: presentation-designer

```
Use the presentation-designer subagent to create a 5-slide test presentation about "AI Marketing Automation" with slides for: title, problem, solution, benefits, and call-to-action. Save as test_presentation.pptx
```

**Expected:** PowerPoint created in outputs/presentations/ folder

---

## ✅ Test 3: social-media-manager

```
Use the social-media-manager subagent to create a LinkedIn post about AI marketing automation, including 3-5 hashtags and keeping it between 1300-1900 characters
```

**Expected:** LinkedIn-formatted post with hashtags

---

## ✅ Test 4: copywriter

```
Use the copywriter subagent to write a 500-word blog post introduction about "The Future of AI in Marketing" with an engaging hook and clear thesis statement
```

**Expected:** Blog post content with professional tone

---

## ✅ Test 5: editor

```
Use the editor subagent to review this text and suggest improvements: "AI is good for marketing. It helps with tasks. Many companies use it. It saves time."
```

**Expected:** Editorial feedback and improved version

---

## ✅ Test 6: visual-designer

```
Use the visual-designer subagent to create a professional header image for a blog post about AI marketing automation. The image should be 1200x630 pixels in landscape format
```

**Expected:** Image generated via GPT-4o, saved to outputs/images/

---

## ✅ Test 7: video-producer (ALREADY TESTED ✅)

```
Use the video-producer subagent to create a 4-second test video showing a modern office workspace
```

**Expected:** Video generated via Sora-2 ($0.40 cost)

---

## ✅ Test 8: email-specialist

```
Use the email-specialist subagent to write a welcome email for new newsletter subscribers introducing our AI marketing tools
```

**Expected:** Professional welcome email copy

---

## ✅ Test 9: gmail-agent

```
Use the gmail-agent subagent to create a draft email (don't send) with subject "Test Email" and body "This is a test from the gmail-agent"
```

**Expected:** Draft created in Gmail (requires Gmail API credentials)

---

## ✅ Test 10: analyst

```
Use the analyst subagent to create a simple analysis framework for measuring email campaign performance with key metrics to track
```

**Expected:** Analysis framework with metrics

---

## ✅ Test 11: content-strategist

```
Use the content-strategist subagent to create a simple 2-week content plan for launching a new AI product, including suggested content types and channels
```

**Expected:** Content calendar/plan

---

## ✅ Test 12: seo-specialist (Requires Perplexity MCP)

```
Use the seo-specialist subagent to research the top 5 keywords for "AI marketing tools" and provide search volume estimates
```

**Expected:** Keyword research results

---

## ✅ Test 13: research-agent (Requires Perplexity MCP)

```
Use the research-agent subagent to research the latest trends in AI-powered content creation and summarize the top 3 findings
```

**Expected:** Research summary with sources

---

## ✅ Test 14: landing-page-specialist

```
Use the landing-page-specialist subagent to create a simple landing page outline for an AI marketing tool, including headline, value proposition, and CTA
```

**Expected:** Landing page structure/outline

---

## ✅ Test 15: router-agent (NEWLY FIXED)

```
Use the router-agent subagent to help me plan a social media campaign for launching an AI product
```

**Expected:** Router asks clarifying questions and suggests which agents to use

---

## 🎯 Quick Test Script

If you want to test multiple at once, copy these commands and run them sequentially:

1. pdf-specialist → Create test whitepaper
2. presentation-designer → Create test presentation
3. social-media-manager → Create LinkedIn post
4. copywriter → Write blog intro
5. editor → Review sample text
6. visual-designer → Generate header image
7. email-specialist → Write welcome email
8. analyst → Create analysis framework
9. content-strategist → Create content plan
10. seo-specialist → Research keywords (requires Perplexity)
11. research-agent → Research trends (requires Perplexity)
12. landing-page-specialist → Create landing page outline
13. router-agent → Plan campaign

---

**Testing Time:** ~20-30 minutes for all 15 agents
**Prerequisites:** Restart Claude Code for MCP changes to take effect
