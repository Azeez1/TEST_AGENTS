# Comprehensive Code Review

Multi-perspective code review from quality, security, and testing angles.

## What This Does

Combines code-reviewer, security-auditor, and test-engineer for thorough code analysis.

## Usage

```
/code-review [file path or directory]
```

## Example

```
/code-review src/api/auth.py
/code-review src/components/
/code-review .
```

## Process

1. **Code Quality Review** (code-reviewer)
   - Code structure and organization
   - Naming conventions
   - Code complexity analysis
   - Design patterns usage
   - DRY principle compliance
   - Error handling
   - Code documentation

2. **Security Audit** (security-auditor)
   - Vulnerability scanning
   - Authentication/authorization issues
   - Input validation
   - SQL injection risks
   - XSS vulnerabilities
   - Secrets in code
   - Dependency vulnerabilities
   - OWASP Top 10 compliance

3. **Test Coverage Analysis** (test-engineer)
   - Existing test coverage
   - Missing test cases
   - Edge cases not covered
   - Test quality assessment
   - Mocking strategy review

4. **Performance Review** (backend-architect)
   - Algorithm efficiency
   - Database query optimization
   - Memory usage patterns
   - Scalability concerns
   - Caching opportunities

5. **Consolidated Report** (cto)
   - Critical issues (must fix)
   - Important improvements (should fix)
   - Nice-to-have optimizations
   - Prioritized action items

## Deliverables

- Code quality report with scores
- Security vulnerability report
- Test coverage analysis
- Performance optimization suggestions
- Prioritized fix list
- Code improvement recommendations

## Review Criteria

**Code Quality (0-10 scale):**
- Readability: 8+
- Maintainability: 8+
- Complexity: Low to moderate

**Security (Pass/Fail):**
- No critical vulnerabilities
- No exposed secrets
- Proper input validation

**Test Coverage:**
- Target: 80%+ coverage
- All critical paths tested
- Edge cases covered

## Time Estimate

15-30 minutes for single file
1-2 hours for module/directory
3-5 hours for full codebase

## Output Format

Markdown report with:
- Executive summary
- Detailed findings by category
- Code snippets with issues highlighted
- Suggested fixes
- Overall health score
