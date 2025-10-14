"""
Platform Formatters
Format content for specific social media platforms
"""

from claude_agent_sdk import tool
import json
import re


@tool(
    "format_twitter_post",
    "Format content for X/Twitter with character limits and hashtag optimization",
    {
        "content": str,
        "hashtags": list,  # List of hashtags (without #)
        "include_link": str  # Optional link to include
    }
)
async def format_twitter_post(args):
    """
    Format content for X/Twitter
    - Max 280 characters
    - 1-2 hashtags max
    - Link shortening consideration
    """
    content = args["content"]
    hashtags = args.get("hashtags", [])
    include_link = args.get("include_link", "")

    # Twitter specs
    MAX_CHARS = 280
    MAX_HASHTAGS = 2
    LINK_LENGTH = 23  # Twitter's t.co link length

    # Limit hashtags
    hashtags = hashtags[:MAX_HASHTAGS]

    # Build post
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags])

    # Calculate available space
    available_chars = MAX_CHARS
    if include_link:
        available_chars -= (LINK_LENGTH + 1)  # +1 for space
    if hashtags:
        available_chars -= (len(hashtag_str) + 1)  # +1 for space

    # Truncate content if needed
    if len(content) > available_chars:
        content = content[:available_chars-3] + "..."

    # Assemble post
    parts = [content]
    if include_link:
        parts.append(include_link)
    if hashtags:
        parts.append(hashtag_str)

    formatted_post = " ".join(parts)

    result = {
        "platform": "twitter",
        "post": formatted_post,
        "character_count": len(formatted_post),
        "character_limit": MAX_CHARS,
        "hashtags_used": hashtags,
        "link_included": bool(include_link),
        "specs": {
            "max_chars": MAX_CHARS,
            "recommended_hashtags": "1-2",
            "image_size": "1200x675px (16:9)",
            "video_length": "2:20 max",
            "engagement_tip": "Use conversational tone, ask questions"
        }
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "format_linkedin_post",
    "Format content for LinkedIn with professional optimization",
    {
        "content": str,
        "hashtags": list,  # List of hashtags (without #)
        "include_link": str,  # Optional link
        "include_cta": str  # Optional call-to-action
    }
)
async def format_linkedin_post(args):
    """
    Format content for LinkedIn
    - Optimal: 1300-1900 characters
    - 3-5 hashtags
    - Professional tone
    - Strong opening line
    """
    content = args["content"]
    hashtags = args.get("hashtags", [])
    include_link = args.get("include_link", "")
    include_cta = args.get("include_cta", "")

    # LinkedIn specs
    OPTIMAL_MIN = 1300
    OPTIMAL_MAX = 1900
    MAX_CHARS = 3000
    MAX_HASHTAGS = 5

    # Limit hashtags
    hashtags = hashtags[:MAX_HASHTAGS]
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags])

    # Build post
    parts = [content]

    if include_cta:
        parts.append(f"\n\n{include_cta}")

    if include_link:
        parts.append(f"\n\n🔗 {include_link}")

    if hashtags:
        parts.append(f"\n\n{hashtag_str}")

    formatted_post = "".join(parts)

    # Check length
    char_count = len(formatted_post)
    length_status = "optimal" if OPTIMAL_MIN <= char_count <= OPTIMAL_MAX else \
                   "too_short" if char_count < OPTIMAL_MIN else \
                   "acceptable" if char_count <= MAX_CHARS else "too_long"

    result = {
        "platform": "linkedin",
        "post": formatted_post,
        "character_count": char_count,
        "length_status": length_status,
        "optimal_range": f"{OPTIMAL_MIN}-{OPTIMAL_MAX}",
        "hashtags_used": hashtags,
        "link_included": bool(include_link),
        "cta_included": bool(include_cta),
        "specs": {
            "optimal_length": "1300-1900 chars",
            "max_chars": MAX_CHARS,
            "recommended_hashtags": "3-5",
            "image_size": "1200x627px (1.91:1)",
            "video_length": "3-5 minutes optimal",
            "engagement_tip": "Hook in first 2 lines, add personal story, ask for engagement"
        }
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "extract_hashtags",
    "Extract and suggest hashtags from content",
    {
        "content": str,
        "platform": str,  # twitter or linkedin
        "topic": str  # Optional topic/industry
    }
)
async def extract_hashtags(args):
    """
    Extract or suggest relevant hashtags from content
    """
    content = args["content"].lower()
    platform = args.get("platform", "twitter")
    topic = args.get("topic", "").lower()

    # Extract existing hashtags
    existing_hashtags = re.findall(r'#(\w+)', content)

    # Common marketing hashtags by category
    hashtag_library = {
        "marketing": ["Marketing", "DigitalMarketing", "ContentMarketing", "MarketingTips"],
        "ai": ["AI", "ArtificialIntelligence", "MachineLearning", "AIMarketing"],
        "social": ["SocialMedia", "SocialMediaMarketing", "SMM", "SocialMediaTips"],
        "seo": ["SEO", "SearchEngineOptimization", "SEOTips", "DigitalStrategy"],
        "content": ["ContentCreation", "ContentStrategy", "Content", "ContentMarketing"],
        "business": ["Business", "Entrepreneur", "Startup", "SmallBusiness"],
        "tech": ["Technology", "Tech", "Innovation", "TechNews"],
        "email": ["EmailMarketing", "EmailStrategy", "Newsletter", "EmailTips"]
    }

    # Suggest hashtags based on content
    suggested = []
    for category, tags in hashtag_library.items():
        if category in content or category in topic:
            suggested.extend(tags[:2])  # Add 2 from each relevant category

    # Combine and limit
    all_hashtags = list(set(existing_hashtags + suggested))

    # Platform-specific limits
    if platform == "twitter":
        recommended_count = 2
    else:  # linkedin
        recommended_count = 5

    recommended_hashtags = all_hashtags[:recommended_count]

    result = {
        "platform": platform,
        "existing_hashtags": existing_hashtags,
        "suggested_hashtags": suggested[:10],  # Top 10 suggestions
        "recommended_for_post": recommended_hashtags,
        "recommended_count": recommended_count
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "optimize_post_for_engagement",
    "Analyze and suggest improvements for social media engagement",
    {
        "content": str,
        "platform": str  # twitter or linkedin
    }
)
async def optimize_post_for_engagement(args):
    """
    Analyze post and suggest engagement optimizations
    """
    content = args["content"]
    platform = args.get("platform", "twitter")

    suggestions = []
    score = 100

    # Check for question (engagement driver)
    if "?" not in content:
        suggestions.append({
            "type": "engagement",
            "suggestion": "Consider adding a question to encourage responses",
            "impact": "high"
        })
        score -= 15

    # Check for CTA
    cta_keywords = ["comment", "share", "thoughts", "what do you think", "let me know", "tag someone"]
    has_cta = any(keyword in content.lower() for keyword in cta_keywords)
    if not has_cta:
        suggestions.append({
            "type": "call_to_action",
            "suggestion": "Add a call-to-action (e.g., 'What's your experience?', 'Share your thoughts')",
            "impact": "high"
        })
        score -= 15

    # Platform-specific checks
    if platform == "twitter":
        # Check length
        if len(content) > 280:
            suggestions.append({
                "type": "length",
                "suggestion": "Post exceeds 280 characters. Shorten or create thread.",
                "impact": "critical"
            })
            score -= 30

        # Check for conversational tone
        if not any(word in content.lower() for word in ["we", "you", "i", "let's"]):
            suggestions.append({
                "type": "tone",
                "suggestion": "Use more conversational language (you, we, I)",
                "impact": "medium"
            })
            score -= 10

    elif platform == "linkedin":
        # Check length
        char_count = len(content)
        if char_count < 1300:
            suggestions.append({
                "type": "length",
                "suggestion": f"Post is {char_count} chars. LinkedIn algorithm favors 1300-1900 characters.",
                "impact": "high"
            })
            score -= 20

        # Check for personal story
        story_indicators = ["i", "my", "our", "when i", "i learned", "experience"]
        has_story = any(indicator in content.lower() for indicator in story_indicators)
        if not has_story:
            suggestions.append({
                "type": "storytelling",
                "suggestion": "Add a personal story or experience for authenticity",
                "impact": "medium"
            })
            score -= 10

        # Check for formatting (line breaks)
        if "\n" not in content:
            suggestions.append({
                "type": "formatting",
                "suggestion": "Add line breaks for readability (LinkedIn rewards well-formatted posts)",
                "impact": "medium"
            })
            score -= 10

    # Check for emojis (subtle engagement boost)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        "]+", flags=re.UNICODE)

    if not emoji_pattern.search(content):
        suggestions.append({
            "type": "visual_appeal",
            "suggestion": "Consider adding 1-2 relevant emojis for visual appeal",
            "impact": "low"
        })
        score -= 5

    result = {
        "platform": platform,
        "engagement_score": max(0, score),
        "score_explanation": "Score based on engagement best practices (100 = optimal)",
        "total_suggestions": len(suggestions),
        "suggestions": suggestions,
        "character_count": len(content)
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "create_post_variations",
    "Create multiple variations of a post for A/B testing",
    {
        "base_content": str,
        "platform": str,
        "variation_count": int  # Number of variations (default 3)
    }
)
async def create_post_variations(args):
    """
    Generate variation strategies for A/B testing
    (Actual content generation should be done by copywriter agent)
    """
    base_content = args["base_content"]
    platform = args.get("platform", "twitter")
    variation_count = args.get("variation_count", 3)

    # Variation strategies
    strategies = [
        {
            "variation": "A",
            "strategy": "Question-first approach",
            "description": "Start with engaging question",
            "example_structure": "Question? + Main point + CTA"
        },
        {
            "variation": "B",
            "strategy": "Stat-first approach",
            "description": "Lead with compelling statistic",
            "example_structure": "Statistic + Context + CTA"
        },
        {
            "variation": "C",
            "strategy": "Story-first approach",
            "description": "Begin with personal anecdote",
            "example_structure": "Personal story + Insight + CTA"
        },
        {
            "variation": "D",
            "strategy": "Bold statement approach",
            "description": "Start with controversial/bold claim",
            "example_structure": "Bold statement + Reasoning + CTA"
        },
        {
            "variation": "E",
            "strategy": "How-to approach",
            "description": "Lead with actionable value",
            "example_structure": "How to [benefit] + Steps + CTA"
        }
    ]

    # Select variations
    selected_strategies = strategies[:variation_count]

    result = {
        "platform": platform,
        "base_content": base_content,
        "variation_count": variation_count,
        "variation_strategies": selected_strategies,
        "testing_recommendation": {
            "sample_size": "At least 100 impressions per variation",
            "metrics_to_track": ["engagement_rate", "click_through_rate", "comments", "shares"],
            "winner_criteria": "Highest engagement rate after statistical significance"
        },
        "note": "Use copywriter agent with these strategies to generate actual variations"
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }
