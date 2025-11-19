# Knowledge Sync

Intelligent documentation maintenance and knowledge base synchronization.

## What This Does

Automatically updates and maintains workspace documentation including:
1. Agent documentation (definitions, capabilities, examples)
2. Command documentation (usage, workflows, examples)
3. Tool registry (inventory, versions, dependencies)
4. Architecture documentation (system design, diagrams)
5. Best practices and guidelines
6. Cross-references and links validation
7. Changelog and version tracking

## Usage

```
/knowledge-sync [scope] [action]
```

## Examples

```
/knowledge-sync "full" "update-all"
/knowledge-sync "agents-only" "regenerate"
/knowledge-sync "commands" "validate-links"
/knowledge-sync "quick" "check-outdated"
```

## Scope Options

- **full** - Complete documentation sync (all components)
- **quick** - Fast check for critical issues only
- **agents-only** - Only agent documentation
- **commands-only** - Only command documentation
- **tools-only** - Only tool registry and tool docs
- **architecture** - Only architecture and design docs

## Actions

- **update-all** - Update all documentation (default)
- **regenerate** - Regenerate from source files
- **validate-links** - Check all cross-references
- **check-outdated** - Find outdated documentation
- **fix-formatting** - Fix markdown formatting issues
- **generate-index** - Create documentation indexes

---

## Process

### 1. Discovery & Inventory

**Scan workspace for:**
- All agent definition files (*.md in .claude/agents/)
- All command files (*.md in .claude/commands/)
- All tool files (*.py in .claude/tools/)
- All MCP server configurations
- All markdown documentation files
- README files across all directories

**Create inventory:**
- Total count of each type
- Last modified timestamps
- File sizes and complexity
- Version information (if available)

### 2. Agent Documentation Sync

**For each agent:**
- Extract metadata from YAML frontmatter
  - Name, description, model
  - Tools and skills declared
  - Dependencies
- Validate agent file structure
- Check for required sections:
  - Description/Purpose
  - Capabilities
  - Tools used
  - Example invocations
  - Related agents
- Update agent registry/index
- Generate agent capability matrix

**Example agent capability matrix:**
```markdown
| Agent | Team | Primary Use | Tools | Complexity |
|-------|------|-------------|-------|------------|
| cto | Engineering | Coordination | 15+ | High |
| debugger | Engineering | Troubleshooting | 8 | Medium |
| router-agent | Marketing | Campaign coordination | 12+ | High |
```

### 3. Command Documentation Sync

**For each command:**
- Validate markdown structure
- Check required sections:
  - Title and description
  - Usage syntax
  - Examples (at least 2)
  - Process/workflow
  - Deliverables
  - Time estimate
  - Related commands
- Verify agent references are valid
- Update command index
- Check time estimates are realistic

**Generate command reference guide:**
```markdown
# Quick Reference: All Commands

## Engineering Commands (9)
- /ship-feature - Complete feature delivery
- /debug-issue - Troubleshooting and fixes
- /code-review - Multi-perspective review
...

## Marketing Commands (8)
- /launch-campaign - Full marketing campaign
- /content-suite - Content package
...

## Cross-Team Commands (3)
- /product-launch - Full product launch
- /quarterly-planning - Strategic planning
...
```

### 4. Tool Registry Sync

**Update TOOL_REGISTRY.md:**
- Scan all tool files for @tool decorators
- Extract tool metadata:
  - Tool name and description
  - Parameters and return types
  - Dependencies
  - Version (if specified)
  - Last modified date
- Check for:
  - Orphaned tools (not used by any agent)
  - Undocumented tools
  - Deprecated tools
  - Tool conflicts (duplicate names)
- Generate usage statistics
- Update tool dependency graph

**Example tool registry entry:**
```markdown
### verify_task_completion
- **File:** supervisor_tools.py
- **Description:** Main orchestrator for supervisor verification
- **Used by:** supervisor agent
- **Dependencies:** check_git_changes, validate_deliverables, run_verification_tests
- **Last updated:** 2025-01-15
- **Status:** Active
```

### 5. Architecture Documentation

**Update or create:**
- System architecture diagram
- Agent interaction flowcharts
- Team structure diagrams
- Workflow diagrams (for major commands)
- Dependency graphs
- Integration diagrams (MCP servers, external APIs)

