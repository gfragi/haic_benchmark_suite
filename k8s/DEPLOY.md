# HAIC Benchmark Suite — Kubernetes Deployment Guide

This guide deploys three components into a single namespace (`benchmarking`):
- **PostgreSQL** — persistent database
- **Backend** — FastAPI service (image from GHCR)
- **Frontend** — Vue/React app served by nginx (image from GHCR)

**Prerequisites:** `kubectl` configured against your cluster, `docker` with buildx, `helm` (for optional ingress/cert-manager setup).

---

## 0. Prepare the images

> Skip if the images are already in GHCR.

### Build and push the backend

```bash
docker build -f Dockerfile.backend -t ghcr.io/gfragi/haic-backend:latest .
docker push ghcr.io/gfragi/haic-backend:latest
```

### Build and push the frontend (React)

```bash
# Uses docker buildx for multi-arch (amd64 + arm64)
# Prompts you to choose the frontend Dockerfile at deploy time
bash deploy_frontend.sh
```

Or specify the Dockerfile directly:

```bash
bash deploy_frontend.sh Dockerfile.frontend
bash deploy_frontend.sh Dockerfile.frontend-react
```

Or manually:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.frontend \
  -t ghcr.io/gfragi/haic-frontend:latest \
  . --push
```

---

## 1. Create the namespace

```bash
kubectl create namespace benchmarking
```

---

## 2. Create secrets

### 2a. GHCR image pull secret

Replace `<YOUR_GITHUB_USERNAME>` and `<YOUR_PAT>` with a GitHub Personal Access Token
that has `read:packages` scope.

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<YOUR_GITHUB_USERNAME> \
  --docker-password=<YOUR_PAT> \
  --namespace=benchmarking
```

### 2b. Backend / database secret

Create a file `k8s/.env.deploy` (do **not** commit it) with these keys:

```ini
DB_NAME=haic_benchmark
DB_USER=haic_user
DB_PASSWORD=<choose-a-strong-password>
DATABASE_URL=postgresql://haic_user:<password>@postgres:5432/haic_benchmark
```

Then apply:

```bash
kubectl create secret generic benchmarking-secret \
  --from-env-file=k8s/.env.deploy \
  --namespace=benchmarking
```

### 2c. Frontend secret

Create `frontend/.env.k8s` (do **not** commit it):

```ini
VUE_APP_API_BASE_URL=/api/v1
VUE_APP_KEYCLOAK_URL=https://<your-keycloak-host>/
VUE_APP_KEYCLOAK_REALM=<your-realm>
VUE_APP_KEYCLOAK_CLIENT_ID=<your-client-id>
```

> If you are not using Keycloak, set the values to empty strings — the frontend
> will fall back to unauthenticated mode.

```bash
kubectl create secret generic frontend-secret \
  --from-env-file=frontend/.env.k8s \
  --namespace=benchmarking
```

---

## 3. Create the database init ConfigMap

This loads the SQL init scripts into Kubernetes so the seed Job can apply them.
Run once from the **repo root**:

```bash
bash k8s/create_configmap.sh benchmarking
```

---

## 4. Deploy PostgreSQL

```bash
# Persistent volume claim
kubectl apply -f k8s/postgres_pvc.yaml -n benchmarking
```

> **⚠ Storage class:** The PVC requests `storageClassName: microk8s-hostpath`.
> If your cluster uses a different storage class (e.g. `standard`, `local-path`,
> `gp2`), edit `k8s/postgres_pvc.yaml` before applying:
>
> ```yaml
> storageClassName: <your-storage-class>
> ```
>
> Find available classes with: `kubectl get storageclass`

```bash
# Postgres deployment + service
kubectl apply -f k8s/postgres_dp.yaml -n benchmarking
kubectl apply -f k8s/postgres_svc.yaml -n benchmarking

# Wait until postgres is ready
kubectl rollout status deployment/postgres -n benchmarking
```

