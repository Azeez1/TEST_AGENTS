"""
Router Tools
Intent classification and agent selection for conversational interface
"""

from claude_agent_sdk import tool
import json


# Intent categories and their agent mappings
INTENT_MAPPING = {
    "create_social_post": {
        "agents": ["social-media-manager", "visual-designer"],
        "description": "Create social media posts for X/Twitter or LinkedIn",
        "keywords": ["social", "tweet", "twitter", "linkedin", "post", "social media"]
    },
    "write_blog": {
        "agents": ["seo-specialist", "copywriter", "editor"],
        "description": "Write blog posts or articles",
        "keywords": ["blog", "article", "write", "content", "blog post", "long form"]
    },
    "create_image": {
        "agents": ["visual-designer"],
        "description": "Generate images using GPT-4o",
        "keywords": ["image", "graphic", "visual", "picture", "photo", "illustration"]
    },
    "create_video": {
        "agents": ["video-producer"],
        "description": "Generate video ads using Sora",
        "keywords": ["video", "sora", "ad video", "video ad", "commercial"]
    },
    "send_email": {
        "agents": ["email-specialist", "gmail-agent"],
        "description": "Create and send emails or campaigns",
        "keywords": ["email", "send", "campaign", "newsletter", "draft"]
    },
    "research_web": {
        "agents": ["seo-specialist"],
        "description": "Research web for trends, keywords, or competitor analysis",
        "keywords": ["research", "search", "seo", "keyword", "competitor", "trends", "web"]
    },
    "create_pdf": {
        "agents": ["pdf-specialist"],
        "description": "Create PDFs like whitepapers or lead magnets",
        "keywords": ["pdf", "whitepaper", "lead magnet", "document", "ebook"]
    },
    "create_presentation": {
        "agents": ["presentation-designer"],
        "description": "Create PowerPoint presentations or pitch decks",
        "keywords": ["presentation", "powerpoint", "pitch deck", "slides", "ppt"]
    },
    "full_campaign": {
        "agents": ["content-strategist"],
        "description": "Create complete marketing campaign with multiple assets",
        "keywords": ["campaign", "full", "complete", "everything", "all assets", "marketing campaign"]
    },
    "analyze_performance": {
        "agents": ["analyst"],
        "description": "Analyze marketing performance and metrics",
        "keywords": ["analyze", "analytics", "performance", "metrics", "data", "stats"]
    }
}


