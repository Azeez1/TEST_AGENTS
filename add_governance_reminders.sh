#!/bin/bash

# Add governance reminder to all 37 agent definitions
# This prevents tool duplication by reminding agents to check TOOL_REGISTRY.md first

GOVERNANCE_SECTION='
## 🔧 Tool Governance (READ BEFORE CREATING TOOLS)

**CRITICAL: Check existing tools FIRST before creating new ones.**

Before creating any new tool, script, or workflow:
1. ☐ Check [TOOL_REGISTRY.md](../../../TOOL_REGISTRY.md) for existing solutions
2. ☐ Follow priority order: MCP → Skill → Custom Tool → New
3. ☐ If creating new tool: Document justification in [PRE_FLIGHT_CHECKS.md](../../../PRE_FLIGHT_CHECKS.md)

**This prevents tool duplication and ensures you use battle-tested code.**

---
'

# Function to add governance section if not already present
add_governance() {
    local file=$1

    # Check if governance section already exists
    if grep -q "## 🔧 Tool Governance" "$file"; then
        echo "✅ Governance already exists in $file"
        return
    fi

    # Add governance section after "Use Configured Capabilities" section
    # Find the line number of the capabilities section
    if grep -q "## ⚠️ CRITICAL: Use Configured Capabilities" "$file"; then
        # Add after this section (find the next ## heading and insert before it)
        awk -v section="$GOVERNANCE_SECTION" '
        /## ⚠️ CRITICAL: Use Configured Capabilities/ {
            in_section=1
            print
            next
        }
        in_section && /^## / && !/## ⚠️ CRITICAL/ {
            print section
            in_section=0
        }
        {print}
        ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"

        echo "✅ Added governance to $file"
    else
        echo "⚠️ Could not find insertion point in $file"
    fi
}

# Process all agents
echo "Adding governance reminders to all 37 agents..."
echo ""

# MARKETING_TEAM (17 agents)
echo "MARKETING_TEAM agents:"
for agent in MARKETING_TEAM/.claude/agents/*.md; do
    add_governance "$agent"
done
echo ""

# QA_TEAM (5 agents)
echo "QA_TEAM agents:"
for agent in QA_TEAM/.claude/agents/*.md; do
    add_governance "$agent"
done
echo ""

# ENGINEERING_TEAM (14 agents)
echo "ENGINEERING_TEAM agents:"
for agent in ENGINEERING_TEAM/.claude/agents/*.md; do
    add_governance "$agent"
done
echo ""

# Supervisor agent (1 agent)
if [ -f ".claude/agents/supervisor.md" ]; then
    echo "Root supervisor agent:"
    add_governance ".claude/agents/supervisor.md"
fi

echo ""
echo "✅ Governance reminders added to all 37 agents!"
