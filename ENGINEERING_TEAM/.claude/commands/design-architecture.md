# Design System Architecture

Create comprehensive system architecture design with professional diagrams.

## What This Does

System-architect designs complete system architecture with Mermaid.js diagrams and documentation.

## Usage

```
/design-architecture [system description] [requirements]
```

## Example

```
/design-architecture "Real-time analytics platform" "handles 10K events/sec, low latency, multi-tenant"
/design-architecture "E-commerce marketplace" "scalable, payment processing, inventory management"
/design-architecture "AI agent orchestration system" "multi-agent coordination, task distribution, monitoring"
```

## Process

1. **Requirements Analysis** (system-architect + cto)
   - Functional requirements breakdown
   - Non-functional requirements (scalability, performance, security)
   - Constraints and assumptions
   - Success criteria
   - SLA requirements

2. **Architecture Design** (system-architect)
   - High-level architecture pattern selection
     - Monolith vs Microservices
     - Event-driven vs Request-response
     - Serverless vs Container-based
   - Component identification
   - Service boundaries
   - Data flow design
   - Technology stack selection

3. **Diagram Creation** (system-architect)
   - **System Context Diagram** (C4 Level 1)
     - System and external actors
     - High-level interactions

   - **Container Diagram** (C4 Level 2)
     - Applications and data stores
     - Technology choices
     - Communication protocols

   - **Component Diagram** (C4 Level 3)
     - Internal component structure
     - Component responsibilities
     - Dependencies

   - **Sequence Diagrams**
     - Key user flows
     - Inter-service communication
     - Error handling flows

   - **Data Flow Diagrams**
     - Data movement through system
     - Transformation points
     - Storage locations

   - **Deployment Diagram**
     - Infrastructure layout
     - Network topology
     - Security zones

4. **Database Architecture** (database-architect + system-architect)
   - Database selection (SQL vs NoSQL)
   - Data modeling approach
   - Entity Relationship Diagrams (ERD)
   - Sharding/partitioning strategy
   - Read/write separation

5. **Integration Architecture** (system-architect)
   - API design approach (REST, GraphQL, gRPC)
   - Authentication/authorization strategy
   - Rate limiting and throttling
   - Versioning strategy
   - Third-party integrations

6. **Scalability Design** (system-architect + devops-engineer)
   - Horizontal scaling strategy
   - Load balancing approach
   - Caching layers (CDN, Redis, in-memory)
   - Database scaling (replicas, sharding)
   - Queue systems (if applicable)
   - Auto-scaling policies

7. **Resilience & Reliability** (system-architect)
   - Failure modes analysis
   - Circuit breaker patterns
   - Retry and timeout strategies
   - Disaster recovery plan
   - Backup strategy
   - Health check design

8. **Security Architecture** (security-auditor + system-architect)
   - Security layers
   - Authentication/authorization
   - Data encryption (at rest, in transit)
   - Network security
   - Secrets management
   - Compliance requirements

9. **Documentation** (system-architect + technical-writer)
   - Architecture overview document
   - Design decisions and rationale
   - Component descriptions
   - Technology stack justification
   - Deployment guide
   - Operational runbook

## Deliverables

### Diagrams (Mermaid.js + PNG exports):
- System Context Diagram
- Container Diagram
- Component Diagram
- Sequence Diagrams (3-5 key flows)
- Data Flow Diagram
- Deployment Diagram
- ERD (Entity Relationship Diagram)

### Documentation:
- Architecture Design Document (20-40 pages PDF)
- Technology Stack Document
- API Design Specification
- Scalability Strategy
- Security Architecture Document
- Disaster Recovery Plan
- ADR (Architecture Decision Record) for key decisions

### Code Artifacts:
- Infrastructure as Code templates (Terraform)
- Docker/Kubernetes configs (skeletal)
- API contract examples (OpenAPI)
- Configuration templates

## Architecture Patterns Considered

**Application Patterns:**
- Monolith
- Microservices
- Modular Monolith
- Event-Driven Architecture
- CQRS (Command Query Responsibility Segregation)
- Event Sourcing
- Serverless

**Integration Patterns:**
- API Gateway
- Service Mesh
- Message Queue
- Event Bus
- GraphQL Federation

**Data Patterns:**
- Database per Service
- Shared Database
- CQRS
- Event Sourcing
- Data Lake
- Cache-Aside

## Mermaid.js Diagram Types

- **Flowchart** - Process flows
- **Sequence Diagram** - Interactions over time
- **Class Diagram** - Object structure
- **ER Diagram** - Database entities
- **State Diagram** - State machines
- **Gantt Chart** - Timeline/roadmap
- **C4 Diagrams** - Architecture layers
- **Deployment Diagram** - Infrastructure

## Time Estimate

- Simple system (< 5 components): 2-3 hours
- Medium system (5-15 components): 4-6 hours
- Complex system (15+ components, distributed): 8-12 hours

## Output Format

- Markdown documentation with embedded Mermaid diagrams
- PDF export of full documentation
- PNG exports of all diagrams (for presentations)
- Editable Mermaid source files
- Terraform/K8s templates

## Success Criteria

- All requirements addressed in design
- Clear component boundaries and responsibilities
- Scalability path defined
- Security considerations documented
- Cost-effective technology choices
- Maintainability and extensibility considered
- Team expertise alignment
