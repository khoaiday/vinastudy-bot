# Script tao file .env tu clipboard
# Chay script nay SAU KHI da copy DATABASE_URL tu Railway

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $projectDir ".env"

# Doc DATABASE_URL tu clipboard
$dbUrl = Get-Clipboard
if (-not $dbUrl -or -not $dbUrl.StartsWith("postgresql")) {
    Write-Host "[LOI] Clipboard khong chua DATABASE_URL hop le." -ForegroundColor Red
    Write-Host "Vui long vao Railway -> Bot-service -> Variables -> Copy DATABASE_URL truoc." -ForegroundColor Yellow
    pause
    exit 1
}

# Doc TELEGRAM_TOKEN neu da co trong .env cu
$telegramToken = ""
if (Test-Path $envFile) {
    $existing = Get-Content $envFile | Where-Object { $_ -match "^TELEGRAM_TOKEN=" }
    if ($existing) { $telegramToken = $existing -replace "^TELEGRAM_TOKEN=", "" }
}

$envContent = @"
DATABASE_URL=$dbUrl
SECRET_KEY=vs-local-dev-key-2026
BASE_DOMAIN=http://localhost:8080
PORT=8080

# Dien vao neu can test bot Telegram:
TELEGRAM_TOKEN=$telegramToken
ADMIN_BOT_TOKEN=
ADMIN_ID=0

# Khong can thiet de chay web server:
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
ANTHROPIC_API_KEY=
REPLICATE_API_TOKEN=
"@

Set-Content -Path $envFile -Value $envContent -Encoding UTF8
Write-Host "Da tao file .env thanh cong!" -ForegroundColor Green
Write-Host "DATABASE_URL: $($dbUrl.Substring(0, 40))..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Chay server: python web_server.py" -ForegroundColor Yellow
pause
