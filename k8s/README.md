# HAIC Benchmark — Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the HAIC Benchmark system from scratch.

## Quick Start

```bash
./50_deploy.sh
```

Or step by step (from the `k8s/` directory):

```bash
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-secrets.yaml
kubectl apply -f 02-seed-metrics-configmap.yaml
kubectl apply -f 10-postgres-pvc.yaml 11-postgres-service.yaml 12-postgres-deployment.yaml
kubectl rollout status deployment/postgres -n benchmarking --timeout=120s
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n benchmarking --timeout=300s
kubectl apply -f 21-seed-db-job.yaml
kubectl wait --for=condition=complete job/seed-db-metrics -n benchmarking --timeout=120s
kubectl apply -f 30-backend-service.yaml 31-backend-deployment.yaml
kubectl apply -f 40-frontend-service.yaml 41-frontend-deployment.yaml
```

## Architecture

- **PostgreSQL** — Primary database, managed with Alembic migrations
- **Backend** — FastAPI service (`ghcr.io/gfragi/haic-backend:latest`) — has no
  authentication of its own; Keycloak only gates the frontend UI, so anything
  that can reach this Service can call it directly. Restrict network exposure
  if that's not acceptable on your cluster.
- **Frontend** — React app served via nginx (`ghcr.io/gfragi/haic-frontend-react:latest`).
  Its Keycloak client id/realm/URL and API base path are baked into the JS
  bundle at **Docker build time** from `frontend-react/.env.production` — they
  are not runtime-configurable via env vars or a k8s Secret. To point a build
  at a different Keycloak realm/client or API host, edit that file and rebuild
  the image before pushing.
- **MinIO** — External object storage (managed separately, outside k8s)

> The old Vue.js frontend (`frontend/`, `Dockerfile.frontend`) is retired — the
> React frontend above is the current and only supported one.

## Build & Push Images

Images must be built for `linux/amd64` (the cluster node architecture) even if building on an Apple Silicon Mac.

```bash
# Authenticate
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

# Build and push backend
docker buildx build --platform linux/amd64 \
  -f Dockerfile.backend \
  -t ghcr.io/gfragi/haic-backend:latest \
  . --push

# Build and push frontend (edit frontend-react/.env.production first if you
# need a different Keycloak realm/client/API host than what's currently there)
docker buildx build --platform linux/amd64 \
  -f Dockerfile.frontend-react \
  -t ghcr.io/gfragi/haic-frontend-react:latest \
  . --push
```

> **Known inconsistency to check before relying on this:** `20-init-db-job.yaml`
> currently pins `ghcr.io/gfragi/haic-backend:rollback` for running migrations,
> while `31-backend-deployment.yaml` runs `ghcr.io/gfragi/haic-backend:latest`
> for the API itself. If those two tags point at different code, migrations
> could run against a different schema version than the API expects. Confirm
> which tag is actually current before a from-scratch deploy, and align both
> files to the same one.

### If the cluster node cannot reach ghcr.io

If the node has no reliable outbound internet, import images directly:

```bash
# Save locally (use --load instead of --push in the build step above)
docker save ghcr.io/gfragi/haic-backend:latest | ssh <user>@<node-ip> 'microk8s ctr images import -'
docker save ghcr.io/gfragi/haic-frontend-react:latest | ssh <user>@<node-ip> 'microk8s ctr images import -'
```

