param(
    [Parameter(Mandatory=$false)]
    [string]$Token = "r8_SnyViTeEsyAE3kP2F2KdMr4ly4fLHln1atZVh"
)

$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type"  = "application/json"
}

$imagePath = "C:\Users\Nam\OneDrive\Desktop\vinastudy-bot\test.jpg"
if (-Not (Test-Path $imagePath)) {
    Write-Host "File $imagePath not found!" -ForegroundColor Red
    exit 1
}

$bytes = [System.IO.File]::ReadAllBytes($imagePath)
$base64 = [System.Convert]::ToBase64String($bytes)
$dataUri = "data:image/jpeg;base64,$base64"

$prompt = "A close-up manga panel portrait of a 10 year old boy math warrior img, upper body shot, head and shoulders, glowing bright green armor, bright sunny space galaxy background with colorful floating math equations, 2D comic book art, anime manga style, pencil sketch strokes, cel shaded, vibrant bright pastel colors, halftone patterns"
$negative_prompt = "realistic, photorealistic, 3d, photography, cinematic, real person, photograph, dark, gloomy, sad"

$outDir = "C:\Users\Nam\.gemini\antigravity\brain\bfbb8ec0-e6a4-4cca-af30-b65e4594f0c3\scratch"
if (-Not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir }

Write-Host "Generating PhotoMaker demo with local image..." -ForegroundColor Cyan
$body = @{
    version = "ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4"
    input   = @{
        input_image = $dataUri
        prompt = $prompt
        style_name = "Comic book"
        style_strength_ratio = 25
    }
} | ConvertTo-Json -Depth 10

try {
    $pred = Invoke-RestMethod -Uri "https://api.replicate.com/v1/predictions" -Headers $headers -Method POST -Body $body
    Write-Host "Prediction ID: $($pred.id)"
} catch {
    Write-Host "POST Error: $_" -ForegroundColor Red
    exit 1
}

$status = "starting"
while ($status -notin @("succeeded","failed","canceled")) {
    Start-Sleep -Seconds 3
    $check  = Invoke-RestMethod -Uri "https://api.replicate.com/v1/predictions/$($pred.id)" -Headers $headers
    $status = $check.status
    Write-Host "." -NoNewline
}
Write-Host ""

if ($status -eq "succeeded") {
    if ($check.output -is [array]) { $outUrl = $check.output[0] } else { $outUrl = $check.output }
    $outPath = "$outDir\photomaker_user_demo.png"
    Invoke-WebRequest -Uri $outUrl -OutFile $outPath
    Write-Host "Saved to $outPath" -ForegroundColor Green
} else {
    Write-Host "Failed: $status $($check.error)" -ForegroundColor Red
}
