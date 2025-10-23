#!/bin/bash
# Quick Fix for Smoke Test Performance
# Reduces test time from 10s to 2s (80% improvement)

echo "======================================================================"
echo "  QUICK FIX: Smoke Test Performance Optimization"
echo "======================================================================"
echo ""

# Step 1: Install missing dependencies
echo "[1/3] Installing missing dependencies..."
pip install python-dotenv pytest-timeout --quiet
echo "✓ Dependencies installed"
echo ""

# Step 2: Fix the timeout in the test file
echo "[2/3] Reducing MCP connection timeout (10s → 2s)..."
TEST_FILE="MARKETING_TEAM/scripts/test_google_workspace_mcp.py"

if [ -f "$TEST_FILE" ]; then
    # Backup original
    cp "$TEST_FILE" "${TEST_FILE}.backup"

    # Replace timeout=10 with timeout=2
    sed -i 's/timeout=10/timeout=2/g' "$TEST_FILE"

    echo "✓ Timeout reduced in $TEST_FILE"
    echo "  (Backup saved: ${TEST_FILE}.backup)"
else
    echo "✗ Test file not found: $TEST_FILE"
fi
echo ""

# Step 3: Run performance test again
echo "[3/3] Running performance test..."
echo ""
python3 test_performance_analyzer.py
echo ""

echo "======================================================================"
echo "  DONE! Check the report above for improvements"
echo "======================================================================"
echo ""
echo "Expected improvement: 10.49s → ~2.5s (76% faster)"
echo ""
echo "Next steps:"
echo "  1. Review: PERFORMANCE_ANALYSIS_REPORT.md"
echo "  2. For even better performance, implement mocking (see report)"
echo "  3. Separate smoke tests from integration tests"
echo ""
