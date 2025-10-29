# Supervisor Agent Architecture

## Overview

The **Supervisor Agent** is a root-level quality assurance layer that sits above all teams in the multi-agent system. It provides independent verification that tasks are truly complete before they're considered "done".

## System Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                      USER / Claude Code                      │
│                    (Main Conversation)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────┐
                              │                         │
                              ▼                         ▼
┌─────────────────────────────────────┐   ┌───────────────────────────┐
│       SUPERVISOR AGENT              │   │      TEAM AGENTS          │
│    (Quality Assurance Layer)        │   │   (Execution Layer)       │
│                                     │   │                           │
│  - Task Verification                │   │  ┌─────────────────────┐  │
│  - Quality Gates                    │   │  │  ENGINEERING_TEAM   │  │
│  - Deliverable Inspection           │   │  │  (14 agents)        │  │
│  - Test Validation                  │   │  │  - cto              │  │
│  - Documentation Checks             │   │  │  - devops-engineer  │  │
│  - Security Scanning                │   │  │  - backend-architect│  │
│  - Git Commit Verification          │   │  │  - frontend-dev     │  │
│  - Comprehensive Reporting          │   │  │  - ... etc          │  │
└─────────────────────────────────────┘   │  └─────────────────────┘  │
                                          │                           │
                                          │  ┌─────────────────────┐  │
                                          │  │  MARKETING_TEAM     │  │
                                          │  │  (17 agents)        │  │
                                          │  │  - router-agent     │  │
                                          │  │  - copywriter       │  │
                                          │  │  - social-media-mgr │  │
                                          │  │  - ... etc          │  │
                                          │  └─────────────────────┘  │
                                          │                           │
                                          │  ┌─────────────────────┐  │
                                          │  │  QA_TEAM            │  │
                                          │  │  (5 agents)         │  │
                                          │  │  - test-orchestrator│  │
                                          │  │  - unit-test-agent  │  │
                                          │  │  - ... etc          │  │
                                          │  └─────────────────────┘  │
                                          └───────────────────────────┘
```

## File Structure

```
/home/user/TEST_AGENTS/
├── .claude/
│   ├── agents/
│   │   └── supervisor.md                    # Root-level supervisor agent definition
│   ├── tools/
│   │   ├── supervisor_tools.py              # Verification tools implementation
│   │   └── supervisor_mcp_server.py         # MCP server for supervisor tools
│   └── settings.json                        # Root workspace configuration
│
├── SUPERVISOR_VERIFICATION_CRITERIA.md      # Verification standards documentation
├── SUPERVISOR_ARCHITECTURE.md               # This file
├── MULTI_AGENT_GUIDE.md                     # Updated with supervisor info
│
├── ENGINEERING_TEAM/
│   └── .claude/agents/                      # 14 engineering agents
│
├── MARKETING_TEAM/
│   └── .claude/agents/                      # 17 marketing agents
│
└── QA_TEAM/
    └── .claude/agents/                      # 5 testing agents
```

## How It Works

### 1. Task Execution Flow

```
User Request → Team Agent(s) → Task Execution → Deliverables

Example:
"Build user authentication feature"
  ↓
ENGINEERING_TEAM/cto
  ↓
├─ backend-architect (creates auth endpoints)
├─ frontend-developer (creates login UI)
├─ test-engineer (creates tests)
└─ technical-writer (updates docs)
  ↓
Code, Tests, Docs committed to git
```

### 2. Verification Flow

```
User: "Use supervisor to verify authentication feature is complete"
  ↓
SUPERVISOR AGENT
  ↓
├─ validate_deliverables()
│    ├─ Check src/auth/routes.py exists
│    ├─ Check tests/test_auth.py exists
│    └─ Check docs/api.md updated
│
├─ check_git_changes()
│    ├─ Verify commits made
│    ├─ Check commit messages
│    └─ Ensure no secrets committed
│
├─ check_code_quality()
│    ├─ Syntax validation
│    ├─ Security scan (hardcoded secrets)
│    └─ Docstring presence
│
├─ run_verification_tests()
│    ├─ Execute test suite
│    ├─ Check all tests pass
│    └─ Verify coverage
│
├─ verify_documentation()
│    ├─ Check docs exist
│    └─ Verify required sections present
│
└─ generate_verification_report()
     ├─ Status: PASSED/FAILED/PARTIAL
     ├─ Quality Score: X/10
     ├─ Issues found: [...]
     ├─ Recommendations: [...]
     └─ Deployment ready: YES/NO
