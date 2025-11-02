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
