# HAIC Benchmark Suite — Kubernetes Deployment Guide

Deploys three components into a single namespace:
- **PostgreSQL** — persistent database
- **Backend** — FastAPI (image: `ghcr.io/gfragi/haic-backend:latest`)
- **Frontend** — React app via nginx (image: `ghcr.io/gfragi/haic-frontend:latest`)

**Prerequisites:** `kubectl` pointing at target cluster, `docker` with buildx, `helm` (for ingress/cert-manager).

---

## 0. Build and push the React frontend image

> Skip if the image is already in GHCR.

```bash
# From the repo root
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.frontend-react \
  -t ghcr.io/gfragi/haic-frontend:latest \
  . --push
```

To build the backend:

```bash
docker build -f Dockerfile.backend -t ghcr.io/gfragi/haic-backend:latest .
docker push ghcr.io/gfragi/haic-backend:latest
```

---

## 1. Create the namespace

```bash
kubectl create namespace benchmarking
```

---

## 2. Create secrets

### 2a. GHCR image pull secret

You need a GitHub Personal Access Token with **`read:packages`** scope.

```bash
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_PAT> \
  --namespace=benchmarking
```

### 2b. Backend / database secret

Create a file `k8s/.env.deploy` (**do not commit it**). It must contain exactly these keys:

```ini
DB_NAME=haic_benchmark
DB_USER=haic_user
DB_PASSWORD=<choose-a-strong-password>
DATABASE_URL=postgresql://haic_user:<same-password>@postgres:5432/haic_benchmark
MINIO_ENDPOINT=<your-minio-host>
MINIO_ACCESS_KEY=<your-minio-access-key>
MINIO_SECRET_KEY=<your-minio-secret-key>
MINIO_BUCKET=benchmarking-suite
MINIO_REGION=us-east-1
MINIO_SECURE=True
LOG_LEVEL=INFO
```

> **MinIO note:** The backend uses MinIO (S3-compatible) to store evaluation result files.
> If GFT has its own MinIO instance, use those credentials here.
> If you want to use the HUA shared MinIO, request the credentials from George.
> MinIO is **not** required for the platform to start — it only affects result file storage.

> **AUTH_URL / Keycloak note:** `AUTH_URL` in `.env.production` is the Keycloak token endpoint
> used by the backend to validate tokens. If your cluster has its own Keycloak, set
> `AUTH_URL`, `KEYCLOAK_SERVER_URL`, `KEYCLOAK_REALM_NAME`, `KEYCLOAK_CLIENT_ID` accordingly.
> These are **optional** — the platform runs without auth in development mode.

```bash
kubectl create secret generic benchmarking-secret \
  --from-env-file=k8s/.env.deploy \
  --namespace=benchmarking
```

### 2c. Frontend secret

Create `k8s/.env.frontend` (**do not commit it**):

```ini
VUE_APP_API_BASE_URL=/api/v1
VUE_APP_KEYCLOAK_URL=https://<your-keycloak-host>/
VUE_APP_KEYCLOAK_REALM=<your-realm>
VUE_APP_KEYCLOAK_CLIENT_ID=<your-client-id>
```

> If not using Keycloak, leave the values as empty strings.

```bash
kubectl create secret generic frontend-secret \
  --from-env-file=k8s/.env.frontend \
  --namespace=benchmarking
```

---

## 3. Create the database init ConfigMap

Run **once from the repo root**:

```bash
bash k8s/create_configmap.sh benchmarking
```

This loads `docker/db-init/00_init.sql` and `docker/db-init/10_seed_metrics.sql`
into a ConfigMap that the seed Job mounts.

---

