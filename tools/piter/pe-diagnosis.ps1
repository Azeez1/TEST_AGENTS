# PITER pipeline for PE Diagnosis generation (Lesson 4)
#
# Five-phase pipeline with gates between phases. You walk away after approving the plan.
#
#   P → Plan        — agent researches firm, drafts PLAN.md (you review)
#   I → Implement   — agent generates diagnosis HTML + PDF from approved plan
#   T → Test        — pe-diagnosis-validator subagent runs 7-rule framework check
#   E → Evaluate    — pe-diagnosis-visual-reviewer subagent scores 1-5 on visual+quality
#   R → Review      — you review the final artifact before shipping
#
# Usage:
#   powershell -File tools/piter/pe-diagnosis.ps1 -FirmName "Kainos Capital"
#
# Outputs:
#   tmp/piter/pe-diagnosis-<firm>-<timestamp>/PLAN.md       (plan, human-approved)
#   MARKETING_TEAM/outputs/reports/<firm>_diagnosis.html    (live diagnosis)
#   MARKETING_TEAM/outputs/reports/<firm>_diagnosis.pdf     (live PDF for upload)
#
# Dependencies:
#   - `claude` CLI on PATH (Claude Code in non-interactive mode)
#   - pe-diagnosis-validator subagent at .claude/agents/pe-diagnosis-validator.md
#   - pe-diagnosis-visual-reviewer subagent at .claude/agents/pe-diagnosis-visual-reviewer.md
#   - pe_validation_gate.ps1 hook (fires on upload commands, runs the closed-loop)
#   - Perplexity MCP (for research phase)

param(
    [Parameter(Mandatory=$true)]
    [string]$FirmName,

    [Parameter(Mandatory=$false)]
    [switch]$SkipPlanApproval  # for testing / re-runs only — skips the human gate after Phase P
)

$ErrorActionPreference = "Stop"

# ─── Setup ──────────────────────────────────────────────────────────────
$REPO_ROOT = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $REPO_ROOT

$TIMESTAMP = Get-Date -Format "yyyy-MM-dd-HHmm"
$SAFE_NAME = ($FirmName -replace '[^A-Za-z0-9]', '_' -replace '_+', '_').Trim('_').ToLower()
$WORK_DIR  = "tmp\piter\pe-diagnosis-$SAFE_NAME-$TIMESTAMP"
$PLAN_PATH = "$WORK_DIR\PLAN.md"
$DIAG_HTML = "MARKETING_TEAM\outputs\reports\${SAFE_NAME}_diagnosis.html"
$DIAG_PDF  = "MARKETING_TEAM\outputs\reports\${SAFE_NAME}_diagnosis.pdf"
$LOG_PATH  = "$WORK_DIR\piter.log"

New-Item -ItemType Directory -Path $WORK_DIR -Force | Out-Null

function Log($msg) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $LOG_PATH -Value $line
}

function Phase($letter, $name) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════"
    Write-Host "  PHASE $letter — $name"
    Write-Host "═══════════════════════════════════════════════"
    Log "Phase $letter started: $name"
}

function Abort($msg) {
    Write-Host ""
    Write-Host "❌ PITER ABORTED: $msg" -ForegroundColor Red
    Log "ABORT: $msg"
    exit 1
}

# ─── Verify claude CLI is available ─────────────────────────────────────
$claude = Get-Command claude -ErrorAction SilentlyContinue
if ($null -eq $claude) {
    Abort "claude CLI not found on PATH. Install Claude Code first."
}

Log "PITER pipeline starting: $FirmName"
Log "Work dir: $WORK_DIR"
Log "Target HTML: $DIAG_HTML"
Log "Target PDF:  $DIAG_PDF"

# ═══ PHASE P — PLAN ═════════════════════════════════════════════════════
Phase "P" "Plan (research + hypothesize)"

$planPrompt = @"
You are planning a PE Operating Partner diagnosis for: $FirmName

Research the firm using Perplexity MCP (or web search if Perplexity unavailable). Find:
- Portfolio company (if applicable) or firm focus
- Industry / sector
- Approximate revenue range (cite source)
- Recent news, public job postings, or signals indicating operational pain
- Likely decision-maker (Operating Partner, PortCo CEO/CTO)

Then draft a 1-page plan at: $PLAN_PATH

The plan must contain:
1. Firm summary (3-5 lines)
2. 3-5 hypothesized pain points, each with a one-sentence evidence basis
3. Recommended framework angle (DBAC / 5-Move / Bottleneck — pick one)
4. Risk factors (claims that need verification, unknowable specifics to avoid)
5. Estimated tone: calm-power, stoic-precision (Dux Machina default)

Do NOT generate the diagnosis itself yet. Only the plan.

End your response with: 'PLAN.md ready for approval at $PLAN_PATH.'
"@

Log "Invoking claude for Phase P..."
claude -p $planPrompt
if ($LASTEXITCODE -ne 0) {
    Abort "Phase P (Plan) failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path $PLAN_PATH)) {
    Abort "Phase P completed but $PLAN_PATH was not created. Check claude output above."
}

Log "Phase P complete. Plan at $PLAN_PATH"

