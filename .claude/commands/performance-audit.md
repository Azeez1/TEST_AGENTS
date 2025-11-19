# Performance Audit

Comprehensive performance analysis and optimization recommendations.

## What This Does

Backend-architect and devops-engineer analyze application performance and identify bottlenecks.

## Usage

```
/performance-audit [scope: frontend | backend | database | infrastructure | full]
```

## Example

```
/performance-audit backend
/performance-audit database
/performance-audit full
```

## Process

### Frontend Performance (frontend-developer + ui-ux-designer)

1. **Load Time Analysis**
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
   - Time to Interactive (TTI)
   - Total Blocking Time (TBT)
   - Cumulative Layout Shift (CLS)

2. **Asset Optimization**
   - Bundle size analysis
   - Code splitting opportunities
   - Image optimization
   - Font loading strategy
   - Lazy loading implementation

3. **Rendering Performance**
   - React re-render analysis
   - Virtual DOM optimization
   - Memoization opportunities
   - Animation performance

### Backend Performance (backend-architect)

4. **API Performance**
   - Response time analysis
   - Endpoint latency breakdown
   - Slow query identification
   - N+1 query detection
   - Caching opportunities

5. **Code Optimization**
   - Algorithm efficiency
   - Memory usage patterns
   - CPU profiling
   - Async/await optimization
   - Connection pooling

### Database Performance (database-architect)

6. **Query Analysis**
   - Slow query log review
   - Query execution plans
   - Missing indexes identification
   - Query optimization
   - Join strategy optimization

7. **Database Tuning**
   - Connection pool sizing
   - Cache hit ratios
   - Buffer pool optimization
   - Index fragmentation
   - Table statistics

### Infrastructure Performance (devops-engineer)

8. **Resource Utilization**
   - CPU usage patterns
   - Memory utilization
   - Disk I/O analysis
   - Network throughput
   - Auto-scaling configuration

9. **Caching Strategy**
   - Redis/cache hit rates
   - CDN performance
   - Browser caching headers
   - Cache invalidation strategy

10. **Load Testing**
    - Stress testing
    - Spike testing
    - Endurance testing
    - Scalability testing
    - Bottleneck identification

## Deliverables

- Performance audit report (PDF, 15-25 pages)
- Bottleneck analysis
- Optimization recommendations (prioritized)
- Load testing results
- Query optimization guide
- Code improvements (with examples)
- Infrastructure tuning recommendations
- Performance baseline metrics
- Improvement roadmap (90 days)

## Performance Metrics

**Frontend:**
- LCP < 2.5s (good)
- FID < 100ms (good)
- CLS < 0.1 (good)
- Bundle size < 500KB initial

**Backend:**
- API p95 < 200ms
- API p99 < 500ms
- Database query p95 < 50ms
- Error rate < 0.1%

**Infrastructure:**
- CPU utilization < 70%
- Memory utilization < 80%
- Cache hit ratio > 90%
- Uptime > 99.9%

## Optimization Techniques

**Frontend:**
- Code splitting
- Image optimization (WebP, lazy loading)
- Tree shaking
- Minification and compression
- Service Workers

**Backend:**
- Database query optimization
- Caching (Redis, in-memory)
- Connection pooling
- Async processing
- Load balancing

**Database:**
- Index optimization
- Query rewriting
- Partitioning
- Read replicas
- Query caching

**Infrastructure:**
- Horizontal scaling
- CDN implementation
- Load balancer tuning
- Container optimization
- Auto-scaling policies

## Time Estimate

- Frontend only: 2-3 hours
- Backend only: 2-3 hours
- Database only: 2-3 hours
- Infrastructure only: 2-3 hours
- Full audit: 6-10 hours

## Output Format

- Executive summary with key findings
- Performance metrics dashboard
- Bottleneck analysis with evidence
- Prioritized optimization list
- Before/after projections
- Implementation guide

## When to Use This vs Other Commands

**Use /performance-audit when:**
- You have PERFORMANCE issues or want optimization
- Need bottleneck identification
- Load testing and capacity planning
- Specific performance metrics and tuning
- Time: 2-10 hours (performance focus)

**Use /review-architecture when:**
- You want SYSTEM-LEVEL architecture review
- Strategic architectural assessment
- Scalability and maintainability (broader than just performance)
- Architecture patterns and design decisions
- Time: 3-16 hours (architecture focus)

**Use /debug-issue when:**
- You have a SPECIFIC BUG (not general performance)
- Functional issue (not performance issue)
- Need root cause analysis for errors
- Time: 30min - 8hrs (debugging focus)

**Use /scalability-analysis when:**
- You want SCALABILITY planning (subset of performance)
- Growth and capacity planning
- Scaling strategy only
- Time: 2-4 hours (scalability focus)

**Use /code-review when:**
- You want CODE QUALITY review (includes performance considerations)
- General code review (not performance-specific)
- Multi-perspective analysis
- Time: 15min - 5hrs (code focus)

**Related Commands:**
- `/review-architecture` - System architecture review
- `/scalability-analysis` - Scalability planning
- `/debug-issue` - Bug fixing (functional issues)
- `/code-review` - Code quality review
- `/deploy-stack` - Deployment (can cause performance issues)
