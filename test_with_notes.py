import asyncio
from claude_agent_sdk import query

async def test():
    notes = """Meeting Notes - USPS Postal Store UI/UX Modernization

1. Addition of How It Works section
   - Mini education on the product details page
   - Helps customers understand if they're buying the right product

2. Product Comparison Table
   - Specific to Shipping Supplies Only
   - Create a comparison table for small boxes"""

    prompt = f"""Here are meeting notes about a USPS e-commerce project:

{notes}

Based on these notes, generate 2 user stories in JSON format:
[
  {{
    "user_story": "As a...",
    "feature_epic": "...",
    "acceptance_criteria": ["..."],
    "business_case": "...",
    "relevant_pages": "..."
  }}
]

Return ONLY the JSON array."""

    print(f"Prompt ({len(prompt)} chars):")
    print(prompt)
    print("\n" + "="*80 + "\n")

    response = ""
    async for msg in query(prompt=prompt):
        if hasattr(msg, 'content'):
            for block in msg.content:
                if hasattr(block, 'text'):
                    response += block.text
                    print(block.text, end='', flush=True)
        elif hasattr(msg, 'result'):
            response = msg.result
            print(msg.result)

    print("\n\nFinal response:")
    print(response)

asyncio.run(test())
