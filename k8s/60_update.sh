#!/bin/bash
set -e

# HAIC Benchmark Update Script
# Updates backend with new migrations

NAMESPACE="haic-benchmark"
TIMEOUT=300

echo "=================================================="
echo "HAIC Benchmark Update Script"
echo "=================================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check parameters
if [ $# -lt 1 ]; then
    echo "Usage: ./update.sh <new-image-tag>"
    echo ""
    echo "Examples:"
    echo "  ./update.sh v2.0"
    echo "  ./update.sh latest"
    echo "  ./update.sh ghcr.io/gfragi/haic-backend:rollback"
    exit 1
fi

IMAGE_TAG=$1

# If it's just a tag, prepend the full image name
if [[ ! "$IMAGE_TAG" == *"/"* ]]; then
    FULL_IMAGE="ghcr.io/gfragi/haic-backend:${IMAGE_TAG}"
else
    FULL_IMAGE="$IMAGE_TAG"
fi

echo "Will update backend to: $FULL_IMAGE"
echo ""
read -p "Has this image already been pushed? (yes/no) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please build and push image first:"
    echo "  docker build -f Dockerfile.backend -t $FULL_IMAGE ."
    echo "  docker push $FULL_IMAGE"
    exit 1
fi

echo ""

# Step 1: Run migrations
print_step "Running database migrations..."
kubectl delete job init-db-migrations -n "$NAMESPACE" 2>/dev/null || true
kubectl apply -f 20-init-db-job.yaml

print_step "Waiting for migrations to complete..."
if kubectl wait --for=condition=complete job/init-db-migrations -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    print_error "Migrations failed!"
    kubectl logs job/init-db-migrations -n "$NAMESPACE"
    exit 1
fi
echo ""

# Step 2: Update backend deployment image
print_step "Updating backend image to $FULL_IMAGE..."
kubectl set image deployment/backend backend=$FULL_IMAGE -n "$NAMESPACE"

# Step 3: Wait for rollout
print_step "Waiting for backend to roll out..."
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout="${TIMEOUT}s"
echo ""

echo "=================================================="
echo -e "${GREEN}✓ Update Complete!${NC}"
echo "=================================================="
echo ""
echo "Backend is now running $FULL_IMAGE"
echo ""
echo "To verify:"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo ""
echo "To rollback if needed:"
echo "  kubectl rollout undo deployment/backend -n $NAMESPACE"
echo ""
