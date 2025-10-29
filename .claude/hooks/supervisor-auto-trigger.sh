#!/bin/bash
#
# Supervisor Auto-Trigger Hook
# Detects when significant work is completed and suggests supervisor verification
#
# This hook runs after Claude Code generates responses to check if supervisor
# verification should be triggered automatically.

# Configuration
TRIGGER_PATTERNS=(
    "All agents have completed"
    "Task complete"
    "Feature implemented"
    "Campaign ready"
    "Tests generated"
    "Deployment complete"
    "All specialists complete"
    "Implementation finished"
    "✅.*complete"
    "ready for production"
    "ready for deployment"
    "ready to deploy"
)

TEAM_PATTERNS=(
    "ENGINEERING_TEAM"
    "MARKETING_TEAM"
    "QA_TEAM"
)

# Check if we're in a completion context
check_completion_context() {
    local message="$1"

    for pattern in "${TRIGGER_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0  # Found completion pattern
        fi
    done

    return 1  # No completion pattern found
}

# Check if a team was involved
check_team_involvement() {
    local message="$1"

    for team in "${TEAM_PATTERNS[@]}"; do
        if echo "$message" | grep "$team" > /dev/null 2>&1; then
            return 0  # Found team involvement
        fi
    done

    return 1  # No team found
}

# Main logic
main() {
    # Read the assistant's response from stdin or environment
    local response="${CLAUDE_RESPONSE:-}"

    # If no response provided, read from file if available
    if [ -z "$response" ] && [ -f "/tmp/claude_last_response.txt" ]; then
        response=$(cat /tmp/claude_last_response.txt)
    fi

    # Check if this looks like a completion
    if check_completion_context "$response"; then
        # Check if a team was involved
        if check_team_involvement "$response"; then
            # Output suggestion for supervisor verification
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🔍 SUPERVISOR VERIFICATION SUGGESTED"
            echo ""
            echo "It looks like significant work was just completed."
            echo ""
            echo "Consider running:"
            echo "  \"Use supervisor to verify this work is complete\""
            echo ""
            echo "Or wait for automatic verification if using CTO/router-agent."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
        fi
    fi
}

main "$@"