> **Image pull policy**: the backend Deployment uses `imagePullPolicy: IfNotPresent` — if you push a new image under the same tag, the node will not re-pull it automatically; either import the image directly (above), `kubectl delete pod` to force a re-pull if the tag changed upstream, or temporarily set `imagePullPolicy: Always` and revert after the pod starts. The frontend Deployment already uses `imagePullPolicy: Always`, so it re-pulls on every rollout.

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
   - `MINIO_USERNAME` / `MINIO_PASSWORD` — MinIO access key / secret key
   - `AUTH_URL` — only for MinIO/S3 behind a Keycloak-style OAuth token
     exchange (uncommon). Leave it as an **empty string**, not commented out —
     `31-backend-deployment.yaml` references this key without `optional: true`,
     so a missing key (as opposed to an empty value) crashes the backend pod
     with `CreateContainerConfigError`.

   There is no `KEYCLOAK_*` / frontend entry here — frontend Keycloak config
   is not part of this secret at all (see Architecture above). If you need
   different Keycloak settings, edit `frontend-react/.env.production` and
   rebuild the frontend image instead.

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
kubectl rollout status deployment/postgres -n benchmarking --timeout=120s
```

### Step 4: Run Alembic Migrations

```bash
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n benchmarking --timeout=300s
```

Monitor live:
```bash
kubectl logs -f job/init-db-migrations -n benchmarking
```

The migration job uses `nc -z postgres 5432` to wait for the database (the backend image does not include `psql` or `pg_isready`).

### Step 4b: Seed Database

Loads metric groups, metrics, and definitions. Safe to run multiple times — uses `ON CONFLICT (name)` which requires the unique index created by the migration.

```bash
kubectl apply -f 21-seed-db-job.yaml
kubectl wait --for=condition=complete job/seed-db-metrics -n benchmarking --timeout=120s
```

**What gets seeded:**
- 6 metric groups: Performance, Efficiency, Adaptability and Learning, Collaboration and Interaction, Trust and Safety, Robustness and Generalization
- 29 metrics with descriptions

### Step 5: Deploy Backend

```bash
kubectl apply -f 30-backend-service.yaml
kubectl apply -f 31-backend-deployment.yaml
kubectl rollout status deployment/backend -n benchmarking
```

The backend pod has an init container (`wait-for-db-migration`) that uses `nc -z postgres 5432` before starting the API.

### Step 6: Deploy Frontend

```bash
kubectl apply -f 40-frontend-service.yaml
kubectl apply -f 41-frontend-deployment.yaml
kubectl rollout status deployment/frontend -n benchmarking
```

### Step 7: Verify

```bash
# Backend health
kubectl port-forward svc/backend 8000:8000 -n benchmarking
curl http://localhost:8000/meta/health

# Frontend
kubectl port-forward svc/frontend 8080:80 -n benchmarking
# Open http://localhost:8080
```

> Note: the health endpoint is `/meta/health`, not `/api/meta/health`. The `/api/v1` prefix applies only to application routes.
>
> **Port-forward testing gap:** the frontend's nginx image only serves static
> files — it does not proxy `/api` or `/meta` anywhere the way the Vite dev
> server does locally. `kubectl port-forward svc/frontend ...` will load the
> page shell, but every API call will hit nginx's SPA fallback and get HTML
> back instead of JSON. That path-based routing only happens at the Ingress
> layer (see Ingress & TLS below). To test end-to-end before wiring ingress,
> either `kubectl port-forward svc/backend 8000:8000` and run `npm run dev`
> locally in `frontend-react/` with `VITE_API_PROXY_TARGET=http://localhost:8000`,
> or apply a temporary namespace-scoped Ingress with its own test hostname.

## Updating the Deployment

### Code-only update (no schema changes)

```bash
./update.sh
```

Or manually:
```bash
kubectl rollout restart deployment/backend -n benchmarking
kubectl rollout status deployment/backend -n benchmarking
```

### Update with new Alembic migrations

```bash
./update.sh --migrate
```

Or manually:
```bash
kubectl delete job init-db-migrations -n benchmarking --ignore-not-found
kubectl apply -f 20-init-db-job.yaml
kubectl wait --for=condition=complete job/init-db-migrations -n benchmarking --timeout=300s
kubectl rollout restart deployment/backend -n benchmarking
kubectl rollout status deployment/backend -n benchmarking
```

**Always run migrations before restarting the backend.**

### Rollback

```bash
kubectl rollout undo deployment/backend -n benchmarking
kubectl rollout status deployment/backend -n benchmarking
```

### Frontend update

```bash
kubectl rollout restart deployment/frontend -n benchmarking
kubectl rollout status deployment/frontend -n benchmarking
```

## Ingress & TLS

External traffic (hostname, TLS) is not covered by the Deployments/Services
above — it's wired separately via an Ingress.

