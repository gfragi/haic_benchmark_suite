#!/bin/bash
set -e

# HAIC Benchmark Kubernetes Deployment Script
# This script automates the deployment of HAIC Benchmark to Kubernetes

NAMESPACE="haic-benchmark"
TIMEOUT=300

echo "=================================================="
echo "HAIC Benchmark Kubernetes Deployment Script"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Create namespace
print_step "Creating namespace '$NAMESPACE'..."
kubectl apply -f 00-namespace.yaml
echo ""

# Step 2: Handle secrets
print_step "Checking secrets configuration..."
if [ ! -f "01-secrets.yaml" ]; then
    if [ -f "01-secrets-template.yaml" ]; then
        print_warn "01-secrets.yaml not found. Creating from template..."
        print_warn "IMPORTANT: Edit 01-secrets.yaml and set your actual values!"
        cp 01-secrets-template.yaml 01-secrets.yaml
        echo ""
        echo "Edit the following file and set your actual values:"
        echo "  vim 01-secrets.yaml"
        echo ""
        read -p "Press Enter after updating 01-secrets.yaml..." -t 300
    else
        print_error "Neither 01-secrets.yaml nor 01-secrets-template.yaml found"
        exit 1
    fi
fi

print_step "Applying secrets from 01-secrets.yaml..."
kubectl apply -f 01-secrets.yaml

print_step "Creating seed data ConfigMap..."
kubectl apply -f 02-seed-metrics-configmap.yaml
echo ""

# Step 3: Deploy PostgreSQL
print_step "Deploying PostgreSQL..."
kubectl apply -f 10-postgres-pvc.yaml
kubectl apply -f 11-postgres-service.yaml
kubectl apply -f 12-postgres-deployment.yaml

print_step "Waiting for PostgreSQL to be ready..."
kubectl rollout status deployment/postgres -n "$NAMESPACE" --timeout="${TIMEOUT}s"
sleep 5  # Give postgres a moment to fully initialize
echo ""

# Step 4: Run migrations
print_step "Running Alembic database migrations..."
kubectl apply -f 20-init-db-job.yaml

print_step "Waiting for migrations to complete..."
if kubectl wait --for=condition=complete job/init-db-migrations -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
    print_error "Migrations failed. Check logs with:"
    echo "  kubectl logs job/init-db-migrations -n $NAMESPACE"
    exit 1
fi
echo ""

# Step 4b: Seed database with metrics and definitions
print_step "Seeding database with metrics and definitions..."
kubectl apply -f 21-seed-db-job.yaml

print_step "Waiting for seed data to complete..."
if kubectl wait --for=condition=complete job/seed-db-metrics -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
    echo -e "${GREEN}✓ Seed data loaded successfully${NC}"
else
    print_error "Seed job failed. Check logs with:"
    echo "  kubectl logs job/seed-db-metrics -n $NAMESPACE"
    exit 1
fi
echo ""

# Step 5: Deploy Backend
print_step "Deploying Backend API..."
kubectl apply -f 30-backend-service.yaml
kubectl apply -f 31-backend-deployment.yaml

print_step "Waiting for Backend to be ready..."
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout="${TIMEOUT}s"
echo ""

# Step 6: Deploy Frontend
print_step "Deploying Frontend..."
kubectl apply -f 40-frontend-service.yaml
kubectl apply -f 41-frontend-deployment.yaml

print_step "Waiting for Frontend to be ready..."
kubectl rollout status deployment/frontend -n "$NAMESPACE" --timeout="${TIMEOUT}s"
echo ""

# Step 7: Verify deployment
print_step "Verifying deployment..."
echo ""
echo "Pods status:"
kubectl get pods -n "$NAMESPACE"
echo ""
echo "Services:"
kubectl get svc -n "$NAMESPACE"
echo ""

# Summary
echo "=================================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "To access your services locally:"
echo ""
echo "Backend API:"
echo "  kubectl port-forward svc/backend 8000:8000 -n $NAMESPACE"
echo "  curl http://localhost:8000/api/meta/health"
echo ""
echo "Frontend:"
echo "  kubectl port-forward svc/frontend 8080:80 -n $NAMESPACE"
echo "  Open: http://localhost:8080"
echo ""
echo "PostgreSQL (for debugging):"
echo "  kubectl port-forward svc/postgres 5432:5432 -n $NAMESPACE"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
echo ""
echo "For more information, see README.md"
echo ""
