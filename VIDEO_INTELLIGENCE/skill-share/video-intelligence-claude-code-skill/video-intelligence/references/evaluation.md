# Evaluation Plan

Evaluate transferable perception, not stylistic resemblance.

## Fixture set

Use generated or rights-safe media covering:

1. talking-head dialogue;
2. silent screen recording with text;
3. fast cuts and a sub-second event;
4. lecture slides plus narration;
5. multiple speakers;
6. software bug reproduction;
7. two-video comparison.

## Measures

- JSON schema validity: 100%.
- Visual-only question accuracy.
- Audio-only question accuracy.
- Timestamp error: target within two seconds for normal events.
- On-screen text accuracy.
- Unsupported-claim count: zero.
- Correct transcript provenance.
- Appropriate high-detail escalation for fleeting evidence.
- Budget enforcement and recorded usage.
- Remote-file cleanup.
- Cache reuse without a second provider call.
- No secret values in logs or outputs.

## Test order

1. Run offline unit tests.
2. Generate the deterministic fixture.
3. Run `--dry-run` and inspect routing/cost.
4. Run one short live test on the generated fixture.
5. Inspect JSON and Markdown independently.
6. Re-run to verify cache behavior.
7. Test a real user-selected video only after the fixture passes.

Do not forward-test with subagents unless the user authorizes parallel agents.
