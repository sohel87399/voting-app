# Quick Reference - Commands Cheat Sheet

## Docker Compose (Local Testing)

```powershell
# Navigate to project root
cd c:\Users\LENOVO\OneDrive\Desktop\votingapp-pro

# Build all images
docker-compose build

# Start services (attach logs)
docker-compose up

# Start services (background)
docker-compose up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f voting-app
docker-compose logs -f result-app
docker-compose logs -f redis

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove volumes (data)
docker-compose down -v
```

## Docker Commands (Manual)

```powershell
# Build image
docker build -t voting-app:local ./voting-app

# List images
docker images

# Run container
docker run -d --name voting-app -p 5000:5000 voting-app:local

# List containers
docker ps
docker ps -a

# View logs
docker logs voting-app
docker logs -f voting-app

# Stop container
docker stop voting-app

# Remove container
docker rm voting-app

# Remove image
docker rmi voting-app:local

# Clean up unused resources
docker system prune -a
```

## Kubernetes Commands

```powershell
# Check cluster connection
kubectl cluster-info
kubectl get nodes

# Apply manifests
kubectl apply -f k8s/
kubectl apply -f k8s/redis-deployment.yaml

# View resources
kubectl get pods
kubectl get svc
kubectl get deployments

# Describe resources
kubectl describe pod <pod-name>
kubectl describe svc redis

# View logs
kubectl logs <pod-name>
kubectl logs -l app=voting-app
kubectl logs -f <pod-name>

# Port forwarding
kubectl port-forward svc/voting-app 5000:5000
kubectl port-forward svc/result-app 8080:8080
kubectl port-forward pod/<pod-name> 6379:6379

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/sh

# Scale deployment
kubectl scale deployment voting-app --replicas=3

# Delete resources
kubectl delete pod <pod-name>
kubectl delete svc redis
kubectl delete -f k8s/

# Watch resources
kubectl get pods -w
kubectl get svc -w

# Get shell into pod
kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -- redis-cli

# Tail logs from all pods with label
kubectl logs -l app=voting-app --all-containers=true -f
```

## Useful PowerShell Aliases

Add to PowerShell profile (`$PROFILE`):

```powershell
Set-Alias -Name dc -Value docker-compose
Set-Alias -Name d -Value docker
Set-Alias -Name k -Value kubectl

# Usage: k get pods, dc up -d, d ps
```

## Testing Endpoints

```powershell
# Test voting-app
Invoke-RestMethod http://localhost:5000

# Submit a vote (JSON)
Invoke-RestMethod -Uri "http://localhost:5000/vote" `
  -Method POST `
  -Headers @{"Content-Type" = "application/json"} `
  -Body (@{choice="Cats"} | ConvertTo-Json)

# Get results
Invoke-RestMethod http://localhost:8080/results
```

## Debugging

```powershell
# Check if port is in use
netstat -ano | findstr :5000

# Kill process on port
taskkill /PID <PID> /F

# View container network
docker network ls
docker network inspect voting-network

# Check DNS resolution (in container)
kubectl exec -it <pod-name> -- nslookup redis

# Check Redis data
kubectl exec -it <pod-name> -- redis-cli
# In redis-cli: HGETALL votes
```

## Common Issues & Fixes

```powershell
# Image pull failed
# Fix: Restart Docker Desktop or check internet

# Port already in use
# Fix: netstat -ano | findstr :PORT ; taskkill /PID <PID> /F

# Cannot connect to Redis
# Fix: Verify service is running: docker-compose ps
#      Verify REDIS_HOST env var is set

# Kubernetes pods stuck in Pending
# Fix: kubectl describe pod <pod-name>
#      Check image exists locally or check imagePullBackOff

# Out of disk space
# Fix: docker system prune -a
#      docker image prune
```

## Performance Tuning

```powershell
# Monitor resource usage
docker stats

# Limit resource usage in docker-compose.yml
# services:
#   voting-app:
#     deploy:
#       resources:
#         limits:
#           cpus: '0.5'
#           memory: 512M

# Check Kubernetes node resources
kubectl top nodes
kubectl top pods
```
