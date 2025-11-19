# Agent Health Check

Comprehensive workspace health check for all agents, tools, MCP servers, and configuration.

## What This Does

Performs a complete diagnostic scan of the multi-agent workspace including:
1. Agent definition validation (all teams)
2. Tool registration and availability checks
3. MCP server connectivity verification
4. Configuration file validation
5. Dependency and permission checks
6. Performance and resource analysis
7. Documentation completeness audit

## Usage

```
/agent-health [scope] [options]
```

## Examples

```
/agent-health "full" "generate-report"
/agent-health "quick" "agents-only"
/agent-health "team:ENGINEERING_TEAM" "verbose"
/agent-health "critical" "fix-issues"
```

## Scope Options

- **full** - Complete health check (all components)
- **quick** - Fast check (agents and critical configs only)
- **agents-only** - Only validate agent definitions
- **tools-only** - Only check tools and MCP servers
- **team:TEAM_NAME** - Check specific team only
- **critical** - Check critical components only

## Process

This command runs diagnostic checks across all workspace components:

### 1. Agent Definition Validation

**Check each agent file (.md) for:**
- Valid YAML frontmatter format
- Required fields (name, description, model)
- Tool declarations are valid
- Skill declarations exist
- Agent file permissions
- Syntax and formatting issues

**Teams checked:**
- ROOT (supervisor)
- ENGINEERING_TEAM (15 agents)
- MARKETING_TEAM (18 agents)
- QA_TEAM (5 agents)
- FINANCIAL_TEAM (10 agents)
- SALES_TEAM (8 agents)

**Report includes:**
- Total agents: 58
- Agents with issues
- Missing required fields
- Invalid tool references
- Orphaned or unused agents

### 2. Tool Registration Check

**Verify all custom tools:**
- Tool files exist and are executable
- Python syntax validation
- Tool decorators properly configured
- Tool imports are valid
- Tool permissions are correct

**Tool locations:**
- `/home/user/TEST_AGENTS/.claude/tools/` (root-level)
- `TEAM_NAME/.claude/tools/` (team-specific)

**Check against TOOL_REGISTRY.md:**
- All registered tools exist
- No unregistered tools in use
- Tool versions match documentation
- Dependencies are installed

### 3. MCP Server Connectivity

**Test each MCP server:**
- Server process is running (if applicable)
- Connection endpoints are reachable
- Authentication is configured
- Response time is acceptable
- Error rates are normal

**MCP servers checked:**
- Google Workspace MCP
- Perplexity MCP
- Bright Data MCP
- n8n MCP
- Supervisor MCP
- Sequential Thinking MCP
- Others as configured

**Report includes:**
- Server status (UP/DOWN/DEGRADED)
- Response times
- Last successful connection
- Error logs (if any)

### 4. Configuration Validation

**Check configuration files:**
- `settings.json` - Valid JSON format
- Required settings present
- Workspace paths are valid
- Permissions are correct
- Environment variables set

**Validate:**
- `.gitignore` includes sensitive files
- Git configuration is correct
- Branch naming conventions
- Hook configurations

### 5. Dependency Check

**Verify required dependencies:**
- Python packages (requirements.txt)
- Node packages (package.json)
- System dependencies
- API credentials available
- File permissions

**Check for:**
- Missing dependencies
- Version conflicts
- Security vulnerabilities
- Deprecated packages

### 6. Performance Analysis

**Measure workspace metrics:**
- Agent invocation counts
- Average response times
- Token usage patterns
- Error rates by agent
- Resource utilization

**Identify:**
- Slow-performing agents
- High-token-usage agents
- Frequently failing agents
- Unused agents (0 invocations)

### 7. Documentation Audit

**Check documentation completeness:**
- Each agent has .md definition
- Commands have documentation
- Tools have docstrings
- TOOL_REGISTRY.md is up-to-date
- Cross-references are valid

**Validate:**
- Links are not broken
- Examples are current
- Version numbers match
- Contact info is correct

