# HAIC Benchmark — Kubernetes Deployment Guide

This directory contains clean, reusable Kubernetes manifests for deploying the HAIC Benchmark system from scratch.

## Quick Start

1. **Create namespace & secrets**: `kubectl apply -f 00-namespace.yaml && cp 01-secrets-template.yaml 01-secrets.yaml && kubectl apply -f 01-secrets.yaml`
2. **Create ConfigMap**: `kubectl apply -f 02-seed-metrics-configmap.yaml`
3. **Deploy postgres**: `kubectl apply -f 10-postgres-*.yaml`
4. **Run migrations**: `kubectl apply -f 20-init-db-job.yaml && kubectl wait --for=condition=complete job/init-db-migrations -n haic-benchmark --timeout=300s`
5. **Seed metrics**: `kubectl apply -f 21-seed-db-job.yaml && kubectl wait --for=condition=complete job/seed-db-metrics -n haic-benchmark --timeout=300s`
6. **Deploy backend & frontend**: `kubectl apply -f 30-*.yaml 40-*.yaml`

Or simply run: `./deploy.sh`

## Architecture

- **PostgreSQL** — Primary database with Alembic migrations
- **Backend** — FastAPI service (ghcr.io/gfragi/haic-backend:rollback)
- **Frontend** — Vue.js app (ghcr.io/gfragi/haic-frontend:rollback)
- **MinIO** — External object storage (managed separately)

### Secret for github registry

To create a secret for the GitHub registry, use the following command:

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<PAT_username> \
  --docker-password=<PAT_secret> \
  --namespace=benchmarking \
  --dry-run=client -o yaml
```

### Generate a Kubernetes secret

To generate a Kubernetes secret from a file, use the following command:

```bash
kubectl create secret generic benchmarking-secret \
  --from-env-file=k8s/.env \
  --namespace=benchmarking
```

### Generate a Kubernetes secret for the frontend

To generate a Kubernetes secret for the frontend, use the following command:

```bash
kubectl create secret generic frontend-secret \
  --from-env-file=frontend/.env \
  --namespace=benchmarking
```

## Build the Frontend Image

``` bash
docker build -f Dockerfile.frontend -t ghcr.io/gfragi/haic-frontend:latest .
```

## Build the Backend Image

``` bash
docker build -f Dockerfile.backend -t ghcr.io/gfragi/haic-backend:latest .
```

## Authenticate to GHCR

``` bash
source k8s/.env
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```

## Push the Images to GHCR

``` bash
docker push ghcr.io/gfragi/haic-backend:latest
docker push ghcr.io/gfragi/haic-frontend:latest
```

## Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install into the ingress-nginx namespace
kubectl create ns ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.publishService.enabled=true
```

## Install cert-manager & configure Let’s Encrypt

### Install cert-manager

```bash
# Install the CRDs
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.crds.yaml

# Create namespace
kubectl create namespace cert-manager

# Install cert-manager itself
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.12.0
```

### Create a Let’s Encrypt issuer

## Detailed Deployment Steps

### Step 1: Create Namespace

```bash
kubectl apply -f 00-namespace.yaml
```

### Step 2: Configure Secrets

1. Copy the template:
```bash
cp 01-secrets-template.yaml 01-secrets.yaml
```

2. Edit `01-secrets.yaml` and update ALL values (never use defaults):
   - `DB_PASSWORD` — Change from `changeme123` to a strong password
   - `DATABASE_URL` — Should match your deployment (usually fine as-is)
   - `MINIO_ENDPOINT` — Your MinIO endpoint
   - `MINIO_USERNAME` / `MINIO_PASSWORD` — MinIO credentials
   - `AUTH_URL` — Your authentication service
   - Frontend Keycloak settings

3. Apply:
```bash
kubectl apply -f 01-secrets.yaml
```

4. **IMPORTANT**: Add to `.gitignore`:
```bash
echo "01-secrets.yaml" >> .gitignore
```

### Step 3: Deploy PostgreSQL

```bash
kubectl apply -f 10-postgres-pvc.yaml
kubectl apply -f 11-postgres-service.yaml
kubectl apply -f 12-postgres-deployment.yaml
```

Verify:
```bash
kubectl rollout status deployment/postgres -n haic-benchmark
```

### Step 4: Run Alembic Migrations

```bash
kubectl apply -f 20-init-db-job.yaml
```

Monitor:
```bash
kubectl logs -f job/init-db-migrations -n haic-benchmark
```

Wait for completion:
```bash
kubectl wait --for=condition=complete job/init-db-migrations -n haic-benchmark --timeout=300s
```

### Step 4b: Seed Database with Metrics & Definitions

This step loads the initial metrics, metric groups, and their descriptions into the database. This is idempotent (safe to run multiple times).

```bash
kubectl apply -f 02-seed-metrics-configmap.yaml
kubectl apply -f 21-seed-db-job.yaml
```

Monitor:
```bash
kubectl logs -f job/seed-db-metrics -n haic-benchmark
```

Wait for completion:
```bash
kubectl wait --for=condition=complete job/seed-db-metrics -n haic-benchmark --timeout=300s
```

**What gets seeded:**
- 6 metric groups: Performance, Efficiency, Adaptability and Learning, Collaboration and Interaction, Trust and Safety, Robustness and Generalization
- 29 metrics with detailed descriptions provided to users
- All data is inserted with `ON CONFLICT DO NOTHING` to prevent duplicates on repeated runs

