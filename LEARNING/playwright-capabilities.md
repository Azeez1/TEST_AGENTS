# Playwright Capabilities Map for a New Automation Tester

A focused tour of the leverage points that separate a competent Playwright user from someone who's just using it like Selenium with a nicer API. Audience: new automation tester, knows what a unit test is, has never seriously used Playwright. Cross-checked against the official docs at playwright.dev as of Playwright **1.60** (current at time of writing, Nov 2026 train).

---

## 1. Core Engine Capabilities Most People Miss

### Auto-waiting / actionability — *every interaction*
- **What:** Before `click`, `fill`, `check`, etc., Playwright waits for the element to be visible, stable across animation frames, enabled, and hit-testable.
- **Why it matters:** You almost never write `WebDriverWait(...).until(...)` again. A whole category of Selenium flake disappears. Resist the urge to add `waitForTimeout` — if you find yourself reaching for it, your locator or assertion is wrong.
- **Doc:** https://playwright.dev/docs/actionability

### Web-first assertions with auto-retry — `expect(locator).toBeVisible()`
- **What:** `expect()` matchers re-query the DOM and retry until the condition passes or the timeout (default 5s) elapses.
- **Why:** No more `await sleep(1000); expect(await el.isVisible()).toBe(true)`. The retry loop lives inside the matcher.
- **Snippet:**
  ```ts
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByTestId('status')).toHaveText('Submitted');
  await expect(page.getByTestId('result')).toHaveText('Done', { timeout: 15000 });
  ```
- **Gotcha:** Never `await el.isVisible()` inside `expect(...)` — it's a one-shot check with no retry [source: https://playwright.dev/docs/best-practices].
- **Escape hatch:** `expect.poll(fn).toBe(x)` and `expect(fn).toPass()` for non-DOM conditions.
- **Doc:** https://playwright.dev/docs/test-assertions

### Locators — `getByRole`, `getByLabel`, `getByTestId`, chaining, `filter()`, `nth()`
- **What:** Semantic locators backed by the accessibility tree; chain and filter instead of writing deep CSS.
- **Why:** Tests survive markup refactors. `getByRole('button', { name: 'Save' })` doesn't care if the dev wrapped it in three more divs.
- **Snippet:**
  ```ts
  const row = page.getByRole('listitem').filter({ hasText: 'Product 2' });
  await row.getByRole('button', { name: 'Add to cart' }).click();
  ```
- **Doc:** https://playwright.dev/docs/locators

### BrowserContext vs Page — multiple users in one browser process
- **What:** A `BrowserContext` is an isolated session (its own cookies/localStorage/IndexedDB). A `Page` is a tab inside a context.
- **Why:** Two contexts = two logged-in users in the same browser, fast and cheap. No multi-browser orchestration.
- **Snippet:**
  ```ts
  const alice = await browser.newContext({ storageState: 'auth/alice.json' });
  const bob   = await browser.newContext({ storageState: 'auth/bob.json' });
  const a = await alice.newPage(); const b = await bob.newPage();
  ```
- **Doc:** https://playwright.dev/docs/browser-contexts

### Network interception — `page.route()` and `routeFromHAR()`
- **What:** Block, rewrite, fulfill, or partially modify any HTTP/WebSocket request. Replay recorded HAR files.
- **Why:** Deterministic tests without standing up a backend. Test error states (503, malformed JSON) trivially.
- **Snippet — patch a real response:**
  ```ts
  await page.route('**/api/fruits', async route => {
    const resp = await route.fetch();
    const json = await resp.json();
    json.push({ name: 'Loquat', id: 100 });
    await route.fulfill({ response: resp, json });
  });
  ```
- **Bonus:** `page.routeWebSocket()` mocks WebSocket streams. `tracing.startHar()` (1.60) makes HAR a first-class trace artifact.
- **Docs:** https://playwright.dev/docs/network · https://playwright.dev/docs/mock

---

## 2. Test Runner Power Features

### Fixtures (built-in + custom, scoped)
- **What:** Dependency injection for tests. `page`, `context`, `request`, `browser` are built-in fixtures. You can extend with your own (`test.extend<{...}>`), scope them `test` or `worker`, mark them `auto`, and even let them depend on other fixtures.
- **Why:** Replaces ad-hoc `beforeAll`/`beforeEach` scaffolding. Worker-scoped fixtures share expensive setup (DB seed, login) across tests in the same worker.
- **Snippet:**
  ```ts
  export const test = base.extend<{ adminPage: Page }>({
    adminPage: async ({ browser }, use) => {
      const ctx = await browser.newContext({ storageState: 'auth/admin.json' });
      const page = await ctx.newPage();
      await use(page);
      await ctx.close();
    },
  });
  ```
