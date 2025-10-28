# Deploy Stack

Deploy complete application stack with infrastructure provisioning.

## What This Does

DevOps-engineer handles end-to-end deployment with monitoring and health checks.

## Usage

```
/deploy-stack [environment] [stack components]
```

## Example

```
/deploy-stack staging "api, frontend, database, redis"
/deploy-stack production "full-stack"
```

## Process

1. **Pre-Deployment Checks** (devops-engineer + security-auditor)
   - Environment variables validation
   - Secrets verification
   - Security scan
   - Dependency audit
   - Configuration review

2. **Infrastructure Provisioning** (devops-engineer)
   - Terraform plan generation
   - Infrastructure as Code review
   - Resource provisioning:
     - Compute (EC2, ECS, Kubernetes)
     - Database (RDS, DynamoDB)
     - Cache (Redis, ElastiCache)
     - Storage (S3, EBS)
     - Networking (VPC, Load Balancers)
   - DNS configuration

3. **Container Build** (devops-engineer)
   - Docker image building
   - Multi-stage build optimization
   - Image scanning
   - Registry push
   - Image tagging strategy

4. **Application Deployment**
   - Kubernetes manifests (if K8s)
   - ECS task definitions (if ECS)
   - Rolling deployment strategy
   - Health check configuration
   - Auto-scaling setup

5. **Database Migration** (database-architect + devops-engineer)
   - Backup current database
   - Migration script validation
   - Schema migration
   - Data migration (if needed)
   - Rollback plan

6. **Monitoring Setup** (devops-engineer)
   - CloudWatch dashboards
   - Prometheus/Grafana (if applicable)
   - Log aggregation (CloudWatch Logs, ELK)
   - Alerting rules
   - Performance baselines

7. **Smoke Testing** (test-engineer)
   - Health endpoint checks
   - Critical path testing
   - Performance validation
   - Error rate monitoring

8. **Documentation** (technical-writer + devops-engineer)
   - Deployment runbook
   - Architecture diagram update
   - Environment configuration docs
   - Rollback procedures

## Deliverables

- Provisioned infrastructure (Terraform state)
- Deployed application (all components)
- Monitoring dashboards
- Alert configurations
- Deployment documentation
- Health check reports
- Rollback plan

## Deployment Strategies

- **Blue-Green:** Zero-downtime, instant rollback
- **Rolling:** Gradual rollout, resource-efficient
- **Canary:** Risk mitigation, gradual traffic shift

## Time Estimate

- Simple stack (API + DB): 1-2 hours
- Medium stack (API + Frontend + DB + Cache): 2-4 hours
- Complex stack (Microservices, K8s): 4-8 hours

## Rollback Triggers

- Health check failures
- Error rate > 5%
- Response time > 2x baseline
- CPU/Memory > 90%

## Post-Deployment

- Monitor for 30 minutes
- Verify all health checks
- Check logs for errors
- Validate key metrics
- Update status page
