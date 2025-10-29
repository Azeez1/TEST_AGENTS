# Supervisor Auto-Trigger Setup Guide

## Overview

You've enabled **hybrid automatic/manual supervisor verification** with two complementary approaches:

### Option 3: Agent Workflow Integration ✅
Team coordinator agents automatically invoke supervisor after completing significant tasks.

### Option 4: Claude Code Hooks ✅
Hooks detect completion patterns and suggest supervisor verification.

---

## What Was Configured

### 1. Agent Workflow Integration (Option 3)

The following coordinator agents now automatically invoke the supervisor:

#### CTO Agent (ENGINEERING_TEAM)
- **File**: `ENGINEERING_TEAM/.claude/agents/cto.md`
- **Triggers on**:
  - Feature development
  - Bug fixes
  - Infrastructure changes
  - Multi-agent workflows (3+ specialists)
  - Security changes
  - API changes
  - Production deployments

#### Router Agent (MARKETING_TEAM)
- **File**: `MARKETING_TEAM/.claude/agents/router-agent.md`
- **Triggers on**:
  - Full campaigns
  - Landing pages
  - Email campaigns
  - Content series
  - Product launches
  - Major announcements
  - Client deliverables

#### Test Orchestrator (QA_TEAM)
- **File**: `QA_TEAM/.claude/agents/test-orchestrator.md`
- **Triggers on**:
  - Full test suite generation
  - Integration test suites
  - Critical path testing
  - Test suite refactoring
  - Pre-production test validation

### 2. Claude Code Hooks (Option 4)

#### Hook Script
- **File**: `.claude/hooks/supervisor-auto-trigger.sh`
- **Purpose**: Detects completion patterns in agent responses
- **Action**: Displays suggestion to run supervisor verification

#### Detection Patterns
The hook looks for these completion signals:
- "All agents have completed"
- "Task complete"
- "Feature implemented"
- "Campaign ready"
- "Tests generated"
- "Deployment complete"
- "✅.*complete"
- "ready for production"
- "ready for deployment"

And these team indicators:
- ENGINEERING_TEAM
- MARKETING_TEAM
- QA_TEAM

---

## How It Works

### Scenario 1: Using Team Coordinators (Automatic)

```bash
You: "Use cto to build user authentication feature"

CTO Agent:
1. Delegates to specialists (backend, frontend, tests, security)
2. All specialists complete their work
3. 🔍 Automatically invokes supervisor
4. Supervisor verifies and returns status
5. CTO presents results with verification report
```

**Result**: Fully automatic verification, no action needed from you.

### Scenario 2: Direct Agent Use (Hook Suggestion)

```bash
You: "Use copywriter to write a blog post"

Copywriter:
1. Writes blog post
2. Editor reviews and approves
3. Returns completed blog post

Hook detects completion and suggests:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SUPERVISOR VERIFICATION SUGGESTED

Consider running:
  "Use supervisor to verify this work is complete"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You: "Use supervisor to verify the blog post is ready for publication"
```

**Result**: Hook reminds you to verify, you manually trigger supervisor.

### Scenario 3: Manual Verification Anytime

```bash
You: "Use supervisor to verify the authentication feature"

Supervisor:
1. Checks code, tests, docs, git, security
2. Returns verification report
3. Status: PASSED ✅ / PARTIAL ⚠️ / FAILED ✗
```

**Result**: You can always manually invoke supervisor when needed.

---

## Activating the Hooks

### Method 1: Claude Code Settings (Recommended)

If Claude Code supports hooks configuration, add to `.claude/settings.json`:

```json
{
  "hooks": {
    "post_response": [
      ".claude/hooks/supervisor-auto-trigger.sh"
    ]
  }
}
```

### Method 2: User Profile Hooks

If your Claude Code installation uses user-level hooks, add to `~/.claude/hooks.json`:

```json
{
  "post_response": {
    "enabled": true,
    "scripts": [
      "/home/user/TEST_AGENTS/.claude/hooks/supervisor-auto-trigger.sh"
    ]
  }
}
```

### Method 3: Manual Execution

Run the hook manually after agent responses:

```bash
# Save agent response to file
echo "$AGENT_RESPONSE" > /tmp/claude_last_response.txt

# Run hook
./.claude/hooks/supervisor-auto-trigger.sh
```

### Method 4: Shell Integration