## 4. Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres_pvc.yaml -n benchmarking
```

> **⚠ Storage class:** The PVC uses `storageClassName: microk8s-hostpath`.
> Check what's available on your cluster:
> ```bash
> kubectl get storageclass
> ```
> Then edit `k8s/postgres_pvc.yaml` and replace `microk8s-hostpath` with your class
> (e.g. `standard`, `local-path`, `gp2`) before applying.

```bash
kubectl apply -f k8s/postgres_dp.yaml -n benchmarking
kubectl apply -f k8s/postgres_svc.yaml -n benchmarking
kubectl rollout status deployment/postgres -n benchmarking
```

---

## 5. Seed the database (run once)

```bash
kubectl apply -f k8s/postgres_job.yaml -n benchmarking
kubectl logs -f job/postgres-seed -n benchmarking
```

Expected output:
```
==> Fresh DB: applying /init/00_init.sql
==> Applying /init/10_seed_metrics.sql
Done.
```

The Job is idempotent — if the schema already exists it skips `00_init.sql`.

> The backend also runs **Alembic migrations on startup**, so any schema additions
> after the initial seed are handled automatically.

---

## 6. Deploy the backend

```bash
kubectl apply -f k8s/backend_dp.yaml -n benchmarking
kubectl apply -f k8s/backend_svc.yaml -n benchmarking
kubectl rollout status deployment/backend -n benchmarking
```

Health check (NodePort 30080):

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

## 8. Configure ingress

Edit `k8s/frontend_ingress.yaml` — update the hostname and TLS secret:

```yaml
rules:
  - host: benchmark-gft.humaine-horizon.eu   # ← your domain
tls:
  - hosts: [benchmark-gft.humaine-horizon.eu]
    secretName: gft-benchmarking-tls          # ← your TLS secret name
```

Remove the `tls:` block and `cert-manager.io/cluster-issuer` annotation if you
are not using cert-manager.

```bash
kubectl apply -f k8s/frontend_ingress.yaml -n benchmarking
```

### NGINX Ingress Controller (if not present)

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx && helm repo update
kubectl create namespace ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.publishService.enabled=true
```

### cert-manager + Let's Encrypt (if needed)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl rollout status deployment/cert-manager -n cert-manager
```

Edit the email in `k8s/cluster_issuer.yaml`, then:

```bash
kubectl apply -f k8s/cluster_issuer.yaml
```

---

## 9. Verify

```bash
kubectl get pods    -n benchmarking
kubectl get svc     -n benchmarking
kubectl get ingress -n benchmarking
```

All pods should be `Running`. Backend pod logs will show Alembic migrations on first start.

---

## Testing in a different namespace

All manifests default to namespace `benchmarking`. To deploy into a different namespace,
pass it through `sed` — this does **not** modify the originals:

```bash
NS=benchmarking-gft

kubectl create namespace $NS

# Secrets (adjust env files as above, then):
kubectl create secret docker-registry ghcr-pull-secret ... --namespace=$NS
kubectl create secret generic benchmarking-secret --from-env-file=k8s/.env.deploy --namespace=$NS
kubectl create secret generic frontend-secret --from-env-file=k8s/.env.frontend --namespace=$NS

# ConfigMap
bash k8s/create_configmap.sh $NS

# All manifests
for f in k8s/postgres_pvc.yaml k8s/postgres_dp.yaml k8s/postgres_svc.yaml \
         k8s/postgres_job.yaml \
         k8s/backend_dp.yaml k8s/backend_svc.yaml \
         k8s/frontend_dp.yaml k8s/frontend_svc.yaml \
         k8s/frontend_ingress.yaml; do
  sed "s/namespace: benchmarking/namespace: $NS/g" "$f" | kubectl apply -f -
done
```

---

## File reference

| File | Purpose |
|---|---|
| `postgres_pvc.yaml` | PersistentVolumeClaim for DB data |
| `postgres_dp.yaml` | Postgres Deployment |
| `postgres_svc.yaml` | Postgres ClusterIP Service |
| `postgres_job.yaml` | One-time DB seed Job (runs `00_init.sql` + `10_seed_metrics.sql`) |
| `create_configmap.sh` | Creates `pg-init-sql` ConfigMap from SQL files |
| `backend_dp.yaml` | Backend Deployment |
| `backend_svc.yaml` | Backend NodePort Service (port 30080) |
| `frontend_dp.yaml` | Frontend Deployment |
| `frontend_svc.yaml` | Frontend NodePort Service (port 80) |
| `frontend_ingress.yaml` | Ingress (nginx + optional TLS) — **edit hostname before applying** |
| `cluster_issuer.yaml` | Let's Encrypt ClusterIssuer — **edit email before applying** |

> `init-db-job.yaml` and `frontend-ingress.yaml` are **deprecated** — do not apply them.
