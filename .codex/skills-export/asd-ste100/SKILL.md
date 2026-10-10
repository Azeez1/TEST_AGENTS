---
name: "asd-ste100"
description: "This skill creates and reviews clear, source-backed technical writing using STE-inspired principles. It applies when ASD-STE100 is requested, when simplifying technical explanations or instructions, or when reviewing wording against a supplied standard. It can reuse ELI5 for visual or interactive teaching."
---

# ASD-STE100

Make technical information easy to understand without changing its meaning.
Work independently for writing and editing. Optionally reuse installed ELI5
for visual teaching; do not make ELI5 depend on this skill.

Use this name as the user's local workflow label. Do not imply ASD affiliation,
endorsement, certification, or verified compliance. Do not reproduce or bundle
the standard's dictionary. Read [official guidance](references/official-guidance.md)
for scope, current-source links, and the limits of this adaptation.

## Choose the writing mode

Default to **STE-inspired clear writing** for explanations, summaries, pages,
diagram labels, and scripts. Apply this workflow while respecting the requested
audience and format. Treat layered depth and ELI5 as local teaching choices,
not ASD standard requirements. Do not label the result compliant.

Use **strict standard review** only when standard checking is requested.
Establish the required issue, procedural or descriptive text type, applicable
official rules and dictionary, and authoritative subject terminology. Use a
lawfully available copy of the required standard. Never infer word approval
from common usage or model memory. Recheck official sources when the current
issue matters. If a required reference is missing, identify unavailable checks
and offer only a scoped, STE-inspired review.

Record strict-review findings as: text location, rule or dictionary entry,
evidence, proposed correction, and review status. Check vocabulary in context,
including meaning and part of speech. Validate technical nouns and verbs against
authoritative terminology. Apply the actual issue's sentence, paragraph,
grammar, and instruction rules; do not substitute a readability score.
Mark unexamined requirements as not checked. Report coverage and remaining
human review. Prompting and partial checks do not establish full compliance
or certification.

## Establish the meaning before editing

Read relevant sources, code, or supplied text fully enough to support the
explanation. Follow workspace instructions. Cite source locations for
consequential technical claims when available. Verify changing or uncertain
facts through primary sources. Keep private sources local unless external
use is authorized.

Note the subject, actor, action, object, sequence, conditions, exceptions,
quantities, units, identifiers, obligations, and uncertainty. Separate observed
behavior from inference. Flag ambiguity rather than inventing a fact or actor.

Preserve negation, thresholds, ranges, versions, and causal limits. Retain the
distinction between can, may, must, and should. Keep warnings and conditions
beside the action or claim they qualify. Preserve controlled wording and flag
clarity conflicts instead of silently rewriting it.

## Write clearly

- Lead with the useful point or action. Use concrete subjects and verbs.
- Express one main idea per sentence. Split long sentences while keeping each
  condition attached to its action. Prefer short, unambiguous sentences; do not
  impose a universal word-count cap on general writing.
- Prefer active voice when the actor is known. Use direct commands for procedures.
  Do not invent an actor to eliminate a passive sentence.
- Use one consistent term for each concept. Preserve actual component names,
  code symbols, UI labels, and identifiers. Avoid decorative synonyms.
- Define necessary jargon at first use. Put the familiar explanation next to
  the technical term. Expand abbreviations when helpful.
- Resolve vague pronouns and stacked nouns when evidence permits. Remove filler,
  idioms, and unsupported emphasis without removing facts.
- Order steps by their dependencies. State prerequisites before actions.
  Keep units, parameters, and exceptions visible.

## Offer depth progressively

Start with a concise orientation, then the mechanism or steps, then optional
implementation details and evidence. Use paragraphs, headings, or expandable
details to suit the requested format. Keep a caveat in the first layer if
omitting it changes the reader's decision or understanding.

Use analogies only when helpful. Map them back to real terms and state their
limits. Treat newcomers as intelligent readers. Preserve technical depth.

## Reuse ELI5 when visuals help

For a requested visual/interactive lesson, or when a visible mechanism materially
improves understanding, read the installed ELI5 skill before composing the
presentation. Resolve it through the current skill catalog or read
[the sibling ELI5 skill](../eli5/SKILL.md) relative to this directory.
Load only the ELI5 references needed for the task.

Carry the topic, audience, requested format, evidence, consistent terminology,
conditions, and caveats into ELI5's workflow. Follow its illustrated, interactive
HTML defaults, visual checks, accessibility, and delivery instructions. Apply
this skill's final meaning and wording review. Do not copy or edit ELI5, or
add a reverse dependency. Reuse means loading instructions in the current task;
it does not require spawning an agent.

Honor text-only requests. If ELI5 is unavailable, complete the writing and state
the unavailable presentation capability. ELI5 creates lessons rather than
finished explainer videos. Use a separately authorized workflow for video
production; apply this skill to script wording without claiming video compliance.

## Verify and deliver

Use [the verification checklist](references/verification-checklist.md) before
delivery. Compare the revision with its original source, not just readability.
Read [the example review](references/example-review.md) for a case preserving
conditions, uncertainty, and a failed-connection alternative.

Return the requested text or artifact. State material unresolved ambiguity and,
when relevant, the mode and checked scope. Keep routine checklist details out
of the user's product. Invocation does not authorize publishing, configuration
changes, or scheduling.
