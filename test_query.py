import asyncio
from claude_agent_sdk import query

async def test():
    prompt = """Generate a simple JSON array with ONE user story about a login feature.

Format:
[
  {
    "user_story": "As a user, I want to log in, so that I can access my account",
    "feature_epic": "Login",
    "acceptance_criteria": ["Given I'm on login page, when I enter credentials, then I'm logged in"],
    "business_case": "Allow user access",
    "relevant_pages": "Login Page"
  }
]

Return ONLY the JSON, nothing else."""

    response = ""
    async for msg in query(prompt=prompt):
        if hasattr(msg, 'content'):
            for block in msg.content:
                if hasattr(block, 'text'):
                    response += block.text
        elif hasattr(msg, 'result'):
            response = msg.result

    print("Response:")
    print(response)

asyncio.run(test())
