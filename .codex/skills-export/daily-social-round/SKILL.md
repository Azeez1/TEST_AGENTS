---
name: "daily-social-round"
description: "Run EZ's daily LinkedIn + X engagement round (on-brand comments, replies, quote-posts, and a post) via Claude-in-Chrome. Finds on-brand posts, captures permalinks, drafts in EZ's voice (Koe x EZ), self-checks against brand rules, presents a batch for one-glance approval, then posts by URL and logs it. Use when EZ says \"run my social round\", \"do my LinkedIn/X comments\", \"daily engagement\", or wants to grow @EZdaArchitect / his LinkedIn."
---

# Daily Social Round

Runs EZ's daily social engagement to grow LinkedIn + X (@EZdaArchitect), on-brand and human. The #1 growth lever per `memory/linkedin-growth-playbook.md` is commenting, so this is the engine. **Batch-approval model: do all the work, then EZ approves the whole batch in one glance, then it posts.** Never blind auto-post.

## READ FIRST (every run)
1. `DUX_MACHINA/social/voice-foundation.md` — the voice + the 3 platform profiles + banned patterns. This governs every draft.
2. Optional context: `DUX_MACHINA/funnel.md` (ICP), the leads sheet (to log ICP engagement).

## SCOPE (which platform)
Default = BOTH platforms. If EZ scopes the run (says "LinkedIn only" / "just X", or the `/social-round` command passes `linkedin` or `x`), do ONLY that platform and skip the other's steps entirely.

## DEFAULT VOLUME (per run, tune on request)
- LinkedIn: 5 comments (3 niche/growth + 2 on PM ICP leaders = doubles as warm-touch).
- X: 5 replies, 4 quote-posts, 1 original post.
- Scoped runs: LinkedIn-only = the 5 comments + optionally 1 post; X-only = the 5 replies + 4 quote-posts + 1 post.
Keep it human-paced; do not blast.

## WORKFLOW

### Step 0 — Connect + verify (prevents wrong-account / not-logged-in disasters)
1. `tabs_context_mcp`. If multiple Chrome browsers, STOP and ask EZ which (AskUserQuestion listing each). `select_browser`.
2. Open LinkedIn and X. **Verify the logged-in account is EZ (LinkedIn = Azeez/EZ; X = @EZdaArchitect).** If a login wall or wrong account, STOP and tell EZ. Do not proceed.

### Step 1 — Find on-brand targets
Scan both feeds. Good target = (a) in EZ's lane (operations, business, building, AI/agentic, his PM niche), (b) ~10 to 50 existing comments (visibility sweet spot), (c) recent, (d) EZ genuinely has a point of view.
**SKIP rules (when in doubt, skip):** politics, religion, controversy, drama, tragedy/grief posts, anything mean or dunking, anyone EZ shouldn't be associated with. Engagement bait you can't add real value to.

**WHERE to source X targets (the For You feed is unreliable):**
- EZ's **For You** feed echoes whatever he last engaged with (often Fable-saturated) and swings to gossip/sports/ads. Bad default.
- **Best source = the "Build in Public" community tab** on `/home` (he also has a "Developers/Designers Learning" tab). Switch via JS: `[...document.querySelectorAll('[role="tab"]')].find(t=>/Build in Public/i.test(t.innerText)).click()`. This pulls fresh builder/ops/founder posts.
- **On-demand top-up = X search** with a quality floor: `https://x.com/search?q=(<on-brand terms>) min_faves:40 -filter:replies since:<yesterday>&f=top`. Caveats: avoid the word "operations" (matches military posts); Latest (`f=live`) is mostly coupon/crypto/figure-shipping noise, prefer `f=top`.
- **Quality targets are genuinely sparse in any given hour.** Quality over quota: post fewer strong items rather than padding with weak ones. Log what you dropped and why.

### Step 2 — Capture the PERMALINK first (critical, prevents lost targets)
For every target, grab its permanent URL BEFORE drafting. The batch is link + draft pairs. Posting later navigates straight to the URL, never relies on scrolling the feed back. **Both platforms need the link saved so EZ can revisit posts.**

**X:** the timestamp link is the permalink. Use `read_page` (filter interactive) and read the status hrefs: `link "Jun 9" href="/user/status/123..."` → `https://x.com/user/status/123...`.