@tool(
    "classify_intent",
    "Classify user intent to determine which marketing agents to invoke",
    {
        "user_message": str,
        "conversation_history": list  # Optional: previous messages for context
    }
)
async def classify_intent(args):
    """
    Classify user intent based on message content
    Returns intent category and recommended agents
    """
    user_message = args["user_message"].lower()
    conversation_history = args.get("conversation_history", [])

    # Score each intent
    intent_scores = {}
    for intent, config in INTENT_MAPPING.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in user_message:
                score += 1
        intent_scores[intent] = score

    # Get highest scoring intent
    if max(intent_scores.values()) > 0:
        best_intent = max(intent_scores, key=intent_scores.get)
        intent_config = INTENT_MAPPING[best_intent]

        result = {
            "intent": best_intent,
            "confidence": "high" if intent_scores[best_intent] >= 2 else "medium",
            "agents_to_invoke": intent_config["agents"],
            "description": intent_config["description"],
            "user_message": args["user_message"]
        }
    else:
        # No clear intent - ask for clarification
        result = {
            "intent": "unclear",
            "confidence": "low",
            "agents_to_invoke": [],
            "description": "Unable to determine intent",
            "user_message": args["user_message"],
            "suggested_clarification": "Could you specify what type of content you'd like to create? (e.g., social post, blog, email, image, video)"
        }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "get_agent_capabilities",
    "Get detailed capabilities of a specific agent",
    {
        "agent_name": str
    }
)
async def get_agent_capabilities(args):
    """
    Return detailed capabilities of a specific agent
    """
    agent_name = args["agent_name"]

    # Agent capabilities database
    capabilities = {
        "content-strategist": {
            "role": "Lead orchestrator for full marketing campaigns",
            "capabilities": [
                "Campaign planning and strategy",
                "Coordinating multiple specialist agents",
                "Content calendar creation",
                "Multi-channel campaign orchestration"
            ],
            "outputs": ["Campaign plans", "Content calendars", "Coordination reports"],
            "tools": ["Task (for subagents)", "Web research"]
        },
        "social-media-manager": {
            "role": "Platform-optimized social media content creator",
            "capabilities": [
                "X/Twitter posts (280 chars, optimized)",
                "LinkedIn posts (1300-1900 chars, professional)",
                "Platform-specific hashtags and formatting",
                "Engagement optimization"
            ],
            "outputs": ["Social media posts", "Platform-specific content", "Hashtag recommendations"],
            "tools": ["format_twitter_post", "format_linkedin_post"]
        },
        "visual-designer": {
            "role": "Image creation using GPT-4o",
            "capabilities": [
                "GPT-4o image generation (gpt-image-1)",
                "Platform-specific image sizing",
                "Brand-consistent visuals",
                "High-quality graphics"
            ],
            "outputs": ["Images", "Graphics", "Visual assets"],
            "tools": ["generate_gpt4o_image", "upload_to_google_drive"]
        },
        "email-specialist": {
            "role": "Email campaign and sequence creator",
            "capabilities": [
                "Email copywriting",
                "Subject line optimization",
                "Campaign sequences",
                "Personalization strategies"
            ],
            "outputs": ["Email copy", "Subject lines", "Campaign sequences"],
            "tools": ["get_brand_voice"]
        },
        "gmail-agent": {
            "role": "Email sending and automation",
            "capabilities": [
                "Send individual emails",
                "Create drafts for review",
                "Send campaigns (rate limited)",
                "Attachment handling (25MB max)"
            ],
            "outputs": ["Sent emails", "Email drafts", "Campaign reports"],
            "tools": ["send_gmail", "create_gmail_draft", "send_email_campaign"]
        },
        "seo-specialist": {
            "role": "Keyword research and web trends analysis",
            "capabilities": [
                "Keyword research via Playwright",
                "Competitor analysis",
                "Web trends research",
                "Real-time data gathering"
            ],
            "outputs": ["SEO reports", "Keyword lists", "Competitor insights", "Trend data"],
            "tools": ["Playwright (browser automation)", "WebSearch", "WebFetch"]
        },
        "copywriter": {
            "role": "Long-form content writer",
            "capabilities": [
                "Blog posts (2000+ words)",
                "Articles and web copy",
                "Ad copy",
                "Brand-aligned writing"
            ],
            "outputs": ["Blog posts", "Articles", "Web copy", "Markdown content"],
            "tools": ["get_brand_voice"]
        },
        "editor": {
            "role": "Content quality assurance and review",
            "capabilities": [
                "Grammar and spelling checks",
                "Brand voice compliance",
                "Clarity and flow improvement",
                "SEO optimization review",
                "CTA effectiveness"
            ],
            "outputs": ["Revision notes", "Approved content", "Quality reports"],
            "tools": []
        }
    }

    if agent_name in capabilities:
        result = {
            "agent": agent_name,
            "details": capabilities[agent_name]
        }
    else:
        result = {
            "agent": agent_name,
            "error": "Agent not found",
            "available_agents": list(capabilities.keys())
        }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "list_available_agents",
    "List all available marketing agents and their purposes",
    {}
)
async def list_available_agents(args):
    """
    Return list of all available agents
    """
    agents = [
        {
            "name": "content-strategist",
            "purpose": "Lead orchestrator for full marketing campaigns",
            "use_for": "Complete campaigns with multiple assets"
        },
        {
            "name": "social-media-manager",
            "purpose": "Social media content creator",
            "use_for": "X/Twitter and LinkedIn posts"
        },
        {
            "name": "visual-designer",
            "purpose": "Image generation using GPT-4o",
            "use_for": "Graphics, images, visual assets"
        },
        {
            "name": "video-producer",
            "purpose": "Video creation using Sora",
            "use_for": "Video ads and commercials"
        },
        {
            "name": "email-specialist",
            "purpose": "Email campaign creator",
            "use_for": "Email copy and campaigns"
        },
        {
            "name": "gmail-agent",
            "purpose": "Email sending automation",
            "use_for": "Sending emails and drafts"
        },
        {
            "name": "seo-specialist",
            "purpose": "Keyword research and web analysis",
            "use_for": "SEO research, competitor analysis"
        },
        {
            "name": "copywriter",
            "purpose": "Long-form content writer",
            "use_for": "Blog posts, articles"
        },
        {
            "name": "editor",
            "purpose": "Content quality assurance",
            "use_for": "Content review and refinement"
        },
        {
            "name": "pdf-specialist",
            "purpose": "PDF creation",
            "use_for": "Whitepapers, lead magnets"
        },
        {
            "name": "presentation-designer",
            "purpose": "Presentation creation",
            "use_for": "PowerPoint decks, pitch decks"
        },
        {
            "name": "analyst",
            "purpose": "Performance analysis",
            "use_for": "Marketing metrics and analytics"
        }
    ]

    result = {
        "total_agents": len(agents),
        "agents": agents
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "format_agent_response",
    "Format agent response for user display",
    {
        "agent_name": str,
        "response": str,
        "status": str  # success, error, in_progress
    }
)
async def format_agent_response(args):
    """
    Format agent responses consistently for user display
    """
    agent_name = args["agent_name"]
    response = args["response"]
    status = args.get("status", "success")

    # Status emojis
    status_emojis = {
        "success": "✅",
        "error": "❌",
        "in_progress": "⏳",
        "warning": "⚠️"
    }

    emoji = status_emojis.get(status, "ℹ️")

    formatted = f"""
{emoji} **{agent_name.replace('-', ' ').title()}**

{response}

---
Status: {status}
"""

    return {
        "content": [{
            "type": "text",
            "text": formatted.strip()
        }]
    }
