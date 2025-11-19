# Ship Feature

End-to-end feature delivery pipeline from development to deployment.

## What This Does

CTO orchestrates the complete feature delivery workflow across all engineering agents.

## Usage

```
/ship-feature [feature description] [target environment]
```

## Example

```
/ship-feature "User authentication with OAuth and JWT" "staging"
/ship-feature "Real-time analytics dashboard" "production"
```

## Process

1. **Requirements & Architecture** (cto + system-architect)
   - Feature requirements breakdown
   - System architecture design
   - Technical approach decision
   - Architecture diagrams (Mermaid.js)
   - Database schema design (database-architect)

2. **Implementation Planning** (cto)
   - Task breakdown and assignment
   - Frontend vs backend work split
   - API contract definition
   - Timeline estimation

3. **Development** (frontend-developer + backend-architect + ai-engineer)
   - Backend API implementation
   - Frontend UI components
   - Integration with existing systems
   - AI/ML components (if applicable)

4. **Code Quality Review** (code-reviewer + security-auditor)
   - Code quality analysis
   - Security vulnerability scan
   - Best practices compliance
   - Performance considerations

5. **Testing** (test-engineer + QA_TEAM)
   - Unit test generation
   - Integration test creation
   - Edge case coverage
   - Test execution and reporting

6. **Documentation** (technical-writer)
   - API documentation
   - User documentation
   - Architecture decision records (ADRs)
   - Deployment guide

7. **Deployment** (devops-engineer)
   - CI/CD pipeline setup
   - Infrastructure provisioning (Terraform)
   - Container configuration (Docker)
   - Kubernetes deployment (if applicable)
   - Health checks and monitoring

8. **Post-Deployment** (devops-engineer + debugger)
   - Smoke tests
   - Monitoring dashboard setup
   - Rollback plan verification
   - Performance baseline

## Deliverables

- Architecture diagrams and design docs
- Implemented feature code (frontend + backend)
- Comprehensive test suite
- API documentation
- User documentation
- CI/CD pipeline configuration
- Deployed to target environment
- Monitoring and alerts configured

## Time Estimate

4-8 hours for medium complexity feature
8-16 hours for complex feature

## Prerequisites

- Feature requirements document or description
- Target environment access
- Necessary API keys/credentials

## Supervisor Verification

After deployment, the CTO automatically triggers supervisor verification to ensure:
- Code quality meets standards
- Tests are passing (unit + integration)
- Security audit completed
- Documentation is complete
- Deployment successful
- Monitoring configured

## When to Use This vs Other Commands

**Use /ship-feature when:**
- You want COMPLETE feature delivery (dev → test → deploy)
- Engineering-focused workflow
- Need end-to-end automation
- Single feature scope

**Use /product-launch when:**
- You need CROSS-TEAM coordination (Engineering + Marketing + Sales + Finance + QA)
- Full product launch (not just engineering)
- Need go-to-market strategy
- Marketing campaign + Sales enablement required
- Time: 2-12 weeks (comprehensive)

**Use /code-review when:**
- You ONLY need code review (not full delivery)
- Want multi-perspective analysis
- Don't need deployment
- Time: 15min - 5hrs (review only)

**Use /debug-issue when:**
- You're FIXING a bug (not building new feature)
- Need root cause analysis
- Targeted troubleshooting
- Time: 30min - 8hrs (debugging focus)

**Use /deploy-stack when:**
- You ONLY need infrastructure deployment
- Infrastructure-as-code focus
- No feature development needed
- Time: 1-3 hours (deployment only)

**Related Commands:**
- `/product-launch` - Full cross-team product launch
- `/code-review` - Code quality review only
- `/debug-issue` - Bug fixing workflow
- `/deploy-stack` - Infrastructure deployment
- `/design-architecture` - Architecture design (pre-development)
- `/security-audit` - Security review only