**LinkedIn link capture — METHODS THAT FAIL (verified dead 2026-06-15 AND 2026-06-16, do not waste time re-trying):**
- Timestamp click → opens the author PROFILE, not the post.
- `innerHTML`/`data-urn` urn regex OR scraping `a[href*="/feed/update/"]` → returns whatever post is currently rendered, NOT your target (gave the WRONG post 3x).
- `navigator.clipboard.readText()` after "Copy link to post" → HANGS the renderer (clipboard-read permission); guard any clipboard read with `Promise.race([..., timeout])` and expect TIMEOUT.
- The "Link copied… View post" toast → fades faster than a separate tool call can click it.
- "Embed this post" dialog → shows the URL on screen but it lives in a shadow/iframe layer JS can't read, and the field is visually truncated. Not machine-readable.

**LinkedIn link capture — THE METHOD THAT WORKS (VERIFIED 2026-06-16, use this): the author's recent-activity page exposes a real `data-urn` per post.**
The main feed hides post IDs, but a person's activity page does NOT. Steps:
1. Get the author's profile handle: click their name in the feed → lands on `/in/<handle>/` → read `location.href`. (If the post has scrolled out of the feed, find them via people search `https://www.linkedin.com/search/results/people/?keywords=<name + headline words>` and click the matching result; verify by their headline/mutuals. NOTE: reading `a[href*="/in/"]` from search results is BLOCKED by a security filter — just CLICK the result, then read `location.href` on their profile.)
2. Navigate to `https://www.linkedin.com/in/<handle>/recent-activity/all/`.
3. Each post container there carries the urn in `data-urn`/`data-id`. Match the post by its text and read its urn:
   ```
   [...document.querySelectorAll('[data-urn],[data-id]')]
     .filter(e=>/urn:li:activity:\d+/.test(e.getAttribute('data-urn')||e.getAttribute('data-id')||''))
     // find the one whose innerText includes a distinctive phrase from the post, then .match(/urn:li:activity:\d+/)
   ```
4. Build the permalink: `https://www.linkedin.com/feed/update/urn:li:activity:<ID>/`. Navigate there → STABLE page (survives feed churn) → confirm author/text → comment there. This permalink is the link you log.
- **Output-block gotcha:** the JS tool BLOCKS results containing full URLs with tracking query-strings ("Cookie/query string data"). Return ONLY the bare urn (regex `urn:li:activity:\d+`) and build the clean permalink yourself — never return raw hrefs/`location.href` with `?...`.
- **Workflow:** capture all targets' permalinks via their activity pages FIRST, present drafts + the post content for ONE approval, then post each on its stable permalink page. Review is on the post content + draft (shown up front); the link is for the log + EZ to revisit.

**LinkedIn link capture — FALLBACK if activity-page fails: comment inline, read link off your own comment.** Comment in the same pass (never scroll away), then extract the post id from your own posted comment's permalink in the light DOM.

