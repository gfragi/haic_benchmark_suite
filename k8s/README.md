# HAIC Benchmark — Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the HAIC Benchmark system from scratch.

## Quick Start

```bash
./deploy.sh
```

Or step by step (from the `k8s/` directory):

```bash
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-secrets.yaml
kubectl apply -f 02-seed-metrics-configmap.yaml
kubectl apply -f 10-postgres-pvc.yaml 11-postgres-service.yaml 12-postgres-deployment.yaml
kubectl rollout status deployment/postgres -n haic-benchmark --timeout=120s
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n haic-benchmark --timeout=300s
kubectl apply -f 21-seed-db-job.yaml
kubectl wait --for=condition=complete job/seed-db-metrics -n haic-benchmark --timeout=120s
kubectl apply -f 30-backend-service.yaml 31-backend-deployment.yaml
kubectl apply -f 40-frontend-service.yaml 41-frontend-deployment.yaml
```

## Architecture

- **PostgreSQL** — Primary database, managed with Alembic migrations
- **Backend** — FastAPI service (`ghcr.io/gfragi/haic-backend:rollback`)
- **Frontend** — Vue.js app (`ghcr.io/gfragi/haic-frontend:rollback`)
- **MinIO** — External object storage (managed separately, outside k8s)

## Build & Push Images

Images must be built for `linux/amd64` (the cluster node architecture) even when building on an Apple Silicon Mac.

```bash
# Authenticate
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

# Build and push backend
docker buildx build --platform linux/amd64 \
  -f Dockerfile.backend \
  -t ghcr.io/gfragi/haic-backend:rollback \
  . --push

# Build and push frontend
docker buildx build --platform linux/amd64 \
  -f Dockerfile.frontend \
  -t ghcr.io/gfragi/haic-frontend:rollback \
  . --push
```

### If the cluster node cannot reach ghcr.io

If the node has no reliable outbound internet, import images directly:

```bash
# Save locally (use --load instead of --push in the build step above)
docker save ghcr.io/gfragi/haic-backend:rollback | ssh <user>@<node-ip> 'microk8s ctr images import -'
docker save ghcr.io/gfragi/haic-frontend:rollback | ssh <user>@<node-ip> 'microk8s ctr images import -'
```

> **Image pull policy**: Deployments use `imagePullPolicy: IfNotPresent`. If you push a new image under the same tag, the node will not re-pull it automatically. Either import the image directly (above) or temporarily set `imagePullPolicy: Always` in the relevant manifest and revert it after the pod starts.

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

2. Edit `01-secrets.yaml` and update all values:
   - `DB_PASSWORD` — strong password
   - `DATABASE_URL` — must match `DB_*` values
   - `MINIO_ENDPOINT` — your MinIO endpoint (host:port)
   - `MINIO_USERNAME` / `MINIO_PASSWORD` — MinIO credentials
   - `AUTH_URL` — Keycloak token endpoint (leave empty to disable)
   - `KEYCLOAK_*` — frontend Keycloak settings

3. Apply:
```bash
kubectl apply -f 01-secrets.yaml
```

4. Keep out of git:

```bash
echo "k8s/01-secrets.yaml" >> .gitignore
```

### Step 3: Deploy PostgreSQL

```bash
kubectl apply -f 10-postgres-pvc.yaml
kubectl apply -f 11-postgres-service.yaml
kubectl apply -f 12-postgres-deployment.yaml
kubectl rollout status deployment/postgres -n haic-benchmark --timeout=120s
```

### Step 4: Run Alembic Migrations

```bash
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n haic-benchmark --timeout=300s
```

Monitor live:
```bash
kubectl logs -f job/init-db-migrations -n haic-benchmark
```

The migration job uses `nc -z postgres 5432` to wait for the database (the backend image does not include `psql` or `pg_isready`).

### Step 4b: Seed Database

Loads metric groups, metrics, and definitions. Safe to run multiple times — uses `ON CONFLICT (name)` which requires the unique index created by the migration.

```bash
kubectl apply -f 21-seed-db-job.yaml
kubectl wait --for=condition=complete job/seed-db-metrics -n haic-benchmark --timeout=120s
```

**What gets seeded:**
- 6 metric groups: Performance, Efficiency, Adaptability and Learning, Collaboration and Interaction, Trust and Safety, Robustness and Generalization
- 29 metrics with descriptions

### Step 5: Deploy Backend

```bash
kubectl apply -f 30-backend-service.yaml
kubectl apply -f 31-backend-deployment.yaml
kubectl rollout status deployment/backend -n haic-benchmark
```

The backend pod has an init container (`wait-for-db-migration`) that uses `nc -z postgres 5432` before starting the API.

