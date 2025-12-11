#!/usr/bin/env pwsh
# Quick start script for Windows PowerShell

Write-Host "=== Voting App Quick Start ===" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $MyInvocation.MyCommandPath

# Check Docker
Write-Host "`n[1/4] Checking Docker..." -ForegroundColor Yellow
if (!(docker --version 2>$null)) {
    Write-Host "ERROR: Docker not installed or not running" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker is running" -ForegroundColor Green

# Build images
Write-Host "`n[2/4] Building images..." -ForegroundColor Yellow
docker build -t voting-app:local "$repoRoot/voting-app" 2>&1 | Select-Object -Last 3
docker build -t result-app:local "$repoRoot/result-app" 2>&1 | Select-Object -Last 3
Write-Host "✓ Images built" -ForegroundColor Green

# Start services
Write-Host "`n[3/4] Starting services..." -ForegroundColor Yellow
docker-compose -f "$repoRoot/docker-compose.yml" up -d
Start-Sleep -Seconds 3
Write-Host "✓ Services started" -ForegroundColor Green

# Show status
Write-Host "`n[4/4] Service status:" -ForegroundColor Yellow
docker-compose -f "$repoRoot/docker-compose.yml" ps

Write-Host "`n=== Ready! ===" -ForegroundColor Cyan
Write-Host "Voting App:  http://localhost:5000" -ForegroundColor Green
Write-Host "Results API: http://localhost:8080/results" -ForegroundColor Green
Write-Host "`nTo stop services: docker-compose down" -ForegroundColor Yellow
