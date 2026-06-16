---
description: One Render deploy status check (designed to be repeated via /loop while a deploy is in flight)
arguments:
  - name: service
    description: Render service name or ID (default - most recently deploying service)
    required: false
---

# Deploy Watch (single pass)

Run ONE status check on a Render deploy. Designed to be repeated via `/loop 5m /deploy-watch <service>`; each invocation is self-contained.

## Process

1. Target = **$ARGUMENTS**. If empty, use `mcp__render__list_services` + `mcp__render__list_deploys` to find the service with the most recent in-progress deploy.
2. Get the latest deploy via `mcp__render__list_deploys` / `mcp__render__get_deploy`.
3. If the deploy FAILED or the service is crash-looping, pull the last ~50 log lines via `mcp__render__list_logs` and include the first real error line.

## Output rules (keep the loop quiet)

- Still building/deploying: ONE line, e.g. `hermes-gateway: build_in_progress (4m elapsed)`.
- Reached `live`: announce success with the deploy ID and total duration, then say the loop can be stopped.
- Failed: announce loudly with the error line from logs and the likely next debugging step, then say the loop can be stopped.
- Use the Render MCP only. Do NOT redeploy, restart, or change env vars — the deploy_approval_gate requires explicit human approval for deploy actions.
