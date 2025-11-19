# Security Audit

Comprehensive security assessment of codebase and infrastructure.

## What This Does

Security-auditor performs deep security analysis with devops-engineer for infrastructure review.

## Usage

```
/security-audit [scope: code | infrastructure | full]
```

## Example

```
/security-audit code
/security-audit infrastructure
/security-audit full
```

## Process

### Code Security (security-auditor)

1. **Vulnerability Scanning**
   - OWASP Top 10 analysis
   - Static code analysis
   - Dependency vulnerability scan
   - Known CVE checks

2. **Authentication & Authorization**
   - Auth flow review
   - Token handling
   - Session management
   - Permission checks
   - OAuth implementation

3. **Data Security**
   - Sensitive data handling
   - Encryption at rest/in transit
   - PII protection
   - SQL injection prevention
   - Input validation

4. **API Security**
   - Rate limiting
   - CORS configuration
   - API key management
   - Input sanitization
   - Response data exposure

### Infrastructure Security (devops-engineer)

5. **Container Security**
   - Docker image scanning
   - Base image vulnerabilities
   - Secrets management
   - Privileged containers
   - Network policies

6. **Cloud Configuration**
   - IAM roles and policies
   - Security groups
   - Encryption settings
   - Logging and monitoring
   - Backup security

7. **CI/CD Security**
   - Pipeline security
   - Secret management
   - Access controls
   - Artifact scanning

8. **Network Security**
   - Firewall rules
   - SSL/TLS configuration
   - VPN setup
   - DDoS protection

### Compliance Review (security-auditor)

9. **Compliance Checks**
   - GDPR compliance
   - SOC 2 requirements
   - HIPAA (if applicable)
   - PCI-DSS (if applicable)

## Deliverables

- Security audit report (PDF, 10-20 pages)
- Vulnerability list with severity ratings
- Compliance checklist
- Remediation roadmap (prioritized)
- Infrastructure security recommendations
- Code-level security fixes
- Configuration hardening guide

## Severity Levels

**Critical:** Immediate fix required
**High:** Fix within 1 week
**Medium:** Fix within 1 month
**Low:** Fix when convenient
**Informational:** Best practice recommendation

## Time Estimate

- Code only: 2-3 hours
- Infrastructure only: 2-3 hours
- Full audit: 4-6 hours

## Output Format

- Executive summary
- Detailed findings with evidence
- Remediation steps for each issue
- Compliance status report
- Security score (0-100)

## When to Use This vs Other Commands

**Use /security-audit when:**
- You ONLY need security analysis (deep dive)
- Compliance requirements (OWASP, SOC2, GDPR, HIPAA, PCI-DSS)
- Pre-deployment security check
- Vulnerability scanning and remediation
- Infrastructure security review
- Time: 2-6 hours (security focus only)

**Use /code-review when:**
- You want MULTI-PERSPECTIVE review (quality + security + tests)
- General code review (includes security but not security-only)
- Production readiness (broader than just security)
- Time: 15min - 5hrs (comprehensive review)

**Use /review-architecture when:**
- You want SYSTEM-LEVEL architecture review (includes security architecture)
- Security architecture patterns and design
- Strategic security assessment (not just vulnerabilities)
- Time: 3-16 hours (architecture focus)

**Use /deploy-stack when:**
- You're DEPLOYING and need security check as part of deployment
- Pre-deployment security validation
- Infrastructure security hardening
- Time: 1-8 hours (deployment + security)

**Related Commands:**
- `/code-review` - Includes security review as part of comprehensive review
- `/review-architecture` - Architecture-level security assessment
- `/deploy-stack` - Deployment with security checks
- `/ship-feature` - Feature delivery with security validation
- Use `security-check.sh` hook - Automatic credential leak prevention