```

## Key Design Principles

### 1. Independence
- Supervisor is **separate** from team agents
- Does **not** participate in execution
- Performs **objective** verification after the fact
- Cannot be influenced by agents' self-assessment

### 2. Evidence-Based
- Uses **automated tools** to gather evidence
- Checks **actual files**, not reports
- Runs **real tests**, not test reports
- Scans **actual code**, not descriptions

### 3. Comprehensive
- Verifies **all aspects** of task completion:
  - Code implementation
  - Tests
  - Documentation
  - Security
  - Git commits
  - Quality standards

### 4. Actionable
- Provides **clear status** (PASSED/FAILED/PARTIAL)
- Lists **specific issues** found
- Offers **concrete recommendations**
- Gives **deployment readiness** assessment

### 5. Cross-Team
- Works across **all teams**:
  - ENGINEERING_TEAM
  - MARKETING_TEAM
  - QA_TEAM
  - USER_STORY_AGENT
- Understands **different verification criteria** for each team
- Adapts verification approach based on task type

## Verification Tools

### Core Tools

| Tool | Purpose | What It Checks |
|------|---------|----------------|
| `verify_task_completion()` | Main orchestrator | Coordinates all verification checks |
| `check_git_changes()` | Git verification | Commits, changed files, commit messages |
| `validate_deliverables()` | File existence | Expected files exist and are not empty |
| `run_verification_tests()` | Test execution | Tests run and pass |
| `check_code_quality()` | Static analysis | Syntax, security, docstrings |
| `verify_documentation()` | Documentation check | Docs exist with required sections |
| `generate_verification_report()` | Reporting | Comprehensive status report |

### Tool Integration

```python
# Tools are exposed via MCP (Model Context Protocol)
# Configuration in .claude/settings.json:

{
  "mcp": {
    "servers": {
      "supervisor-tools": {
        "command": "python3",
        "args": ["/home/user/TEST_AGENTS/.claude/tools/supervisor_mcp_server.py"]
      }
    }
  }
}
```

## Usage Patterns

### Pattern 1: Post-Development Verification

```
# After feature development
User: "Use supervisor to verify the payment processing feature"

Supervisor:
1. Checks code files exist
2. Verifies tests pass
3. Scans for security issues
4. Checks documentation
5. Reviews git commits
6. Returns PASSED/FAILED/PARTIAL
```

### Pattern 2: Pre-Deployment Gate

```
# Before deployment
User: "Use supervisor to verify everything is ready for production deployment"

Supervisor:
1. Comprehensive verification of all recent changes
2. Security audit
3. Test suite execution
4. Documentation completeness
5. Deployment readiness assessment
6. Returns GO/NO-GO recommendation
```

### Pattern 3: Bug Fix Validation

```
# After bug fix
User: "Use supervisor to verify the login timeout bug is fixed"

Supervisor:
1. Checks regression test exists
2. Verifies test would fail before fix
3. Confirms test passes after fix
4. Checks no side effects introduced
5. Verifies documentation updated
6. Returns verification status
```

### Pattern 4: Multi-Team Campaign Verification

```
# After marketing campaign creation
User: "Use supervisor to verify Q4 product launch campaign is ready"

Supervisor:
1. Checks all content deliverables (blog, social, email)
2. Verifies visual assets exist and optimized
3. Tests landing page works
4. Validates all links
5. Checks email templates render
6. Returns launch readiness
```

## Verification Criteria by Team

### ENGINEERING_TEAM

| Aspect | Criteria |
|--------|----------|
| Code | Syntax valid, no security issues, follows patterns |
| Tests | Exist, pass, >80% coverage |
| Docs | README, API docs, comments |
| Git | Clean commits, descriptive messages |
| Security | No secrets, input validation, secure patterns |

### MARKETING_TEAM

| Aspect | Criteria |
|--------|----------|
| Content | Grammar, brand voice, accuracy |
| SEO | Keywords, meta descriptions, headings |
| Assets | Images optimized, alt text, attribution |
| Distribution | Saved correctly, links work, published |
| Quality | Engaging, factually correct, on-brand |

### QA_TEAM

| Aspect | Criteria |
|--------|----------|
| Tests | Exist for all scenarios |
| Coverage | >80% code coverage |
| Quality | Clear, good assertions, isolated |
| Fixtures | Proper setup/teardown |
| Docs | Test purpose clear, how to run |

## Status Definitions

### ✅ PASSED (Score 8-10)
- All critical criteria met
- All tests pass
- Documentation complete
- No security issues
- Ready for deployment

**Example:**
```
VERIFICATION PASSED ✓
Quality Score: 9/10
Deployment Ready: YES
```

### ⚠️ PARTIAL (Score 5-7)
- Most criteria met
- Some minor issues
- Tests mostly pass
- Documentation adequate
- Needs minor fixes before deployment

**Example:**
```
VERIFICATION PARTIAL ⚠
Quality Score: 7/10
Deployment Ready: NO - Minor fixes needed
Issues: 2 minor, 0 critical
```

### ❌ FAILED (Score 0-4)
- Critical criteria not met
- Tests failing
- Security issues
- Documentation missing
- NOT ready for deployment

**Example:**
```
VERIFICATION FAILED ✗
Quality Score: 4/10
Deployment Ready: NO - Critical issues
Issues: 5 (2 critical, 3 minor)
```

## Integration with Existing Workflow

### Before Supervisor

```
User: "Build authentication feature"
  ↓
