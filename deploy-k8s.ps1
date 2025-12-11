#!/usr/bin/env pwsh
# Kubernetes quick apply script

Write-Host "=== Kubernetes Deployment ===" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $MyInvocation.MyCommandPath

# Check kubectl
Write-Host "`nChecking kubectl..." -ForegroundColor Yellow
if (!(kubectl version 2>$null)) {
    Write-Host "ERROR: kubectl not installed or cluster not accessible" -ForegroundColor Red
    exit 1
}
Write-Host "✓ kubectl is connected" -ForegroundColor Green

# Build and load images
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
docker build -t voting-app:latest "$repoRoot/voting-app"
docker build -t result-app:latest "$repoRoot/result-app"

# For Docker Desktop Kubernetes, images are available automatically
# For minikube, uncomment:
# minikube image load voting-app:latest
# minikube image load result-app:latest

Write-Host "`nApplying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f "$repoRoot/k8s/"

Write-Host "`n✓ Deployments applied!" -ForegroundColor Green
Write-Host "`nChecking pod status (wait 30s for full startup):" -ForegroundColor Yellow
kubectl get pods -w

Write-Host "`n=== Access Services ===" -ForegroundColor Cyan
Write-Host "In separate terminal windows, run:" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/voting-app 5000:5000" -ForegroundColor Green
Write-Host "  kubectl port-forward svc/result-app 8080:8080" -ForegroundColor Green
