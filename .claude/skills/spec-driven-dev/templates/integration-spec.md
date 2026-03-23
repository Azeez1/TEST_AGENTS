# Integration Spec: {Integration Name}

| Field | Value |
|-------|-------|
| **Author** | {name} |
| **Date** | {YYYY-MM-DD} |
| **Team** | {ENGINEERING_TEAM / etc.} |
| **Status** | Draft / In Review / Approved / Implemented |
| **Integration Type** | REST API / Webhook / MCP Server / SDK / File Transfer |

## Purpose

{What does this integration enable? What two systems are being connected and why?}

## Endpoints / Interfaces

### Endpoint 1: {Name}

| Attribute | Value |
|-----------|-------|
| **Method** | GET / POST / PUT / DELETE |
| **Path** | `/api/v1/{resource}` |
| **Auth** | Bearer token / API key / OAuth 2.0 |
| **Rate limit** | {X requests/minute} |

**Request:**
```json
{
  "field1": "string (required)",
  "field2": "number (optional, default: 0)"
}
```

**Response (200):**
```json
{
  "id": "string",
  "status": "success",
  "data": {}
}
```

**Error responses:**
| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Validate input and retry |
| 401 | Unauthorized | Refresh token |
| 429 | Rate limited | Exponential backoff, max 3 retries |
| 500 | Server error | Log and alert, do not retry |

## Data Contracts

### Input Schema
```json
{
  "type": "object",
  "required": ["field1"],
  "properties": {
    "field1": { "type": "string", "maxLength": 255 },
    "field2": { "type": "number", "minimum": 0 }
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" }
  }
}
```

## Authentication

- **Method:** {Bearer token / API key / OAuth}
- **Token storage:** {Environment variable name, e.g., `MY_API_KEY`}
- **Token rotation:** {How often, who manages it}
- **Scopes required:** {List of OAuth scopes if applicable}

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Network timeout | Retry with exponential backoff (1s, 2s, 4s), max 3 attempts |
| Invalid response format | Log error, return graceful failure to caller |
| Auth failure | Attempt token refresh once, then fail with clear error |
| Rate limit hit | Respect Retry-After header, queue remaining requests |

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | {API returns empty array} | {Treat as valid, return empty result} |
| 2 | {Partial failure in batch} | {Process successful items, report failed ones} |
| 3 | {Upstream API is down} | {Return cached data if available, else graceful error} |

## Acceptance Criteria

```gherkin
Given valid credentials and a well-formed request
When the endpoint is called
Then it returns a 200 response within {X}ms

Given the upstream API is rate-limiting
When a 429 response is received
Then the client retries with exponential backoff up to 3 times

Given invalid input data
When the endpoint is called
Then it returns a 400 with a descriptive error message
```

## Out of Scope

- {Webhook callbacks / polling only}
- {Batch operations / single-record only}
- {Real-time streaming / request-response only}

## Dependencies

- {API documentation URL}
- {SDK or client library}
- {Environment variables needed}
- {Network/firewall requirements}