**Tools used:**
- Mermaid for diagrams
- GraphViz for dependency graphs
- Manual markdown for descriptions

### 6. Link Validation

**Check all documentation for:**
- Broken internal links (to files, agents, commands)
- Broken external links (URLs)
- Missing referenced files
- Circular references
- Outdated paths

**Fix automatically:**
- Update file paths that moved
- Fix broken relative links
- Remove or update dead external links
- Add missing cross-references

### 7. Formatting & Consistency

**Standardize:**
- Markdown formatting (headers, lists, code blocks)
- Naming conventions (file names, agent names)
- Section ordering (consistent structure)
- Code examples (syntax highlighting)
- Table formatting
- Emoji usage (if policy defined)

**Apply style guide:**
- Header levels (# for main title, ## for sections)
- Code block language tags
- List formatting (- vs *)
- Line length limits
- Blank line usage

### 8. Changelog Generation

**Create or update CHANGELOG.md:**
- Recent changes (last 30 days)
- New agents added
- New commands added
- New tools registered
- Breaking changes
- Deprecations
- Bug fixes in documentation

**Format:**
```markdown
## [2025-01-19]

### Added
- New command: /quarterly-planning for strategic planning
- New command: /financial-analysis for Financial team
- New hook: team-collaboration-detector.sh
- Enhanced supervisor-auto-trigger.sh with confidence scoring

### Updated
- TOOL_REGISTRY.md: 5 new tools added
- Agent count: 58 agents across 6 teams

### Fixed
- Broken links in MULTI_AGENT_GUIDE.md
- Formatting issues in 3 command files
```

### 9. Version Tracking

**Update version information in:**
- Main README.md
- Package metadata (if applicable)
- Documentation header files
- Agent version compatibility

**Track:**
- Documentation version
- Last sync timestamp
- Changes since last sync
- Compatibility notes

### 10. Index Generation

**Create comprehensive indexes:**

**Agent Index (agents-index.md):**
```markdown
# Agent Index

## By Team
- [Engineering Team](#engineering-team) (15 agents)
- [Marketing Team](#marketing-team) (18 agents)
...

## By Capability
- **Coordination:** cto, router-agent, sales-manager, cfo-agent
- **Content Creation:** copywriter, technical-writer, proposal-specialist
...

## Alphabetical
- [account-executive](#account-executive)
- [accountant](#accountant)
...
```

**Command Index (commands-index.md):**
- By team
- By complexity (simple, moderate, complex)
- By time estimate
- Alphabetical

**Tool Index (within TOOL_REGISTRY.md):**
- By category
- By team
- By usage frequency
- Alphabetical

---

## Deliverables

### Updated Documentation Files
- **agents-index.md** - Complete agent reference
- **commands-index.md** - Complete command reference
- **TOOL_REGISTRY.md** - Updated tool inventory
- **CHANGELOG.md** - Recent changes log
- **architecture-overview.md** - System architecture
- **workflow-diagrams/** - Visual workflow diagrams

### Validation Reports
- **broken-links-report.txt** - All broken links found
- **outdated-docs-report.txt** - Documentation needing updates
- **orphaned-tools-report.txt** - Unused tools
- **consistency-issues-report.txt** - Formatting problems

### Statistics
- **documentation-stats.json** - Metrics and counts
  ```json
  {
    "agents": 58,
    "commands": 27,
    "tools": 20,
    "mcp_servers": 7,
    "total_docs": 145,
    "last_sync": "2025-01-19T10:30:00Z",
    "broken_links": 0,
    "outdated_docs": 3
  }
  ```

### Diagrams
- **agent-dependency-graph.mmd** - Mermaid diagram
- **team-structure.mmd** - Team organization
- **workflow-diagrams/*.mmd** - Command workflows

---

## Auto-Fix Capabilities

The knowledge sync can automatically fix:
- ✅ Broken internal links (if target exists)
- ✅ Outdated file paths
- ✅ Markdown formatting issues
- ✅ Missing required sections (adds templates)
- ✅ Inconsistent naming
- ✅ Table formatting
- ✅ Code block syntax highlighting
- ⚠️  Broken external links (flags for manual review)
- ⚠️  Content accuracy (flags for review)

---

## Smart Features

### Intelligent Updates

**Detects:**
- New agents added (auto-documents with template)
- Commands modified (updates timestamps)
- Tools added/removed (updates registry)
- Architecture changes (flags for diagram update)

**Suggests:**
- Missing documentation sections
- Related commands to cross-reference
- Similar agents for "See also" sections
- Documentation improvements

### Conflict Resolution

If multiple versions exist:
- Compares timestamps
- Checks git history
- Identifies canonical version
- Merges or flags for manual review

### Template Generation

For new agents/commands without docs:
- Generates documentation template
- Includes all required sections
- Pre-fills known metadata
- Flags for human completion

---

## Time Estimate

- **Quick check:** 30 seconds - 1 minute
- **Agents-only sync:** 2-3 minutes
- **Commands-only sync:** 2-3 minutes
- **Full sync with validation:** 5-10 minutes
- **Full sync with diagrams:** 10-15 minutes

---

## Best Practices

1. **Run weekly** - Keep documentation fresh
2. **Run after major changes** - New agents, commands, or tools
3. **Review auto-fixes** - Verify changes make sense
4. **Update manually** - Complex architecture changes
5. **Version control** - Commit documentation updates
6. **Notify team** - Share documentation changes

---

## Related Commands

- `/agent-health` - Check agent operational status
- `/agent-suggest` - Discover agents for tasks

---

## Configuration

Edit `.claude/knowledge-sync-config.json` to customize:
```json
{
  "auto_fix_links": true,
  "auto_fix_formatting": true,
  "generate_diagrams": true,
  "check_external_links": false,
  "max_outdated_days": 90,
  "exclude_paths": [
    "node_modules/",
    ".git/",
    "temp/"
  ]
}
```

---

## Example Output

```bash
🔄 Running Knowledge Sync (full update)...

[1/10] Discovering documentation...
  ✓ Found 58 agent files
  ✓ Found 27 command files
  ✓ Found 20 tool files
  ✓ Found 87 markdown docs

[2/10] Syncing agent documentation...
  ✓ Updated 58 agent entries
  ✓ Generated agent capability matrix
  ⚠️  3 agents missing examples (flagged)

[3/10] Syncing command documentation...
  ✓ Updated 27 command entries
  ✓ Validated all command structures
  ✅ Fixed 2 broken internal links

[4/10] Updating tool registry...
  ✓ Registered 20 tools
  ⚠️  Found 2 orphaned tools (unused)
  ✓ Generated dependency graph

[5/10] Validating links...
  ✓ Checked 234 internal links (2 fixed)
  ⚠️  Skipped external link check (disabled)

[6/10] Fixing formatting issues...
  ✓ Fixed 5 markdown formatting issues
  ✓ Standardized 12 code blocks

[7/10] Generating indexes...
  ✓ Created agents-index.md
  ✓ Created commands-index.md
  ✓ Updated TOOL_REGISTRY.md

[8/10] Creating diagrams...
  ✓ Generated agent-dependency-graph.mmd
  ✓ Generated team-structure.mmd

[9/10] Updating changelog...
  ✓ Added 8 new entries to CHANGELOG.md

[10/10] Generating reports...
  ✓ Created documentation-stats.json
  ⚠️  Created outdated-docs-report.txt (3 files)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ KNOWLEDGE SYNC COMPLETE

Summary:
  • 58 agents documented
  • 27 commands documented
  • 20 tools registered
  • 2 links fixed
  • 5 formatting issues fixed
  • 3 warnings (see reports)

Warnings:
  1. 3 agents missing usage examples
  2. 2 tools are orphaned (not used)
  3. 3 docs outdated (>90 days old)

Next Steps:
  1. Review: outdated-docs-report.txt
  2. Add examples to flagged agents
  3. Consider removing orphaned tools

Files updated: 15 files modified
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Notes

- Safe to run anytime (non-destructive)
- Creates backups before major changes
- Can run in dry-run mode (preview only)
- Integrates with git (respects .gitignore)
- Supports incremental updates (only changed files)
- Can be scheduled (cron job for automatic syncing)
