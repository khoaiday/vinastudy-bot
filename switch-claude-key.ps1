# Switch Claude API Key Script
# Dung: .\switch-claude-key.ps1

$keyFile = "$env:USERPROFILE\.claude_key_index"
$envFile = "$PSScriptRoot\.env.keys"

# Kiem tra file chua key
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Khong tim thay file .env.keys" -ForegroundColor Red
    Write-Host "👉 Tao file .env.keys voi noi dung:" -ForegroundColor Yellow
    Write-Host "   ANTHROPIC_API_KEY_1=sk-ant-xxxxx" -ForegroundColor Cyan
    Write-Host "   ANTHROPIC_API_KEY_2=sk-ant-yyyyy" -ForegroundColor Cyan
    exit 1
}

# Doc keys tu file
$keys = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^(ANTHROPIC_API_KEY_\d+)=(.+)$") {
        $keys[$matches[1]] = $matches[2].Trim()
    }
}

if ($keys.Count -lt 2) {
    Write-Host "❌ Can it nhat 2 key trong file .env.keys" -ForegroundColor Red
    exit 1
}

# Doc index hien tai
$index = 1
if (Test-Path $keyFile) {
    $index = [int](Get-Content $keyFile)
}

# Chon key
$currentKey = $keys["ANTHROPIC_API_KEY_$index"]
$nextIndex = if ($index -eq 1) { 2 } else { 1 }

# Set bien moi truong
$env:ANTHROPIC_API_KEY = $currentKey

# Luu index ke tiep
$nextIndex | Out-File $keyFile -Encoding utf8

# Hien thi trang thai
Write-Host ""
Write-Host "✅ Da chuyen sang Key $index" -ForegroundColor Green
Write-Host "🔑 Key: $($currentKey.Substring(0,20))..." -ForegroundColor Cyan
Write-Host "⏭️  Lan sau se dung Key $nextIndex" -ForegroundColor Gray
Write-Host ""

# Khoi dong Claude Code
Write-Host "🚀 Khoi dong Claude Code..." -ForegroundColor Yellow
claude
