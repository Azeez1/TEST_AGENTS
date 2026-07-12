# Supervisor Agent - Verification Criteria

## Overview

The **Supervisor Agent** is a root-level quality assurance agent that sits above all teams (ENGINEERING_TEAM, MARKETING_TEAM, QA_TEAM) to independently verify that tasks are truly complete before they're considered "done."

## Purpose

When agents or teams report tasks as complete, the supervisor provides:

1. **Independent Verification** - Checks work objectively without bias
2. **Quality Gates** - Ensures standards are met before approval
3. **Evidence-Based Assessment** - Uses concrete metrics and checks
4. **Comprehensive Reporting** - Provides detailed pass/fail analysis
5. **Issue Identification** - Finds gaps and missing elements
6. **Risk Assessment** - Identifies deployment readiness

## Verification Standards by Task Type

### 1. Feature Development (Engineering)

| Category | Criteria | How Verified |
|----------|----------|--------------|
| **Code Implementation** | - Feature works as specified<br>- Follows project patterns<br>- No obvious bugs<br>- Proper error handling | - Read code files<br>- Check for edge cases<br>- Verify error handling exists<br>- Compare to requirements |
| **Tests** | - Unit tests exist (>80% coverage)<br>- Integration tests if needed<br>- All tests pass<br>- Edge cases covered | - Run pytest on test files<br>- Check coverage report<br>- Verify test assertions<br>- Look for edge case tests |
| **Code Quality** | - No syntax errors<br>- Docstrings present<br>- Clean code structure<br>- Follows conventions | - Python compile check<br>- Scan for docstrings<br>- Review function length<br>- Check naming conventions |
| **Security** | - No hardcoded secrets<br>- Input validation<br>- No SQL injection risks<br>- Dependencies secure | - Scan for password patterns<br>- Check user input handling<br>- Review DB queries<br>- Check dependency versions |
| **Documentation** | - README updated<br>- API docs if public<br>- Inline comments<br>- Changelog updated | - Check README exists<br>- Look for docstrings<br>- Verify complex logic explained<br>- Check CHANGELOG.md |
| **Git** | - Clean commits<br>- Descriptive messages<br>- Proper branch<br>- No secrets committed | - Review git log<br>- Check commit messages<br>- Verify branch name<br>- Scan for credentials |

**Quality Score**: 9-10 = Excellent, 7-8 = Good, 5-6 = Needs work, <5 = Not ready

**Deployment Ready**: Must score ≥7 with no critical security/functionality issues

---

### 2. Bug Fix (Engineering)

| Category | Criteria | How Verified |
|----------|----------|--------------|
| **Root Cause** | - Cause identified<br>- Documented in commit/PR | - Read commit message<br>- Check for comments explaining cause |
| **Fix Quality** | - Addresses root cause<br>- Not just symptoms<br>- Minimal changes<br>- No side effects | - Review code changes<br>- Check scope of fix<br>- Test related functionality |
| **Tests** | - Regression test added<br>- Fix verified by test<br>- Related tests still pass | - Find new test for bug<br>- Run test suite<br>- Check test actually fails without fix |
| **Documentation** | - Bug documented<br>- Fix explained<br>- Breaking changes noted | - Check issue/PR description<br>- Review changelog<br>- Look for migration notes |

**Quality Score**: 8-10 = Complete fix, 6-7 = Fix works but incomplete, <6 = Needs more work

**Deployment Ready**: Must score ≥7 with regression test

---

### 3. Content Creation (Marketing)

| Category | Criteria | How Verified |
|----------|----------|--------------|
| **Deliverable** | - Content exists<br>- Correct format<br>- Saved to right location | - Check file exists<br>- Verify format (MD, HTML, etc.)<br>- Confirm location (Google Drive) |
| **Quality** | - Grammar correct<br>- Brand voice consistent<br>- Factually accurate<br>- Engaging | - Read content<br>- Check for errors<br>- Verify facts<br>- Assess readability |
| **SEO** (if applicable) | - Keywords included<br>- Meta description<br>- Proper headings (H1, H2)<br>- Alt text for images | - Search for target keywords<br>- Check meta tags<br>- Verify heading structure<br>- Check image alt text |
| **Visual Assets** | - Images optimized<br>- Proper resolution<br>- Alt text included<br>- Attribution if needed | - Check file sizes<br>- Verify dimensions<br>- Look for alt attributes<br>- Check image credits |
| **Distribution** | - Published if required<br>- Links work<br>- Accessible to audience | - Verify publication status<br>- Test all links<br>- Check permissions |

