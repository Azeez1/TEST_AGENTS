# X MCP Routing Notes

Purpose: keep the working X routes distinct so future Codex work does not mix
read-only MCP access with user-context posting.

## Working Routes

Mental model: keep two X lanes separate.

1. Search/research lane: MCP read access only.
2. Posting/action lane: user-context write access only.

Do not use the read lane for account actions, and do not use the write lane for
bulk discovery/search.

- `x-docs`
  - Remote MCP: `https://docs.x.com/mcp`
  - Use for X documentation lookup only.
  - No X app credentials or account actions.

- `xapi-direct`
  - Remote MCP: `https://api.x.com/mcp`
  - Auth: app-only bearer token via `X_BEARER_TOKEN`.
  - Use for live public X reads/searches, for example `search_posts_all`,
    `get_users_by_username`, trends, news, and public post lookup.
  - Do not use for posting, likes, follows, bookmarks, DMs, or other actions as
    the user.

- `xapi-fresh-direct`
  - Remote MCP: `https://api.x.com/mcp`
  - Auth: app-only bearer token via `X_BEARER_TOKEN_FRESH`.
  - New app/project read-only route kept separate for validation.
  - Requires a Codex app restart before the namespace appears as a callable MCP
    tool.

- `xurl` OAuth1 default profile
  - Auth: OAuth 1.0a user context configured with consumer key/secret plus user
    access token/secret.
  - Use for posting as `@EZdaArchitect`.
  - Confirmed working with `xurl --auth oauth1 post "test123"`.
  - Native `xurl --auth oauth1 quote ...` returned 403 on 2026-07-02 even
    though normal posting works. For quote tweets, try the API path first if
    explicitly requested, but be ready to fall back to the logged-in Chrome UI.
  - Posting must only happen after the user gives exact post text and explicit
    approval.

## Disabled / Avoid

- `xapi`
  - Stdio bridge: `npx @xdevplatform/xurl mcp https://api.x.com/mcp`
  - Currently disabled.
  - This is the OAuth2 user-context bridge and previously opened a broken X
    OAuth authorization page.
  - Do not re-enable until OAuth2 client/app state is intentionally revisited.

## Practical Rule

- For search/research: use `mcp__xapi_direct` or `mcp__x_docs`.
- For X articles, long posts, or threads: preview cards, search snippets, and
  browser-visible excerpts are not enough to claim a full read. Use the X
  read/search route or another canonical full-body source, then verify the
  first paragraph, last paragraph, visible title, and approximate length before
  summarizing. If only a preview is available, say so explicitly.
- For tweeting/posting: use the OAuth1 user-context posting route, not
  `xapi-direct`.
- For quote tweets: search/read with MCP, then post through the write lane. If
  `xurl quote` returns 403, use the logged-in Chrome quote composer and verify
  the quote card before clicking Post.
- Keep secrets in `.codex/secrets.local.env` and Windows user environment only;
  never write token values into docs or generated config.
