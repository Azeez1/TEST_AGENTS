"""
Test script for Perplexity API research capabilities
Tests different models and parameters to see what works best for research
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

if not PERPLEXITY_API_KEY:
    print("[ERROR] PERPLEXITY_API_KEY not found in .env file")
    exit(1)

print(f"[OK] API Key found: {PERPLEXITY_API_KEY[:20]}...")

# Perplexity API endpoint
API_URL = "https://api.perplexity.ai/chat/completions"

def test_perplexity_research(query, model="sonar-pro"):
    """
    Test Perplexity API for research

    Available models:
    - sonar-pro (recommended for research)
    - sonar (faster, cheaper)
    - sonar-reasoning (deep analysis)
    """

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a research assistant. Provide comprehensive, well-cited research on the given topic. Include statistics, trends, and actionable insights."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 4000,  # More tokens for comprehensive research
        "temperature": 0.2,  # Lower temperature for factual accuracy
        "top_p": 0.9,
        "search_domain_filter": [],  # Can filter to specific domains
        "return_images": False,
        "return_related_questions": True,  # Get related questions for deeper research
        "search_recency_filter": "month",  # Focus on recent data
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    try:
        print(f"\n{'='*60}")
        print(f"Testing model: {model}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()

            # Extract the research content
            content = data['choices'][0]['message']['content']

            print("[SUCCESS]\n")
            print("RESEARCH OUTPUT:")
            print("-" * 60)
            print(content)
            print("-" * 60)

            # Show citations if available
            if 'citations' in data:
                print("\nCITATIONS:")
                for i, citation in enumerate(data['citations'], 1):
                    print(f"{i}. {citation}")

            # Show related questions if available
            if 'related_questions' in data:
                print("\nRELATED QUESTIONS:")
                for q in data['related_questions']:
                    print(f"  - {q}")

            # Show usage stats
            if 'usage' in data:
                usage = data['usage']
                print(f"\nUSAGE STATS:")
                print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")

            return True, content

        else:
            print(f"[FAILED] - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None

    except Exception as e:
        print(f"[ERROR]: {str(e)}")
        return False, None


def main():
    """Run multiple research tests"""

    # Test 1: Marketing research
    print("\n" + "="*60)
    print("TEST 1: AI Marketing Automation Trends")
    print("="*60)

    success1, _ = test_perplexity_research(
        "Research the current state of AI-powered marketing automation in 2025. "
        "Include key trends, top tools, adoption rates, ROI data, and future predictions. "
        "Focus on B2B SaaS companies.",
        model="sonar-pro"
    )

    # Test 2: Competitive intelligence
    print("\n" + "="*60)
    print("TEST 2: Lead Generation Tool Comparison")
    print("="*60)

    success2, _ = test_perplexity_research(
        "Compare the top 5 B2B lead generation tools in 2025. "
        "Include pricing, features, user reviews, and ideal use cases. "
        "Provide a recommendation matrix.",
        model="sonar-pro"
    )

    # Test 3: Using sonar-reasoning for deeper analysis
    print("\n" + "="*60)
    print("TEST 3: Strategic Analysis with Reasoning Model")
    print("="*60)

    success3, _ = test_perplexity_research(
        "Analyze why multi-agent AI systems are becoming more popular than monolithic AI "
        "for marketing automation. What are the strategic advantages?",
        model="sonar-reasoning"
    )

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Test 1 (Marketing trends - sonar-pro): {'[PASSED]' if success1 else '[FAILED]'}")
    print(f"Test 2 (Competitive intel - sonar-pro): {'[PASSED]' if success2 else '[FAILED]'}")
    print(f"Test 3 (Strategic analysis - sonar-reasoning): {'[PASSED]' if success3 else '[FAILED]'}")

    if success1 or success2 or success3:
        print("\n[SUCCESS] At least one model works! We can build a custom research tool.")
        print("\nNext steps:")
        print("1. Create perplexity_research.py tool in MARKETING_TEAM/tools/")
        print("2. Add @tool decorator for Claude SDK integration")
        print("3. Update research-agent.md to use the new tool")
    else:
        print("\n[FAILED] No models worked. Check API key permissions or plan.")


if __name__ == "__main__":
    main()
