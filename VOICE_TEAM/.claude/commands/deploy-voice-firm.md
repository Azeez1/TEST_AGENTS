# Deploy Voice Firm

Deploy or re-deploy a law firm's AI voice agent to Retell.

## What This Does

Invokes the `voice-deployer` agent to:
1. Read `VOICE_TEAM/memory/firms/<firm-slug>.yml`
2. Render the global prompt + intake flow templates
3. POST a new conversation flow to Retell
4. POST a new agent to Retell
5. Attach the firm's phone number to the agent
6. Write a deployment artifact to `VOICE_TEAM/outputs/deployments/<firm-slug>.json`

## Usage

```
/deploy-voice-firm <firm-slug>
```

## Examples

```
/deploy-voice-firm sterling_legal
/deploy-voice-firm jones_family_law
/deploy-voice-firm hartwell_pi
```

## Prerequisites

Before running this command:
- The firm.yml MUST exist at `VOICE_TEAM/memory/firms/<firm-slug>.yml`
- The phone number specified in firm.yml MUST be already purchased in Retell
- `RETELL_API_KEY` must be set in `MARKETING_TEAM/.env`

If you haven't created the firm.yml yet, run `/new-voice-firm` first to onboard the firm.

## Output

On success, the command prints:
- Agent ID (e.g., `agent_046ea303e87fa84eb156c48ff4`)
- Conversation flow ID
- Phone number → agent binding confirmation
- Dashboard URL
- Test call instructions

## Re-Deployment

If the firm.yml has changed and you want to push updates, just re-run the command. The script will create a new agent + flow (the old one becomes orphaned — clean up periodically via Retell dashboard or `/voice-cleanup`).