- **Doc:** https://playwright.dev/docs/test-fixtures

### Projects (matrix testing)
- **What:** Multiple named configurations in `playwright.config.ts` — Chromium, Firefox, WebKit, iPhone 14, "staging", etc.
- **Why:** One codebase, declarative matrix. `--project=firefox` runs just one slice. Projects also chain via `dependencies`, which powers the auth setup pattern below.
- **Doc:** https://playwright.dev/docs/test-projects

### Sharding & parallelization
- **What:** Files run in parallel across workers by default; `fullyParallel: true` parallelizes within a file. `--shard=1/4` splits the suite across CI machines.
- **Why:** Linear scaling on CI. Pair with blob reports + `merge-reports` to get one unified HTML report.
- **Snippet:**
  ```bash
  npx playwright test --shard=2/4 --workers=6
  npx playwright merge-reports --reporter html ./all-blob-reports
  ```
- **Docs:** https://playwright.dev/docs/test-parallel · https://playwright.dev/docs/test-sharding

### Tagging & grep
- **What:** Tag tests in the title (`'@smoke checkout works'`) or via metadata; filter at the CLI with `--grep=@smoke` / `--grep-invert=@flaky`.
- **Why:** Smoke vs nightly vs regression without separate file trees. Regex means you can express OR/AND.
- **Doc:** https://playwright.dev/docs/test-annotations

### Global setup/teardown — prefer the *setup project* pattern
- **What:** Two flavors: the old `globalSetup` function, or a dedicated project (`testMatch: /global\.setup\.ts/`) other projects `dependencies: ['setup']` on.
- **Why setup project wins:** It runs in the standard test pipeline, so you get traces, screenshots, and HTML report entries for the setup itself. Teardown is just another project with `teardown: 'cleanup'`.
- **Doc:** https://playwright.dev/docs/test-global-setup-teardown

### `test.step()` — readable traces
- **What:** Wrap a logical chunk in `await test.step('Add to cart', async () => {...})`. Each step appears as a collapsible node in the trace and HTML report.
- **Why:** Big user journeys stay in one test (preserving isolation) but failures pinpoint the step. Replaces the urge to `test.describe.serial`.
- **Doc:** https://playwright.dev/docs/api/class-test

---

## 3. Debugging & Diagnostics

### Trace Viewer — the killer feature
- **What:** A trace is a `.zip` with the full action timeline, DOM snapshots before/after each step, network waterfall with bodies, console logs, source, and screenshots.
- **Why:** When CI fails at 3 AM, the trace is a full time-travel debugger you can open locally with `npx playwright show-trace trace.zip` (1.60 accepts the `.zip` directly, no unzip).
- **Setup:** `use: { trace: 'on-first-retry' }` is the recommended CI default. 1.59 adds `'retain-on-failure-and-retries'` for comparing the passing vs failing run of a flaky test.
- **Doc:** https://playwright.dev/docs/trace-viewer

### UI Mode — `npx playwright test --ui`
- **What:** Interactive runner with sidebar, watch mode, live trace, DOM/network/console panels, and built-in locator picker.
- **Why:** The fastest feedback loop while authoring tests. Click an element in the snapshot, get a resilient locator pasted into your code.
- **Remote/Codespaces:** `--ui-host=0.0.0.0 --ui-port=8080`.
- **Doc:** https://playwright.dev/docs/test-ui-mode

### Codegen — `npx playwright codegen https://your-app.com`
- **What:** Record interactions, get generated code using `getByRole`/`getByText`/`getByTestId`. As of 1.55 it can auto-insert `toBeVisible()` assertions.
- **Why:** Best teaching tool for learning Playwright-idiomatic locators. Also a shortcut for first-draft tests.
- **Doc:** https://playwright.dev/docs/codegen

### Inspector + `PWDEBUG=1` + `page.pause()`
- **What:** Three ways into the same headed step-through debugger: `npx playwright test --debug`, `PWDEBUG=1 node script.js`, or drop `await page.pause()` mid-test to break exactly where you want.
- **Why:** `page.pause()` is the magic line — let the test run to a tricky moment, then explore the live page, try locators in the inspector, resume.
- **Doc:** https://playwright.dev/docs/debug

