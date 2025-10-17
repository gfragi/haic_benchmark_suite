## K8s configuration

This directory contains the configuration files for deploying the application on Kubernetes.

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
