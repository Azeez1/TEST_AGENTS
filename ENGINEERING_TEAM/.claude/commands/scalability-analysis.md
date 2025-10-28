# Scalability Analysis

Analyze system scalability and create scaling roadmap.

## What This Does

System-architect evaluates current scalability and designs scaling strategy.

## Usage

```
/scalability-analysis [target scale] [current metrics]
```

## Example

```
/scalability-analysis "10x user growth from 1K to 10K users" "current: 100 req/min, p95 200ms"
/scalability-analysis "Handle 1M daily events" "current: 50K events/day"
/scalability-analysis "Global expansion to 5 regions" "current: single US region"
```

## Process

1. **Current State Assessment** (system-architect + devops-engineer)

   **Performance Baseline:**
   - Current user load
   - Request rate (req/sec, req/min)
   - Response times (p50, p95, p99)
   - Database query performance
   - Resource utilization (CPU, memory, disk, network)
   - Error rates
   - Concurrent connections

   **Infrastructure Inventory:**
   - Current architecture diagram
   - Server/container specs
   - Database configuration
   - Cache setup
   - Load balancer config
   - CDN usage
   - Auto-scaling policies

2. **Target Scale Definition** (system-architect + cto)
   - Target user count
   - Expected traffic patterns
   - Data volume projections
   - Geographic distribution
   - Performance SLAs
   - Timeline for growth

3. **Bottleneck Identification** (system-architect + backend-architect)

   **Application Layer:**
   - Synchronous blocking operations
   - Inefficient algorithms
   - Memory leaks
   - Poor connection pooling
   - Missing caching

   **Database Layer:**
   - Slow queries
   - Missing indexes
   - Lock contention
   - Connection pool exhaustion
   - Single write master

   **Infrastructure Layer:**
   - CPU bottlenecks
   - Memory constraints
   - Network bandwidth limits
   - Disk I/O limitations
   - Single points of failure

4. **Scalability Strategies** (system-architect)

   **Horizontal Scaling:**
   - Stateless application design
   - Load balancer configuration
   - Session management (Redis, JWT)
   - Auto-scaling policies
   - Container orchestration

   **Vertical Scaling:**
   - Resource limits analysis
   - Cost-benefit analysis
   - When vertical makes sense

   **Database Scaling:**
   - Read replicas
   - Write scaling (sharding)
   - Connection pooling
   - Query optimization
   - Database partitioning
   - CQRS pattern

   **Caching Strategy:**
   - Cache layers (CDN, Redis, in-memory)
   - Cache-aside pattern
   - Write-through vs write-behind
   - Cache invalidation strategy
   - TTL configuration

   **Asynchronous Processing:**
   - Message queues (RabbitMQ, SQS, Kafka)
   - Background job processing
   - Event-driven architecture
   - Batch processing

   **Content Delivery:**
   - CDN implementation
   - Static asset optimization
   - Edge computing
   - Geographic distribution

5. **Load Testing** (system-architect + test-engineer)
   - Load testing plan
   - Stress testing scenarios
   - Spike testing
   - Endurance testing
   - Scalability testing
   - Tools: k6, JMeter, Locust, Artillery

6. **Capacity Planning** (system-architect + devops-engineer)
   - Resource requirements calculation
   - Growth projections
   - Headroom planning (2-3x capacity)
   - Cost modeling
   - Infrastructure provisioning plan

7. **Scaling Roadmap** (system-architect + cto)

   **Phase 1: Quick Wins (0-30 days)**
   - Low-hanging fruit optimizations
   - Caching implementation
   - Query optimization
   - Resource right-sizing

   **Phase 2: Architectural Changes (30-90 days)**
   - Horizontal scaling setup
   - Database read replicas
   - Async processing introduction
   - CDN implementation

   **Phase 3: Strategic Evolution (90+ days)**
   - Microservices migration (if needed)
   - Multi-region deployment
   - Advanced caching strategies
   - Event-driven architecture

8. **Risk Assessment** (system-architect)
   - Scaling risks
   - Single points of failure
   - Data consistency challenges
   - Migration complexity
   - Mitigation strategies

9. **Cost Analysis** (devops-engineer + system-architect)
   - Current infrastructure costs
   - Projected costs at scale
   - Cost optimization opportunities
   - Reserved capacity vs on-demand
   - TCO (Total Cost of Ownership)

## Deliverables

### Analysis Report (PDF, 25-35 pages):
- Executive summary
- Current state assessment
- Bottleneck analysis
- Target scale requirements
- Scalability strategy
- Load testing results
- Capacity planning
- Scaling roadmap (phased)
- Cost analysis
- Risk assessment

### Diagrams:
- Current architecture (with bottlenecks highlighted)
- Target architecture (scaled)
- Scaling progression diagrams
- Data flow at scale
- Geographic distribution (if applicable)

### Technical Artifacts:
- Load testing scripts
- Capacity planning spreadsheet
- Cost modeling spreadsheet
- Auto-scaling policies
- Infrastructure as Code (Terraform)
- Database optimization scripts

### Implementation Guides:
- Horizontal scaling guide
- Database scaling guide
- Caching implementation guide
- Async processing setup
- Monitoring and alerts

## Scalability Patterns

**Application Scaling:**
- Stateless services
- Load balancing
- Session externalization
- Connection pooling
- Bulk operations

**Data Scaling:**
- Database sharding
- Read replicas
- CQRS (Command Query Responsibility Segregation)
- Event Sourcing
- Partitioning

**Integration Scaling:**
- API rate limiting
- Circuit breakers
- Bulkhead pattern
- Queue-based load leveling
- Throttling

**Performance Optimization:**
- Caching (multi-layer)
- Content delivery (CDN)
- Lazy loading
- Pagination
- Compression

## Load Testing Scenarios

**Baseline Test:**
- Normal load conditions
- Establish performance baseline

**Load Test:**
- Expected peak load
- Sustained over time

**Stress Test:**
- Beyond expected peak
- Find breaking point

**Spike Test:**
- Sudden traffic surge
- Recovery behavior

**Endurance Test:**
- Sustained high load (hours/days)
- Memory leak detection

## Scaling Metrics

**Performance:**
- Response time (p50, p95, p99)
- Throughput (requests/sec)
- Error rate (< 0.1%)
- Concurrent users

**Resource Utilization:**
- CPU utilization (< 70% avg)
- Memory utilization (< 80%)
- Disk I/O
- Network bandwidth

**Database:**
- Query execution time
- Connection pool usage
- Lock wait time
- Replication lag

**Application:**
- Request queue depth
- Background job lag
- Cache hit ratio (> 90%)
- Session count

## Time Estimate

- Simple application: 4-6 hours
- Medium complexity: 8-12 hours
- Complex/distributed system: 16-24 hours

## Output Format

- PDF analysis report with diagrams
- Excel cost modeling spreadsheet
- Mermaid.js architecture diagrams
- Load testing scripts and results
- Infrastructure as Code templates

## Success Criteria

**After Implementation:**
- [ ] Handles target scale with acceptable performance
- [ ] Auto-scaling works as expected
- [ ] No single points of failure
- [ ] Cost within budget
- [ ] Monitoring and alerts in place
- [ ] Documented scaling procedures
- [ ] Team trained on new architecture

## Follow-Up Commands

After analysis:
- `/design-architecture` - Design scaled architecture
- `/deploy-stack` - Implement scaling infrastructure
- `/performance-audit` - Validate scaling improvements
- `/generate-docs` - Document scaling architecture
