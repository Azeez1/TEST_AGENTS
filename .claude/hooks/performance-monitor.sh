#!/bin/bash
#
# Performance Monitor Hook
# Tracks agent performance, token usage, and costs for optimization
#
# This hook runs after Claude Code generates responses to collect performance
# metrics, track costs, and identify optimization opportunities.

# Configuration
METRICS_DIR="/home/user/TEST_AGENTS/.claude/metrics"
METRICS_FILE="$METRICS_DIR/performance-metrics.json"
DAILY_REPORT="$METRICS_DIR/daily-report.json"
COST_TRACKING="$METRICS_DIR/cost-tracking.json"

# Pricing (as of Jan 2025 - update as needed)
SONNET_INPUT_COST=3.00   # per 1M tokens
SONNET_OUTPUT_COST=15.00 # per 1M tokens
HAIKU_INPUT_COST=0.25    # per 1M tokens
HAIKU_OUTPUT_COST=1.25   # per 1M tokens
OPUS_INPUT_COST=15.00    # per 1M tokens
OPUS_OUTPUT_COST=75.00   # per 1M tokens

# Thresholds for warnings
TOKEN_WARNING_THRESHOLD=50000      # Warn if single response > 50k tokens
COST_WARNING_THRESHOLD=1.00        # Warn if single response > $1.00
DAILY_COST_WARNING=50.00           # Warn if daily cost > $50.00
RESPONSE_TIME_WARNING=30           # Warn if response > 30 seconds

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create metrics directory if it doesn't exist
mkdir -p "$METRICS_DIR"

# Initialize metrics file if it doesn't exist
if [ ! -f "$METRICS_FILE" ]; then
    echo '{"sessions": [], "total_tokens": 0, "total_cost": 0}' > "$METRICS_FILE"
fi

# Get current date
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIMESTAMP=$(date +%s)

# Extract metrics from response (placeholder - adapt based on actual API response format)
extract_metrics() {
    local response="$1"

    # Try to detect agent usage
    local agent_used="unknown"
    if echo "$response" | grep -q "cto"; then
        agent_used="cto"
    elif echo "$response" | grep -q "router-agent"; then
        agent_used="router-agent"
    elif echo "$response" | grep -q "supervisor"; then
        agent_used="supervisor"
    elif echo "$response" | grep -q "test-orchestrator"; then
        agent_used="test-orchestrator"
    fi

    # Estimate token usage based on response length (rough approximation)
    # Average: 1 token ≈ 4 characters
    local response_length=${#response}
    local estimated_tokens=$((response_length / 4))

    # Detect model used
    local model="sonnet"  # Default assumption
    if echo "$response" | grep -iq "haiku"; then
        model="haiku"
    elif echo "$response" | grep -iq "opus"; then
        model="opus"
    fi

    # Calculate estimated cost
    local cost=0
    case $model in
        "sonnet")
            # Assume 70% input, 30% output ratio
            local input_tokens=$((estimated_tokens * 70 / 100))
            local output_tokens=$((estimated_tokens * 30 / 100))
            cost=$(echo "scale=6; ($input_tokens / 1000000 * $SONNET_INPUT_COST) + ($output_tokens / 1000000 * $SONNET_OUTPUT_COST)" | bc)
            ;;
        "haiku")
            local input_tokens=$((estimated_tokens * 70 / 100))
            local output_tokens=$((estimated_tokens * 30 / 100))
            cost=$(echo "scale=6; ($input_tokens / 1000000 * $HAIKU_INPUT_COST) + ($output_tokens / 1000000 * $HAIKU_OUTPUT_COST)" | bc)
            ;;
        "opus")
            local input_tokens=$((estimated_tokens * 70 / 100))
            local output_tokens=$((estimated_tokens * 30 / 100))
            cost=$(echo "scale=6; ($input_tokens / 1000000 * $OPUS_INPUT_COST) + ($output_tokens / 1000000 * $OPUS_OUTPUT_COST)" | bc)
            ;;
    esac

    echo "$agent_used|$model|$estimated_tokens|$cost"
}

# Log metrics to file
log_metrics() {
    local agent="$1"
    local model="$2"
    local tokens="$3"
    local cost="$4"

    # Create session entry
    local session_entry=$(cat <<EOF
{
  "timestamp": $CURRENT_TIMESTAMP,
  "date": "$CURRENT_DATE",
  "agent": "$agent",
  "model": "$model",
  "estimated_tokens": $tokens,
  "estimated_cost": $cost
}
EOF
)

    # Append to metrics file (simplified - in production use jq for proper JSON manipulation)
    # For now, just append to a log file
    echo "$session_entry" >> "$METRICS_DIR/session-log.jsonl"
}

# Calculate daily totals
calculate_daily_totals() {
    local today_total_tokens=0
    local today_total_cost=0
    local session_count=0

    # Count today's sessions and sum tokens/costs
    if [ -f "$METRICS_DIR/session-log.jsonl" ]; then
        while IFS= read -r line; do
            local date=$(echo "$line" | grep -o '"date": "[^"]*"' | cut -d'"' -f4)
            if [ "$date" = "$CURRENT_DATE" ]; then
                local tokens=$(echo "$line" | grep -o '"estimated_tokens": [0-9]*' | awk '{print $2}')
                local cost=$(echo "$line" | grep -o '"estimated_cost": [0-9.]*' | awk '{print $2}')
                today_total_tokens=$((today_total_tokens + tokens))
                today_total_cost=$(echo "scale=6; $today_total_cost + $cost" | bc)
                session_count=$((session_count + 1))
            fi
        done < "$METRICS_DIR/session-log.jsonl"
    fi

    echo "$session_count|$today_total_tokens|$today_total_cost"
}

