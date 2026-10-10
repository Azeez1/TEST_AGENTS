# Build acceptance for software projects

Use this procedure only when implementation/testing is part of the authorized project. Ordinary administrative tasks need their own observable result, not artificial build paperwork.

Agree on a small milestone's user-visible behavior, acceptance criteria, relevant regression paths, execution thread/owner, target runtime and acceptance owner. Send the selected implementer a bounded handoff only through authorized continuation. Ask for changed behavior, source revision/branch plus material uncommitted changes, artifact/build identity (hash where useful), reproducible launch, controls/test data/assets, and checks actually run versus unrun. Label that handback Implementer reported.

Verify artifact identity in the test environment. A moving URL without a stable build identifier limits exact-version acceptance. Distinguish current available build from last verified build. Run the essential journey on the actual product and affected failure/retry/persistence paths appropriate to scope. Static review, compilation and a still screenshot cannot prove interaction behavior.

Record each material criterion with exact build, environment/device, actual starting state/actions, expected/observed result, timestamp/timezone, evidence link and one result: passed, failed, blocked or not run. Keep raw screenshots/recordings; label annotations. Generated concepts are illustrations, never acceptance evidence. Preserve build-specific historical results and unavailable device/coverage gaps.

Send reproducible failures to the same implementation owner with impact, minimal steps, build/environment, expected versus actual result and evidence. Label suspected causes as hypotheses. After a fix, identify the new build, repeat the failed case and affected regressions, and keep failed/passing runs separate. Code fixed is not verified fixed.

Accept only evidenced criteria on the intended build and any required owner/user acceptance. Record an explicit criterion waiver with approver and consequences; a mere deferral does not satisfy the criterion. Map release/project completion to current evidence and outstanding required decisions. Do not deploy, merge, publish or widen sharing as a consequence of passing QA.
