# Technology Stack Recommendation

Get data-driven technology stack recommendations for your project.

## What This Does

System-architect analyzes requirements and recommends optimal technology choices.

## Usage

```
/tech-stack-recommendation [project type] [requirements]
```

## Example

```
/tech-stack-recommendation "SaaS analytics platform" "real-time data, 10K users, team of 5"
/tech-stack-recommendation "E-commerce marketplace" "high traffic, payment processing, mobile apps"
/tech-stack-recommendation "AI agent platform" "LLM integration, vector search, multi-agent orchestration"
```

## Process

1. **Requirements Analysis** (system-architect + cto)
   - Project scope and goals
   - Functional requirements
   - Non-functional requirements (performance, scalability, security)
   - Team size and expertise
   - Timeline and budget constraints
   - Existing infrastructure
   - Compliance requirements

2. **Constraint Identification**
   - Team expertise (what languages/frameworks team knows)
   - Performance requirements (latency, throughput)
   - Scalability needs (users, data volume)
   - Budget constraints (cloud costs, licensing)
   - Time to market
   - Maintenance capacity
   - Vendor preferences/restrictions

3. **Technology Evaluation** (system-architect + relevant specialists)

   **Frontend Stack:**
   - Framework options (React, Vue, Angular, Svelte, Next.js)
   - State management (Redux, Zustand, Jotai, MobX)
   - Styling approach (Tailwind, CSS-in-JS, Sass)
   - Build tools (Vite, Webpack, Turbopack)
   - Testing (Vitest, Jest, Playwright, Cypress)

   **Backend Stack:**
   - Language (Python, Node.js, Go, Rust, Java)
   - Framework (FastAPI, Express, NestJS, Django, Spring Boot)
   - API style (REST, GraphQL, gRPC, tRPC)
   - Authentication (NextAuth, Passport, OAuth libraries)

   **Database:**
   - Relational (PostgreSQL, MySQL, SQLite)
   - NoSQL (MongoDB, DynamoDB, Cassandra)
   - Vector DB (Pinecone, Weaviate, Qdrant) - for AI apps
   - Cache (Redis, Memcached)
   - Search (Elasticsearch, Algolia, Typesense)

   **Infrastructure:**
   - Cloud provider (AWS, GCP, Azure, Vercel, Railway)
   - Container orchestration (Docker, Kubernetes, ECS)
   - Serverless (Lambda, Cloud Functions, Edge Functions)
   - CDN (CloudFront, Cloudflare, Fastly)
   - IaC (Terraform, Pulumi, CloudFormation)

   **AI/ML (if applicable):**
   - LLM providers (OpenAI, Anthropic, Cohere, local models)
   - Vector databases (Pinecone, Weaviate, Qdrant)
   - ML frameworks (PyTorch, TensorFlow, scikit-learn)
   - ML orchestration (MLflow, Kubeflow, Weights & Biases)

4. **Comparative Analysis** (system-architect)
   - Create comparison matrix
   - Pros/cons for each option
   - Cost analysis
   - Learning curve assessment
   - Community support
   - Long-term viability
   - Performance benchmarks

5. **Risk Assessment** (system-architect + security-auditor)
   - Technology maturity
   - Vendor lock-in risk
   - Security considerations
   - Maintenance burden
   - Team adoption risk
   - Migration complexity

6. **Recommendation** (system-architect + cto)
   - Primary recommendation with justification
   - Alternative options
   - Technology stack diagram
   - Integration architecture
   - Deployment architecture
   - Cost estimate (infrastructure)

7. **Implementation Roadmap** (system-architect)
   - Setup guide
   - Learning resources
   - Proof of concept scope
   - Migration path (if applicable)
   - Success metrics

## Deliverables

### Documentation:
- Technology Stack Recommendation Report (PDF, 15-25 pages)
  - Executive summary
  - Requirements analysis
  - Technology comparison matrix
  - Recommended stack with justification
  - Alternative options
  - Risk assessment
  - Cost analysis
  - Implementation roadmap

### Diagrams:
- Technology stack architecture diagram
- Integration architecture
- Deployment architecture
- Data flow with technology labels

### Artifacts:
- Technology comparison spreadsheet (Excel)
- Cost estimation model
- Learning resource list
- Starter project template (optional)

## Evaluation Criteria

**Performance:**
- Request latency requirements
- Throughput capacity
- Concurrent users
- Data processing speed

**Scalability:**
- Horizontal scaling capability
- Vertical scaling limits
- Auto-scaling support
- Multi-region deployment

**Developer Experience:**
- Learning curve
- Documentation quality
- Community size
- Tooling ecosystem
- Debugging experience

**Operational:**
- Deployment complexity
- Monitoring capabilities
- Maintenance overhead
- Upgrade path
- Vendor support

**Cost:**
- Infrastructure costs
- Licensing fees
- Developer productivity
- Operational overhead
- Total Cost of Ownership (TCO)

**Security:**
- Security track record
- Built-in security features
- Compliance support
- Vulnerability response

## Popular Stack Recommendations

**Modern Full-Stack SaaS:**
- Frontend: Next.js 14+ (App Router), TypeScript, Tailwind CSS
- Backend: Next.js API routes or FastAPI
- Database: PostgreSQL (Supabase or Neon)
- Auth: NextAuth.js or Clerk
- Deployment: Vercel
- Rationale: Fast development, great DX, serverless scaling

**High-Performance API:**
- Backend: FastAPI (Python) or Go (Gin/Echo)
- Database: PostgreSQL + Redis
- Queue: Redis or RabbitMQ
- Deployment: Docker + Kubernetes
- Rationale: High throughput, low latency, horizontal scaling

**Real-Time Application:**
- Frontend: React + Socket.io client
- Backend: Node.js + Socket.io
- Database: PostgreSQL + Redis (pub/sub)
- Queue: Redis Streams or Kafka
- Rationale: WebSocket support, real-time events, scalable

**AI/ML Application:**
- Backend: FastAPI (Python)
- Vector DB: Pinecone or Weaviate
- LLM: OpenAI or Anthropic
- Cache: Redis
- Queue: Celery + Redis
- Rationale: Python ML ecosystem, async API, vector search

**Microservices:**
- Language: Go or Node.js (TypeScript)
- API: gRPC + REST Gateway
- Service Mesh: Istio
- Database: PostgreSQL per service
- Message Broker: Kafka or RabbitMQ
- Deployment: Kubernetes
- Rationale: Service independence, polyglot, scalable

## Anti-Recommendations

**Avoid if:**
- Technology too new (< 1 year old) for production
- Small community (hard to find help)
- Team has no expertise and tight timeline
- Vendor lock-in without clear benefits
- Over-engineering (using Kubernetes for 100 users)
- Under-engineering (SQLite for 1M users)

## Time Estimate

- Simple project: 1-2 hours
- Medium project: 2-4 hours
- Complex/enterprise: 4-8 hours

## Output Format

- PDF recommendation report
- Excel comparison matrix
- Architecture diagrams (Mermaid.js)
- Cost estimation spreadsheet
- Implementation checklist

## Follow-Up Commands

After recommendation, consider:
- `/setup-project` - Initialize project with recommended stack
- `/design-architecture` - Design detailed architecture
- `/generate-docs` - Create technical documentation