### Step 5: Deploy Backend

```bash
kubectl apply -f 30-backend-service.yaml
kubectl apply -f 31-backend-deployment.yaml
```

Verify:
```bash
kubectl rollout status deployment/backend -n haic-benchmark
kubectl logs -f deployment/backend -n haic-benchmark
```

### Step 6: Deploy Frontend

```bash
kubectl apply -f 40-frontend-service.yaml
kubectl apply -f 41-frontend-deployment.yaml
```

Verify:
```bash
kubectl rollout status deployment/frontend -n haic-benchmark
```

### Step 7: Test

Port-forward to access locally:

```bash
# Backend API
kubectl port-forward svc/backend 8000:8000 -n haic-benchmark
curl http://localhost:8000/api/meta/health

# Frontend
kubectl port-forward svc/frontend 8080:80 -n haic-benchmark
# Open browser to http://localhost:8080
```

## Updating Your Deployment

### New Code Release (No Schema Changes)

If you're only updating code (no database migrations):

```bash
# Edit 31-backend-deployment.yaml and update image tag
kubectl apply -f 31-backend-deployment.yaml
kubectl rollout status deployment/backend -n haic-benchmark
```

Or use the automated script:
```bash
./update.sh v2.0
```

### Code + Database Migrations

If your update includes new Alembic migrations:

**Option 1: Automated (recommended)**
```bash
./update.sh v2.0
```

The script will:
1. Run Alembic migrations
2. Wait for completion
3. Update backend image
4. Roll out the update

**Option 2: Manual steps**

```bash
# 1. Run migrations first
kubectl delete job init-db-migrations -n haic-benchmark
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n haic-benchmark --timeout=300s

# 2. Update image tag in 31-backend-deployment.yaml, then apply
kubectl apply -f 31-backend-deployment.yaml
kubectl rollout status deployment/backend -n haic-benchmark
```

**Important:** Always run migrations BEFORE updating the backend image. This prevents the backend from starting before the database schema is ready.

### Rollback

If something goes wrong:
```bash
kubectl rollout undo deployment/backend -n haic-benchmark
kubectl rollout status deployment/backend -n haic-benchmark
```

### Frontend Updates

Frontend updates don't require migrations - just update the image tag:

```bash
# Edit 41-frontend-deployment.yaml and update image tag
kubectl apply -f 41-frontend-deployment.yaml
kubectl rollout status deployment/frontend -n haic-benchmark
```

## Troubleshooting

### Backend pod won’t start

```bash
# Check logs
kubectl logs deployment/backend -n haic-benchmark

# Check events
kubectl describe pod -l app=backend -n haic-benchmark

# Test database connection
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n haic-benchmark -- \
  psql -h postgres -U haic_user -d haic_benchmark -c "SELECT 1;"
```

### Migrations failed

```bash
# View the job logs
kubectl logs job/init-db-migrations -n haic-benchmark

# If you need to retry
kubectl delete job init-db-migrations -n haic-benchmark
kubectl apply -f 20-init-db-job.yaml
kubectl logs -f job/init-db-migrations -n haic-benchmark
```

### Seed job failed

```bash
# Check seed job logs
kubectl logs job/seed-db-metrics -n haic-benchmark

# Verify metrics were seeded
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n haic-benchmark -- \
  psql -h postgres -U haic_user -d haic_benchmark -c "SELECT COUNT(*) FROM metrics;"

# If you need to retry (safe - uses ON CONFLICT DO NOTHING)
kubectl delete job seed-db-metrics -n haic-benchmark
kubectl apply -f 21-seed-db-job.yaml
kubectl logs -f job/seed-db-metrics -n haic-benchmark
```

### Frontend can’t reach backend

- Verify `VUE_APP_API_BASE_URL` in secret: `kubectl get secret haic-frontend-secret -n haic-benchmark -o yaml`
- Check frontend logs: `kubectl logs deployment/frontend -n haic-benchmark`
- Check backend is running: `kubectl get pods -n haic-benchmark | grep backend`

### View pod details

```bash
# List all pods
kubectl get pods -n haic-benchmark

# Describe a pod to see status and events
kubectl describe pod <pod-name> -n haic-benchmark

# Get pod logs
kubectl logs <pod-name> -n haic-benchmark

# Get previous logs (if pod crashed)
kubectl logs <pod-name> -n haic-benchmark --previous
```

## File Reference

| File | Purpose |
|------|---------|
| `00-namespace.yaml` | Kubernetes namespace definition |
| `01-secrets-template.yaml` | Template for secrets (copy and fill in values) |
| `02-seed-metrics-configmap.yaml` | ConfigMap with metric and definition seed data |
| `10-postgres-pvc.yaml` | Persistent volume for database |
| `11-postgres-service.yaml` | Service to expose postgres |
| `12-postgres-deployment.yaml` | PostgreSQL deployment |
| `20-init-db-job.yaml` | Alembic migrations job |
| `21-seed-db-job.yaml` | Seed metrics and definitions job |
| `30-backend-service.yaml` | Service to expose backend API |
| `31-backend-deployment.yaml` | Backend deployment (with init containers) |
| `40-frontend-service.yaml` | Service to expose frontend |
| `41-frontend-deployment.yaml` | Frontend deployment |
| `deploy.sh` | Automated deployment script |
| `update.sh` | Automated update script (runs migrations + updates backend) |

## Cleanup

To remove everything:

```bash
kubectl delete namespace haic-benchmark