ENGINEERING_TEAM executes
  ↓
Agents report "Done!"
  ↓
User: "Is it really done?" ← No objective verification
```

### With Supervisor

```
User: "Build authentication feature"
  ↓
ENGINEERING_TEAM executes
  ↓
Agents report "Done!"
  ↓
User: "Use supervisor to verify it's done"
  ↓
SUPERVISOR performs independent verification
  ↓
Returns: PASSED ✓ (with evidence) or FAILED ✗ (with issues)
  ↓
User has confidence it's truly complete
```

## Benefits

### 1. Confidence
- **Know** work is complete, not just trust it
- **Evidence-based** verification
- **Objective** assessment

### 2. Quality
- **Enforces** standards across all teams
- **Catches** issues before deployment
- **Improves** overall code quality

### 3. Accountability
- **Clear** pass/fail criteria
- **Documented** issues and gaps
- **Transparent** verification process

### 4. Risk Reduction
- **Prevents** broken deployments
- **Identifies** security issues
- **Ensures** tests actually pass

### 5. Efficiency
- **Automated** verification
- **Consistent** standards
- **Faster** than manual review

## Best Practices

### For Users

1. **Verify significant work** - Use supervisor for important features
2. **Before deployment** - Always verify before production
3. **After bug fixes** - Confirm fixes are complete
4. **Multi-team tasks** - Verify coordination worked

### For Team Agents

1. **Self-check first** - Meet criteria before claiming "done"
2. **Write tests** - Makes verification automatic
3. **Document changes** - Makes verification easier
4. **Follow standards** - Pass verification first time

### For Supervisor

1. **Be objective** - Don't accept reports blindly
2. **Use automation** - Run tools, don't just read
3. **Be thorough** - Check all criteria
4. **Be clear** - Unambiguous status
5. **Be helpful** - Suggest fixes, not just criticize

## Automatic Triggering (NEW!) 🔥

The supervisor now features **hybrid automatic/manual verification** with two complementary approaches:

### Option 3: Agent Workflow Integration ✅ IMPLEMENTED

Team coordinator agents automatically invoke supervisor after completing significant tasks:

- **CTO Agent** (ENGINEERING_TEAM) - Auto-verifies features, bug fixes, deployments
- **Router Agent** (MARKETING_TEAM) - Auto-verifies campaigns, landing pages, client work
- **Test Orchestrator** (QA_TEAM) - Auto-verifies test suites, integration tests

**How it works:**
```
User: "Use cto to build authentication feature"
  ↓
CTO coordinates specialists
  ↓
All work complete
  ↓
CTO automatically: Task(supervisor): Verify authentication feature...
  ↓
Supervisor returns verification report
  ↓
User sees results with quality assurance ✅
```

### Option 4: Claude Code Hooks ✅ IMPLEMENTED

Hook script detects completion patterns and suggests verification:

- **File**: `.claude/hooks/supervisor-auto-trigger.sh`
- **Detects**: "All agents complete", "Task complete", "ready for production", etc.
- **Action**: Displays suggestion to run supervisor verification

**Setup Guide**: See `SUPERVISOR_AUTO_TRIGGER_SETUP.md` for full configuration instructions.

---

## Future Enhancements

### Potential Additions

1. **Historical Tracking**
   - Track quality scores over time
   - Identify problem areas
   - Team performance metrics

2. **Custom Criteria**
   - User-defined verification rules
   - Project-specific standards
   - Team-specific requirements

3. **Integration with CI/CD**
   - Run supervisor in GitHub Actions
   - Block merges if verification fails
   - Automated deployment gates

4. **Advanced Security Scanning**
   - Dependency vulnerability scanning
   - SAST/DAST integration
   - License compliance checking

## Conclusion

The Supervisor Agent provides a critical quality gate for the multi-agent system. By offering independent, evidence-based verification, it ensures that when agents say work is "done," it truly is complete, tested, documented, and ready for deployment.

**Location**: `/home/user/TEST_AGENTS/.claude/agents/supervisor.md`

**Tools**: `/home/user/TEST_AGENTS/.claude/tools/supervisor_tools.py`

**Documentation**: `/home/user/TEST_AGENTS/SUPERVISOR_VERIFICATION_CRITERIA.md`

**Usage**: `"Use supervisor to verify [task description]"`