Add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
# Claude Code Supervisor Hook
export CLAUDE_HOOKS_DIR="/home/user/TEST_AGENTS/.claude/hooks"
alias claude-check='$CLAUDE_HOOKS_DIR/supervisor-auto-trigger.sh'
```

Then run `claude-check` after agent responses to check if verification is suggested.

---

## Configuration Options

### Customize Detection Patterns

Edit `.claude/hooks/supervisor-auto-trigger.sh` to add/remove patterns:

```bash
TRIGGER_PATTERNS=(
    "All agents have completed"
    "Task complete"
    "Your custom pattern here"
)
```

### Disable Auto-Trigger for Specific Agents

If you want an agent to skip auto-verification, add this to their definition:

```markdown
### When to Skip Auto-Verification

Skip supervisor for:
- All tasks (this agent doesn't need verification)
```

### Adjust Verification Threshold

Edit coordinator agents to change when they auto-verify:

In `cto.md`, `router-agent.md`, or `test-orchestrator.md`:

```markdown
### When to Auto-Invoke Supervisor

Automatically use the supervisor agent when you've completed:
1. [Add or remove criteria here]
```

---

## Testing the Setup

### Test 1: CTO Auto-Verification

```bash
You: "Use cto to implement a simple hello world API endpoint"

Expected:
- CTO delegates to backend-architect
- Backend creates endpoint
- CTO automatically invokes supervisor
- Supervisor verifies code, tests, docs
- You see verification report
```

### Test 2: Router-Agent Auto-Verification

```bash
You: "Use router-agent to create a complete product launch campaign"

Expected:
- Router coordinates multiple content agents
- All content created and editor-reviewed
- Router automatically invokes supervisor
- Supervisor verifies all deliverables
- You see verification report
```

### Test 3: Hook Detection

```bash
You: "Use copywriter to write a blog post about AI"

Expected:
- Copywriter writes post
- Editor reviews
- Hook detects "complete" pattern
- Hook suggests supervisor verification
```

### Test 4: Manual Verification

```bash
You: "Use supervisor to verify the blog post is publication-ready"

Expected:
- Supervisor checks content quality
- Returns verification report
- Status, quality score, issues, recommendations
```

---

## Verification Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│        Coordinator Agent (CTO/Router/Test-Orch)             │
│                                                             │
│  1. Analyzes request                                        │
│  2. Delegates to specialists                                │
│  3. Coordinates execution                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Specialist Agents Execute                      │
│                                                             │
│  - Backend, Frontend, Tests, Docs (Engineering)             │
│  - Copywriter, Designer, Email (Marketing)                  │
│  - Unit, Integration, Edge Case Tests (QA)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │  Work Complete?  │
                   └──────────────────┘
                     │              │
         ┌───────────┘              └───────────┐
         │ Significant               │ Minor     │
         │ Work                      │ Work      │
         ▼                           ▼           │
┌──────────────────────┐    ┌─────────────────────────────────┐
│   AUTO-TRIGGER       │    │   HOOK SUGGESTION               │
│   Supervisor         │    │   (Optional verification)       │
│                      │    │                                 │
│ Coordinator calls:   │    │ Hook detects completion:        │
│ Task(supervisor)     │    │ "🔍 Verification suggested"     │
└──────────────────────┘    └─────────────────────────────────┘
         │                           │
         │                           │ (User decides)
         │                           │
         └───────────┬───────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUPERVISOR AGENT                          │
│                                                             │
│  1. validate_deliverables()                                 │
│  2. check_git_changes()                                     │
│  3. check_code_quality()                                    │
│  4. run_verification_tests()                                │
│  5. verify_documentation()                                  │
│  6. generate_verification_report()                          │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              VERIFICATION REPORT                            │
│                                                             │
│  Status: PASSED ✅ / PARTIAL ⚠️ / FAILED ✗                  │
│  Quality Score: X/10                                        │
│  Issues: [list]                                             │
│  Recommendations: [list]                                    │
│  Deployment Ready: YES/NO                                   │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────┐
         │  Status: PASSED?  │
         └──────────────────┘
           │              │
     ┌─────┘              └─────┐
     │ YES                    NO │
     ▼                           ▼
┌──────────┐          ┌────────────────────┐
│ DELIVER  │          │ FIX ISSUES         │
│ TO USER  │          │ RE-RUN SUPERVISOR  │
└──────────┘          └────────────────────┘
```

---

## When Auto-Verification Triggers

### CTO (ENGINEERING_TEAM)

| Task Type | Auto-Verify? |
|-----------|--------------|
| Complete feature (code + tests + docs) | ✅ YES |
| Bug fix with regression test | ✅ YES |
| Infrastructure/DevOps changes | ✅ YES |
| Multi-agent workflows (3+ specialists) | ✅ YES |
| Security or auth changes | ✅ YES |
| API endpoint changes | ✅ YES |
| Production deployments | ✅ YES |
| Simple code exploration | ❌ NO |
| Documentation-only changes | ❌ NO |
| Quick prototypes | ❌ NO |

### Router-Agent (MARKETING_TEAM)

| Task Type | Auto-Verify? |
|-----------|--------------|
| Full campaign (blog + social + email) | ✅ YES |
| Complete landing page | ✅ YES |
| Multi-email campaign | ✅ YES |
| Product launch content | ✅ YES |
| Major announcements | ✅ YES |
| Client deliverables | ✅ YES |
| Single social post | ❌ NO |
| Quick research | ❌ NO |
| Draft content | ❌ NO |

### Test-Orchestrator (QA_TEAM)

| Task Type | Auto-Verify? |
|-----------|--------------|
| Full test suite for module/project | ✅ YES |
| Integration test suites | ✅ YES |
| Critical path testing | ✅ YES |
| Test suite refactoring | ✅ YES |
| Pre-production validation | ✅ YES |
| Single function test | ❌ NO |
| Experimental tests | ❌ NO |
| Debugging tests | ❌ NO |

---

## Troubleshooting

### Hook Not Running

**Problem**: Hook doesn't detect completions

**Solutions**:
1. Check hook is executable: `ls -l .claude/hooks/supervisor-auto-trigger.sh`
2. Run manually: `./.claude/hooks/supervisor-auto-trigger.sh`
3. Check Claude Code supports hooks (version-dependent)
4. Verify hook configuration in settings

### Supervisor Not Auto-Triggered

**Problem**: CTO/Router doesn't invoke supervisor automatically

**Solutions**:
1. Check you're using the updated agent definitions
2. Verify task complexity meets auto-trigger threshold
3. Check agent instructions include supervisor section
4. Re-read agent definition: `cat ENGINEERING_TEAM/.claude/agents/cto.md`

### Too Many Verifications

**Problem**: Supervisor runs too frequently

**Solutions**:
1. Adjust auto-trigger criteria in agent definitions
2. Add exclusions to hook patterns
3. Use manual verification instead: disable auto-trigger
4. Increase complexity threshold for auto-verification

### Hook False Positives

**Problem**: Hook suggests verification when not needed

**Solutions**:
1. Refine detection patterns in hook script
2. Add exclusion patterns for common false positives
3. Adjust team detection logic
4. Disable hook and rely only on agent workflow integration

---

## Best Practices

### 1. Trust Auto-Verification for Critical Work
- Let CTO auto-verify features and deployments
- Let Router auto-verify campaigns
- Let Test-Orchestrator auto-verify test suites

### 2. Manual Verification for Quick Tasks
- Single social posts
- Quick bug fixes
- Exploratory work

### 3. Always Verify Before Production
- Even for small changes, verify before deployment
- Use: "Use supervisor to verify this is production-ready"

### 4. Review Verification Reports
- Don't just see PASSED ✅ and move on
- Read the quality score and recommendations
- Fix issues even if status is PARTIAL ⚠️

### 5. Iterate on Failures
- If supervisor returns FAILED ❌, fix issues immediately
- Don't deploy until verification passes
- Use recommendations to improve quality

---

## Summary

You now have **two layers of automatic quality assurance**:

1. **Agent Workflow Integration** - Coordinators automatically verify significant work
2. **Hook Detection** - CLI suggests verification when patterns detected

This hybrid approach ensures:
- ✅ Critical work is always verified
- ✅ Quick tasks don't slow you down
- ✅ You're reminded when verification would be helpful
- ✅ You can always manually verify anytime

**The supervisor is now an active part of your workflow, not just a tool you remember to use sometimes.**

---

## Files Created/Modified

### New Files
- `.claude/hooks/supervisor-auto-trigger.sh` - Hook script
- `SUPERVISOR_AUTO_TRIGGER_SETUP.md` - This guide

### Modified Files
- `ENGINEERING_TEAM/.claude/agents/cto.md` - Added auto-verification
- `MARKETING_TEAM/.claude/agents/router-agent.md` - Added auto-verification
- `QA_TEAM/.claude/agents/test-orchestrator.md` - Added auto-verification

### Configuration
- `.claude/settings.json` - May need hook configuration (version-dependent)

---

## Next Steps

1. **Test the setup** - Try the test scenarios above
2. **Adjust thresholds** - Fine-tune when auto-verification triggers
3. **Monitor effectiveness** - Track how often verification catches issues
4. **Iterate** - Adjust patterns and criteria based on your workflow

**Ready to use!** Your supervisor agent now automatically verifies significant work across all teams. 🚀