## Deliverables

### Standard Report (Quick Mode)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 AGENT WORKSPACE HEALTH REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ AGENTS: 58/58 healthy
✅ TOOLS: 20/20 registered
⚠️  MCP SERVERS: 6/7 healthy (1 degraded)
✅ CONFIGURATION: Valid
⚠️  DEPENDENCIES: 2 warnings
✅ DOCUMENTATION: Complete

Overall Status: HEALTHY (minor warnings)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Detailed Report (Full Mode)
- Complete diagnostic report (markdown)
- Health score by component (0-10)
- Detailed issue list with remediation steps
- Performance metrics and trends
- Recommended optimizations
- Action items with priorities

### Generated Files
- `workspace-health-report.md` - Full diagnostic report
- `agent-inventory.json` - Machine-readable agent registry
- `performance-metrics.json` - Performance data
- `issues-found.txt` - List of issues (if any)
- `remediation-plan.md` - Step-by-step fixes

## Auto-Fix Capability

When run with `fix-issues` option:
- Automatically fixes common issues
- Repairs file permissions
- Updates documentation references
- Regenerates configuration files
- Installs missing dependencies
- Restarts MCP servers

**Note:** Critical issues require manual intervention

## Time Estimate

- **Quick check:** 30 seconds - 1 minute
- **Full diagnostic:** 2-4 minutes
- **With auto-fix:** 5-10 minutes (depends on issues)

## Related Commands

- `/workspace-audit` - Similar but focuses on structure
- `/cleanup-workspace` - Removes unused files
- `/knowledge-sync` - Updates documentation

## Example Output

```bash
🏥 Running Agent Health Check (full diagnostic)...

[1/7] Validating agent definitions...
  ✅ ROOT: supervisor (healthy)
  ✅ ENGINEERING_TEAM: 15 agents (all healthy)
  ✅ MARKETING_TEAM: 18 agents (all healthy)
  ✅ QA_TEAM: 5 agents (all healthy)
  ✅ FINANCIAL_TEAM: 10 agents (all healthy)
  ✅ SALES_TEAM: 8 agents (all healthy)

[2/7] Checking tool registration...
  ✅ 20 custom tools registered
  ✅ All tools have valid syntax
  ⚠️  Warning: path_validator.py not used in 30 days

[3/7] Testing MCP server connectivity...
  ✅ Google Workspace MCP (42ms response)
  ✅ Perplexity MCP (89ms response)
  ⚠️  Bright Data MCP (SLOW: 1200ms response)
  ✅ n8n MCP (35ms response)
  ✅ Supervisor MCP (28ms response)
  ❌ Sequential Thinking MCP (CONNECTION FAILED)

[4/7] Validating configuration...
  ✅ settings.json valid
  ✅ Git configuration correct
  ✅ Environment variables set

[5/7] Checking dependencies...
  ✅ Python packages installed
  ⚠️  2 packages have updates available
  ✅ System dependencies met

[6/7] Analyzing performance...
  📊 Most used agents: cto (142×), router-agent (98×)
  📊 Avg response time: 3.2s
  📊 Total token usage: 2.4M tokens (last 30 days)

[7/7] Auditing documentation...
  ✅ All agents documented
  ✅ All commands documented
  ✅ Tool registry up-to-date

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL HEALTH: 8.5/10 (GOOD)

Issues Found: 3 warnings, 1 error
Priority Actions:
  1. [HIGH] Fix Sequential Thinking MCP connection
  2. [MEDIUM] Optimize Bright Data MCP response time
  3. [LOW] Update 2 Python packages
  4. [LOW] Review unused path_validator.py tool

Full report saved to: workspace-health-report.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Best Practices

- Run `/agent-health quick` daily for monitoring
- Run `/agent-health full` weekly for comprehensive audit
- Run `/agent-health` after adding new agents or tools
- Use `/agent-health fix-issues` to auto-remediate common problems
- Review performance metrics monthly to optimize workflows
