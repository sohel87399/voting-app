# Voting App - Complete Workflow Guide

## Overview

This document explains the entire workflow of the Voting App project, from local development to Kubernetes deployment.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     End User                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐         ┌────▼──────┐
   │ Voting   │         │ Results   │
   │ App      │         │ Dashboard │
   │ Port 5000│         │ Port 8080 │
   └────┬─────┘         └────┬──────┘
        │                    │
        └────────┬───────────┘
                 │
            ┌────▼─────────┐
            │   Redis      │
            │  Port 6379   │
            │  Vote Store  │
            └──────────────┘
```

---

## Development Workflow

### 1. **Local Development (Your Machine)**

#### Step 1.1: Clone & Setup
```bash
git clone https://github.com/sohel87399/voting-app.git
cd voting-app
```

#### Step 1.2: Project Structure
```
voting-app/
├── voting-app/          # Flask frontend (Python)
│   ├── app.py          # Main Flask app
│   ├── Dockerfile      # Container config
│   ├── requirements.txt # Dependencies
│   └── templates/
│       └── index.html  # Voting UI
│
├── result-app/         # Results API (Flask)
│   ├── server.py       # Main Flask app
│   ├── Dockerfile      # Container config
│   ├── requirements.txt # Dependencies
│   ├── templates/
│   │   └── index.html  # Results UI with Chart.js
│   └── static/
│       └── style.css   # Styling
│
├── docker-compose.yml  # Local dev setup
├── k8s/                # Kubernetes manifests
│   ├── redis-deployment.yaml
│   ├── voting-deployment.yaml
│   └── result-deployment.yaml
│
└── README.md           # Documentation
```

---

## Workflow Steps

### **Phase 1: Local Testing with Docker Compose**

#### Command 1: Build Images
```powershell
cd C:\Users\LENOVO\OneDrive\Desktop\votingapp-pro
docker build -t voting-app:latest ./voting-app
docker build -t result-app:latest ./result-app
```

**What happens:**
- Reads `Dockerfile` from each app folder
- Pulls Python 3.11-slim base image
- Installs dependencies from `requirements.txt`
- Copies source code into image
- Layers are cached for faster builds

#### Command 2: Start Services with Docker Compose
```powershell
docker-compose up -d
```

**What happens:**
- Reads `docker-compose.yml`
- Creates a custom bridge network (`voting-network`)
- Starts 3 containers:
  - `voting-redis` (redis:7.0-alpine)
  - `voting-app` (port 5000)
  - `result-app` (port 8080)
- Services can talk to each other via DNS names

#### Command 3: Verify Services
```powershell
docker-compose ps
docker-compose logs -f
```

**Expected output:**
```
NAME           STATUS          PORTS
voting-redis   Up 2 minutes    0.0.0.0:6379->6379/tcp
voting-app     Up 2 minutes    0.0.0.0:5000->5000/tcp
result-app     Up 2 minutes    0.0.0.0:8080->8080/tcp
```

#### Command 4: Test in Browser
- **Voting App**: http://localhost:5000
  - Click "Vote Cats" or "Vote Dogs"
  - See live count updates
- **Results Dashboard**: http://localhost:8080
  - See Chart.js bar chart
  - Live count updates every 2 seconds

---

### **Phase 2: Data Flow in Running App**

#### Vote Submission Flow
```
1. User clicks "Vote Cats" button on http://localhost:5000
   │
2. JavaScript sends POST request to /vote endpoint
   │
3. voting-app/app.py receives vote
   │
4. app.py increments Redis hash: r.hincrby('votes', 'Cats', 1)
   │
5. Redis updates in-memory data: {Cats: 5, Dogs: 3}
   │
6. JavaScript polls /results endpoint (every 2 seconds)
   │
7. result-app/server.py fetches from Redis
   │
8. Returns JSON: {"Cats": 5, "Dogs": 3}
   │