1. Edit `frontend_ingress.yaml` (underscore, not hyphen — see note below) and
   update the hostname and TLS secret name:

   ```yaml
   rules:
     - host: your-domain.example.com   # ← your domain
   tls:
     - hosts: [your-domain.example.com]
       secretName: your-tls-secret-name
   ```

   Remove the `tls:` block and `cert-manager.io/cluster-issuer` annotation if
   you're not using cert-manager.

2. Apply it:

   ```bash
   kubectl apply -f frontend_ingress.yaml -n benchmarking
   ```

> **Only one ingress file:** `frontend_ingress.yaml` (underscore) is the
> current, correct one — it routes both `/api` → `backend:8000` and `/` →
> `frontend:80`, and its issuer name matches `cluster_issuer.yaml`. A
> duplicate `frontend-ingress.yaml` (hyphen) previously existed with a
> different issuer and hostname and has been removed from the repo to avoid
> the two being applied by mistake — if you still have a local copy of it,
> discard it.

### NGINX Ingress Controller (if not already present on your cluster)

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx && helm repo update
kubectl create namespace ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.publishService.enabled=true
```

### cert-manager + Let's Encrypt (if you want automatic TLS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl rollout status deployment/cert-manager -n cert-manager
```

Edit the ACME contact email in `cluster_issuer.yaml` (it currently has a
placeholder comment but a real, hardcoded address — change it to your own),
then:

```bash
kubectl apply -f cluster_issuer.yaml
```

`cluster_issuer.yaml` creates a cluster-scoped `ClusterIssuer`, not a
namespaced resource — the `namespace:` field in its metadata has no effect,
don't worry about matching it to `benchmarking`.

## Troubleshooting

### Pod stuck in ContainerCreating

Usually an image pull problem. Check events:
```bash
kubectl describe pod -l app=backend -n benchmarking | grep -A 20 Events
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
kubectl logs job/init-db-migrations -n benchmarking

# Retry
kubectl delete job init-db-migrations -n benchmarking --ignore-not-found
kubectl apply -f 20-init-db-job.yaml
```

### Seed job failed

```bash
kubectl logs job/seed-db-metrics -n benchmarking

# Verify data
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n benchmarking -- \
  psql -h postgres -U haic_user -d haic_benchmark -c "SELECT COUNT(*) FROM metrics;"

# Retry (idempotent)
kubectl delete job seed-db-metrics -n benchmarking --ignore-not-found
kubectl apply -f 21-seed-db-job.yaml
```

### Backend won't start

```bash
kubectl logs deployment/backend -n benchmarking
kubectl describe pod -l app=backend -n benchmarking
```

Test database connectivity directly:
```bash
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n benchmarking -- \
  psql -h postgres -U haic_user -d haic_benchmark -c "SELECT 1;"
```

### Namespace stuck in Terminating

```bash
kubectl proxy &
kubectl get namespace benchmarking -o json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); d['spec']['finalizers']=[]; print(json.dumps(d))" \
  | curl -s -k -H "Content-Type: application/json" -X PUT \
    http://127.0.0.1:8001/api/v1/namespaces/benchmarking/finalize -d @-
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
| `frontend_ingress.yaml` | Ingress (nginx + optional TLS) — **edit hostname before applying** |
| `cluster_issuer.yaml` | Let's Encrypt ClusterIssuer — **edit email before applying** |
| `50_deploy.sh` | Full deployment from scratch |
| `60_update.sh` | Backend image version bump (`kubectl set image`) post-initial-deploy |
| `update.sh` | Lighter-weight rolling restart (code-only or `--migrate`); only picks up a new `:latest` image if the node hasn't already cached that tag |
| `seed-metrics.sql` | SQL loaded into the seed ConfigMap |
| `nginx.conf` | Frontend nginx template — resolves the backend via `${POD_NAMESPACE}` (Downward API), so it works in any namespace without editing |

> `create_configmap.sh` is unused by the current manifest set (it builds a
> `pg-init-sql` ConfigMap that nothing references — `02-seed-metrics-configmap.yaml`
> is applied directly instead). Safe to ignore.

## Cleanup

```bash
kubectl delete namespace benchmarking
```

If stuck, see the "Namespace stuck in Terminating" section above.
