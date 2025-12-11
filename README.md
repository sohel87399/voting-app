# Voting App Demo - Docker & Kubernetes

A distributed voting application with three components:
- **voting-app** - Python Flask frontend for voting between Cats and Dogs
- **result-app** - Node.js API service that returns vote counts  
- **redis** - Redis instance to store votes

---

## Architecture

```
┌─────────────┐
│ Voting App  │  (Port 5000)
│   Flask     │──→ Redis
└─────────────┘
                  ↓
            ┌──────────┐
            │  Redis   │  (Port 6379)
            └──────────┘
                  ↑
             ┌────────────┐
             │ Result App │ (Port 8080)
             │  Node.js   │
             └────────────┘
```

---

## Prerequisites

- **Docker Desktop** installed and running
- **kubectl** installed (for Kubernetes; optional for local testing)
- **Python 3.11+** (optional, for local dev)

---

## Local Testing with Docker Compose

### 1. Build and Start Services

From the repo root:

```powershell
cd c:\Users\LENOVO\OneDrive\Desktop\votingapp-pro
docker-compose build
docker-compose up -d
```

### 2. Verify Services Are Running

```powershell
docker-compose ps
```

Expected output shows `voting-redis`, `voting-app`, and `result-app` all running.

### 3. Test the Services

**Vote on the Voting App:**
```
http://localhost:5000
```

Click "Vote Cats" or "Vote Dogs" buttons to submit votes.

**View Results (JSON API):**
```
http://localhost:8080/results
```

Returns:
```json
{
  "Cats": 5,
  "Dogs": 3
}
```

### 4. Cleanup

```powershell
docker-compose down
```

---

## Manual Docker Image Builds

If you prefer to build images individually:

```powershell
# Build voting-app image
docker build -t voting-app:local ./voting-app

# Build result-app image  
docker build -t result-app:local ./result-app
```

Then run with docker-compose or manually:

```powershell
# Run Redis
docker run -d --name redis -p 6379:6379 redis:7.0-alpine

# Run voting-app
docker run -d --name voting-app -p 5000:5000 -e REDIS_HOST=host.docker.internal voting-app:local

# Run result-app
docker run -d --name result-app -p 8080:8080 -e REDIS_HOST=host.docker.internal result-app:local
```

---

## Kubernetes Deployment

### Prerequisites

- A running Kubernetes cluster (local with Docker Desktop, minikube, or remote)
- `kubectl` configured and connected to your cluster

### 1. Build and Push Images (if using remote cluster)

For local Kubernetes (Docker Desktop k8s or minikube), you can load images directly:

```powershell
# Docker Desktop Kubernetes
docker build -t voting-app:latest ./voting-app
docker build -t result-app:latest ./result-app

# If using minikube, load images into the cluster
minikube image load voting-app:latest
minikube image load result-app:latest
```

For a remote registry (e.g., Docker Hub):

```powershell
docker build -t myregistry/voting-app:latest ./voting-app
docker push myregistry/voting-app:latest

docker build -t myregistry/result-app:latest ./result-app
docker push myregistry/result-app:latest

# Update k8s manifests to use myregistry/voting-app:latest, etc.
```

### 2. Apply Kubernetes Manifests

```powershell
# Apply all manifests at once
kubectl apply -f k8s/

# Or apply individually
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/voting-deployment.yaml
kubectl apply -f k8s/result-deployment.yaml
```

### 3. Verify Deployments

```powershell
kubectl get pods
kubectl get svc
kubectl describe deployment voting-app
```

### 4. Access Services via Port-Forwarding

In separate terminal windows:

```powershell
# Terminal 1: voting-app
kubectl port-forward svc/voting-app 5000:5000
```

```powershell
# Terminal 2: result-app
kubectl port-forward svc/result-app 8080:8080
```

Then visit `http://localhost:5000` and `http://localhost:8080/results`.

### 5. Scale Deployments

```powershell
# Scale voting-app to 3 replicas
kubectl scale deployment voting-app --replicas=3

# View updated pods
kubectl get pods
```

### 6. View Logs

```powershell
# Logs from voting-app pod
kubectl logs -l app=voting-app

# Logs from result-app pod
kubectl logs -l app=result-app

# Follow logs (tail -f)
kubectl logs -l app=voting-app -f
```

### 7. Cleanup

```powershell
kubectl delete -f k8s/
```

---

## Project Structure

```
votingapp-pro/
├── docker-compose.yml          # Local testing with Docker Compose
├── README.md                   # This file
│
├── voting-app/                 # Python Flask frontend
│   ├── Dockerfile
│   ├── app.py                  # Main Flask app
│   ├── requirements.txt         # Python dependencies
│   └── templates/
│       └── index.html          # Voting UI
│
├── result-app/                 # Node.js results API
│   ├── Dockerfile
│   ├── server.js               # Express app
│   └── package.json            # Node dependencies
│
└── k8s/                        # Kubernetes manifests
    ├── redis-deployment.yaml   # Redis deployment & service
    ├── voting-deployment.yaml  # Voting app deployment & service
    └── result-deployment.yaml  # Result app deployment & service
```

---

## Environment Variables

**voting-app and result-app:**
- `REDIS_HOST` - Redis hostname (default: `redis`)
- `REDIS_PORT` - Redis port (default: `6379`)
- `FLASK_APP` - Flask app file (voting-app only; default: `app.py`)

**result-app:**
- `PORT` - Server port (default: `8080`)

---

## Troubleshooting

### Docker Network Issues
If you see connection errors when pulling images, ensure:
1. Internet connection is stable
2. Docker Desktop settings → Resources → Network is configured correctly
3. Restart Docker Desktop

### Redis Connection Errors
Ensure `REDIS_HOST` environment variable matches the service name:
- Docker Compose: `redis` (service name)
- Kubernetes: `redis` (service DNS name)

### Port Already in Use
If ports 5000, 8080, or 6379 are already in use:
```powershell
# Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different ports in docker-compose.yml
```

### Kubernetes Image Pull Errors
For local clusters, ensure images are built/loaded before applying manifests:
```powershell
docker build -t voting-app:latest ./voting-app
docker build -t result-app:latest ./result-app
```

---

## Production Considerations

1. **Persistent Storage**: Use a StatefulSet or managed Redis service for production
2. **Ingress**: Add an Ingress controller for external access instead of port-forwarding
3. **Image Registry**: Push images to Docker Hub, AWS ECR, or your private registry
4. **Monitoring**: Add Prometheus/Grafana for metrics and Loki for centralized logging
5. **Security**: Use NetworkPolicies, RBAC, and secrets management (no hardcoded creds)
6. **Health Checks**: Add liveness and readiness probes to deployments
