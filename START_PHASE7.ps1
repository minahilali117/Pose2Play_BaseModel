# Phase 7 - Start RL API Server and Demo
# This script starts the Flask API server and opens the web demo

Write-Host "================================" -ForegroundColor Cyan
Write-Host " Phase 7: RL Web Integration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Change to ml directory
$mlPath = "d:\university\fyp\milestones\mid eval\cv model iter 2\Pose2Play base model iteration 1\ml"
$demoPath = "d:\university\fyp\milestones\mid eval\cv model iter 2\Pose2Play base model iteration 1\demo"

# Check if model exists
$modelPath = Join-Path $mlPath "models\dqn\DQN_rehab_final.zip"
if (-not (Test-Path $modelPath)) {
    Write-Host "[ERROR] Model not found: $modelPath" -ForegroundColor Red
    Write-Host "   Please train the model first:" -ForegroundColor Yellow
    Write-Host "   python train_rl.py --algorithm DQN --timesteps 100000 --output ./models/dqn" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Model found: DQN_rehab_final.zip" -ForegroundColor Green
Write-Host ""

# Start API server in new window
Write-Host "[INFO] Starting Flask API Server..." -ForegroundColor Cyan
$apiScript = @"
cd '$mlPath'
.\rl_env\Scripts\activate
python api_server.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiScript

# Wait a bit for server to start
Write-Host "[INFO] Waiting for API server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test API
Write-Host "[INFO] Testing API connection..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
    if ($response.status -eq "ok") {
        Write-Host "[OK] API is running and healthy!" -ForegroundColor Green
        Write-Host "   Model loaded: $($response.model_loaded)" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] API not responding yet (this is normal)" -ForegroundColor Yellow
    Write-Host "   Check the API server window for startup messages" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Opening Web Demo..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Open demo
Start-Process (Join-Path $demoPath "index.html")

Write-Host ""
Write-Host "[OK] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "What's Running:" -ForegroundColor Cyan
Write-Host "   1. Flask API Server (new PowerShell window)" -ForegroundColor White
Write-Host "   2. Web Demo (browser)" -ForegroundColor White
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Cyan
Write-Host "   1. Allow camera access in browser" -ForegroundColor White
Write-Host "   2. Click 'Start Detection'" -ForegroundColor White
Write-Host "   3. Do squats!" -ForegroundColor White
Write-Host "   4. Every 5 reps, RL agent will analyze and adjust" -ForegroundColor White
Write-Host "   5. Press F12 in browser to see RL decisions in console" -ForegroundColor White
Write-Host ""
Write-Host "To Stop:" -ForegroundColor Cyan
Write-Host "   Close the Flask API Server window" -ForegroundColor White
Write-Host ""
