"""
Perplexity Research Tool - Claude SDK Integration
Comprehensive research capabilities for marketing agents
"""

import os
import requests
from anthropic import tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# API Configuration
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
API_URL = "https://api.perplexity.ai/chat/completions"


@tool
def conduct_research(
    query: str,
    model: str = "sonar-pro",
    search_recency: str = "month"
) -> str:
    """
    Conduct comprehensive research using Perplexity AI

    Use this tool for:
    - Market research and competitive intelligence
    - Industry trends and statistics
    - Evidence-backed insights with citations
    - Strategic analysis and recommendations

    Args:
        query: Research question or topic. Be specific and detailed.
            Examples:
            - "What are the top 5 AI marketing automation tools in 2025? Include pricing, features, and user reviews."
            - "Research B2B SaaS content marketing trends. Focus on ROI data and adoption rates."
            - "Compare multi-agent vs monolithic AI systems for marketing. Include strategic advantages."

        model: Perplexity model to use
            - "sonar-pro" (DEFAULT, RECOMMENDED): Comprehensive research with citations, best for marketing research
            - "sonar": Faster option, good for quick facts
            - "sonar-reasoning": Deep strategic analysis with thinking process

        search_recency: How recent sources should be
            - "month" (DEFAULT): Last 30 days - best for current trends
            - "week": Last 7 days - very recent news
            - "day": Last 24 hours - breaking news
            - "year": Last 12 months - broader trends

    Returns:
        Comprehensive research report with:
        - Detailed analysis and insights
        - Statistics and data
        - Numbered citations [1], [2], etc.
        - Related research questions
        - Actionable recommendations

    Example usage:
        result = conduct_research(
            query="Research the ROI of AI-powered email marketing in 2025. Include case studies and statistics.",
            model="sonar-pro",
            search_recency="month"
        )
    """

    if not PERPLEXITY_API_KEY:
        return "[ERROR] PERPLEXITY_API_KEY not found in environment variables. Add to MARKETING_TEAM/.env file."

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    # System prompt optimized for marketing research
    system_prompt = """You are a marketing research assistant.

Provide comprehensive, well-structured research with:
1. Executive summary (2-3 sentences)
2. Key findings with data and statistics
3. Detailed analysis organized into sections
4. Actionable insights and recommendations
5. Future trends and predictions

Format guidelines:
- Use clear section headers
- Include specific numbers and percentages
- Cite sources inline [1][2][3]
- Use bullet points for clarity
- Highlight key takeaways
- Keep insights actionable for marketers"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "max_tokens": 4000,
        "temperature": 0.2,  # Lower for factual accuracy
        "top_p": 0.9,
        "search_recency_filter": search_recency,
        "return_related_questions": True,
        "return_images": False,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()

            # Build formatted output
            output = []

            # Main research content
            output.append("="*70)
            output.append("PERPLEXITY RESEARCH REPORT")
            output.append("="*70)
            output.append("")
            output.append(data['choices'][0]['message']['content'])
            output.append("")

            # Citations
            if 'citations' in data and data['citations']:
                output.append("-"*70)
                output.append("SOURCES & CITATIONS:")
                output.append("-"*70)
                for i, citation in enumerate(data['citations'], 1):
                    output.append(f"[{i}] {citation}")
                output.append("")

            # Related research questions
            if 'related_questions' in data and data['related_questions']:
                output.append("-"*70)
                output.append("RECOMMENDED FOLLOW-UP RESEARCH:")
                output.append("-"*70)
                for q in data['related_questions']:
                    output.append(f"  • {q}")
                output.append("")

            # Metadata
            usage = data.get('usage', {})
            output.append("-"*70)
            output.append(f"Model: {model} | Tokens: {usage.get('total_tokens', 'N/A')} | Recency: {search_recency}")
            output.append("="*70)

            return "\n".join(output)

        else:
            return f"[ERROR] Perplexity API request failed (Status {response.status_code})\n\nDetails: {response.text}"

    except requests.exceptions.Timeout:
        return "[ERROR] Research request timed out after 60 seconds. Try a more focused query or try again."

    except Exception as e:
        return f"[ERROR] Unexpected error during research: {str(e)}"


@tool
def quick_research(query: str) -> str:
    """
    Quick research for fast facts and brief answers

    Use this for:
    - Quick definitions or explanations
    - Fast competitor checks
    - Brief market overviews
    - Simple statistics

    This uses the faster "sonar" model for quicker results.

    Args:
        query: Research question (keep it focused)

    Returns:
        Brief research summary with citations

    Example:
        result = quick_research("What is the average email open rate for B2B SaaS in 2025?")
    """

    return conduct_research(
        query=query,
        model="sonar",
        search_recency="month"
    )


@tool
def strategic_analysis(query: str) -> str:
    """
    Deep strategic analysis with reasoning

    Use this for:
    - Competitive strategy analysis
    - Complex comparisons
    - Strategic decision-making
    - "Why" and "how" questions

    This uses the "sonar-reasoning" model which shows its thinking process.

    Args:
        query: Strategic question requiring analysis

    Returns:
        In-depth analysis with reasoning, comparisons, and recommendations

    Example:
        result = strategic_analysis(
            "Should B2B SaaS companies invest in multi-agent AI systems "
            "vs traditional marketing automation? Compare strategic advantages."
        )
    """

    return conduct_research(
        query=query,
        model="sonar-reasoning",
        search_recency="month"
    )


# For testing
if __name__ == "__main__":
    print("Testing Perplexity Research Tool...\n")

    # Test comprehensive research
    result = conduct_research(
        query="What are the top 3 lead generation strategies for B2B SaaS in 2025?",
        model="sonar-pro"
    )

    print(result)
