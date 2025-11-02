# Architecture Review

Comprehensive architecture assessment and improvement recommendations.

## What This Does

System-architect reviews existing architecture for scalability, maintainability, and best practices.

## Usage

```
/review-architecture [codebase path or architecture description]
```

## Example

```
/review-architecture .
/review-architecture "Review our microservices architecture in the /services directory"
/review-architecture "Analyze current monolith before microservices migration"
```

## Process

1. **Architecture Discovery** (system-architect + cto)
   - Code structure analysis
   - Component identification
   - Dependency mapping
   - Technology stack inventory
   - Integration points
   - Data flow analysis

2. **Architecture Reconstruction** (system-architect)
   - Generate current-state diagrams
   - Document existing architecture
   - Identify implicit patterns
   - Map service boundaries
   - Trace data flows

3. **Architecture Assessment**

   **a) Design Principles** (system-architect)
   - Single Responsibility Principle
   - Separation of Concerns
   - DRY (Don't Repeat Yourself)
   - SOLID principles
   - Coupling and Cohesion
   - Abstraction levels

   **b) Scalability Analysis** (system-architect + devops-engineer)
   - Horizontal scaling capability
   - Vertical scaling limits
   - Bottleneck identification
   - Resource utilization
   - Load distribution
   - Auto-scaling readiness

   **c) Reliability & Resilience**
   - Single points of failure
   - Failure mode analysis
   - Recovery mechanisms
   - Circuit breakers
   - Retry logic
   - Graceful degradation

   **d) Maintainability** (code-reviewer + system-architect)
   - Code organization
   - Module boundaries
   - Technical debt assessment
   - Refactoring opportunities
   - Documentation quality
   - Testability

   **e) Security** (security-auditor + system-architect)
   - Security architecture
   - Authentication/authorization
   - Data protection
   - Network security
   - Secrets management
   - Attack surface analysis

   **f) Performance** (backend-architect + system-architect)
   - Architectural bottlenecks
   - Caching strategy
   - Database design
   - Asynchronous processing
   - Resource optimization

   **g) Cost Efficiency** (devops-engineer + system-architect)
   - Infrastructure costs
   - Over-provisioning
   - Resource waste
   - Cost optimization opportunities
   - Serverless opportunities

4. **Pattern Analysis** (system-architect)
   - Identify existing patterns (good and bad)
   - Anti-pattern detection:
     - God objects
     - Spaghetti architecture
     - Big Ball of Mud
     - Vendor lock-in
     - Tight coupling
   - Pattern recommendations:
     - Design patterns
     - Architecture patterns
     - Integration patterns

5. **Modernization Assessment** (system-architect + cto)
   - Technology obsolescence
   - Migration opportunities
   - Cloud-native readiness
   - Containerization potential
   - Microservices suitability
   - Serverless opportunities

6. **Recommendations** (system-architect)
   - Prioritized improvement list
   - Quick wins (0-30 days)
   - Medium-term improvements (30-90 days)
   - Long-term strategic changes (90+ days)
   - Migration paths
   - Risk assessment

7. **Target Architecture** (system-architect)
   - Proposed future-state architecture
   - Migration roadmap
   - Phased approach
   - Risk mitigation strategies
   - Success metrics

## Deliverables

### Diagrams:
- Current-state architecture (as-is)
- Component dependency graph
- Data flow diagrams
- Future-state architecture (to-be)
- Migration roadmap

### Documentation:
- Architecture Review Report (PDF, 30-50 pages)
  - Executive summary
  - Current architecture analysis
  - Findings by category
  - Risk assessment
  - Recommendations (prioritized)
  - Target architecture design
  - Migration roadmap
  - Cost-benefit analysis

### Artifacts:
- Technical debt inventory
- Anti-pattern catalog
- Architecture Decision Records (ADRs)
- Refactoring guide
- Migration plan

## Review Criteria

**Scalability (0-10 scale):**
- Horizontal scaling: 8+
- Performance under load: 8+
- Resource efficiency: 7+

**Reliability (0-10 scale):**
- Fault tolerance: 8+
- Recovery capability: 8+
- Monitoring & observability: 7+

**Maintainability (0-10 scale):**
- Code organization: 8+
- Module independence: 7+
- Documentation: 7+
- Testability: 8+

**Security (Pass/Fail):**
- No critical vulnerabilities
- Security best practices followed
- Compliance requirements met

**Cost Efficiency (0-10 scale):**
- Resource utilization: 7+
- Infrastructure optimization: 7+

## Common Architecture Smells

**Structural:**
- Cyclic dependencies
- God classes/services
- Feature envy
- Shotgun surgery
- Divergent change

**Scalability:**
- Synchronous coupling
- Lack of caching
- N+1 query problems
- Monolithic database
- Single points of failure

**Maintainability:**
- Unclear boundaries
- Tight coupling
- Poor abstraction
- Lack of documentation
- Technical debt accumulation

**Performance:**
- Inefficient data access
- Over-fetching
- Lack of pagination
- Synchronous blocking
- Resource leaks

## Time Estimate

- Small codebase (< 10K LOC): 3-4 hours
- Medium codebase (10-50K LOC): 6-8 hours
- Large codebase (50K+ LOC): 10-16 hours
- Enterprise system: 2-3 days

## Output Format

- PDF report with executive summary
- Mermaid.js diagrams (current + future state)
- Markdown documentation
- Excel spreadsheet (technical debt inventory)
- PowerPoint slides (executive presentation)

## Follow-Up Actions

After review, consider:
- `/refactor-plan` - Create refactoring roadmap
- `/design-architecture` - Design target architecture
- `/migration-plan` - Plan migration strategy
- `/setup-project` - Set up new architecture structure
