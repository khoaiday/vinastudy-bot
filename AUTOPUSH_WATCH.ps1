# AUTOPUSH WATCHER - polls git every 5s, pushes changes to origin/main
# Run: PowerShell -ExecutionPolicy Bypass -File AUTOPUSH_WATCH.ps1

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pollSec    = 5

Write-Host "[START] Polling every ${pollSec}s: $projectDir" -ForegroundColor Cyan
Write-Host "[INFO]  Ctrl+C to stop`n" -ForegroundColor Gray

Push-Location $projectDir

while ($true) {
  Start-Sleep -Seconds $pollSec

  # Clear stale locks
  if (Test-Path ".git\index.lock") { Remove-Item ".git\index.lock" -Force -ErrorAction SilentlyContinue }
  if (Test-Path ".git\HEAD.lock")  { Remove-Item ".git\HEAD.lock"  -Force -ErrorAction SilentlyContinue }

  # Check for local changes (untracked + modified)
  git add -A 2>$null
  $dirty = git status --porcelain 2>$null

  if ($dirty) {
    $ts = Get-Date -Format "dd-MMM-yy HH:mm:ss"

    # Sync with remote first to avoid non-fast-forward
    git fetch origin main 2>$null
    git reset --soft origin/main 2>$null
    git add -A 2>$null
    git commit -m "chore: auto-push $ts" 2>$null

    $result = git push origin HEAD:main 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host "[OK] Pushed at $ts" -ForegroundColor Green
    } else {
      Write-Host "[ERR] $result" -ForegroundColor Red
    }
  }
}
