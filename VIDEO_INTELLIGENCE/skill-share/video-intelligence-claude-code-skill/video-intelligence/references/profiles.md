# Analysis Profiles

Profiles add domain-specific questions without changing the canonical schema.
Use `custom` with `--rubric-file` when none of the built-ins fit.

| Profile | Use | Required emphasis |
|---|---|---|
| `general` | Unknown or broad request | Summary, chapters, important visual/audio events, notable dialogue, uncertainty |
| `timeline` | Event or scene reconstruction | Dense chronological events, transitions, timestamps, causal sequence |
| `transcript` | Dialogue-heavy content | Transcript segments, speaker labels only when supported, visual context, provenance |
| `tutorial-sop` | Demonstrations and workflows | Ordered steps, tools, inputs, decisions, success checks, exceptions |
| `meeting-interview` | Interviews, panels, meetings | Speakers, topics, questions, answers, decisions, disagreements, action items |
| `education` | Lectures, lessons, explainers | Concepts, definitions, examples, misconceptions, knowledge checks |
| `product-demo` | Product walkthroughs | Features, user flow, value claims, friction, UI states, unanswered questions |
| `software-qa` | Bug recordings and test evidence | Actions, UI state, observed result, expected result, reproduction steps, severity evidence |
| `creative-marketing` | Ads, UGC, social, brand video | Hook, audience, angle, pacing, proof, offer, CTA, visual language; never infer actual performance |
| `compliance-review` | Claims and policy checks | Claims, disclosures, risky wording/visuals, evidence timestamps, uncertainty; not legal advice |
| `comparison` | Two or more videos | Shared schema, repeated patterns, differences, strengths, limitations, evidence per source |
| `custom` | User-defined evaluation | Apply only the supplied rubric while preserving the canonical evidence fields |

## Transcript rules

Prefer transcript evidence in this order and record the selected provenance:

1. Manual captions supplied by the source.
2. Embedded subtitles.
3. Platform auto-captions.
4. Gemini audio interpretation.
5. A dedicated speech-to-text fallback when explicitly configured.

Do not label inferred speakers as identified people. Use `Speaker 1`,
`Speaker 2`, or visible role descriptions unless identity is established by
the source itself.

## Custom rubric format

Accept Markdown, text, or JSON. A strong rubric defines:

- the question or decision;
- observable criteria;
- evidence requirements;
- weights or pass thresholds when scoring is requested;
- prohibited inferences;
- the desired output additions.

Treat reference examples as evaluation anchors, not content to imitate.
