#!/bin/bash
#
# Supervisor Auto-Trigger Hook (Enhanced with Confidence Scoring)
# Detects when significant work is completed and suggests supervisor verification
# with confidence scoring and intelligent recommendations
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

# Additional patterns for confidence scoring
HIGH_CONFIDENCE_PATTERNS=(
    "All tests passing"
    "Build successful"
    "Deployment verified"
    "supervisor.*verified"
    "validation complete"
    "Quality assurance passed"
)

LOW_CONFIDENCE_PATTERNS=(
    "warning"
    "error"
    "failed"
    "incomplete"
    "skipped"
    "TODO"
    "FIXME"
    "need to"
    "should.*but"
)

TEAM_PATTERNS=(
    "ENGINEERING_TEAM"
    "MARKETING_TEAM"
    "QA_TEAM"
    "FINANCIAL_TEAM"
    "SALES_TEAM"
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

# Calculate confidence score (0-10)
calculate_confidence() {
    local message="$1"
    local confidence=7  # Base confidence score

    # Increase confidence for high-confidence indicators
    for pattern in "${HIGH_CONFIDENCE_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            confidence=$((confidence + 1))
        fi
    done

    # Decrease confidence for low-confidence indicators
    for pattern in "${LOW_CONFIDENCE_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            confidence=$((confidence - 2))
        fi
    done

    # Check for test mentions
    if echo "$message" | grep -iE "(test|spec).*pass" > /dev/null 2>&1; then
        confidence=$((confidence + 1))
    elif echo "$message" | grep -iE "no.*test" > /dev/null 2>&1; then
        confidence=$((confidence - 1))
    fi

    # Check for git commits
    if echo "$message" | grep -iE "commit.*push" > /dev/null 2>&1; then
        confidence=$((confidence + 1))
    fi

    # Check for documentation
    if echo "$message" | grep -iE "document" > /dev/null 2>&1; then
        confidence=$((confidence + 1))
    fi

    # Cap between 0 and 10
    if [ $confidence -gt 10 ]; then
        confidence=10
    elif [ $confidence -lt 0 ]; then
        confidence=0
    fi

    echo $confidence
}

# Determine verification criteria based on message content
determine_verification_criteria() {
    local message="$1"
    local criteria=""

    # Engineering work
    if echo "$message" | grep -iE "(feature|bug|code|implement)" > /dev/null 2>&1; then
        criteria="Engineering verification:\n"
        criteria+="  • Code quality and standards\n"
        criteria+="  • Tests passing (unit, integration)\n"
        criteria+="  • Security audit\n"
        criteria+="  • Documentation completeness\n"
        criteria+="  • Git commits and code review"
    fi

    # Marketing work
    if echo "$message" | grep -iE "(campaign|content|landing|marketing)" > /dev/null 2>&1; then
        criteria="Marketing verification:\n"
        criteria+="  • Brand voice compliance (tone score 7+)\n"
        criteria+="  • Content quality and accuracy\n"
        criteria+="  • SEO optimization\n"
        criteria+="  • Visual assets quality\n"
        criteria+="  • Call-to-action clarity"
    fi

    # QA work
    if echo "$message" | grep -iE "(test|qa|quality)" > /dev/null 2>&1; then
        criteria="QA verification:\n"
        criteria+="  • Test coverage adequacy\n"
        criteria+="  • Edge cases covered\n"
        criteria+="  • Test quality and maintainability\n"
        criteria+="  • Fixtures properly implemented\n"
        criteria+="  • Documentation completeness"
    fi

    # Financial work
    if echo "$message" | grep -iE "(financial|budget|forecast|analysis)" > /dev/null 2>&1; then
        criteria="Financial verification:\n"
        criteria+="  • Data accuracy and sources\n"
        criteria+="  • Calculations verified\n"
        criteria+="  • Assumptions documented\n"
        criteria+="  • Compliance requirements met\n"
        criteria+="  • Scenario analysis completeness"
    fi

    # Sales work
    if echo "$message" | grep -iE "(proposal|sales|rfp|pitch)" > /dev/null 2>&1; then
        criteria="Sales verification:\n"
        criteria+="  • Proposal completeness\n"
        criteria+="  • Pricing accuracy\n"
        criteria+="  • Value proposition clarity\n"
        criteria+="  • Customer pain points addressed\n"
        criteria+="  • Compliance and legal review"
    fi

    # Default criteria
    if [ -z "$criteria" ]; then
        criteria="General verification:\n"
        criteria+="  • Requirements met\n"
        criteria+="  • Quality standards\n"
        criteria+="  • Documentation complete\n"
        criteria+="  • Deliverables ready"
    fi

    echo -e "$criteria"
}

# Estimate verification time based on confidence and complexity
estimate_verification_time() {
    local confidence="$1"
    local message="$2"

    # Base time: 5 minutes
    local base_time=5

    # Adjust based on confidence
    if [ $confidence -ge 8 ]; then
        echo "~2-3 minutes (high confidence)"
    elif [ $confidence -ge 5 ]; then
        echo "~5-10 minutes (moderate confidence)"
    else
        echo "~10-15 minutes (thorough review needed)"
    fi
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
            # Calculate confidence score
            local confidence=$(calculate_confidence "$response")

            # Get verification criteria
            local criteria=$(determine_verification_criteria "$response")

            # Get estimated time
            local est_time=$(estimate_verification_time "$confidence" "$response")

            # Determine confidence level label
            local confidence_label=""
            local confidence_icon=""
            if [ $confidence -ge 8 ]; then
                confidence_label="HIGH"
                confidence_icon="🟢"
            elif [ $confidence -ge 5 ]; then
                confidence_label="MODERATE"
                confidence_icon="🟡"
            else
                confidence_label="LOW (manual review recommended)"
                confidence_icon="🔴"
            fi

            # Output enhanced suggestion
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🔍 SUPERVISOR VERIFICATION SUGGESTED"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "It looks like significant work was just completed."
            echo ""
            echo "Confidence Score: $confidence_icon $confidence/10 ($confidence_label)"
            echo "Estimated Verification Time: $est_time"
            echo ""
            echo "$criteria"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "RECOMMENDED ACTIONS:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""

            if [ $confidence -ge 8 ]; then
                echo "✅ High confidence - Quick verification recommended:"
                echo "   \"Use supervisor to verify this work is complete\""
            elif [ $confidence -ge 5 ]; then
                echo "⚠️  Moderate confidence - Standard verification recommended:"
                echo "   \"Use supervisor to verify this work is complete\""
            else
                echo "❗ Low confidence - Thorough review STRONGLY recommended:"
                echo "   \"Use supervisor to verify this work is complete\""
                echo ""
                echo "   Consider checking for:"
                echo "   • Incomplete tasks or warnings in the output"
                echo "   • Missing tests or documentation"
                echo "   • Unresolved errors or edge cases"
            fi

            echo ""
            echo "Or wait for automatic verification if using CTO/router-agent."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
        fi
    fi
}

main "$@"