# ─── Gate: human approves the plan ──────────────────────────────────────
if (-not $SkipPlanApproval) {
    Write-Host ""
    Write-Host "─── GATE: Human review of plan ───"
    Write-Host "Open and review: $PLAN_PATH"
    Write-Host ""
    $approval = Read-Host "Approve plan and proceed to Phase I (Implement)? [y/N]"
    if ($approval -ne 'y' -and $approval -ne 'Y') {
        Abort "User did not approve plan. Plan preserved at $PLAN_PATH for revision."
    }
    Log "Plan approved by user."
} else {
    Log "Plan approval skipped (--SkipPlanApproval flag)."
}

# ═══ PHASE I — IMPLEMENT ════════════════════════════════════════════════
Phase "I" "Implement (generate diagnosis from approved plan)"

$implementPrompt = @"
Execute the approved plan at: $PLAN_PATH

Generate the PE diagnosis HTML at: $DIAG_HTML
Then render it to PDF at: $DIAG_PDF

Follow the canonical structure from past diagnoses in MARKETING_TEAM/outputs/reports/*_diagnosis.html.

Required structure:
- Header (firm name + 1-line positioning hook)
- Diagnosis body (the hypothesized pain points from the plan, framed as findings)
- Recommendations block (priority-ordered, with concrete first steps)
- Timeline / metrics section
- Footer signature with: linkedin.com/in/azeez-oseni and duxmachina.com (both REQUIRED for the validation hook)

Use the brand voice from MARKETING_TEAM/memory/brand_voice.json if present.

After rendering, output the absolute paths to both files.
"@

Log "Invoking claude for Phase I..."
claude -p $implementPrompt
if ($LASTEXITCODE -ne 0) {
    Abort "Phase I (Implement) failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path $DIAG_HTML)) {
    Abort "Phase I completed but $DIAG_HTML was not created."
}
if (-not (Test-Path $DIAG_PDF)) {
    Abort "Phase I completed but $DIAG_PDF was not created."
}

Log "Phase I complete. HTML + PDF generated."

# ═══ PHASE T — TEST (closed-loop structural validator) ══════════════════
Phase "T" "Test (7-rule validator + closed-loop retry)"

$testPrompt = @"
Use the pe-diagnosis-validator subagent (.claude/agents/pe-diagnosis-validator.md) on this PDF: $DIAG_PDF

The subagent will run the 7-rule Verification Framework and write either a .validation_pass or .validation_fail file alongside the PDF.

If the subagent reports FAIL with specific issues, fix the underlying HTML and re-render the PDF, then re-run the validator. The pe_validation_gate.ps1 hook will enforce up to 3 closed-loop retries.

When the validator reports PASS, return: 'TEST PHASE PASS' followed by a one-line summary.
"@

Log "Invoking claude for Phase T..."
claude -p $testPrompt
if ($LASTEXITCODE -ne 0) {
    Abort "Phase T (Test) failed with exit code $LASTEXITCODE. Check $DIAG_PDF and the .validation_pass/.validation_fail files."
}

# Verify the pass file was actually written
$passFile = $DIAG_PDF -replace '\.pdf$', '.validation_pass'
if (-not (Test-Path $passFile)) {
    Abort "Phase T returned but no .validation_pass file exists at $passFile. Validator did not approve."
}

Log "Phase T complete. .validation_pass file exists."

# ═══ PHASE E — EVALUATE (visual + quality reviewer) ═════════════════════
Phase "E" "Evaluate (visual fidelity + content quality)"

$evalPrompt = @"
Use the pe-diagnosis-visual-reviewer subagent (.claude/agents/pe-diagnosis-visual-reviewer.md) on this HTML: $DIAG_HTML

The subagent will sample 3-5 canonical past diagnoses and score this one 1-5 on:
- A. Format Match
- B. Content Quality
- C. Framework Adherence

Capture the verdict and the three scores.

If any score is below 4, the diagnosis needs another pass. Identify specific corrections from the subagent's report, fix the HTML, re-render the PDF, re-run Phase T, then re-run this Phase E.

When all three scores are 4 or higher, return: 'EVAL PHASE PASS — scores A/B/C' with the actual numbers.
"@

Log "Invoking claude for Phase E..."
claude -p $evalPrompt
if ($LASTEXITCODE -ne 0) {
    Abort "Phase E (Evaluate) failed with exit code $LASTEXITCODE"
}

Log "Phase E complete."

# ═══ PHASE R — REVIEW (human) ═══════════════════════════════════════════
Phase "R" "Review (you approve the final artifact)"

Write-Host ""
Write-Host "✅ All automated phases passed."
Write-Host ""
Write-Host "Final artifacts:"
Write-Host "  HTML:  $DIAG_HTML"
Write-Host "  PDF:   $DIAG_PDF"
Write-Host "  Plan:  $PLAN_PATH"
Write-Host "  Log:   $LOG_PATH"
Write-Host ""
Write-Host "Next step: open the PDF, review, and if approved run the upload command."
Write-Host "  python tools/upload_to_drive.py $DIAG_PDF"
Write-Host ""
Write-Host "The pe_validation_gate.ps1 hook will re-check on upload — guaranteed footer-cutoff detection."

Log "PITER pipeline complete. Awaiting human review of final artifact."

exit 0
