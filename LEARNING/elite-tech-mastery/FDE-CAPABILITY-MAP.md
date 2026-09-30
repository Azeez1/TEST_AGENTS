# Exceptional AI FDE capability map

**Purpose:** One integrated reference for the skills needed to lead difficult customer AI deployments at a frontier lab. This is a target profile, not a claim that every FDE must be a specialist in every domain or that studying a list proves mastery.

## The end-to-end job

Discover the customer's workflow → choose a valuable use case → define requirements and success metrics → design the system → build and integrate it → evaluate the AI behavior → secure and deploy it → observe and repair it → drive adoption → turn field learning into reusable product patterns.

Current role descriptions from [OpenAI](https://openai.com/careers/forward-deployed-engineer-(fde)-sf-san-francisco/) and [Anthropic](https://job-boards.greenhouse.io/anthropic/jobs/5302966008) explicitly emphasize customer discovery, production code, deployment, AI applications, evaluation, autonomy, and adoption. The detailed skill map below is a synthesis of those requirements and the engineering work required to deliver them.

## The capability stack

| Domain | Skills an exceptional FDE can apply | Evidence of ability |
|---|---|---|
| 1. Customer and domain discovery | Interview users; map workflows and constraints; identify data owners, exceptions, incentives, and adoption blockers; translate ambiguity into requirements and acceptance criteria | A customer validates the problem and measurable outcome |
| 2. Product and delivery judgment | Prioritize use cases; prototype rapidly; decide human-versus-AI responsibility; sequence milestones; handle scope, speed, quality, and cost tradeoffs | A useful pilot reaches adoption, not just a demo |
| 3. Software engineering | Write and review Python plus a practical second stack; data structures, algorithms, types, interfaces, tests, debugging, version control, code review, maintainability; build APIs and full-stack features | Independently ship and repair working features |
| 4. Data and enterprise integration | SQL, schemas, transactions, migrations, search/vector indexes, ETL/streaming basics, API/webhook/MCP integration, identity and permissions, data quality and lineage | Customer data moves correctly between systems with clear ownership |
| 5. System design | Requirements, service boundaries, read/write/async/live lanes, consistency, caching, queues, idempotency, failure modes, scaling, latency, cost, and architecture tradeoffs | Explain and defend an end-to-end design under changed requirements |
| 6. Networking and cloud | HTTP, DNS, TLS, load balancing, network boundaries, VPC/private connectivity, containers, cloud compute/storage/databases, infrastructure as code | Deploy and troubleshoot an application in the customer's environment |
| 7. DevOps and reliability | CI/CD, release gates, rollback, config/secrets, logs, metrics, traces, alerts, SLOs, incident response, capacity and cost management | A safe release and recovery plan works when something breaks |
| 8. Security, privacy, and governance | Threat modeling, authentication/authorization, least privilege, encryption, secrets, audit trails, tenant isolation, data retention, vendor risk, and applicable regulatory controls | Sensitive data and tool actions have enforceable boundaries |
| 9. AI application and agent engineering | Model capability selection; prompting/context; retrieval; tool use; structured outputs; agent state, memory, orchestration, permissions, and human review; latency/cost tradeoffs | An AI workflow completes real tasks reliably within constraints |
| 10. Evaluation and AI controls | Golden datasets, task-specific metrics, offline/online evals, regression tests, failure taxonomies, prompt-injection defenses, policy checks, fallback/escalation, quality monitoring | Launch decisions are based on measured behavior, including failure cases |
| 11. Communication and field leadership | Explain tradeoffs to engineers, operators, and executives; write plans and handoffs; work inside customer teams; unblock stakeholders; teach adoption; stay effective under ambiguity | Customer and internal teams trust and act on the technical plan |
| 12. Platform feedback and reuse | Identify repeated deployment patterns; turn them into templates, tools, SDK improvements, playbooks, and product/research feedback | One deployment makes the next deployment easier or improves the platform |

## Depth rule

An exceptional FDE does **not** need to be a principal network engineer, security researcher, SRE, and model scientist simultaneously. They need independent end-to-end delivery ability, enough fluency to spot and investigate risks across those domains, judgment to involve specialists, and unusual depth in one or two areas. For an AI FDE, software implementation, system design, customer delivery, and AI evaluation are the central overlap.

## How this maps to the video levels

- **L1 code primitives:** implement and debug individual behaviors.
- **L2 code structure:** navigate and change a codebase safely.
- **L3 data and execution:** move data, run tools/scripts, and inspect runtime behavior.
- **L4 delivery and intent:** own an application, repository, plan, and documentation.
- **L5 agentic system:** design the product, agent workflows, AI-assisted developer process, and reusable delivery system.

The levels describe **range of motion**, not seniority. A top FDE moves between them: from a customer outcome down to a failing line or data record and back up to the deployed product.

## Local starting point and proof gap

See the [cross-track map](../CONNECTION-MAP.md), [system-design state](../system-design/CURRENT_STATE.md), and [Python practice](../python/README.md). Existing client solutioning frameworks, architecture reps, and agent work provide meaningful evidence. The immediate interview constraint is unaided Python writing. The larger proof for elite FDE capability is repeated production delivery with personally owned implementation, evaluation, security/reliability decisions, and adoption outcomes.