---

## 4. Specialized Testing Modes

### API testing — the `request` fixture
- **What:** `APIRequestContext` for raw HTTP. Honors `baseURL` and `extraHTTPHeaders` from config. Reuses `storageState` so an authenticated UI session and an authenticated API client share cookies.
- **Why:** Seed data via API, then verify in UI. Or run pure-HTTP test suites with the same runner.
- **Snippet:**
  ```ts
  test.use({ baseURL: 'https://api.github.com', extraHTTPHeaders: { Authorization: `token ${process.env.TOK}` } });
  test('create then delete repo', async ({ request }) => {
    expect((await request.post('/user/repos', { data: { name: 'tmp' }})).ok()).toBeTruthy();
    expect((await request.delete('/repos/me/tmp')).ok()).toBeTruthy();
  });
  ```
- **Doc:** https://playwright.dev/docs/api-testing

### Component testing (experimental)
- **What:** Mount a React/Vue component in a real browser, drive it with Playwright locators.
- **Why:** Real layout and CSS, no full app, no backend. Bridge between Jest-style unit and full E2E.
- **Caveat:** Still flagged experimental; `@playwright/experimental-ct-svelte` was removed in 1.59. Validate the import name in current release notes before committing to it.
- **Doc:** https://playwright.dev/docs/test-components

### Visual regression — `toHaveScreenshot()`
- **What:** `await expect(page).toHaveScreenshot('home.png')` captures on first run, diffs on subsequent runs. Baselines are per project/browser/platform.
- **Why:** Catches layout drift no DOM assertion can express. Use `stylePath` to hide dynamic elements (clocks, ads). Update with `--update-snapshots`.
- **Doc:** https://playwright.dev/docs/test-snapshots

### Accessibility — `@axe-core/playwright`
- **What:** Run axe-core inside a Playwright test, scoped to specific roots or WCAG tags.
- **Why:** Catches a large slice of a11y bugs automatically. For legacy apps with known violations, snapshot a *fingerprint* (count + rule IDs) and assert it doesn't get worse instead of asserting zero.
- **Snippet:**
  ```ts
  const results = await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa']).analyze();
  expect(results.violations).toEqual([]);
  ```
- **Doc:** https://playwright.dev/docs/accessibility-testing

### Mobile emulation, geolocation, permissions, locale, timezone
- **What:** Set `...devices['iPhone 14']`, `geolocation`, `permissions: ['geolocation']`, `locale`, `timezoneId`, `colorScheme: 'dark'`, `offline: true`, `javaScriptEnabled: false` per project or per context.
- **Why:** Test "near me" features, dark mode, internationalization without real devices.
- **Doc:** https://playwright.dev/docs/emulation

---

## 5. Authentication Patterns (2025-2026 modern approach)

### `storageState` + setup project — **the recommended pattern**
- **What:** A dedicated `tests/auth.setup.ts` file in a `setup` project logs in once and writes `playwright/.auth/user.json`. Every other project declares `dependencies: ['setup']` and `use: { storageState: 'playwright/.auth/user.json' }`.
- **Why:** Login UI runs ~once per CI run instead of once per test. Setup gets full reporting/tracing because it's a normal test. Bypasses MFA/SSO pain.
- **Snippet (config):**
  ```ts
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    { name: 'chromium', use: { storageState: 'playwright/.auth/user.json' }, dependencies: ['setup'] },
  ]
  ```
- **Multiple users:** Run multiple setup tests writing to different JSON files (`admin.json`, `user.json`, `viewer.json`), each project picks its file. For stateful tests, use the "auth per worker" pattern: one unique account per worker process.
- **1.59 bonus:** `browserContext.setStorageState()` swaps storage in-place without creating a new context.
- **Doc:** https://playwright.dev/docs/auth

---

## 6. CI/CD and Reporting

