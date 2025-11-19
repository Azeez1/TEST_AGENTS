#!/bin/bash
#
# Team Collaboration Detector Hook
# Suggests when multiple teams should work together for optimal results
#
# This hook analyzes task descriptions and detects opportunities for
# cross-team collaboration, suggesting relevant workflows.

# Configuration
# Engineering + Marketing patterns
ENG_MARKETING_PATTERNS=(
    "landing.*page"
    "product.*page"
    "website.*feature"
    "interactive.*demo"
    "web.*application"
    "product.*launch"
    "documentation.*site"
)

# Sales + Marketing patterns
SALES_MARKETING_PATTERNS=(
    "proposal.*campaign"
    "sales.*collateral"
    "customer.*acquisition"
    "lead.*generation"
    "demo.*materials"
    "case.*stud"
    "pitch.*deck.*content"
)

# Finance + Sales patterns
FINANCE_SALES_PATTERNS=(
    "pricing.*strategy"
    "deal.*structure"
    "revenue.*forecast"
    "commission.*plan"
    "sales.*compensation"
    "quota.*planning"
    "roi.*calculator"
)

# Finance + Marketing patterns
FINANCE_MARKETING_PATTERNS=(
    "marketing.*budget"
    "campaign.*roi"
    "customer.*acquisition.*cost"
    "marketing.*spend"
    "attribution.*model"
)

# Engineering + QA patterns
ENG_QA_PATTERNS=(
    "release"
    "deployment"
    "production.*ready"
    "feature.*complete"
    "testing.*needed"
)

# All teams patterns
ALL_TEAMS_PATTERNS=(
    "product.*launch"
    "company.*launch"
    "quarterly.*planning"
    "strategic.*initiative"
    "business.*plan"
)

