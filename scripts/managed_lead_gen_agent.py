"""
Lead Generation Agent - Ported to Claude Managed Agents
========================================================
Ports the MARKETING_TEAM lead-gen-agent to run autonomously in the cloud.

Requirements:
  pip install --upgrade anthropic

Environment variables needed:
  ANTHROPIC_API_KEY  - Your Anthropic API key
  BRIGHT_DATA_API_KEY - Your Bright Data API token (for scraping)

Usage:
  python scripts/managed_lead_gen_agent.py "Find 20 B2B SaaS companies in Austin TX with 50-200 employees"
  python scripts/managed_lead_gen_agent.py "Find local cleaning services in Miami FL with 4+ star ratings"
  python scripts/managed_lead_gen_agent.py --list-sessions  (show past sessions)
  python scripts/managed_lead_gen_agent.py --resume SESSION_ID "Follow up message"
"""

import os
import sys
import json
from anthropic import Anthropic


# ── Memory configs (ported from MARKETING_TEAM/memory/) ──────────────────

BRAND_VOICE = {
    "brand_name": "Dux Machina",
    "parent_company": "Dux Vitae",
    "tagline": "Strategy that builds. Systems that scale.",
    "positioning": "Hybrid AI consultancy — 60% strategic advisory, 40% implementation",
    "tone": "Calm Power. Strategic Precision. Elite Execution.",
    "vibe": "Tech Samurai meets McKinsey Strategist",
}

GOOGLE_DRIVE_CONFIG = {
    "user_google_email": "sabaazeez12@gmail.com",
    "lead_gen_folder_id": "1G5AQYEcKv_kKUMfr8QgPVAlkcMjvhEB_",
    "lead_gen_folder_name": "LEAD_GEN",
}

EMAIL_CONFIG = {
    "default_to": "sabaazeez12@gmail.com",
    "default_cc": "aoseni@duxvitaecapital.com",
}


# ── System prompt (adapted from lead-gen-agent.md) ───────────────────────

SYSTEM_PROMPT = """You are a business lead generation specialist for Dux Machina, a hybrid AI consultancy (60% strategic advisory, 40% implementation).

Your job is to discover, enrich, qualify, and export B2B and local business leads using web research, web scraping, and data analysis.

## Brand Context
- Company: Dux Machina (parent: Dux Vitae)
- Tagline: "Strategy that builds. Systems that scale."
- Target: Enterprise CTOs/VPs, growth-stage founders, SMBs — industry-agnostic
- Email: sabaazeez12@gmail.com / aoseni@duxvitaecapital.com

## Your Capabilities
You have bash, file read/write/edit, web search, and web fetch tools. Use these to:
1. Search the web for businesses matching criteria
2. Scrape company websites for contact info, team pages, about pages
3. Check LinkedIn company pages, Google Maps listings, review sites
4. Enrich leads with emails, phone numbers, social profiles
5. Score and qualify leads
6. Export to CSV files

## Bright Data API Access
If a BRIGHT_DATA_API_KEY is available in /tmp/config/credentials.json, use it with curl for advanced scraping:
- Endpoint: https://api.brightdata.com/datasets/v3/trigger
- Use for: LinkedIn company data, Google Maps listings, business directories

## Lead Scoring Criteria
- Tier 1 (Hot Lead, 8-10 pts): Has website + business email + active social + positive reviews + in target range
- Tier 2 (Warm Lead, 5-7 pts): Most criteria met
- Tier 3 (Cold Lead, 3-4 pts): Basic info only
- Tier 4 (Disqualified, <3 pts): Missing key criteria

## Contact Discovery Methods
- Extract from "Contact Us" and "About" pages via web_fetch
- Identify email patterns (firstname.lastname@company.com)
- Find general emails (info@, contact@, sales@, hello@)
- Extract from Google Maps listings
- Find social media profiles (LinkedIn, Instagram, Facebook, Twitter)

## Output Format
Always export leads as a CSV file saved to /home/user/leads/ with this schema:
```
Company,Industry,Location,Employees,Website,Email,Phone,LinkedIn,Rating,Score,Tier,Source,Notes,Date_Added
```

Also provide a summary report with:
- Total leads found
- Breakdown by tier
- Top 5 hottest leads with rationale
- Recommended next steps

## Lead Export Priority
1. Save CSV to /home/user/leads/
2. If task mentions Google Sheets, provide the data formatted for easy paste

## Quality Standards
- NEVER fabricate contact information — only use verified data from actual web sources
- Always note the source of each data point
- If an email can't be verified, mark it as "unverified" in Notes
- Include the date each lead was added
- De-duplicate by company name + location
"""


def create_agent(client: Anthropic) -> dict:
    """Create the lead-gen managed agent (reusable across sessions)."""
    agent = client.beta.agents.create(
        name="Dux Machina Lead Gen Agent",
        model="claude-sonnet-4-6",
        system=SYSTEM_PROMPT,
        tools=[
            {"type": "agent_toolset_20260401"},
        ],
    )
    print(f"Agent created: {agent.id} (version {agent.version})")
    return agent


