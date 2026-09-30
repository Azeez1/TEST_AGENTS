# Model Routing and Cost Controls

## Routing aliases

- `auto` and `standard` -> `gemini-3.5-flash`
- `budget` -> `gemini-3.1-flash-lite`
- `deep` -> `gemini-3.5-flash`

`gemini-2.5-flash` remains in the price table only for reproducibility on
existing projects. Google returns `404` for it on new-user projects as of July
2026, so do not route new work to it automatically.

Use stable model IDs by default. Allow an explicit model ID for controlled
experiments, but mark unknown pricing as an estimate unavailable.

## Cost model

Estimate video tokens at 258 per second and audio tokens at 32 per second.
Add the configured output-token allowance. Estimates are guards, not invoices;
provider pricing and media processing can change.

Default maximum estimated run cost: `$0.50`. Refuse a live call above the cap
unless the caller supplies a higher `--max-cost-usd` value. Include escalation
passes in the same budget.

## Escalation

Keep the first pass on the selected model. For bounded high-detail analysis:

1. Extract only the requested segment.
2. Keep the selected model so the preflight budget remains exact; choose the
   `deep` alias for the whole run when higher reasoning quality is required.
3. Stop at the configured maximum escalation count.
4. Stop when the cumulative estimate reaches the budget.
5. Append findings; never silently replace the first-pass evidence.

## API surfaces

- Use Gemini Files API for local or downloaded video.
- In `auto` mode, download public YouTube video temporarily and use the Files
  API so timestamps are grounded in the acquired media. Use direct public
  YouTube input only when acquisition fails or the caller selects `direct`.
- Use Interactions API with `store=false` and JSON Schema structured output.
- Delete uploaded Gemini files after processing by default.
- Keep API keys in environment or an explicitly discovered gitignored secrets
  file. Never serialize or log a key.
