# Shared runtime hardening — implementation contract

This implements the September 5 audit with Codex as the initial integration
target. Existing Claude role definitions and live MCP settings remain the
source of truth. Shared helpers may change where the audit identified defects.

Acceptance:
- Generated agent YAML parses, descriptions and source hashes survive export,
  and staged generation validates before replacing live artifacts.
- Path helpers use one workspace registry and reject escapes.
- Hook payload adapters recognize current Codex and legacy Claude forms.
- Health checks report schema, drift, references, and behavior separately.
- Offline tests run from a locked environment without private memory or sends.
- Shared Codex operating instructions replace repeated runtime boilerplate;
  source domain instructions and specialist identities remain available.
- Representative routing, resume, and tool-contract evaluations are executable.
- Every claimed completion has an artifact and verification record.

Project relocation, global skill replacement, and live deployments are separate
migrations. Role mergers will be evaluated through compatibility entry points;
the audit did not provide enough usage evidence to delete specialist roles.