def create_environment(client: Anthropic) -> dict:
    """Create the cloud environment with necessary packages."""
    environment = client.beta.environments.create(
        name="lead-gen-env",
        config={
            "type": "cloud",
            "packages": {
                "pip": ["openpyxl", "requests", "beautifulsoup4"],
            },
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"Environment created: {environment.id}")
    return environment


def setup_session_files(client: Anthropic, session_id: str):
    """Write config files into the container so the agent has context."""
    credentials = {}
    bright_data_key = os.getenv("BRIGHT_DATA_API_KEY")
    if bright_data_key:
        credentials["bright_data_api_key"] = bright_data_key

    setup_script = f"""
# Create working directories
mkdir -p /home/user/leads
mkdir -p /tmp/config

# Write brand config
cat > /tmp/config/brand.json << 'BRAND'
{json.dumps(BRAND_VOICE, indent=2)}
BRAND

# Write Google Drive config
cat > /tmp/config/google_drive.json << 'DRIVE'
{json.dumps(GOOGLE_DRIVE_CONFIG, indent=2)}
DRIVE

# Write email config
cat > /tmp/config/email.json << 'EMAIL'
{json.dumps(EMAIL_CONFIG, indent=2)}
EMAIL

# Write credentials (if available)
cat > /tmp/config/credentials.json << 'CREDS'
{json.dumps(credentials, indent=2)}
CREDS

echo "Config files written. Ready for lead generation."
ls -la /tmp/config/
"""

    # Send setup as first message
    client.beta.sessions.events.send(
        session_id,
        events=[{
            "type": "user.message",
            "content": [{
                "type": "text",
                "text": f"Run this setup script first, then confirm ready:\n```bash\n{setup_script}\n```",
            }],
        }],
    )


def run_session(client: Anthropic, agent_id: str, env_id: str, task: str):
    """Start a session, set up files, then send the lead gen task."""

    # Create session
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        title=f"Lead Gen: {task[:50]}",
    )
    print(f"Session started: {session.id}")
    print(f"(Save this ID to resume later: --resume {session.id})")
    print()

    # Stream: setup phase
    print("--- Setting up environment ---")
    with client.beta.sessions.events.stream(session.id) as stream:
        setup_session_files(client, session.id)
        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        print(block.text, end="")
                case "agent.tool_use":
                    print(f"\n[Tool: {event.name}]")
                case "session.error":
                    err = event.error if hasattr(event, 'error') else "Unknown error"
                    print(f"\n[ERROR] {err}")
                case "session.status_idle":
                    print("\n--- Setup complete ---\n")
                    break

    # Stream: actual lead gen task
    print("--- Running lead generation ---\n")
    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{
                "type": "user.message",
                "content": [{
                    "type": "text",
                    "text": task,
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
                case "session.error":
                    err = event.error if hasattr(event, 'error') else "Unknown error"
                    print(f"\n[ERROR] {err}")
                case "session.status_idle":
                    print("\n\n--- Lead generation complete ---")
                    print(f"Session ID: {session.id}")
                    print("Resume with: python scripts/managed_lead_gen_agent.py "
                          f"--resume {session.id} \"your follow-up\"")
                    break

    return session.id


def resume_session(client: Anthropic, session_id: str, message: str):
    """Resume an existing session with a follow-up message."""
    print(f"Resuming session: {session_id}\n")
    with client.beta.sessions.events.stream(session_id) as stream:
        client.beta.sessions.events.send(
            session_id,
            events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": message}],
            }],
        )
        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        print(block.text, end="")
                case "agent.tool_use":
                    print(f"\n[Tool: {event.name}]")
                case "session.error":
                    err = event.error if hasattr(event, 'error') else "Unknown error"
                    print(f"\n[ERROR] {err}")
                case "session.status_idle":
                    print("\n\n--- Done ---")
                    break


def list_sessions(client: Anthropic):
    """List recent sessions."""
    sessions = client.beta.sessions.list()
    print("Recent Lead Gen Sessions:")
    print("-" * 60)
    for s in sessions.data:
        if "Lead Gen" in (s.title or ""):
            print(f"  {s.id}  |  {s.title}  |  {s.status}")
    print()


# ── Agent/Environment persistence ────────────────────────────────────────

CONFIG_FILE = os.path.expanduser("~/.config/dux-machina/managed_agents.json")


def save_ids(agent_id: str, env_id: str):
    """Save agent and environment IDs for reuse."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    config["lead_gen_agent_id"] = agent_id
    config["lead_gen_env_id"] = env_id
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"IDs saved to {CONFIG_FILE}")


def load_ids() -> tuple:
    """Load saved agent and environment IDs."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        return config.get("lead_gen_agent_id"), config.get("lead_gen_env_id")
    return None, None


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    client = Anthropic()
    args = sys.argv[1:]

    # List sessions
    if "--list-sessions" in args:
        list_sessions(client)
        return

    # Resume session
    if "--resume" in args:
        idx = args.index("--resume")
        session_id = args[idx + 1]
        message = " ".join(args[idx + 2:])
        if not message:
            message = input("Enter follow-up message: ")
        resume_session(client, session_id, message)
        return

    # Get or create agent and environment
    agent_id, env_id = load_ids()

    if not agent_id or "--new-agent" in args:
        agent = create_agent(client)
        agent_id = agent.id
    else:
        print(f"Using saved agent: {agent_id}")

    if not env_id or "--new-env" in args:
        env = create_environment(client)
        env_id = env.id
    else:
        print(f"Using saved environment: {env_id}")

    save_ids(agent_id, env_id)

    # Get task from args or prompt
    task_args = [a for a in args if not a.startswith("--")]
    task = " ".join(task_args) if task_args else input("Enter lead gen task: ")

    if not task:
        print("No task provided. Example:")
        print('  python scripts/managed_lead_gen_agent.py "Find 20 SaaS companies in Austin TX"')
        sys.exit(1)

    run_session(client, agent_id, env_id, task)


if __name__ == "__main__":
    main()