9. UI updates progress bars and counters
```

#### Data Storage
```
Redis Hash: "votes"
├── Cats → 5
├── Dogs → 3
└── (ephemeral, lost if Redis restarts)
```

---

### **Phase 3: Docker Image Layers**

#### Voting App Image Build Layers
```
Layer 1: FROM python:3.11-slim
         └─ 150 MB base image

Layer 2: COPY requirements.txt
         └─ Flask, redis client

Layer 3: RUN pip install
         └─ Compile dependencies

Layer 4: COPY . /app
         └─ Source code (app.py, templates/)

Result: voting-app:latest (~214 MB)
```

#### Result App Image Build Layers
```
Layer 1: FROM python:3.11-slim
         └─ 150 MB base image

Layer 2: COPY requirements.txt
         └─ Flask, redis client

Layer 3: RUN pip install
         └─ Compile dependencies

Layer 4: COPY . /app
         └─ Source code (server.py, templates/)

Result: result-app:latest (~214 MB)
```

---

### **Phase 4: Pushing to GitHub**

#### Step 4.1: Add Remote Repository
```powershell
git remote add origin https://github.com/sohel87399/voting-app.git
```

#### Step 4.2: Rename Branch (if needed)
```powershell
git branch -M main
```

#### Step 4.3: Push to GitHub
```powershell
git push -u origin main
```

**What happens:**
- All commits, files, and history are uploaded to GitHub
- GitHub creates branches, tags, and references
- Code is now publicly/privately available
- Others can clone and collaborate

---

### **Phase 5: Kubernetes Deployment**

#### Step 5.1: Push Images to Registry
```powershell
# Tag images for Docker Hub
docker tag voting-app:latest YOUR_USERNAME/voting-app:latest
docker tag result-app:latest YOUR_USERNAME/result-app:latest

# Push to registry
docker push YOUR_USERNAME/voting-app:latest
docker push YOUR_USERNAME/result-app:latest
```

#### Step 5.2: Update K8s Manifests
Edit `k8s/voting-deployment.yaml`:
```yaml
spec:
  containers:
  - name: voting-app
    image: YOUR_USERNAME/voting-app:latest  # Update this line
```

Edit `k8s/result-deployment.yaml`:
```yaml
spec:
  containers:
  - name: result-app
    image: YOUR_USERNAME/result-app:latest  # Update this line
```

#### Step 5.3: Deploy to Cluster
```powershell
# Connect to Kubernetes cluster
kubectl cluster-info

# Apply manifests
kubectl apply -f k8s/

# Verify
kubectl get pods
kubectl get svc
```

**K8s Objects Created:**
```
Deployments (3):
├── redis → 1 replica
├── voting-app → 2 replicas
└── result-app → 1 replica

Services (3):
├── redis:6379 (ClusterIP)
├── voting-app:5000 (ClusterIP)
└── result-app:8080 (ClusterIP)

Pods (4):
├── redis-xxx
├── voting-app-xxx
├── voting-app-yyy
└── result-app-zzz
```

#### Step 5.4: Access Services
```powershell
# Port-forward voting app
kubectl port-forward svc/voting-app 5000:5000

# Port-forward results
kubectl port-forward svc/result-app 8080:8080

# Access in browser
# http://localhost:5000
# http://localhost:8080
```

#### Step 5.5: Scale Deployment
```powershell
# Increase replicas
kubectl scale deployment voting-app --replicas=5

# Watch scaling
kubectl get pods -w
```

---

## Complete Command Reference

### Docker Compose Workflow
```powershell
# Build
docker-compose build

# Start
docker-compose up -d

# View status
docker-compose ps

# Logs
docker-compose logs -f voting-app
docker-compose logs -f result-app
docker-compose logs -f redis

# Stop
docker-compose stop

# Remove
docker-compose down
docker-compose down -v  # with data cleanup
```

### Manual Docker Commands
```powershell
# Build individual images
docker build -t voting-app:latest ./voting-app
docker build -t result-app:latest ./result-app

