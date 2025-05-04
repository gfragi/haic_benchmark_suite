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
  --from-env-file=.env \
  --namespace=benchmarking
```

