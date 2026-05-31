$now = Get-Date
$formatted = $now.ToString("yyyy-MM-dd HH:mm:ss")
$dayOfWeek = $now.DayOfWeek
$timeOfDay = if ($now.Hour -lt 12) { "morning" }
             elseif ($now.Hour -lt 17) { "afternoon" }
             elseif ($now.Hour -lt 21) { "evening" }
             else { "night" }
$tz = [System.TimeZoneInfo]::Local.Id

Write-Output "Session started at: $formatted ($dayOfWeek $timeOfDay, $tz). Adjust any 'tonight/tomorrow' assumptions accordingly - verify against this stamp before referencing time of day."
