# Debug Issue

Root cause analysis and issue resolution workflow.

## What This Does

Debugger agent performs systematic troubleshooting with support from relevant specialists.

## Usage

```
/debug-issue [issue description or error message]
```

## Example

```
/debug-issue "API returning 500 errors on user login endpoint"
/debug-issue "Memory leak in production after 24 hours uptime"
/debug-issue "Database queries timing out during peak load"
```

## Process

1. **Issue Triage** (debugger + cto)
   - Severity assessment (Critical, High, Medium, Low)
   - Impact analysis (users affected, business impact)
   - Initial hypothesis generation
   - Resource assignment

2. **Information Gathering** (debugger + devops-engineer)
   - Log analysis (application, system, database)
   - Metrics review (CPU, memory, network, DB)
   - Recent changes (deployments, config changes)
   - User reports and reproduction steps
   - Environment details

3. **Root Cause Analysis** (debugger + relevant specialists)
   - Code review of affected components
   - Database query analysis (database-architect)
   - Infrastructure review (devops-engineer)
   - Security analysis (security-auditor, if applicable)
   - Performance profiling
   - Stack trace analysis
   - 5 Whys technique

4. **Hypothesis Testing** (debugger)
   - Reproduce issue in test environment
   - Isolate variables
   - Test potential causes
   - Validate root cause

5. **Solution Implementation** (relevant developer agents)
   - Fix development (frontend/backend/devops)
   - Code review (code-reviewer)
   - Security check (security-auditor)
   - Test creation (test-engineer)

6. **Verification** (debugger + test-engineer)
   - Unit tests for fix
   - Integration testing
   - Regression testing
   - Production validation (if deployed)

7. **Post-Mortem** (cto + technical-writer)
   - Incident timeline
   - Root cause documentation
   - Fix description
   - Prevention measures
   - Action items
   - Lessons learned

## Deliverables

- Root cause analysis report
- Issue reproduction steps
- Fix implementation (code changes)
- Test cases covering the issue
- Post-mortem document (for critical issues)
- Prevention recommendations
- Monitoring improvements

## Debugging Techniques

- Log analysis and correlation
- Performance profiling
- Memory leak detection
- Network traffic analysis
- Database query profiling
- Code execution tracing
- A/B comparison (working vs broken)

## Time Estimate

- Simple bugs: 30-60 minutes
- Medium complexity: 1-3 hours
- Complex issues: 3-8 hours
- Critical production incidents: Until resolved

## Severity Levels

**Critical (P0):**
- Production down
- Data loss risk
- Security breach
- Immediate response

**High (P1):**
- Major feature broken
- Significant user impact
- Fix within 24 hours

**Medium (P2):**
- Feature partially working
- Workaround available
- Fix within 1 week

**Low (P3):**
- Minor issue
- Low user impact
- Fix in next sprint

## Output Format

Markdown report with:
- Executive summary
- Timeline of investigation
- Root cause explanation
- Fix description
- Prevention recommendations
- Code changes (diff)