**Quality Score**: 9-10 = Ready to publish, 7-8 = Minor edits, <7 = Needs revision

**Publication Ready**: Must score ≥8 with no broken links or factual errors

---

### 4. Infrastructure/DevOps

| Category | Criteria | How Verified |
|----------|----------|--------------|
| **Configuration** | - IaC files exist<br>- Syntax valid<br>- Follows patterns<br>- Properly parameterized | - Check Terraform/Helm files<br>- Run validation<br>- Review for hardcoding |
| **Security** | - Secrets in vault<br>- Least privilege<br>- Network policies<br>- Encryption enabled | - Scan for credentials<br>- Review IAM policies<br>- Check network rules<br>- Verify TLS/encryption |
| **Documentation** | - Architecture diagram<br>- Deployment instructions<br>- Runbooks<br>- Rollback plan | - Check for diagrams<br>- Read deployment docs<br>- Verify runbook exists<br>- Review rollback steps |
| **Testing** | - Config validated<br>- Smoke tests pass<br>- Monitoring works | - Run terraform validate<br>- Execute smoke tests<br>- Check metrics/alerts |
| **Monitoring** | - Metrics defined<br>- Alerts configured<br>- Dashboards exist<br>- Logging enabled | - List metrics<br>- Review alert rules<br>- Check dashboard links<br>- Verify log collection |

**Quality Score**: 9-10 = Production ready, 7-8 = Staging ready, <7 = Not ready

**Deployment Ready**: Must score ≥8 with no security issues and working rollback

---

### 5. Test Suite (QA)

| Category | Criteria | How Verified |
|----------|----------|--------------|
| **Test Coverage** | - Tests exist for all scenarios<br>- Edge cases included<br>- Coverage >80% | - Run coverage report<br>- Review test cases<br>- Check edge case tests |
| **Test Quality** | - Tests are clear<br>- Good assertions<br>- Isolated tests<br>- Fast execution | - Read test code<br>- Check assertion quality<br>- Verify test isolation<br>- Check execution time |
| **Fixtures** | - Proper setup/teardown<br>- Reusable fixtures<br>- Mock data clean | - Review fixture code<br>- Check for duplication<br>- Verify cleanup |
| **Documentation** | - Test purpose clear<br>- How to run tests<br>- Known issues noted | - Read test docstrings<br>- Check README<br>- Look for TODO comments |

**Quality Score**: 9-10 = Comprehensive, 7-8 = Good coverage, <7 = Gaps exist

**Acceptance Ready**: Must score ≥7 with all tests passing

---

### 6. Campaign (Multi-Team)

| Category | Criteria | How Verified |
|----------|----------|--------------|
| **Content** | - Blog post complete<br>- Social posts created<br>- Email templates ready<br>- Landing page done | - Check all content files<br>- Verify formats<br>- Test rendering |
| **Visual Assets** | - Images generated<br>- Videos produced<br>- Graphics optimized | - Check asset files<br>- Verify quality<br>- Test loading |
| **Technical** | - Landing page deployed<br>- Email system configured<br>- Analytics tracking<br>- Forms working | - Test landing page<br>- Verify email sending<br>- Check analytics tags<br>- Submit test forms |
| **Distribution** | - Schedule set<br>- Automation configured<br>- Backup plan exists | - Check calendar<br>- Verify n8n workflows<br>- Review contingency |

**Quality Score**: 9-10 = Ready to launch, 7-8 = Almost ready, <7 = Missing elements

**Launch Ready**: Must score ≥8 with all components tested

---

## Verification Process

### Phase 1: Gather Context
1. Read task description
2. Identify teams/agents involved
3. Determine expected deliverables
4. Set verification criteria

### Phase 2: Collect Evidence
Use verification tools to check:
- `validate_deliverables()` - Files exist
- `check_git_changes()` - Commits made
- `run_verification_tests()` - Tests pass
- `check_code_quality()` - Quality standards
- `verify_documentation()` - Docs complete

### Phase 3: Analyze Results
- Compare findings to criteria
- Identify gaps and issues
- Calculate quality score
- Determine deployment readiness