# Colors for output
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect engineering + marketing needs
check_eng_marketing() {
    local message="$1"

    for pattern in "${ENG_MARKETING_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Detect sales + marketing needs
check_sales_marketing() {
    local message="$1"

    for pattern in "${SALES_MARKETING_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Detect finance + sales needs
check_finance_sales() {
    local message="$1"

    for pattern in "${FINANCE_SALES_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Detect finance + marketing needs
check_finance_marketing() {
    local message="$1"

    for pattern in "${FINANCE_MARKETING_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Detect engineering + QA needs
check_eng_qa() {
    local message="$1"

    for pattern in "${ENG_QA_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Detect all teams needs
check_all_teams() {
    local message="$1"

    for pattern in "${ALL_TEAMS_PATTERNS[@]}"; do
        if echo "$message" | grep -iE "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Show engineering + marketing suggestions
suggest_eng_marketing() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}🤝 CROSS-TEAM COLLABORATION OPPORTUNITY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This task could benefit from ENGINEERING + MARKETING collaboration!"
    echo ""
    echo "Consider these approaches:"
    echo ""
    echo "1. Coordinated Approach (Recommended):"
    echo "   → /product-launch [product] [date] [audience]"
    echo "   • Full cross-team coordination"
    echo "   • Engineering builds + Marketing promotes"
    echo ""
    echo "2. Marketing-Led with Engineering Support:"
    echo "   → /launch-campaign [topic] [audience] [goals]"
    echo "   • Then involve: landing-page-specialist + frontend-developer"
    echo ""
    echo "3. Engineering-Led with Marketing Input:"
    echo "   → /ship-feature [feature-name]"
    echo "   • Then involve: router-agent for launch materials"
    echo ""
    echo "Benefits of collaboration:"
    echo "  ✓ Technical excellence + Marketing polish"
    echo "  ✓ Functional features + User engagement"
    echo "  ✓ Code quality + Content quality"
    echo "  ✓ SEO optimization + Performance optimization"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show sales + marketing suggestions
suggest_sales_marketing() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}🤝 CROSS-TEAM COLLABORATION OPPORTUNITY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This task could benefit from SALES + MARKETING collaboration!"
    echo ""
    echo "Consider these approaches:"
    echo ""
    echo "1. Complete Package (Recommended):"
    echo "   → /proposal-package [prospect] [solution] [deadline]"
    echo "   • Includes marketing support for collateral"
    echo ""
    echo "2. Lead Generation Campaign:"
    echo "   → \"Use router-agent for lead gen campaign, then sales-manager for follow-up\""
    echo "   • Marketing generates leads"
    echo "   • Sales converts to customers"
    echo ""
    echo "3. Content + Sales Enablement:"
    echo "   → /content-suite [topic] [audience]"
    echo "   • Marketing creates content"
    echo "   • Sales uses for outreach"
    echo ""
    echo "Benefits of collaboration:"
    echo "  ✓ High-quality leads + Effective conversion"
    echo "  ✓ Compelling content + Sales expertise"
    echo "  ✓ Brand consistency + Customer focus"
    echo "  ✓ Marketing reach + Sales relationships"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show finance + sales suggestions
suggest_finance_sales() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}🤝 CROSS-TEAM COLLABORATION OPPORTUNITY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This task could benefit from FINANCE + SALES collaboration!"
    echo ""
    echo "Consider these approaches:"
    echo ""
    echo "1. Pricing Strategy (Recommended):"
    echo "   → \"Use cfo-agent + sales-manager to develop pricing strategy\""
    echo "   • Finance models profitability"
    echo "   • Sales validates market fit"
    echo ""
    echo "2. Revenue Forecasting:"
    echo "   → /financial-analysis \"Sales forecast\" \"next-quarter\""
    echo "   • Then: \"Use sales-manager to validate assumptions\""
    echo ""
    echo "3. Deal Structuring:"
    echo "   → \"Use deal-analyst (Finance) + account-executive (Sales)\""
    echo "   • Finance analyzes deal value"
    echo "   • Sales negotiates terms"
    echo ""
    echo "Benefits of collaboration:"
    echo "  ✓ Profitable pricing + Market competitiveness"
    echo "  ✓ Accurate forecasts + Sales reality"
    echo "  ✓ Financial discipline + Customer relationships"
    echo "  ✓ Data-driven decisions + Market insights"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show finance + marketing suggestions
suggest_finance_marketing() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}🤝 CROSS-TEAM COLLABORATION OPPORTUNITY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This task could benefit from FINANCE + MARKETING collaboration!"
    echo ""
    echo "Consider these approaches:"
    echo ""
    echo "1. Marketing Budget & ROI:"
    echo "   → \"Use cfo-agent to set budget, then router-agent to plan campaigns\""
    echo "   • Finance allocates resources"
    echo "   • Marketing optimizes spend"
    echo ""
    echo "2. CAC & Attribution:"
    echo "   → \"Use financial-analyst + analyst (Marketing)\""
    echo "   • Track customer acquisition cost"
    echo "   • Optimize marketing efficiency"
    echo ""
    echo "3. Campaign ROI Analysis:"
    echo "   → /launch-campaign [topic] [audience] [goals]"
    echo "   • Then: /financial-analysis for ROI tracking"
    echo ""
    echo "Benefits of collaboration:"
    echo "  ✓ Budget discipline + Creative excellence"
    echo "  ✓ ROI tracking + Marketing impact"
    echo "  ✓ Cost efficiency + Growth goals"
    echo "  ✓ Financial accountability + Brand building"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show engineering + QA suggestions
suggest_eng_qa() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}🤝 CROSS-TEAM COLLABORATION OPPORTUNITY${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This task could benefit from ENGINEERING + QA collaboration!"
    echo ""
    echo "Consider these approaches:"
    echo ""
    echo "1. Complete Feature Delivery (Recommended):"
    echo "   → /ship-feature [feature-name]"
    echo "   • Engineering develops + QA validates"
    echo "   • Includes comprehensive testing"
    echo ""
    echo "2. Quality-First Development:"
    echo "   → \"Use cto for development, then test-orchestrator for QA\""
    echo ""
    echo "3. Bug Fix with Testing:"
    echo "   → /debug-issue [issue] [environment]"
    echo "   • Includes test creation and validation"
    echo ""
    echo "Benefits of collaboration:"
    echo "  ✓ Feature quality + Comprehensive testing"
    echo "  ✓ Fewer bugs + Faster releases"
    echo "  ✓ Code confidence + Production stability"
    echo "  ✓ Developer velocity + Quality assurance"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show all teams suggestions
suggest_all_teams() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}🌟 MAJOR CROSS-TEAM INITIATIVE DETECTED${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This task requires ALL TEAMS working together!"
    echo ""
    echo "Recommended Commands:"
    echo ""
    echo "1. Product Launch (Most Common):"
    echo "   → /product-launch [product] [launch-date] [audience]"
    echo "   • Engineering: Feature development"
    echo "   • Marketing: Launch campaign"
    echo "   • Sales: Proposals and enablement"
    echo "   • QA: Quality assurance"
    echo "   • Finance: Pricing and forecasts"
    echo ""
    echo "2. Quarterly Planning (Strategic):"
    echo "   → /quarterly-planning [quarter] [year] [focus]"
    echo "   • All teams: OKRs and roadmaps"
    echo "   • Cross-team alignment"
    echo "   • Resource allocation"
    echo "   • Timeline coordination"
    echo ""
    echo "⏱️  Time Required: Multiple weeks"
    echo "💰 Resources: Significant (all teams involved)"
    echo "📊 Impact: Company-wide"
    echo ""
    echo "💡 Pro Tip: Start with /quarterly-planning to align all teams first!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Main logic
main() {
    # Read the user's input or last message
    local user_message="${CLAUDE_USER_MESSAGE:-}"

    # If no message provided, read from file if available
    if [ -z "$user_message" ] && [ -f "/tmp/claude_last_user_message.txt" ]; then
        user_message=$(cat /tmp/claude_last_user_message.txt)
    fi

    # Skip if no message
    if [ -z "$user_message" ]; then
        return 0
    fi

    # Check for collaboration opportunities (highest priority first)
    if check_all_teams "$user_message"; then
        suggest_all_teams
        return 0
    fi

    if check_eng_marketing "$user_message"; then
        suggest_eng_marketing
        return 0
    fi

    if check_sales_marketing "$user_message"; then
        suggest_sales_marketing
        return 0
    fi

    if check_finance_sales "$user_message"; then
        suggest_finance_sales
        return 0
    fi

    if check_finance_marketing "$user_message"; then
        suggest_finance_marketing
        return 0
    fi

    if check_eng_qa "$user_message"; then
        suggest_eng_qa
        return 0
    fi

    # No collaboration detected
    return 0
}

main "$@"