**LinkedIn (HARD — read this, it cost a whole round on 2026-06-15):**
- **The LinkedIn feed VIRTUALIZES and RESHUFFLES.** Posts you scroll past get DELETED from the DOM (recycled), and new posts get injected, so positions shift under you. You cannot reliably scroll back to a post you found earlier — it is often gone. Treat every found target as ephemeral.
- **The `document.body.innerHTML` urn regex is UNRELIABLE for identifying a specific post.** It returns whatever single `urn:li:activity` happens to be rendered, NOT the post you clicked. Proven 2026-06-15: navigating to the "captured" urn loaded a DIFFERENT post than intended. Do NOT trust it to map to your target. (`data-urn` / `.feed-shared-update-v2` selectors also do not exist on current LinkedIn; as of 2026-06-23 the feed carries the urn in `componentkey="urn:li:activity:<ID>"` on empty marker DIVs, and still only the in-view post's urn is present, which is exactly why this regex misfires. Reconfirmed the trap 2026-06-23: grabbed the wrong author's urn from the feed. Use the author's recent-activity page method above instead.)
- **THE RULE EZ INSISTS ON: get the link FIRST, then comment.** Two reliable ways to pin a specific post:
  1. **Comment inline in the SAME pass** (primary): the moment you find a target in the feed, scroll its action bar into view (use the `computer` `scroll` action — JS `scrollIntoView` often does NOT move the LinkedIn viewport), click ITS **Comment** button, and post right there before scrolling away. Do NOT batch-find-then-return.
  2. **Land on the post's own permalink page** (for a stable page that survives churn): open the post on its own `/feed/update/urn:li:activity:<ID>/` page and CONFIRM the author/text in the URL+page match your target before commenting. The URL bar is the source of truth, not the feed DOM.
- **Capturing the permalink to log:** once you are ON the post's own permalink page, the URL is the link. Inline-in-feed comments often can't expose a clean link (LinkedIn hides it) — if so, log the target by author+gist and note "link not captured" rather than guessing.
- Do NOT click the author name/avatar (opens profile). The post's own page is reached via its permalink URL or the post's "..." menu "Copy link to post".
- **Comment submit button:** after typing, a blue **"Comment"** button appears at the bottom-right of the comment box (`button` with text "Comment", distinct from the post's action-bar Comment toggle). The editor is a ProseMirror/tiptap `[contenteditable="true"]`; verify `activeElement` is inside it before typing.

### Step 3 — Draft in the platform voice + SELF-CHECK
Write each draft in the correct voice (LinkedIn = calm professional; X = sharp builder; see voice-foundation). Then run the self-check on EVERY draft:
- No em dashes (—) or en dashes (–). No hashtags. No AI-tells (delve, tapestry, game-changer, etc.).
- No fabricated claims/stats (only Prime Fleet 6hr to 60sec is real).
- One idea, thesis-first, sounds like a human operator.
- Fits the platform limit (X replies <= 280 chars so they show in full; trim if over).
(A hard hook also blocks any post containing banned patterns — but self-check first so it rarely fires.)

### Step 4 — Assemble the batch + log it
Build the batch as a numbered list of {platform, target permalink, action type, draft text}. Write it to `DUX_MACHINA/social/log/round-YYYY-MM-DD.md` (status: drafted) so nothing lives only on screen.

### Step 5 — Present for approval (the one review)
Show EZ the full batch at once: each target (1-line context + link) and its draft. Ask for a single approval, or edits. WAIT. Apply any edits. Only approved items proceed.

### Step 6 — Post by URL, verify each step
For each approved item: navigate to the permalink, open the reply/quote/compose box, type the draft, SCREENSHOT to verify the right text on the right post, then click post. Confirm the "sent" state. Never re-click (avoids double-post).

### Step 7 — Update logs + sheet
1. Mark each item posted/skipped in the per-round log `DUX_MACHINA/social/log/round-YYYY-MM-DD.md`.
2. **ALWAYS append every posted item to the master running record `DUX_MACHINA/social/activity-log.md`** — add/extend today's dated section (newest day first), one table row per item (platform · type · target · permalink), and update the day's total + the running totals. This is EZ's permanent "what did I post and when" record. Capture the LINK for every item (see Step 2) so posts can be revisited.
3. For any PM ICP leader you commented on, note it in the leads sheet (that's Touch 1 warm-touch).

## PACING — avoid X bot-detection / throttling (learned 2026-06-16, the hard way)
**⛔ REAL CONSEQUENCE (2026-06-16): automated bursts got @EZdaArchitect LABELED for "platform manipulation / spam" — reach limited, excluded from trends/replies/recommended/search.** This is the actual penalty, not a hypothetical. It happened after thread retries + back-to-back quote-posts in one session. The account is reach-limited until the label clears.
- **The skeleton-only render IS X's warning shot. Treat it as STOP-FOR-THE-DAY, not "wait 15 min."** If post pages render only "Show replies" skeletons / the composer keeps closing / posts silently fail → you are being throttled → END the X round immediately, persist remaining work, and tell EZ. Do NOT "let it settle and resume" the same day; that escalation is what earned the label.
- **After a label appears:** do NOT click "Request Review" (EZ's decision, his account — surface it, never submit). Recommend: stop ALL X automation for ~a week, behave human-normal, request review only after a quiet stretch. Never argue with the system fast.
- **Safe cadence going forward:** a couple of X actions per day, widely spaced, by hand-like pacing. No thread + multiple quotes in one session. Quality, tiny, slow.

X throttles sessions that behave robotically: many rapid navigations, back-to-back searches/profile-hops, and dozens of JS calls in a few minutes. Symptom: post pages stop rendering (only "Show replies" skeletons, no article/compose), the renderer freezes, and posting silently fails. Once throttled you must STOP (for the day); hammering escalates to an account label.
- **Keep X rounds SMALL and SPACED.** Do a few items, not a marathon. A thread + several quotes + rescans + retries in one burst is too much.
- **Minimize navigation churn:** don't bounce profile → search → feed → permalink repeatedly. Capture what you need, act, move on.
- **Space actions out** with brief waits; act at a human pace, not a tight machine loop.
- **If pages stop rendering or the composer keeps closing, you are likely throttled** — pause the round, persist remaining work to `log/round-YYYY-MM-DD-x.md`, and resume later in smaller pieces. Do NOT keep retrying.
- Prefer fewer, higher-quality items per session over hitting a big number in one go.

## POSTING MECHANICS — X (DOM-driven, survives renderer freezes) — USE THIS
The Chrome renderer freezes often during rounds: `Page.captureScreenshot` times out (~30s) but the DOM stays live. So **drive by JS/DOM, use screenshots only to confirm a box's position.** `javascript_tool` and `read_page` keep working when screenshots are dead.

**Golden rule — verify state BEFORE every irreversible action** (same discipline as the Money Rule). The failure mode is an *orphan post*: a stray/mis-scaled click sends your keystrokes to the document, X reads them as keyboard shortcuts, and the quote card silently drops or text lands nowhere. Prevent it by checking focus + attachment first.

**Coordinate gotcha:** JS `getBoundingClientRect()` is in the page viewport (~1884px wide); screenshots are 1568px. Scale ≈ `1568/1884 ≈ 0.832` (same for y). But the editor's JS *center-x* (~714) is too far right for clicks — the reliable click point for an inline "Post your reply" box is **x≈592**, y varies by post (screenshot to get y). The quote-composer editor ("Add a comment") sits at screenshot **(650, 137)**.

**Reply flow (per target):**
1. `navigate` to the target status permalink (clean page, never rely on the feed).
2. JS: `editor = document.querySelector('div[data-testid="tweetTextarea_0"]')`; `editor.scrollIntoView({block:'center'})`. Screenshot to find the "Post your reply" box, physical `left_click` it (≈ x592).
3. JS-verify focus: `document.activeElement === editor` must be true BEFORE typing.
4. `computer` `type` the draft (this is what the brand_voice_gate hook gates — keep it on the computer tool).
5. JS-verify: editor text correct, no `[—–]`, no `#`, length ≤ 280.
6. Submit by JS click: `document.querySelector('button[data-testid="tweetButtonInline"]').click()` (button moves as the composer grows; a coordinate click often misses — JS click is reliable).
7. Confirm success: `editor.innerText === ''` (the editor clears on submit).

**Quote-post flow (per target):**
1. `navigate` to the target status.
2. JS-click repost: `document.querySelector('button[data-testid="retweet"]').click()`. In a *separate* call (menu needs a beat to mount), JS-click the Quote item: `[...document.querySelectorAll('[role="menuitem"]')].find(m=>/Quote/i.test(m.innerText)).click()` (Quote's href = `/compose/post`).
3. Composer opens. **Three-check gate before posting:** (a) quote card embedded — `dialog.innerText` includes a distinctive phrase from the target; (b) `activeElement === editor` after clicking (650,137); (c) text correct + no dashes/hashtags + ≤280. Note: right after open, `dialog.innerText` is briefly `''` (mount race) — if a check disagrees with the screenshot, re-check after the paint, don't act on the first read.
4. Submit: `document.querySelector('div[role="dialog"] button[data-testid="tweetButton"]').click()`.
5. Confirm: no `div[role="dialog"]` left + URL back to the target status = posted. **TRUST THIS SIGNAL.** Your profile `/EZdaArchitect` Posts tab LAGS by a minute or two, so a quote being absent there right after is NOT proof it failed (learned 2026-06-12 — a quote that posted fine was absent from the profile, I wrongly re-attempted, and hit X's "Whoops! You already said that" duplicate block). The target tweet's repost-button state is also NOT a reliable indicator of whether you quoted it. So: do not re-post a quote just because it hasn't appeared on your profile yet. If you genuinely must re-verify, the duplicate-block on a re-attempt is the tiebreaker (and means the original DID post — discard the dup via a forced "Leave site?" dismissal, never force it through).

**Thread flow (multi-tweet, verified 2026-06-14):**
A thread is a chain of tweet boxes published together with one "Post all".
1. Open `/compose/post`. Click the editor (≈650,137), verify focus, `type` tweet 1 (the brand hook fires per box). Each tweet must independently pass the self-check + ≤280.
2. Once tweet 1 has text, an **"Add post" button** appears — `data-testid="addButton"`, aria-label "Add post", the small circled **"+"** at the bottom-right of the composer, just LEFT of the Post button. **Click it with a REAL mouse click (`computer` left_click) — programmatic `.click()` does NOT fire it** (React synthetic-event quirk).
   - **The "+" DRIFTS as the thread grows (learned 2026-06-14), so do NOT reuse a stale coordinate.** For the first couple of tweets the footer (toolbar + "+" + Post) sits higher and moves *down* incrementally as each box is added (≈y358 at 1 box, ≈y528 at 2). Once the composer hits max height (~3+ tweets) the footer locks to a fixed bottom position (≈913,630 at a 1568-wide screenshot) and the tweet content scrolls internally above it. A coordinate that worked for tweet 2 will miss by tweet 4 — a miss lands a harmless cursor-click inside the editor and adds NO box.
   - **Safeguard: after every "+" click, JS-verify a new `tweetTextarea_<n>` actually exists and is focused.** If it didn't appear, screenshot, re-locate the "+", and click again. Screenshot-locate whenever unsure rather than guessing y.
3. Clicking "+" adds the next editor (`tweetTextarea_1`, then `_2`, …), AUTO-FOCUSES it (placeholder "Add another post"), and flips the submit button label to **"Post all"**. Each added box has its own "✕" to remove that tweet from the chain.
4. Type the next tweet into the now-focused box (verify `activeElement` is `tweetTextarea_<n>` first). Repeat "+" → type for each tweet. Verify all boxes via JS: `document.querySelector('div[data-testid="tweetTextarea_<n>"]').innerText`.
5. Publish the whole chain: click **"Post all"** (`button[data-testid="tweetButton"]`, label "Post all"). One click posts every tweet in order, correctly chained as replies.
6. Discard a thread draft without posting = navigate away with `force:true` (dismisses the "Leave site?" dialog, dumps the draft). Use this to dry-run the mechanic without polluting the feed.
- **Thread drafting rules (EZ voice):** tweet 1 is the hook (contrarian, stated as settled fact, must stop the scroll on its own); every tweet must be standalone-quotable; one idea builds to the next; last tweet resolves + soft CTA. Still: no em/en dashes, no hashtags, no AI-tells, no fabricated claims (only Prime Fleet 6hr→60s is real). Present the full thread as a numbered batch for ONE approval before posting (same batch-approval model).

**Hook note:** JS `.click()` to submit bypasses `brand_voice_gate.ps1` (it only fires on the `computer` tool) — that's fine because the text was already hook-gated at the `type` step (Step 4). Never type via JS; always type via the `computer` tool so the gate sees it.

**Verifying + permalinks:** Grab your reply/quote permalinks from `/EZdaArchitect` (Posts) or `/EZdaArchitect/with_replies` via DOM. **Replies to Community posts (e.g. "Build in Public") do NOT appear in `/with_replies`** — confirm those on the target thread (the reply-count ticks up, e.g. 21→22) instead of assuming failure.

## EDGE CASES (handle these explicitly)
- **Multiple Chrome browsers / wrong account** → select browser; verify handle before posting.
- **Not logged in / session expired** → detect login wall, STOP, tell EZ.
- **Stale/scrolled-away target** → solved by permalink-first; always post by URL.
- **Deleted/protected/404 post** → skip, note in log.
- **Already replied to that post** → check before posting; no duplicates.
- **X 280 limit** → trim to fit fully visible (don't let it truncate with "show more").
- **Em dash / hashtag / AI-tell slipped in** → self-check catches it; the hook hard-blocks as backstop; rewrite and retry.
- **UI changed / reply box didn't open** → screenshot-verify each step; if the page is unexpected, STOP and report rather than clicking blindly.
- **Double-post risk** → confirm "sent" before moving on; never re-click a post button.
- **Rate/spam safety** → keep to default volume, space actions out.
- **LinkedIn external-link penalty** → no links in post bodies; link in a comment if needed.
- **Approval not given** → post nothing. A run with no approval just leaves drafts in the log.

## NOTES
- From Claude Code this runs with full context (voice, funnel, sheet) so no brief needed. The standalone Chrome extension needs `DUX_MACHINA/social/daily-engagement-brief.md` instead.
- **RUN ON-DEMAND, not on a background timer.** Proven 2026-06-11: a local `/loop` (ScheduleWakeup) does NOT fire while the session sits idle/away — the timer only advances when the session is being actively driven, so scheduled rounds silently no-op until EZ pokes the session. A cloud `/schedule` *does* fire unattended but can't drive EZ's logged-in Chrome, so it can't post as him. There is no local setup that both fires unattended AND posts. Therefore: EZ runs `/social-round x` (or "do a social round") when he's at the machine, and it posts right then. Don't promise a hands-off timer.
- **Autonomous vs batch-approval:** default is batch-approval (show drafts, one yes, then post). EZ may pre-authorize autonomous posting for a specific scoped run ("just post 4 non-Fable replies, don't make me review") — honor that for that run, but still self-check + rely on the hook + skip-when-in-doubt. Quote-posts land prominently on his own feed, so prefer a quick batch-approval for those even when replies are autonomous.
