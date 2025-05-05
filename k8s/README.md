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
  --from-env-file=k8s\.env \
  --namespace=benchmarking
```

## Build the Frontend Image

``` bash
docker build -f Dockerfile.frontend -t ghcr.io/gfragi/haic-frontend:latest .
```

## Authenticate to GHCR

``` bash
source k8s/.env 
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```


## Postgres 

Create a db script as a configmap

```bash
kubectl create configmap init-db-script \
  --from-file=init.sql=./init.sql \
  --namespace=benchmarking
```

- PostgreSQL service must already be running (name: postgres in benchmarking namespace).
- Create the ConfigMap using the path above.
- Apply the init-db job manifest.