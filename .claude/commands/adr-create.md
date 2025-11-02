# Create Architecture Decision Record

Document important architecture decisions with rationale and consequences.

## What This Does

System-architect creates formal Architecture Decision Records (ADRs) following industry standards.

## Usage

```
/adr-create [decision topic]
```

## Example

```
/adr-create "Choice of PostgreSQL over MongoDB for primary database"
/adr-create "Migration from monolith to microservices"
/adr-create "Adoption of GraphQL for public API"
/adr-create "Use of Redis for caching layer"
```

## What is an ADR?

Architecture Decision Records (ADRs) are documents that capture important architectural decisions along with their context and consequences. They help teams:

- Understand why decisions were made
- Avoid repeating past mistakes
- Onboard new team members
- Track architectural evolution
- Enable informed future decisions

## Process

1. **Decision Context** (system-architect + cto)
   - What decision needs to be made?
   - Why is it important?
   - What triggered this decision?
   - Current situation analysis
   - Constraints and requirements

2. **Options Analysis** (system-architect)
   - Identify all viable options (minimum 2-3)
   - Research each option
   - Document pros and cons
   - Analyze trade-offs
   - Gather data/benchmarks

3. **Evaluation** (system-architect + relevant specialists)
   - Technical feasibility
   - Cost implications
   - Team expertise alignment
   - Performance impact
   - Security considerations
   - Scalability implications
   - Maintainability impact

4. **Decision** (cto + system-architect)
   - Select preferred option
   - Document rationale
   - Explain why alternatives were rejected
   - Identify decision-makers
   - Set decision date

5. **Consequences** (system-architect)
   - Positive outcomes expected
   - Negative trade-offs accepted
   - Risks identified
   - Mitigation strategies
   - Success metrics

6. **ADR Documentation** (system-architect + technical-writer)
   - Follow standard ADR template
   - Clear, concise language
   - Evidence-based reasoning
   - Actionable consequences

## ADR Template

```markdown
# ADR-XXX: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Decision Makers:** [Names/Roles]
**Consulted:** [Names/Roles]

## Context

What is the issue we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Options Considered

### Option 1: [Name]
**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

### Option 2: [Name]
**Pros:**
- [Pro 1]

**Cons:**
- [Con 1]

### Option 3: [Name]
[...]

## Decision Rationale

Why did we choose Option X over the alternatives?

## Consequences

### Positive
- [Expected benefit 1]
- [Expected benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Risks
- [Risk 1] - Mitigation: [...]
- [Risk 2] - Mitigation: [...]

## Implementation

- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

## Success Metrics

How will we know this decision was successful?
- [Metric 1]: [Target]
- [Metric 2]: [Target]

## References

- [Link to research]
- [Benchmark results]
- [Related ADRs]

## Notes

Additional context, assumptions, or constraints.
```

## ADR Status Lifecycle

**Proposed:** Decision is under consideration
**Accepted:** Decision has been approved and is in effect
**Deprecated:** Decision is no longer recommended but still in use
**Superseded:** Decision has been replaced by ADR-XXX

## Deliverables

- ADR document (Markdown)
- Stored in `/docs/adr/` directory
- Numbered sequentially (ADR-001, ADR-002, etc.)
- Included in architecture documentation
- Referenced in related code/config

## Common ADR Topics

**Technology Choices:**
- Database selection
- Framework selection
- Cloud provider choice
- Programming language
- Build tools

**Architecture Patterns:**
- Monolith vs microservices
- Event-driven vs request-response
- CQRS adoption
- API style (REST vs GraphQL vs gRPC)

**Infrastructure:**
- Container orchestration platform
- CI/CD tooling
- Monitoring solution
- Logging strategy

**Security:**
- Authentication mechanism
- Authorization approach
- Encryption strategy
- Secrets management

**Development Practices:**
- Branching strategy
- Testing approach
- Code review process
- Documentation standards

## Best Practices

**DO:**
- Write ADRs for significant decisions
- Document options considered
- Be honest about trade-offs
- Update status when superseded
- Keep ADRs concise (1-2 pages)
- Use data and evidence

**DON'T:**
- Write ADRs for trivial decisions
- Hide negative consequences
- Make decisions without options analysis
- Delete or modify old ADRs
- Use jargon without explanation
- Make decisions in isolation

## Time Estimate

- Simple decision: 30-45 minutes
- Medium complexity: 1-2 hours
- Complex/strategic: 2-4 hours

## Output Format

- Markdown file: `/docs/adr/ADR-XXX-title.md`
- PDF export (for distribution)
- Added to ADR index/catalog
- Linked from architecture docs

## ADR Management

**Storage:**
```
docs/
└── adr/
    ├── README.md (ADR index)
    ├── ADR-001-database-choice.md
    ├── ADR-002-api-architecture.md
    ├── ADR-003-caching-strategy.md
    └── template.md
```

**Index Example:**
```markdown
# Architecture Decision Records

## Active Decisions
- [ADR-001](ADR-001-database-choice.md) - PostgreSQL for Primary Database
- [ADR-002](ADR-002-api-architecture.md) - REST API over GraphQL

## Superseded Decisions
- [ADR-003](ADR-003-caching-strategy.md) - Redis Caching (superseded by ADR-015)
```

## Integration with Development

- Reference ADR in code comments for critical decisions
- Include ADR links in PR descriptions
- Review ADRs during architecture reviews
- Update ADRs when assumptions change
- Create new ADR when superseding old one

## Follow-Up Commands

After creating ADR:
- `/design-architecture` - Implement architecture from ADR
- `/generate-docs` - Update architecture documentation
- `/review-architecture` - Validate implementation against ADR
