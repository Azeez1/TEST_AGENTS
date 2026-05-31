# document_skill_gate.ps1 — PreToolUse hook.
# Deterministically forces use of the document skills (docx/pptx/xlsx/pdf):
# you cannot GENERATE one of those files until you've Read that format's SKILL.md
# this session. Reading the SKILL.md lifts the gate (sets a session marker).
#
# Registered for tools: Read, Write, Edit, Bash, PowerShell  (PreToolUse)
# Block mechanism: exit code 2 + reason on stderr (Claude Code feeds it back to the model).

$ErrorActionPreference = 'SilentlyContinue'

# --- parse hook input (JSON on stdin) ---
try { $j = ([Console]::In.ReadToEnd() | ConvertFrom-Json) } catch { exit 0 }
$tool = [string]$j.tool_name
$sid  = [string]$j.session_id; if (-not $sid) { $sid = 'nosession' }
$ti   = $j.tool_input
$cwd  = [string]$j.cwd

$fmts = @('docx','pptx','xlsx','pdf')
$mdir = Join-Path $env:TEMP 'claude_skill_ack'
[void](New-Item -ItemType Directory -Force -Path $mdir)
function Marker($f) { Join-Path $mdir ("{0}_{1}.ack" -f $sid, $f) }

# --- 1) Reading a document-skill SKILL.md lifts the gate for that format ---
if ($tool -eq 'Read') {
    $p = ([string]$ti.file_path) -replace '\\','/'
    if ($p -match 'document-skills/(docx|pptx|xlsx|pdf)/SKILL\.md') {
        Set-Content -Path (Marker $Matches[1]) -Value 'ack'
    }
    exit 0
}

# --- 2) Direct file creation via Write/Edit: gate by extension ---
if ($tool -in @('Write','Edit')) {
    $path = ([string]$ti.file_path).ToLower()
    foreach ($f in $fmts) {
        if ($path -match "\.$f`$" -and -not (Test-Path (Marker $f))) {
            [Console]::Error.WriteLine("BLOCKED by document_skill_gate: creating a .$f file. You MUST use the $f skill. Read .claude/skills/document-skills/$f/SKILL.md (and its reference doc) FIRST this session, then generate via the skill's method. Reading that SKILL.md lifts this gate.")
            exit 2
        }
    }
    exit 0
}

# --- 3) Generation via Bash/PowerShell: gate on library/tool signatures ---
if ($tool -in @('Bash','PowerShell')) {
    $cmd = [string]$ti.command
    $hay = $cmd
    # also scan any script files the command invokes (node x.js / python x.py / etc.)
    foreach ($m in [regex]::Matches($cmd, '[\w\.\\/\-]+\.(py|js|mjs|ts|ps1)')) {
        foreach ($cand in @($m.Value, (Join-Path $cwd $m.Value))) {
            if (Test-Path $cand) { $hay += "`n" + (Get-Content $cand -Raw) }
        }
    }
    $sig = @{
        docx = 'python-docx|from docx import|docx-js|Packer\.toBuffer|officegen|docxtemplater|pandoc[^\n]*\.docx'
        pptx = 'python-pptx|from pptx import|pptxgenjs|officegen|pandoc[^\n]*\.pptx'
        xlsx = 'openpyxl|xlsxwriter|exceljs|\.to_excel|pandoc[^\n]*\.xlsx'
        pdf  = 'reportlab|fpdf|weasyprint|wkhtmltopdf|pdfkit|pikepdf|--convert-to\s+pdf|soffice[^\n]*pdf|libreoffice[^\n]*pdf|pandoc[^\n]*\.pdf'
    }
    foreach ($f in $fmts) {
        if ($hay -match $sig[$f] -and -not (Test-Path (Marker $f))) {
            [Console]::Error.WriteLine("BLOCKED by document_skill_gate: .$f generation detected (lib/tool signature). You MUST use the $f skill. Read .claude/skills/document-skills/$f/SKILL.md (and its reference doc) FIRST this session, then generate via the skill. Reading that SKILL.md lifts this gate.")
            exit 2
        }
    }
}
exit 0
