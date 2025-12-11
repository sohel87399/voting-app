# Voting App - Technical Implementation Guide

## Overview

This is a complete 3-tier distributed application demonstrating Docker containerization and Kubernetes orchestration:

1. **Voting App** (Python Flask) - Frontend for casting votes
2. **Result App** (Node.js Express) - API for retrieving vote counts
3. **Redis** - In-memory data store for vote persistence

---

## File Descriptions

### Application Code

#### `voting-app/app.py`
- Flask web server on port 5000
- Serves HTML form with voting buttons (Cats vs Dogs)
- Stores votes in Redis hash with key `votes`
- Endpoints:
  - `GET /` - Renders voting page
  - `POST /vote` - Accepts vote via form or JSON
  - `GET /results` - JSON API returning vote counts

#### `voting-app/templates/index.html`
- Simple voting UI with two buttons
- JavaScript polls `/results` every 3 seconds to show live count updates

#### `result-app/server.js`
- Express.js server on port 8080
- Single endpoint: `GET /results` returns JSON with vote counts
- Connects to Redis and reads from the `votes` hash
- Includes CORS for cross-origin requests

#### `voting-app/requirements.txt` & `result-app/package.json`
- Dependencies for each app
- Flask, Redis Python client for voting-app
- Express, Redis Node.js client for result-app

### Docker Configuration

#### `voting-app/Dockerfile`
- Base: Python 3.11-slim (minimal image, ~150MB)
- Installs dependencies from requirements.txt
- Runs with gunicorn (production-ready WSGI server, 2 workers)
- Listens on 0.0.0.0:5000

#### `result-app/Dockerfile`
- Base: Node.js 20-alpine (minimal image, ~170MB)
- Installs production dependencies only
- Runs with node server.js
- Listens on 0.0.0.0:8080

#### `docker-compose.yml`
- Defines 3 services: redis, voting-app, result-app
- Sets up custom bridge network for inter-service communication
- Port mappings for local access
- Environment variables for service discovery (REDIS_HOST=redis)
- `depends_on` ensures Redis starts before apps

### Kubernetes Manifests

#### `k8s/redis-deployment.yaml`
```yaml
Deployment:
  - replicas: 1
  - image: redis:7.0-alpine
  - containerPort: 6379

Service:
  - type: ClusterIP (internal cluster DNS)
  - port: 6379
  - selector: app=redis
```

#### `k8s/voting-deployment.yaml`
```yaml
Deployment:
  - replicas: 2 (for high availability)
  - image: voting-app:latest
  - port: 5000
  - env: REDIS_HOST=redis (service DNS name)

Service:
  - type: ClusterIP
  - port: 5000
  - For external access, add Ingress or use port-forward
```

#### `k8s/result-deployment.yaml`
```yaml
Deployment:
  - replicas: 1
  - image: result-app:latest
  - port: 8080
  - env: REDIS_HOST=redis

Service:
  - type: ClusterIP
  - port: 8080
```

---

## How It Works

### Docker Compose Flow

1. **Start**: `docker-compose up --build`
2. **Network**: Creates `voting-network` bridge network
3. **Service Order**:
   - Redis container starts
   - Voting-app and result-app wait for Redis (depends_on)
   - Both apps connect via `redis` (DNS resolved by Docker)
4. **Port Access**:
   - localhost:5000 → voting-app:5000
   - localhost:8080 → result-app:8080
   - localhost:6379 → redis:6379 (for debugging)

### Kubernetes Flow

1. **Build & Load**: Images must exist locally or in a registry
2. **Apply Manifests**: `kubectl apply -f k8s/`
3. **Scheduler**:
   - Kubernetes creates pods for each deployment
   - Pods get IP addresses within cluster network
   - Service `redis` gets a stable internal DNS name
   - Voting and result apps discover Redis via DNS
4. **External Access**: Use `kubectl port-forward` to tunnel local ports to services

---

## Key Design Decisions

### Image Choices
- **Python 3.11-slim**: Minimal Python image, no unnecessary packages
- **Node.js 20-alpine**: Alpine Linux for smallest footprint (~170MB)
- **redis:7.0-alpine**: Official Redis, small and latest stable version

### Network Architecture
- **Docker Compose**: Services communicate via custom bridge network
- **Kubernetes**: Services use ClusterIP and DNS for internal communication
- **External Access**: Both use port-forwarding/mapping for local testing

### Data Storage
- Redis runs in-memory (ephemeral)
- For production: Use StatefulSet or managed Redis service

### Scaling
- **Docker Compose**: Limited to single host
- **Kubernetes**: Easily scale with `kubectl scale deployment voting-app --replicas=N`

### Environment Variables
- Loose coupling: Apps read REDIS_HOST from env (default: "redis")
- Easy to override for different environments

---

## Build & Deploy Commands Summary

### Local Testing (Docker Compose)
```powershell
# Build images
docker build -t voting-app:local ./voting-app
docker build -t result-app:local ./result-app

# Or build via docker-compose
docker-compose build

# Start
docker-compose up -d

# Check status
docker-compose ps

# Cleanup
docker-compose down
```

### Kubernetes
```powershell
# Build images
docker build -t voting-app:latest ./voting-app
docker build -t result-app:latest ./result-app

# Deploy
kubectl apply -f k8s/

# Verify
kubectl get pods
kubectl get svc

# Port-forward (in separate terminals)
kubectl port-forward svc/voting-app 5000:5000
kubectl port-forward svc/result-app 8080:8080

# Scale
kubectl scale deployment voting-app --replicas=3

# Cleanup
kubectl delete -f k8s/
```

---

## Troubleshooting

### Images Won't Build
- Check internet connectivity (Docker pulls base images)
- Verify Docker Desktop is running: `docker version`
- Check disk space: `docker system df`

### Services Can't Connect to Redis
- **Docker Compose**: Ensure service name in env var matches service name in compose file
- **Kubernetes**: Verify service exists: `kubectl get svc redis`
- Check Redis is running: `kubectl logs -l app=redis`

### Ports in Use
```powershell
# Find process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Kubernetes Image Pull Errors
- For local k8s (Docker Desktop), images must be built locally: `docker build ...`
- For remote registry, push images: `docker push myregistry/voting-app:latest`

---

## Next Steps (Production)

1. **Storage**: Migrate to persistent Redis (Redis Cloud, AWS ElastiCache)
2. **Ingress**: Replace port-forward with Ingress controller for production URLs
3. **Logging**: Add EFK stack (Elasticsearch, Fluentd, Kibana) or Loki
4. **Monitoring**: Add Prometheus + Grafana for metrics
5. **Security**: Add NetworkPolicy, RBAC, secrets management
6. **Health Checks**: Add liveness/readiness probes
7. **CI/CD**: Automate builds and deployments with GitHub Actions/GitLab CI
