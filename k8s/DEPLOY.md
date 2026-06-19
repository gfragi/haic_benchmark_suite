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
docker build -f Dockerfile.frontend-react -t ghcr.io/gfragi/haic-frontend-react:latest .
docker push ghcr.io/gfragi/haic-frontend-react:latest
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
DB_HOST=postgres
DB_PORT=5432
MINIO_ENDPOINT=<your-minio-host>
MINIO_ACCESS_KEY=<your-minio-access-key>
MINIO_SECRET_KEY=<your-minio-secret-key>
MINIO_BUCKET=benchmarking-suite
MINIO_REGION=us-east-1
MINIO_SECURE=True
AUTH_URL=
LOG_LEVEL=INFO
```

`backend_dp.yaml` wires all of these keys into the backend pod's environment via
`secretKeyRef`. **All of them must exist in the secret** even if empty — the pod
fails `CreateContainerConfigError` on any key it references that's missing from
the secret, not just the ones the app actually reads at runtime.

> **MinIO note:** The backend uses MinIO (S3-compatible) to store evaluation result
> files. **MinIO IS required for the platform to start** — `get_minio_client()` runs
> at import time in several routers, and a missing/invalid `MINIO_ENDPOINT` crashes
> the backend pod immediately (it does not degrade gracefully).
> If GFT has its own MinIO instance, use those credentials here.
> If you want to use the HUA shared MinIO, request the credentials from George.

> **AUTH_URL / Keycloak-fronted MinIO note:** if `AUTH_URL` is set, the backend's
> MinIO client authenticates via Keycloak token exchange using `MINIO_USERNAME` /
> `MINIO_PASSWORD` instead of `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` — add those
> two keys instead in that case (see `k8s/01-secrets.yaml` for an example against
> the HUA shared MinIO). Leave `AUTH_URL` empty to use direct access-key auth and
> skip Keycloak token validation entirely (the platform runs without auth in dev mode).

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

The React frontend (`frontend-react/`) is the current default — it calls relative
`/api` and `/meta` paths (see `frontend-react/vite.config.js`), so it has no
build-time or runtime backend URL to configure; whichever ingress serves it
determines the backend it talks to.

```bash
kubectl apply -f k8s/frontend-react_dp.yaml -n benchmarking
kubectl apply -f k8s/frontend-react_svc.yaml -n benchmarking
kubectl rollout status deployment/frontend-react -n benchmarking
```

> **Port-forward testing gap:** the served nginx image only serves static files —
> it does **not** proxy `/api` anywhere (unlike the Vite dev server's `server.proxy`).
> `kubectl port-forward svc/frontend-react ...` will load the page shell, but every
> API call will hit nginx's SPA fallback and get HTML back instead of JSON. Path-based
> `/api` routing only happens at the Ingress layer (see `frontend_ingress.yaml`'s
> rules). To test end-to-end before wiring ingress, either:
>
> - `kubectl port-forward svc/backend 8000:8000` and run `npm run dev` locally in
>   `frontend-react/` with `VITE_API_PROXY_TARGET=http://localhost:8000`, or
> - apply a temporary namespace-scoped Ingress with its own test hostname (distinct
>   from the production host) instead of port-forwarding the frontend directly.

The old Vue frontend (`frontend_dp.yaml` / `frontend_svc.yaml`) is still present but
deploys a stale image build. Its `env:` block has no effect at runtime — Vue CLI
bakes `VUE_APP_*` values in at *build time* from `frontend/.env.production`, which is
hardcoded to the production hostname. Don't use it for namespace-isolated testing
without first rebuilding the image with a different `.env.production`.

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
         k8s/frontend-react_dp.yaml k8s/frontend-react_svc.yaml; do
  sed "s/namespace: benchmarking/namespace: $NS/g" "$f" | kubectl apply -f -
done
# Add k8s/frontend_ingress.yaml to the list above once you're ready to wire
# ingress for this namespace - see the port-forward testing note in step 7.
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
| `frontend-react_dp.yaml` | React Frontend Deployment (current default) |
| `frontend-react_svc.yaml` | React Frontend NodePort Service (port 80) |
| `frontend_dp.yaml` | Legacy Vue Frontend Deployment — image/env are stale, see step 7 |
| `frontend_svc.yaml` | Legacy Vue Frontend NodePort Service (port 80) |
| `frontend_ingress.yaml` | Ingress (nginx + optional TLS) — **edit hostname before applying** |
| `cluster_issuer.yaml` | Let's Encrypt ClusterIssuer — **edit email before applying** |

> `init-db-job.yaml` and `frontend-ingress.yaml` are **deprecated** — do not apply them.
> `secret_pull.yaml` has been removed — it committed a literal GHCR token to git.
> Create `ghcr-pull-secret` imperatively per step 2a instead.
