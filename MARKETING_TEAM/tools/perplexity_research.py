"""
Perplexity Research Tool
Comprehensive research capabilities using Perplexity API
"""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
API_URL = "https://api.perplexity.ai/chat/completions"


def perplexity_research(
    query: str,
    model: str = "sonar-pro",
    max_tokens: int = 4000,
    search_recency: str = "month",
    include_related_questions: bool = True
) -> Dict[str, Any]:
    """
    Conduct comprehensive research using Perplexity API

    Args:
        query: Research question or topic
        model: Perplexity model to use
            - "sonar-pro" (recommended): Comprehensive research with citations
            - "sonar": Faster, cheaper option
            - "sonar-reasoning": Deep strategic analysis with reasoning
        max_tokens: Maximum response length (default: 4000)
        search_recency: How recent sources should be
            - "month" (default): Last 30 days
            - "week": Last 7 days
            - "day": Last 24 hours
            - "year": Last 12 months
        include_related_questions: Whether to return related research questions

    Returns:
        Dictionary containing:
            - content: Research report
            - citations: List of sources
            - related_questions: Follow-up research questions (if enabled)
            - usage: Token usage stats
            - success: Whether the request succeeded

    Example:
        result = perplexity_research(
            query="What are the top AI marketing trends in 2025?",
            model="sonar-pro",
            search_recency="month"
        )

        print(result['content'])  # Research report
        print(result['citations'])  # Sources
    """

    if not PERPLEXITY_API_KEY:
        return {
            "success": False,
            "error": "PERPLEXITY_API_KEY not found in environment variables",
            "content": None
        }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Provide comprehensive, well-cited research "
                    "on the given topic. Include statistics, trends, and actionable insights. "
                    "Format your response clearly with sections, bullet points, and data."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,  # Lower for factual accuracy
        "top_p": 0.9,
        "search_recency_filter": search_recency,
        "return_related_questions": include_related_questions,
        "return_images": False,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()

            result = {
                "success": True,
                "content": data['choices'][0]['message']['content'],
                "citations": data.get('citations', []),
                "related_questions": data.get('related_questions', []),
                "usage": data.get('usage', {}),
                "model": model
            }

            return result

        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "details": response.text,
                "content": None
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out after 60 seconds",
            "content": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "content": None
        }


def format_research_output(result: Dict[str, Any]) -> str:
    """
    Format research results for display

    Args:
        result: Dictionary from perplexity_research()

    Returns:
        Formatted string with research content and citations
    """

    if not result.get('success'):
        return f"[ERROR] Research failed: {result.get('error', 'Unknown error')}"

    output = []

    # Research content
    output.append("="*60)
    output.append("RESEARCH RESULTS")
    output.append("="*60)
    output.append("")
    output.append(result['content'])
    output.append("")

    # Citations
    if result.get('citations'):
        output.append("-"*60)
        output.append("CITATIONS:")
        output.append("-"*60)
        for i, citation in enumerate(result['citations'], 1):
            output.append(f"[{i}] {citation}")
        output.append("")

    # Related questions
    if result.get('related_questions'):
        output.append("-"*60)
        output.append("RELATED RESEARCH QUESTIONS:")
        output.append("-"*60)
        for q in result['related_questions']:
            output.append(f"  - {q}")
        output.append("")

    # Usage stats
    if result.get('usage'):
        usage = result['usage']
        output.append("-"*60)
        output.append(f"Model: {result.get('model', 'N/A')}")
        output.append(f"Tokens used: {usage.get('total_tokens', 'N/A')}")
        output.append("="*60)

    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    # Test the research function
    result = perplexity_research(
        query="What are the top 3 B2B lead generation strategies in 2025?",
        model="sonar-pro",
        search_recency="month"
    )

    print(format_research_output(result))