### Phase 4: Generate Report
- Status (PASSED/FAILED/PARTIAL)
- Findings for each criterion
- Issues found
- Recommendations
- Quality score (0-10)
- Deployment readiness (YES/NO)

---

## Quality Scoring System

### 10/10 - Exceptional
- All criteria met or exceeded
- Zero issues found
- Documentation excellent
- Tests comprehensive
- Ready for immediate deployment

### 9/10 - Excellent
- All critical criteria met
- Minor cosmetic issues only
- Documentation complete
- Tests thorough
- Ready for deployment

### 8/10 - Very Good
- All critical criteria met
- 1-2 minor issues
- Documentation adequate
- Tests sufficient
- Ready after minor fixes

### 7/10 - Good
- Most criteria met
- 2-3 minor issues
- Documentation present
- Tests exist
- Ready after fixes

### 6/10 - Adequate
- Core functionality works
- Several minor issues
- Documentation incomplete
- Test coverage gaps
- Needs work before deployment

### 5/10 - Needs Improvement
- Basic functionality works
- Multiple issues
- Documentation minimal
- Few tests
- Not ready for deployment

### 4/10 - Poor
- Functionality incomplete
- Many issues
- Little documentation
- No tests
- Significant work needed

### 1-3/10 - Unacceptable
- Major issues
- Doesn't work as intended
- No documentation
- No tests
- Start over or major rework

---

## Issue Severity Levels

### CRITICAL (Must Fix Before Deployment)
- Security vulnerabilities
- Data loss risks
- Breaking changes without migration
- Core functionality broken
- No tests for critical paths

### HIGH (Should Fix Before Deployment)
- Performance issues
- Error handling gaps
- Missing important tests
- Incomplete documentation
- Poor user experience

### MEDIUM (Can Fix After Deployment)
- Code style issues
- Missing edge case tests
- Documentation typos
- Minor UX improvements
- Optimization opportunities

### LOW (Nice to Have)
- Code comments
- Additional tests
- Documentation expansion
- Cosmetic improvements
- Refactoring opportunities

---

## Verification Tools

### 1. verify_task_completion()
**Purpose**: Main orchestrator for comprehensive task verification

**Inputs**:
- `task_description`: What was supposed to be done
- `team`: Which team(s) worked on it
- `agents_involved`: List of agents
- `expected_deliverables`: Files/outputs expected

**Outputs**:
- Overall status (PASSED/FAILED/PARTIAL)
- Findings by category
- Issues found
- Evidence collected

### 2. check_git_changes()
**Purpose**: Verify code changes are committed properly

**Checks**:
- Current branch
- Recent commits
- Changed files
- Commit messages
- Expected files in commits

### 3. validate_deliverables()
**Purpose**: Ensure expected files/outputs exist

**Checks**:
- File existence
- File sizes (not empty)
- Last modified dates
- Missing files list

### 4. run_verification_tests()
**Purpose**: Execute tests and collect results

**Checks**:
- Test execution
- Pass/fail status
- Test output
- Error messages
- Coverage if available

### 5. check_code_quality()
**Purpose**: Static analysis and quality checks

**Checks**:
- Syntax errors
- Docstrings present
- Security issues (hardcoded secrets)
- Code patterns
- Best practices

### 6. verify_documentation()
**Purpose**: Ensure documentation is complete

**Checks**:
- Documentation files exist
- Required sections present
- Not empty
- Formatted correctly

### 7. generate_verification_report()
**Purpose**: Create comprehensive verification report

**Outputs**:
- Task ID and timestamp
- Overall status
- All findings
- Quality score
- Deployment readiness
- Recommendations

---

## Example Verification Workflows

### Example 1: Verify Feature Implementation

```
Task: "Add user authentication feature"
Team: ENGINEERING_TEAM
Agents: backend-architect, frontend-developer, test-engineer

Verification Steps:
1. validate_deliverables([
     "src/auth/routes.py",
     "src/auth/models.py",
     "tests/test_auth.py",
     "docs/api.md"
   ])

2. check_code_quality([
     "src/auth/routes.py",
     "src/auth/models.py"
   ], criteria=["no_syntax_errors", "no_security_issues"])

3. run_verification_tests(["tests/test_auth.py"])

4. verify_documentation(
     ["docs/api.md"],
     required_sections=["Authentication", "Endpoints"]
   )

5. check_git_changes(expected_files=[
     "src/auth/routes.py",
     "src/auth/models.py",
     "tests/test_auth.py"
   ])

6. generate_verification_report(
     task_id="auth-feature-001",
     verification_status="PASSED|FAILED|PARTIAL",
     findings={...},
     issues_found=[...],
     recommendations=[...]
   )
```

