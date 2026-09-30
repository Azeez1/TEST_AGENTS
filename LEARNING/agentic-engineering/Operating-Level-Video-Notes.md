# Operating level: where to focus your attention

**Source:** [IndyDevDan, “Agentic Engineering Operating Level: WHERE to FOCUS your AGENTS?”](https://www.youtube.com/watch?v=rPWCYB62wvI) (36:32; published August 31, 2026). [Full auto-generated transcript](sources/Agentic%20Engineering%20Operating%20Level%20WHERE%20to%20FOCUS%20your%20AGENTS.md) was read end to end on September 24, 2026. Caption wording may contain errors.

## The idea

An *operating level* is the part of the software system where you and an agent put your attention. The video moves from code primitives (lines, functions, types), through files and modules, data and execution, application plans and documentation, to agent workflows and a software factory. Moving upward can increase leverage and speed. Moving downward gives more control and understanding. The useful skill is choosing the level for the task, then changing levels when the evidence calls for it. [Overview, 1:04–9:20](https://www.youtube.com/watch?v=rPWCYB62wvI&t=64s)

## Decision rule to practice

| Move up toward reusable workflows when… | Move down toward code, data, and tests when… |
|---|---|
| The domain is familiar and the task repeats. | The domain or system is unfamiliar. |
| Inputs, outputs, and a pass/fail check are clear. | The result is high impact or hard to reverse. |
| You can inspect failures and correct them. | Validation is weak or performance details matter. |

The video's “three repetitions” trigger for automation is a heuristic, not a requirement. [When to move, 20:19–25:58](https://www.youtube.com/watch?v=rPWCYB62wvI&t=1219s)

## Apply it to your work

- **Your agent system:** A recurring, well-understood task can become a skill or AI developer workflow. First define its inputs, outputs, tests, and failure path. If output quality slips, inspect the relevant prompt, tool call, file, function, schema, or test instead of only rerunning the top-level agent.
- **FDE preparation:** Your strength at planning and client/system discussions lets you work at the application and workflow levels. The current gap you identified is reading, writing, and debugging Python quickly. Work down to loops, indexing, functions, and tests until you can verify an agent's implementation and pass a no-AI coding screen yourself. The speaker's opinion about hand-written code does not change an interview's rules.
- **A software factory:** In the video, this means several repeatable developer workflows (for example feature, hotfix, and staging), each with validation, composed together. One agent loop alone is not a factory. [Workflows, 30:01–36:27](https://www.youtube.com/watch?v=rPWCYB62wvI&t=1801s)

## Where this fits in the rep plan

- **M3 — loop and harness:** Make the agent's actions observable and define termination and failure checks.
- **M4 — multi-agent:** Delegate only when the work is understood enough to specify and verify.
- **M5 — leverage points:** Turn repeated, verified steps into skills, commands, or workflows.
- **M6 — evaluation:** Tests and outcome checks are what let you safely move upward.

**Recall rep:** Pick one task in TEST_AGENTS. Name its current operating level, one reason to move up or down, and the concrete evidence you would need before trusting an agent to run it. Then point to the exact file, test, or result that supplies that evidence.
