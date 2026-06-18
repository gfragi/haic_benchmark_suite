#!/bin/bash
set -e

NAMESPACE="haic-benchmark"
TIMEOUT=300

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step()  { echo -e "${GREEN}[STEP]${NC} $1"; }
print_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

MIGRATE=false
for arg in "$@"; do
  case $arg in
    --migrate) MIGRATE=true ;;
    *) print_warn "Unknown argument: $arg" ;;
  esac
done

if [ "$MIGRATE" = true ]; then
  print_step "Running Alembic migrations..."
  kubectl delete job init-db-migrations -n "$NAMESPACE" --ignore-not-found

  kubectl apply -f 20-init-db-job.yaml

  print_step "Waiting for migrations to complete..."
  if kubectl wait --for=condition=complete job/init-db-migrations -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
    echo -e "${GREEN}✓ Migrations completed${NC}"
  else
    print_error "Migrations failed. Check logs:"
    echo "  kubectl logs job/init-db-migrations -n $NAMESPACE"
    exit 1
  fi
fi

print_step "Rolling out backend update..."
kubectl rollout restart deployment/backend -n "$NAMESPACE"
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout="${TIMEOUT}s"
echo -e "${GREEN}✓ Backend updated${NC}"

echo ""
echo "To also update the frontend:"
echo "  kubectl rollout restart deployment/frontend -n $NAMESPACE"