### Example 2: Verify Marketing Campaign

```
Task: "Launch Q4 product campaign"
Team: MARKETING_TEAM
Agents: copywriter, visual-designer, email-specialist

Verification Steps:
1. validate_deliverables([
     "campaigns/q4/blog_post.md",
     "campaigns/q4/social_posts.json",
     "campaigns/q4/email_template.html",
     "campaigns/q4/assets/hero_image.png"
   ])

2. Read and check content quality:
   - Grammar and spelling
   - Brand voice consistency
   - Factual accuracy
   - Call-to-action present

3. Check visual assets:
   - Images optimized
   - Correct dimensions
   - Alt text present

4. Verify links work:
   - All URLs accessible
   - No broken links
   - Tracking parameters present

5. Check distribution:
   - Files in Google Drive
   - Email system configured
   - Publication schedule set

6. Generate report with go/no-go recommendation
```

### Example 3: Verify Bug Fix

```
Task: "Fix login timeout bug"
Team: ENGINEERING_TEAM
Agents: debugger, backend-architect, test-engineer

Verification Steps:
1. check_git_changes() to find fix commits

2. Read commit messages to understand:
   - Root cause of bug
   - What was changed
   - Why this fixes it

3. validate_deliverables([
     "src/auth/session.py",
     "tests/test_session_timeout.py"
   ])

4. Verify regression test exists:
   - Test that would fail before fix
   - Test passes after fix

5. run_verification_tests([
     "tests/test_session_timeout.py",
     "tests/test_auth.py"
   ])

6. Check no side effects:
   - Related tests still pass
   - No new issues introduced

7. Generate report confirming:
   - Bug fixed
   - Test added
   - No regressions
```

---

## Best Practices

### For the Supervisor

1. **Be Objective** - Don't accept agent reports blindly
2. **Use Tools** - Run automated checks when possible
3. **Be Thorough** - Check all criteria, not just some
4. **Provide Evidence** - Show what you found, not just opinions
5. **Be Constructive** - Suggest fixes for issues found
6. **Prioritize** - Focus on critical issues first
7. **Be Clear** - Make status unambiguous (PASSED/FAILED/PARTIAL)
8. **Document** - Record findings for future reference

### For Teams

1. **Self-Check First** - Don't wait for supervisor to find obvious issues
2. **Provide Context** - Tell supervisor what to verify
3. **List Deliverables** - Make it easy to find your work
4. **Write Tests** - Automated verification is faster
5. **Document Changes** - Explain what you did and why
6. **Commit Properly** - Clean commits make verification easier
7. **Follow Standards** - Meet criteria first time
8. **Fix Issues Promptly** - Address supervisor findings quickly

---

## Integration with Teams

### Engineering Team
- Verifies code, tests, docs, security
- Checks against CTO standards
- Validates deployment readiness
- Confirms no regressions

### Marketing Team
- Verifies content quality and completeness
- Checks brand consistency
- Validates SEO requirements
- Confirms publication readiness

### QA Team
- Verifies test coverage and quality
- Checks test execution and results
- Validates fixtures and test data
- Confirms testing standards met

---

## Reporting Format

### Status Badge
- ✅ **PASSED** - All criteria met, ready for deployment
- ⚠️ **PARTIAL** - Most criteria met, minor issues to address
- ❌ **FAILED** - Significant issues, not ready

### Report Structure
```
VERIFICATION [STATUS] [SCORE/10]

Task: [Task description]
Team: [Team name]
Agents: [Agent list]

Verified:
✓ [Criterion]: [Details]
✓ [Criterion]: [Details]
✗ [Criterion]: [Details on failure]
⚠ [Criterion]: [Details on partial]

Issues Found:
1. [Issue with severity]
2. [Issue with severity]

Quality Score: X/10
Deployment Ready: YES/NO

Recommendations:
1. [Recommendation]
2. [Recommendation]
```

---

## Conclusion

The Supervisor Agent provides an essential quality gate to ensure that work is truly complete before being marked as "done". By using objective criteria, automated tools, and thorough verification, it builds confidence in the multi-agent system's outputs and maintains high quality standards across all teams.
