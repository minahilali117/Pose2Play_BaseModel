# Phase 7 - Start RL API Server and Demo
# This script starts the Flask API server and opens the web demo

Write-Host "================================" -ForegroundColor Cyan
Write-Host " Phase 7: RL Web Integration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$mlPath = "D:\university\fyp\milestones\mid eval\ayaans work\Pose2Play_BaseModel\Pose2Play_BaseModel\ml"

# Start Flask server (serves both API and demo)
Write-Host "Starting Pose2Play..." -ForegroundColor Cyan
$serverScript = @"
cd '$mlPath'
python api_server.py
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $serverScript

Write-Host "Waiting for server..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Open browser
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Pose2Play Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. ALLOW camera when browser asks" -ForegroundColor Yellow
Write-Host "  2. Click 'Start Detection'" -ForegroundColor Yellow
Write-Host "  3. Do shoulder exercises!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Close the server window to stop" -ForegroundColor Gray
Write-Host ""