- **Sharding pattern:** `--shard=$INDEX/$TOTAL` on N machines, `reporter: process.env.CI ? 'blob' : 'html'`, then a final job runs `npx playwright merge-reports --reporter html ./all-blob-reports`. Preserves traces and tags.
- **HTML reporter highlights:** 1.57 added a "Speedboard" tab (tests sorted by slowness). 1.58 added a Timeline for merged reports. 1.60 accepts `.zip` HTML reports without unzipping.
- **GitHub Actions:** `npm init playwright` scaffolds a workflow. Install only the browsers you need: `npx playwright install chromium --with-deps` saves a lot of CI minutes.
- **Retries:** Set `retries: process.env.CI ? 2 : 0` — local runs fail loud, CI gets one retry to absorb true infra flake.
- **Docs:** https://playwright.dev/docs/test-sharding · https://playwright.dev/docs/ci-intro

---

## 7. Advanced / Niche Features Worth Knowing Exist

| Feature | One-liner | Doc |
|---|---|---|
| `page.addInitScript()` | Inject JS before any page script runs (mock `Math.random`, patch globals, seed feature flags) | https://playwright.dev/docs/evaluating |
| `page.clock` | Freeze/fast-forward time. `setFixedTime`, `install`, `pauseAt`, `runFor`. Test 24-hour expiry in 5 ms. | https://playwright.dev/docs/clock |
| HAR record/replay | `recordHar` option on context, `page.routeFromHAR()` to serve recorded traffic. 1.60 promoted it to `tracing.startHar()`. | https://playwright.dev/docs/mock |
| Downloads | `const dl = await page.waitForEvent('download'); await dl.saveAs(...)` | https://playwright.dev/docs/downloads |
| Uploads | `locator.setInputFiles()` for inputs; **`locator.drop()` (new in 1.60)** for drag-and-drop upload zones | https://playwright.dev/docs/api/class-locator |
| Popups | `const popup = await page.waitForEvent('popup')` then drive it like any page | https://playwright.dev/docs/pages |
| File chooser | `page.on('filechooser', fc => fc.setFiles([...]))` for hidden inputs | https://playwright.dev/docs/api/class-filechooser |
| Dialogs | `page.on('dialog', d => d.accept())` — auto-dismissed if you don't register | https://playwright.dev/docs/dialogs |
| Soft assertions | `expect.soft(...).toBeVisible()` collects failures instead of bailing | https://playwright.dev/docs/test-assertions#soft-assertions |
| `test.fail / test.fixme / test.slow` | Mark known bugs (CI fails if accidentally fixed), skip broken, triple timeout | https://playwright.dev/docs/test-annotations |
| ARIA snapshots | `expect(locator).toMatchAriaSnapshot()` — YAML-ish accessibility-tree assertion | https://playwright.dev/docs/aria-snapshots |
| `expect.poll` / `expect.toPass` | Structured retry for arbitrary async conditions | https://playwright.dev/docs/test-assertions |

---

## 8. What's New in Playwright (2025-2026)

Verified against https://playwright.dev/docs/release-notes (current as of 1.60):

- **1.60** — `tracing.startHar()` / `stopHar()` as first-class API. **`locator.drop()`** for synthetic drag-and-drop file uploads cross-browser. `expect(page).toMatchAriaSnapshot()` now works on a page directly. `test.abort()` to bail from inside a fixture/hook. `browser.on('context')` event. `npx playwright show-report` reads `.zip` directly.
- **1.59 (Apr 2026)** — **Screencast API** (`page.screencast`): video recording with action annotations, chapter overlays, real-time frame streaming for AI vision pipelines, "agentic video receipts". `browser.bind()` for sharing a browser session with `playwright-cli` / `@playwright/mcp`. **`--debug=cli`** for coding-agent attached debugging. **`await using`** support for auto-cleanup of routes, init scripts, contexts. `locator.normalize()` rewrites locators to best practices. `page.pickLocator()` programmatic locator-picking mode. Trace mode `'retain-on-failure-and-retries'`.
- **1.58 (Jan 2026)** — HTML report Timeline for merged reports. UI Mode/Trace Viewer search (Cmd/Ctrl+F), system theme, auto-formatted JSON. Removed `_react` / `_vue` selectors and `:light` engine.
- **1.57 (Dec 2025)** — **Chrome for Testing replaces Chromium** in headed mode (functionally identical, new icon). New `webServer.wait: { stdout: /regex/ }` waits for a log pattern before tests start, with named-capture-group → env-var passthrough. Removed deprecated `page.accessibility` — use `@axe-core/playwright`. Service Worker requests now routable through `BrowserContext`.
- **1.56 (Nov 2025)** — **Playwright Test Agents**: `npx playwright init-agents --loop=claude|vscode|opencode` generates planner/generator/healer agent definitions for LLM-driven test authoring and self-healing.
- **1.55 (Sep 2025)** — Codegen auto-inserts `toBeVisible()` assertions. Dropped Chromium extension manifest v2.
- **1.54 (Aug 2025)** — Partitioned cookies (CHIPS) support. `--user-data-dir` on multiple CLI commands to persist browser state across sessions.