# Run containers manually
docker run -d --name redis -p 6379:6379 redis:7.0-alpine
docker run -d --name voting-app -p 5000:5000 -e REDIS_HOST=redis voting-app:latest
docker run -d --name result-app -p 8080:8080 -e REDIS_HOST=redis result-app:latest

# View containers
docker ps
docker ps -a

# Inspect container
docker inspect voting-app

# View logs
docker logs voting-app
docker logs -f result-app

# Execute command in container
docker exec voting-app ls -la
docker exec voting-redis redis-cli HGETALL votes

# Stop containers
docker stop voting-app result-app redis
docker rm voting-app result-app redis
```

### Git Workflow
```powershell
# Initialize repo
git init
git add -A
git commit -m "Initial commit"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/voting-app.git

# Check remote
git remote -v

# Push
git push -u origin main

# Pull (to get latest)
git pull origin main

# View history
git log --oneline
git show COMMIT_HASH
```

### Kubernetes Workflow
```powershell
# Cluster info
kubectl cluster-info
kubectl get nodes

# Deploy
kubectl apply -f k8s/
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/voting-deployment.yaml
kubectl apply -f k8s/result-deployment.yaml

# Check status
kubectl get pods
kubectl get svc
kubectl get deployments
kubectl describe pod POD_NAME

# Logs
kubectl logs POD_NAME
kubectl logs -l app=voting-app
kubectl logs -f DEPLOYMENT_NAME

# Port-forward
kubectl port-forward svc/voting-app 5000:5000
kubectl port-forward svc/result-app 8080:8080

# Scale
kubectl scale deployment voting-app --replicas=3

# Delete
kubectl delete -f k8s/
kubectl delete pod POD_NAME
```

---

## Environment Variables

### Voting App
- `REDIS_HOST` (default: "redis") - Redis hostname
- `REDIS_PORT` (default: 6379) - Redis port
- `FLASK_APP` (default: "app.py") - Flask app file

### Result App
- `REDIS_HOST` (default: "redis") - Redis hostname
- `REDIS_PORT` (default: 6379) - Redis port
- `PORT` (default: 8080) - Server port

---

## Testing Endpoints

### Voting App
```
GET http://localhost:5000/
  - Returns voting page (HTML)

POST http://localhost:5000/vote
  - Body: {"choice": "Cats"}
  - Response: {"ok": true}

GET http://localhost:5000/results
  - Response: {"Cats": 5, "Dogs": 3}
```

### Result App
```
GET http://localhost:8080/
  - Returns dashboard (HTML with Chart.js)

GET http://localhost:8080/results
  - Response: {"Cats": 5, "Dogs": 3}
```

---

## CI/CD Pipeline (Optional - Future)

```
1. Developer pushes to GitHub
   ↓
2. GitHub Actions triggers build
   ↓
3. Docker images built and tested
   ↓
4. Push images to Docker Registry
   ↓
5. Update K8s manifests
   ↓
6. Deploy to cluster automatically
   ↓
7. Smoke tests run
   ↓
8. Notify on success/failure
```

---

## Troubleshooting Workflow

### Issue: Services won't start
```powershell
# 1. Check Docker is running
docker --version

# 2. Check logs
docker-compose logs

# 3. Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Can't vote / Redis error
```powershell
# 1. Check Redis is up
docker-compose ps redis

# 2. Check Redis connection
docker exec voting-redis redis-cli ping
# Expected: PONG

# 3. Check votes data
docker exec voting-redis redis-cli HGETALL votes
```

### Issue: Port already in use
```powershell
# 1. Find process
netstat -ano | findstr :5000

# 2. Kill process
taskkill /PID <PID> /F

# 3. Or change docker-compose ports
# Edit docker-compose.yml and restart
```

---

## Summary

**Local Dev Loop:**
1. Edit code → 2. Rebuild image → 3. Restart container → 4. Test in browser

**Deployment Flow:**
1. Code on GitHub → 2. Build image → 3. Push to registry → 4. Update K8s → 5. Deploy to cluster

**Data Flow:**
User votes → Flask app → Redis → Dashboard fetches → Chart updates
