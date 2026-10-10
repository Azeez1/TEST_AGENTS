# Example: preserve meaning and caveats

Use this invented source fixture to exercise STE-inspired editing. It describes
no measured service and is not formally checked STE.

## Source

When the connection is available, the client may reuse a cached response for up
to 60 seconds unless the server marks it invalid; if the connection fails,
the client returns an error rather than stale data, and this behavior has not
been tested under sustained load.

## Revised text

When the connection is available, the client may reuse a cached response for up
to 60 seconds. A cached response is a saved reply. The client must not reuse the
response if the server marks it invalid. If the connection fails, the client
returns an error. It does not return stale data. This behavior has not been
tested under sustained load.

## Meaning review

| Source requirement | Preserved in revision |
|---|---|
| Available connection conditions reuse | First sentence retains that condition. |
| Reuse is possible, not guaranteed | Retains "may". |
| Maximum stated interval is 60 seconds | Retains "up to 60 seconds". |
| Server invalidation prevents reuse | Keeps the exception beside the reuse explanation. |
| Connection failure returns an error | Retains the result and condition. |
| Stale data is not returned on failure | Retains explicit negation. |
| Sustained-load behavior is untested | Keeps uncertainty in the main text. |

Treat "must not" as the explicit equivalent of the source's exclusion, not a
new independent requirement. Do not change "up to 60 seconds" into "every
60 seconds" or "always 60 seconds". Do not call this tested service behavior.

For a visual follow-up, load ELI5 and show available, invalidated, and failed
connection cases. Keep the load caveat visible and label the sequence illustrative.
For text-only requests, deliver the text without invoking presentation.