Sources: https://playwright.dev/docs/release-notes · https://testdino.com/blog/playwright-2026-new-features/ · https://bug0.com/blog/whats-new-playwright-1-59

---

## 9. Anti-patterns Experienced Users Say Newcomers Make

Cross-referenced from official best practices and community lists (https://elaichenkov.github.io/posts/17-playwright-testing-mistakes-you-should-avoid/, https://medium.com/@gunashekarr11/anti-patterns-in-playwright-people-dont-realize-they-re-doing-00f84cd7dff0):

1. **`waitForTimeout(2000)` as a flake band-aid.** If you need it, a locator/assertion is wrong. Use `expect(...).toBeVisible()` or `expect.poll`.
2. **Wrapping `isVisible()`/`textContent()` in `expect(...)`.** These are one-shot; no retry. Always `await expect(locator).toBeVisible()`.
3. **`force: true` to bypass actionability.** Hides real bugs (overlays, disabled state). Almost never the answer.
4. **CSS/XPath locators by class name.** Refactor breaks every test. Lead with `getByRole` / `getByLabel` / `getByTestId`.
5. **Overusing `nth(0)` and `.first()`.** Positional locators are coupling. Use `filter({ hasText })` or refine the role.
6. **`test.describe.serial` to share state across tests.** Kills parallelism, makes failures cascade. Use one test with `test.step()`, or worker-scoped fixtures.
7. **`networkidle` as "page is ready".** Modern apps with analytics/websockets never go idle. Wait on a visible element instead.
8. **Logging in via UI in every test.** Use the setup-project + `storageState` pattern.
9. **Missing `await`.** The entire API is async. Add `@typescript-eslint/no-floating-promises` to ESLint and `tsc --noEmit` to CI.
10. **Testing third-party sites you don't control.** Mock them with `route()` or HAR.

---

## 10. When NOT to Use Playwright

- **Native mobile or desktop apps** — use Appium, XCUITest, Espresso, WinAppDriver instead. Playwright is browser-only.
- **High-volume load testing** — Playwright launches real browsers; that's 1000x heavier than HTTP load. Use k6, Locust, or JMeter for capacity testing; reserve Playwright for end-user experience checks at low concurrency.
- **True unit tests** — pure function logic belongs in Vitest/Jest. Playwright component testing fills the integration layer, not the unit layer.
- **Pixel-perfect cross-device design QA at scale** — visual platforms like Percy/Chromatic/Applitools manage hundreds of baseline combinations more cleanly. Playwright's screenshot diffing is excellent for a focused set of breakpoints, not for design-review workflows.
- **Automating external/third-party sites you don't control** — fragile and noisy. Mock them.

---

## Top 10 Hidden Gems — Day-One Cheat Sheet

If you only internalize ten things from this document, make it these:

1. **Trace Viewer with `trace: 'on-first-retry'`.** The single biggest debugging upgrade over Selenium. CI failures become a time-travel debugger you open locally.
2. **`getByRole` + `filter()` + chaining.** Locators that survive refactors. Stop reaching for CSS.
3. **Web-first assertions (`expect(locator).toBeVisible()`) — never `isVisible()` inside `expect`.** Auto-retry is the whole point.
4. **`storageState` + setup project pattern.** Log in once per CI run, not once per test. The biggest CI speedup you can make.
5. **`page.route()` for API mocking.** Decouples your UI tests from backend flake; lets you test 503s, slow responses, malformed JSON in seconds.
6. **`test.step()`.** Keep journeys in one test; get a clean trace breakdown for free. Replaces the urge to do `describe.serial`.
7. **UI Mode (`--ui`) for authoring, `page.pause()` for debugging.** UI Mode = best authoring experience; `page.pause()` = best mid-test inspector.
8. **Custom fixtures.** Promote any helper you call in three tests to a fixture. Worker-scoped for expensive setup; test-scoped for per-test state.
9. **`page.clock`.** Freeze or fast-forward time for countdowns, session expiry, scheduled UI — test in milliseconds what takes hours in real time.
10. **`expect.soft`, `test.fixme`, `test.slow`.** Soft assertions for multi-field forms; `fixme` for known bugs (with the auto-fail-on-fix safety net); `slow` to triple timeout on heavy flows without bumping the global.

---

## 11. The 20 Feynman Lessons (Plain-English Capability Tour)

A narrative, no-jargon walkthrough of the 20 highest-leverage capabilities — written for someone who knows what browser automation is but hasn't lived in Playwright. Each lesson has the same shape: a plain-English analogy, the problem the feature kills, a short code peek, and an "**AI footnote**" — what AI-generated code typically gets wrong here, so you can review PRs intelligently in an AI-augmented workflow.

---

### Lesson 1 — Auto-waiting (the thing that makes Playwright different)

Selenium is like a customer who reaches for their coffee the *instant* they order it — air, drop, fail. Playwright is the patient customer: when you call `click()`, it silently checks "is the element present, visible, enabled, not covered, stable?" up to 30 seconds before clicking. Five invisible safety checks for free.

```js
await page.getByRole('button', { name: 'Order' }).click();
```

**AI footnote:** AI loves to insert `await page.waitForTimeout(2000)` because old Selenium tutorials taught that. Delete those — Playwright already waits for the *right* thing, not a wall-clock guess.

---

### Lesson 2 — Web-first assertions (the flake-killer)

Two ways to check "is the success message visible?":

```js
expect(await locator.isVisible()).toBe(true);   // ❌ checks ONCE, no retry
await expect(locator).toBeVisible();             // ✅ keeps re-checking up to 5s
```

The `await` goes on `expect`, not inside it. Web-first matchers (`toBeVisible`, `toHaveText`, `toHaveCount`, `toBeEnabled`, `toContainText`) auto-retry. This single distinction is the #1 source of flaky tests in the wild.

**AI footnote:** AI trained on stale Stack Overflow will absolutely write `expect(await x.isVisible()).toBe(true)`. Treat it as a code smell every single time.

---

### Lesson 3 — Trace Viewer (the time machine)

Instead of "element not found" at 3am, you get a downloadable `trace.zip` with: timeline of every action, screenshot at every step, full DOM snapshot you can hover/inspect at that exact moment, all network calls + responses, console logs, source line. Open with `npx playwright show-trace trace.zip`.

```js
// playwright.config.ts
use: { trace: 'on-first-retry' }
```

**AI footnote:** AI rarely configures traces. Day-one move on any new project: open `playwright.config.ts`, ensure `trace` is `'on-first-retry'` or `'retain-on-failure'`.

---

### Lesson 4 — Locators (and the accessibility secret)

Worst → best: `page.locator('.btn-v2')` → `page.locator('//div[2]/button')` → `page.getByRole('button', { name: 'Sign In' })`. Role-based locators read from the browser's accessibility tree — the same data a screen reader uses. If they work, your app is probably accessible. They also chain naturally:

```js
page.getByRole('row', { name: 'Joe April' }).getByRole('button', { name: 'Delete' }).click();
```

**AI footnote:** AI defaults to CSS selectors. Push back: "rewrite as `getByRole` / `getByLabel`." Failing locators are often hidden 508/WCAG violations (`4.1.2 Name, Role, Value`).

---

### Lesson 5 — Fixtures (the "don't repeat yourself" engine)

A fixture is named setup handed to your test on a silver platter. Declare it in the function signature; Playwright runs setup + teardown automatically.

```js
test('checkout works', async ({ loggedInPage }) => {
  await loggedInPage.getByRole('button', { name: 'Buy' }).click();
});
```

Built-in: `page`, `browser`, `context`, `request`. Custom ones go in `fixtures.ts`.

**AI footnote:** AI copy-pastes login code into every test. Prompt: "extract this into a custom fixture."

---

### Lesson 6 — Projects (5 browsers, no copy-paste)

Define browser/device flavors in config; every test runs once per project.

```js
projects: [
  { name: 'chromium', use: devices['Desktop Chrome'] },
  { name: 'firefox',  use: devices['Desktop Firefox'] },
  { name: 'webkit',   use: devices['Desktop Safari'] },
  { name: 'mobile',   use: devices['iPhone 13'] },
]
```

Also used for "setup project" (login-once) and smoke-vs-regression splits.

**AI footnote:** AI defaults to chromium-only. Verify the `projects` array on day one — if only chromium, you're not actually cross-browser testing.

---

### Lesson 7 — Network interception (lie to your own app)

Intercept any request and respond with whatever you want — fake errors, delays, partial failures.

```js
await page.route('**/api/checkout', route =>
  route.fulfill({ status: 500, body: 'Server exploded' })
);
```

Test edge cases impossible to reproduce against a real backend (timeouts, 503s, malformed JSON).

**AI footnote:** When AI says "this test needs a real backend running," push back: "can we mock with `page.route()` instead?" 80% of the time, yes.

---

### Lesson 8 — Browser contexts (parallel users in one test)

A context = an incognito window. One browser can run many, each pretending to be a different user.

```js
const adminContext = await browser.newContext({ storageState: 'admin.json' });
const userContext  = await browser.newContext({ storageState: 'user.json' });
```

For chat apps, real-time editors, permission flows. Save context state to JSON and reuse across tests.

**AI footnote:** AI usually opens two pages in the same session and wonders why they share cookies. For multi-user tests, explicitly prompt: "use separate browser contexts."

---

### Lesson 9 — Sharding (split the suite across CI machines)

`npx playwright test --shard=N/M` splits the suite into M chunks; run each on a separate runner. 500 tests in 40 min → 4 min with 10 shards. Merge partial reports via the **blob reporter** for one unified HTML dashboard.

**AI footnote:** Sharding lives in CI config (GitHub Actions, GitLab). AI rarely sets this up — read Playwright's CI docs directly.

---

### Lesson 10 — Codegen + UI Mode (record-and-play + the interactive debugger)

- **Codegen** (`npx playwright codegen example.com`) — click around, Playwright writes the test.
- **UI Mode** (`npx playwright test --ui`) — interactive panel, live Trace Viewer, scrub backward through any test, edit locators and re-test instantly.

UI Mode is *the* place to verify AI-generated tests — scrub the trace, spot the bad locator, ask AI to fix it.

**AI footnote:** AI doesn't know about UI Mode. It's your human-in-the-loop superpower.

---

### Lesson 11 — Auth patterns (log in once, reuse forever)

Modern (2025-2026) pattern: a `setup` project logs in once, saves cookies+localStorage to a JSON file. Every other test starts already-logged-in via `storageState`.

```js
projects: [
  { name: 'setup', testMatch: /.*\.setup\.ts/ },
  { name: 'chromium', dependencies: ['setup'],
    use: { storageState: 'auth/user.json' } },
]
```

Replaces the legacy `globalSetup` function (which doesn't show up in traces).

**AI footnote:** AI generates `globalSetup` because that's what older tutorials show. Replace with a setup project.

---

### Lesson 12 — Visual regression (catch what your eyes catch)

```js
await expect(page).toHaveScreenshot('checkout.png');
```

First run saves baseline; future runs pixel-diff. Tolerance is configurable. Per-browser/OS baselines (fonts render differently on Mac vs Linux).

**AI footnote:** AI can't run a test to take the baseline. You set it up; AI maintains it. Don't forget to commit the `*-snapshots/` directory.

---

### Lesson 13 — API testing (Playwright without a browser)

The `request` fixture is a built-in HTTP client. Same runner, same reporting, no browser launched. 50–100x faster than browser tests.

```js
test('order API returns 201', async ({ request }) => {
  const res = await request.post('/api/orders', { data: { item: 'x' } });
  expect(res.status()).toBe(201);
});
```

Mix API + browser tests in the same suite. Use API calls to set up state for browser tests (faster than clicking through signup).

**AI footnote:** AI launches a full browser for everything. If you see `page.goto('/api/...')`, that's a code smell — use the `request` fixture.

---

### Lesson 14 — Mobile emulation + permissions/geolocation

Fake an entire user environment in one config block.

```js
use: {
  ...devices['iPhone 13'],
  geolocation: { latitude: 29.76, longitude: -95.37 },   // Houston
  permissions: ['geolocation', 'camera'],
  locale: 'es-MX',
  timezoneId: 'America/Mexico_City',
  colorScheme: 'dark',
}
```

For i18n, location features, permission flows, dark mode.

**AI footnote:** AI defaults to desktop chrome / US English / light mode. Explicitly request the personas you care about.

---

### Lesson 15 — `page.clock` (control time itself)

Test "show banner after 30 min idle" or "session expires after 24h" in milliseconds.

```js
await page.clock.install({ time: new Date('2026-01-01 09:00:00') });
await page.goto('/dashboard');
await page.clock.fastForward('00:30');
await expect(page.getByText('Still there?')).toBeVisible();
```

`setTimeout`, `setInterval`, `Date.now()`, animations — all controlled.

**AI footnote:** AI training is thin on `page.clock` (added 2024). It often suggests `waitForTimeout(30*60*1000)` — a 30-minute test. Counter with `page.clock.fastForward`.

---

### Lesson 16 — Soft assertions + `test.step` (fail smarter)

`expect.soft` lets the test continue past failures and report all of them at once.

```js
await expect.soft(page.getByTestId('total')).toHaveText('$100');
await expect.soft(page.getByTestId('tax')).toHaveText('$8');
await expect.soft(page.getByTestId('shipping')).toHaveText('$5');
```

`test.step('User logs in', async () => { ... })` groups actions under named labels in the trace.

**AI footnote:** AI rarely reaches for either. For long verification tests, prompt: "convert verifications to `expect.soft`, wrap phases in `test.step`."

---

### Lesson 17 — `init-agents` (Playwright's own AI authoring layer, Nov 2026)

Playwright 1.56 shipped `npx playwright init-agents --loop=claude|copilot|cursor` — scaffolds three official agents into your project:

- **Planner** — English → structured test plan
- **Generator** — plan → Playwright code
- **Healer** — analyzes failures, proposes fixes

Sets up rules files so your AI coding tool defaults to Playwright best practices (auto-waiting, `getByRole`, fixtures, web-first assertions). Probably the highest-leverage first-week PR you can make on a team that hasn't run it yet.

**AI footnote:** the whole feature *is* the AI footnote. Bring it up on day one.

---

### Lesson 18 — HAR recording (capture and replay real network traffic)

A HAR file = every request a page made, with responses. Record one:

```js
const context = await browser.newContext({ recordHar: { path: 'session.har' } });
```

Two uses: (a) debug production bugs by replaying a real user's session locally, (b) replay HAR as a mock backend in CI for realistic responses without backend dependency.

```js
await context.routeFromHAR('session.har');
```

Playwright 1.60 added `tracing.startHar()` for mid-test HAR slices.

**AI footnote:** When CI is flaky because of a flaky backend, the answer is often "record a HAR, replay it" — not "retry 3 times."

---

### Lesson 19 — Component testing (React/Vue/Svelte in isolation)

Mount a single component in a real browser (not jsdom):

```js
test('DatePicker rejects past dates', async ({ mount }) => {
  const cmp = await mount(<DatePicker minDate={new Date()} />);
  await cmp.getByLabel('Date').fill('2020-01-01');
  await expect(cmp.getByText('Date must be in the future')).toBeVisible();
});
```

Still officially experimental in 2026. Use for components where CSS/rendering matters; otherwise Vitest is faster and more mature.

**AI footnote:** AI sometimes suggests Playwright component testing where Vitest would fit better. Rule: visual concerns → Playwright; pure logic → Vitest.

---

### Lesson 20 — When NOT to use Playwright (the senior move)

- **Pure unit tests** → Vitest/Jest
- **Load testing** → k6, Locust, JMeter
- **Security pen-testing** → Burp, ZAP
- **Native mobile apps** → Appium, Detox
- **Native desktop apps** → Sikuli, Robot Framework (Electron is OK)
- **Full WCAG/508 audits** → Playwright catches structural a11y, but you also need `@axe-core/playwright` + human review
- **Design quality review** → visual regression catches *changes*, not *quality*

**AI footnote:** AI will enthusiastically solve everything in Playwright because you asked about Playwright. The senior move is correctly naming the problem — "this is a load test, not E2E."

---

### Day-One Field Guide (Distilled)

The first three things to check on any new Playwright project:

1. **`playwright.config.ts` → `trace: 'on-first-retry'`** — if missing, that's PR #1.
2. **`projects:` array has more than chromium** — if not, you're not cross-browser. PR #2.
3. **Auth uses setup-project + `storageState`** (not `globalSetup`) — if legacy, modernize. PR #3.

Plus: ask if anyone's run `npx playwright init-agents` yet. If no, that's PR #4 and signals you're current with the 2026 tooling.

---

*Verified against playwright.dev as of Playwright 1.60. Release-notes claims for 1.54-1.60 cross-checked at https://playwright.dev/docs/release-notes.*
