# Gotchas — Careful (Destructive Command Guard)

> Known edge cases and workarounds.

## 1. npm install --force Gets Blocked
**Symptom:** Running `npm install --force` is blocked because the command contains "force".
**Why:** The hook scans for `force-push` as a substring. `--force` in other contexts is a false positive.
**Workaround:** The current patterns are specific enough (`git push -f`, `git push --force`) that general `--force` should NOT be blocked. If you see a false positive, check if the blocked pattern matches exactly.

---

## 2. Only Blocks Bash, Not File Edits
**Symptom:** Claude edits a config file to add a destructive cron job or modifies a script to include `rm -rf`.
**Why:** The careful hook only intercepts the Bash tool. Edit and Write tools are not monitored.
**Fix:** If you need file protection too, activate the `freeze` skill alongside `careful`.

---

## 3. PowerShell Must Be Available
**Symptom:** Hook doesn't fire — destructive commands go through unblocked.
**Why:** The hook runs via `powershell.exe`. If PowerShell is restricted or unavailable, the hook silently fails.
**Fix:** Ensure PowerShell execution policy allows bypass: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

---

## 4. Case Sensitivity
**Symptom:** `drop table` is blocked but `Drop Table` passes through.
**Why:** PowerShell's `-match` is case-insensitive by default, so this should work. But the blocked list includes explicit lowercase and uppercase variants as a safety net.
**Fix:** If you find a case variant that slips through, add it to the `$blocked` array in the hook command.