# Show performance insights
show_insights() {
    local tokens="$1"
    local cost="$2"
    local agent="$3"
    local model="$4"

    # Get daily totals
    local daily_stats=$(calculate_daily_totals)
    local daily_sessions=$(echo "$daily_stats" | cut -d'|' -f1)
    local daily_tokens=$(echo "$daily_stats" | cut -d'|' -f2)
    local daily_cost=$(echo "$daily_stats" | cut -d'|' -f3)

    # Check for warnings
    local has_warnings=0

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 PERFORMANCE METRICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This Response:"
    echo "  Agent: $agent"
    echo "  Model: $model"
    echo "  Est. Tokens: $(printf "%'d" $tokens)"
    echo "  Est. Cost: \$$(printf "%.4f" $cost)"
    echo ""

    # Token warning
    if [ $tokens -gt $TOKEN_WARNING_THRESHOLD ]; then
        echo -e "  ${YELLOW}⚠️  High token usage! Consider breaking into smaller tasks.${NC}"
        has_warnings=1
    fi

    # Cost warning
    local cost_check=$(echo "$cost > $COST_WARNING_THRESHOLD" | bc)
    if [ "$cost_check" = "1" ]; then
        echo -e "  ${YELLOW}⚠️  High cost for single response!${NC}"
        has_warnings=1
    fi

    echo ""
    echo "Today's Summary ($CURRENT_DATE):"
    echo "  Sessions: $daily_sessions"
    echo "  Total Tokens: $(printf "%'d" $daily_tokens)"
    echo "  Total Cost: \$$(printf "%.2f" $daily_cost)"
    echo ""

    # Daily cost warning
    local daily_cost_check=$(echo "$daily_cost > $DAILY_COST_WARNING" | bc)
    if [ "$daily_cost_check" = "1" ]; then
        echo -e "  ${RED}⚠️  Daily cost threshold exceeded! (\$$DAILY_COST_WARNING)${NC}"
        echo -e "  ${YELLOW}Consider optimizing agent usage or using lighter models.${NC}"
        has_warnings=1
    fi

    # Show top agents if log exists
    if [ -f "$METRICS_DIR/session-log.jsonl" ]; then
        echo "Top Agents Today:"
        grep "\"date\": \"$CURRENT_DATE\"" "$METRICS_DIR/session-log.jsonl" 2>/dev/null | \
            grep -o '"agent": "[^"]*"' | cut -d'"' -f4 | sort | uniq -c | sort -rn | head -3 | \
            while read count agent; do
                echo "  - $agent: $count invocations"
            done
    fi

    echo ""

    # Optimization suggestions
    if [ $has_warnings -eq 1 ]; then
        echo "💡 Optimization Tips:"
        echo "  • Use haiku model for simple tasks"
        echo "  • Break complex tasks into smaller steps"
        echo "  • Review agent selection (use most specific agent)"
        echo "  • Use /agent-suggest to find optimal agents"
        echo "  • Run /agent-health to identify inefficiencies"
        echo ""
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Generate weekly report (run on Mondays)
generate_weekly_report() {
    local day_of_week=$(date +%u)  # 1 = Monday, 7 = Sunday

    if [ "$day_of_week" = "1" ] && [ -f "$METRICS_DIR/session-log.jsonl" ]; then
        local week_start=$(date -d "7 days ago" +%Y-%m-%d)

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📈 WEEKLY PERFORMANCE REPORT"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Week: $week_start to $CURRENT_DATE"
        echo ""
        echo "Most Active Agents:"
        grep "\"date\": \"" "$METRICS_DIR/session-log.jsonl" 2>/dev/null | \
            grep -o '"agent": "[^"]*"' | cut -d'"' -f4 | sort | uniq -c | sort -rn | head -5 | \
            while read count agent; do
                echo "  $count × $agent"
            done
        echo ""
        echo "For detailed analysis, review: $METRICS_DIR/session-log.jsonl"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
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

    # Skip if no response
    if [ -z "$response" ]; then
        return 0
    fi

    # Extract metrics
    local metrics=$(extract_metrics "$response")
    local agent=$(echo "$metrics" | cut -d'|' -f1)
    local model=$(echo "$metrics" | cut -d'|' -f2)
    local tokens=$(echo "$metrics" | cut -d'|' -f3)
    local cost=$(echo "$metrics" | cut -d'|' -f4)

    # Log metrics
    log_metrics "$agent" "$model" "$tokens" "$cost"

    # Show insights (only show every 5th response to avoid clutter)
    local session_count=$(wc -l < "$METRICS_DIR/session-log.jsonl" 2>/dev/null || echo 0)
    local show_frequency=5

    if [ $((session_count % show_frequency)) -eq 0 ]; then
        show_insights "$tokens" "$cost" "$agent" "$model"
    fi

    # Generate weekly report (Mondays only)
    generate_weekly_report
}

main "$@"
