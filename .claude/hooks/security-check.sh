#!/bin/bash
#
# Security Check Hook
# Prevents credential leaks and security vulnerabilities in code changes
#
# This hook scans for common security issues before committing code:
# - API keys, tokens, passwords
# - Hardcoded secrets
# - Common vulnerability patterns
# - Sensitive file types

# Configuration
SENSITIVE_PATTERNS=(
    # API Keys and Tokens
    "api[_-]?key\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "apikey\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "api[_-]?secret\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "access[_-]?token\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "auth[_-]?token\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "bearer\s+[a-zA-Z0-9_-]{20,}"

    # AWS Credentials
    "aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*['\"]?AKIA[A-Z0-9]{16}['\"]?"
    "aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"][a-zA-Z0-9/+=]{40}['\"]"

    # Private Keys
    "-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----"
    "private[_-]?key\s*[=:]\s*['\"][^'\"]{20,}['\"]"

    # Passwords
    "password\s*[=:]\s*['\"][^'\"]{8,}['\"]"
    "passwd\s*[=:]\s*['\"][^'\"]{8,}['\"]"
    "pwd\s*[=:]\s*['\"][^'\"]{8,}['\"]"

    # Database Connection Strings
    "mongodb(\+srv)?://[^'\"\s]+"
    "postgres://[^'\"\s]+"
    "mysql://[^'\"\s]+"
    "(jdbc|odbc):[^'\"\s]+"

    # OAuth and Client Secrets
    "client[_-]?secret\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "client[_-]?id\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "consumer[_-]?secret\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"

    # GitHub/GitLab Tokens
    "gh[ps]_[a-zA-Z0-9]{36}"
    "glpat-[a-zA-Z0-9_-]{20,}"

    # Slack Tokens
    "xox[baprs]-[a-zA-Z0-9-]+"

    # Stripe Keys
    "sk_live_[a-zA-Z0-9]{24,}"
    "pk_live_[a-zA-Z0-9]{24,}"

    # Generic Secrets
    "secret\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "token\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
    "encryption[_-]?key\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
)

SENSITIVE_FILES=(
    "*.pem"
    "*.key"
    "*.p12"
    "*.pfx"
    "*.jks"
    "*.keystore"
    "*_rsa"
    "*_dsa"
    "*_ed25519"
    "*_ecdsa"
    "credentials.json"
    "service-account*.json"
    ".env.production"
    ".env.local"
    "secrets.yml"
    "secrets.yaml"
)

# Whitelist patterns (safe to ignore)
WHITELIST_PATTERNS=(
    "example"
    "test"
    "mock"
    "dummy"
    "fake"
    "sample"
    "placeholder"
    "your-api-key-here"
    "xxx"
    "***"
    "redacted"
)

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if a pattern is whitelisted
is_whitelisted() {
    local line="$1"

    for pattern in "${WHITELIST_PATTERNS[@]}"; do
        if echo "$line" | grep -i "$pattern" > /dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

# Scan file for sensitive patterns
scan_file() {
    local file="$1"
    local issues_found=0

    # Skip binary files
    if file "$file" | grep -q "binary" 2>/dev/null; then
        return 0
    fi

    # Scan for patterns
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        local matches=$(grep -nE "$pattern" "$file" 2>/dev/null)

        if [ -n "$matches" ]; then
            # Check each match against whitelist
            while IFS= read -r match; do
                if ! is_whitelisted "$match"; then
                    if [ $issues_found -eq 0 ]; then
                        echo -e "${RED}⚠️  SECURITY ISSUE in $file:${NC}"
                    fi
                    echo -e "   Line: $match"
                    issues_found=1
                fi
            done <<< "$matches"
        fi
    done

    return $issues_found
}

# Check for sensitive file types
check_sensitive_files() {
    local files_found=0

    for pattern in "${SENSITIVE_FILES[@]}"; do
        local matches=$(find . -type f -name "$pattern" 2>/dev/null | grep -v ".git/")

        if [ -n "$matches" ]; then
            if [ $files_found -eq 0 ]; then
                echo -e "${YELLOW}⚠️  SENSITIVE FILE TYPES DETECTED:${NC}"
            fi
            echo "$matches" | while read -r file; do
                # Check if file is in .gitignore
                if ! git check-ignore -q "$file" 2>/dev/null; then
                    echo -e "   ${RED}NOT IGNORED:${NC} $file"
                    files_found=1
                else
                    echo -e "   ${GREEN}IGNORED:${NC} $file"
                fi
            done
        fi
    done

    return $files_found
}

# Main logic
main() {
    local total_issues=0

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔒 SECURITY CHECK: Scanning for credentials and secrets..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Get list of changed files (staged for commit)
    local changed_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)

    # If not in git or no staged files, scan all modified files
    if [ -z "$changed_files" ]; then
        changed_files=$(git diff --name-only 2>/dev/null)
    fi

    # If still no files, scan recent file writes
    if [ -z "$changed_files" ]; then
        changed_files=$(find . -type f -mmin -5 2>/dev/null | grep -v ".git/" | head -20)
    fi

    if [ -z "$changed_files" ]; then
        echo -e "${GREEN}✓ No files to scan${NC}"
        echo ""
        return 0
    fi

    # Scan each file
    echo "Scanning files:"
    echo "$changed_files" | while read -r file; do
        if [ -f "$file" ]; then
            echo "  - $file"
            if scan_file "$file"; then
                : # No issues
            else
                total_issues=$((total_issues + 1))
            fi
        fi
    done

    echo ""

    # Check for sensitive file types
    if check_sensitive_files; then
        total_issues=$((total_issues + 1))
    fi

    echo ""

    # Report results
    if [ $total_issues -gt 0 ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${RED}❌ SECURITY ISSUES DETECTED!${NC}"
        echo ""
        echo "Potential credentials or secrets were found in your code."
        echo ""
        echo "Recommended actions:"
        echo "  1. Remove hardcoded secrets from code"
        echo "  2. Use environment variables instead"
        echo "  3. Add sensitive files to .gitignore"
        echo "  4. Use secret management tools (e.g., .env files, vaults)"
        echo "  5. Rotate any exposed credentials immediately"
        echo ""
        echo "To bypass this check (NOT RECOMMENDED):"
        echo "  git commit --no-verify"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        # In hook mode, exit with error to block commit
        if [ "${HOOK_MODE:-0}" = "1" ]; then
            exit 1
        fi
    else
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}✅ Security check passed!${NC}"
        echo ""
        echo "No obvious credentials or secrets detected."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi

    return 0
}

main "$@"