---

## 5. Seed the database (run once)

```bash
kubectl apply -f k8s/postgres_job.yaml -n benchmarking

# Tail the logs
kubectl logs -f job/postgres-seed -n benchmarking
```

Expected output:
```
==> Fresh DB: applying /init/00_init_dump.sql
==> Applying /init/10_seed_metrics.sql
==> Applying /init/12_create_surveys.sql
Done.
```

The Job is idempotent: if the schema already exists it skips `00_init_dump.sql`.

---

## 6. Deploy the backend

```bash
kubectl apply -f k8s/backend_dp.yaml -n benchmarking
kubectl apply -f k8s/backend_svc.yaml -n benchmarking

kubectl rollout status deployment/backend -n benchmarking
```

Quick health check (NodePort 30080):

```bash
curl http://<node-ip>:30080/health
```

---

## 7. Deploy the frontend

```bash
kubectl apply -f k8s/frontend_dp.yaml -n benchmarking
kubectl apply -f k8s/frontend_svc.yaml -n benchmarking

kubectl rollout status deployment/frontend -n benchmarking
```

---

## 8. Configure ingress (optional)

Use `k8s/frontend_ingress.yaml`. Before applying, update the hostname and TLS secret
to match your environment:

```yaml
# frontend_ingress.yaml — edit these two lines:
  - host: benchmark.humaine-horizon.eu   # ← change to your domain
  tls:
  - hosts: [benchmark.humaine-horizon.eu]
    secretName: hua-benchmarking-tls     # ← change if needed
```

If you don't have cert-manager, remove the `tls:` block and the
`cert-manager.io/cluster-issuer` annotation.

```bash
kubectl apply -f k8s/frontend_ingress.yaml -n benchmarking
```

### Installing NGINX Ingress Controller (if not already present)

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
kubectl create namespace ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.publishService.enabled=true
```

### Installing cert-manager + Let's Encrypt (if needed)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
# Wait for cert-manager to be ready
kubectl rollout status deployment/cert-manager -n cert-manager
```

Edit `k8s/cluster_issuer.yaml` — replace the email address:

```yaml
email: your@email.com
```

```bash
kubectl apply -f k8s/cluster_issuer.yaml
```

---

## 9. Verify the deployment

```bash
kubectl get pods -n benchmarking
kubectl get svc  -n benchmarking
kubectl get ingress -n benchmarking
```

All pods should be in `Running` state. The backend pod logs should show Alembic
migrations completing on startup.

---

## Namespace isolation (testing in a new namespace)

To test in a different namespace, replace `benchmarking` with your target namespace
in every command above, and update the `namespace:` field in all YAML files — or use:

```bash
# Quick find-and-replace for a fresh namespace (does NOT modify originals)
sed 's/namespace: benchmarking/namespace: <new-ns>/g' k8s/*.yaml | kubectl apply -f -
```

---

## File reference

| File | Purpose |
|---|---|
| `postgres_pvc.yaml` | PersistentVolumeClaim for DB data |
| `postgres_dp.yaml` | Postgres Deployment |
| `postgres_svc.yaml` | Postgres ClusterIP Service |
| `postgres_job.yaml` | One-time DB seed Job |
| `create_configmap.sh` | Creates `pg-init-sql` ConfigMap from SQL files |
| `backend_dp.yaml` | Backend Deployment |
| `backend_svc.yaml` | Backend NodePort Service (port 30080) |
| `frontend_dp.yaml` | Frontend Deployment |
| `frontend_svc.yaml` | Frontend NodePort Service (port 80) |
| `frontend_ingress.yaml` | Ingress (nginx + optional TLS) |
| `cluster_issuer.yaml` | Let's Encrypt ClusterIssuer |
| `secret_pull.yaml` | GHCR pull secret (pre-encoded — prefer step 2a) |

> `init-db-job.yaml` and `frontend-ingress.yaml` are **deprecated** — do not apply them.
