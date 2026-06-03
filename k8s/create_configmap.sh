#!/bin/bash
# Creates the pg-init-sql ConfigMap from the SQL init files.
# Run this ONCE from the repo root before applying the postgres Job.
# Safe to re-run: --dry-run=client -o yaml | kubectl apply -f - is idempotent.

set -euo pipefail

NAMESPACE="${1:-benchmarking}"
SQL_DIR="docker/db-init"

echo "Creating pg-init-sql ConfigMap in namespace: $NAMESPACE"

kubectl create configmap pg-init-sql \
  --from-file="${SQL_DIR}/00_init.sql" \
  --from-file="${SQL_DIR}/10_seed_metrics.sql" \
  --from-file="${SQL_DIR}/12_create_surveys.sql" \
  --namespace="$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Done."