### Step 6: Deploy Frontend

```bash
kubectl apply -f 40-frontend-service.yaml
kubectl apply -f 41-frontend-deployment.yaml
kubectl rollout status deployment/frontend -n haic-benchmark
```

### Step 7: Verify

```bash
# Backend health
kubectl port-forward svc/backend 8000:8000 -n haic-benchmark
curl http://localhost:8000/meta/health

# Frontend
kubectl port-forward svc/frontend 8080:80 -n haic-benchmark
# Open http://localhost:8080
```

> Note: the health endpoint is `/meta/health`, not `/api/meta/health`. The `/api/v1` prefix applies only to application routes.

## Updating the Deployment

### Code-only update (no schema changes)

```bash
./update.sh
```

Or manually:
```bash
kubectl rollout restart deployment/backend -n haic-benchmark
kubectl rollout status deployment/backend -n haic-benchmark
```

### Update with new Alembic migrations

```bash
./update.sh --migrate
```

Or manually:
```bash
kubectl delete job init-db-migrations -n haic-benchmark --ignore-not-found
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n haic-benchmark --timeout=300s
kubectl rollout restart deployment/backend -n haic-benchmark
kubectl rollout status deployment/backend -n haic-benchmark
```

**Always run migrations before restarting the backend.**

### Rollback

```bash
kubectl rollout undo deployment/backend -n haic-benchmark
kubectl rollout status deployment/backend -n haic-benchmark
```

### Frontend update

```bash
kubectl rollout restart deployment/frontend -n haic-benchmark
kubectl rollout status deployment/frontend -n haic-benchmark
```

## Troubleshooting

### Pod stuck in ContainerCreating

Usually an image pull problem. Check events:
```bash
kubectl describe pod -l app=backend -n haic-benchmark | grep -A 20 Events
```

If the node cached an old image with the same tag and won't re-pull:
```bash
# On the node
microk8s ctr images rm ghcr.io/gfragi/haic-backend:rollback
# Then delete and reapply the job/deployment
```

Or import the new image directly (see Build & Push section above).

### Migrations failed

```bash
kubectl logs job/init-db-migrations -n haic-benchmark

# Retry
kubectl delete job init-db-migrations -n haic-benchmark --ignore-not-found
kubectl apply -f 20-init-db-job.yaml
```

### Seed job failed

```bash
kubectl logs job/seed-db-metrics -n haic-benchmark

# Verify data
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n haic-benchmark -- \
  psql -h postgres -U haic_user -d haic_benchmark -c "SELECT COUNT(*) FROM metrics;"

# Retry (idempotent)
kubectl delete job seed-db-metrics -n haic-benchmark --ignore-not-found
kubectl apply -f 21-seed-db-job.yaml
```

### Backend won't start

```bash
kubectl logs deployment/backend -n haic-benchmark
kubectl describe pod -l app=backend -n haic-benchmark
```

Test database connectivity directly:
```bash
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n haic-benchmark -- \
  psql -h postgres -U haic_user -d haic_benchmark -c "SELECT 1;"
```

### Namespace stuck in Terminating

```bash
kubectl proxy &
kubectl get namespace haic-benchmark -o json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); d['spec']['finalizers']=[]; print(json.dumps(d))" \
  | curl -s -k -H "Content-Type: application/json" -X PUT \
    http://127.0.0.1:8001/api/v1/namespaces/haic-benchmark/finalize -d @-
kill %1
```

## File Reference

| File | Purpose |
| ---- | ------- |
| `00-namespace.yaml` | Namespace definition |
| `01-secrets-template.yaml` | Template — copy to `01-secrets.yaml` and fill in values |
| `01-secrets.yaml` | Actual secrets (gitignored) |
| `02-seed-metrics-configmap.yaml` | ConfigMap with seed SQL |
| `10-postgres-pvc.yaml` | Persistent volume for database |
| `11-postgres-service.yaml` | PostgreSQL service |
| `12-postgres-deployment.yaml` | PostgreSQL deployment |
| `20-init-db-job.yaml` | Alembic migrations job |
| `21-seed-db-job.yaml` | Seed metrics and definitions |
| `30-backend-service.yaml` | Backend service |
| `31-backend-deployment.yaml` | Backend deployment (includes DB-ready init container) |
| `40-frontend-service.yaml` | Frontend service |
| `41-frontend-deployment.yaml` | Frontend deployment |
| `deploy.sh` | Full deployment from scratch |
| `update.sh` | Rolling update (code-only or with migrations) |
| `seed-metrics.sql` | SQL loaded into the seed ConfigMap |

## Cleanup

```bash
kubectl delete namespace haic-benchmark
```

If stuck, see the "Namespace stuck in Terminating" section above.
