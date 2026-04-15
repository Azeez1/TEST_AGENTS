"""
Quick test for Claude Managed Agents (public beta).
Requires: pip install --upgrade anthropic
Uses: ANTHROPIC_API_KEY from environment
"""
import os
from anthropic import Anthropic

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable first.")
        return

    client = Anthropic()

    # Step 1: Create agent
    print("Creating agent...")
    agent = client.beta.agents.create(
        name="Test Agent",
        model="claude-sonnet-4-6",
        system="You are a helpful assistant. Be concise.",
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"Agent ID: {agent.id}")

    # Step 2: Create environment
    print("Creating environment...")
    env = client.beta.environments.create(
        name="test-env",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    print(f"Environment ID: {env.id}")

    # Step 3: Start session
    print("Starting session...")
    session = client.beta.sessions.create(
        agent=agent.id,
        environment_id=env.id,
        title="Managed Agents Test",
    )
    print(f"Session ID: {session.id}")

    # Step 4: Send message and stream response
    print("\n--- Agent Response ---\n")
    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{
                "type": "user.message",
                "content": [{
                    "type": "text",
                    "text": "Write a Python script that prints 'Hello from Managed Agents!' and save it as hello.py, then run it.",
                }],
            }],
        )

        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        print(block.text, end="")
                case "agent.tool_use":
                    print(f"\n[Tool: {event.name}]")
                case "session.status_idle":
                    print("\n\n--- Agent finished. ---")
                    break

    print("\nManaged Agents is working! Your API key is connected.")


if __name__ == "__main__":
    main()
