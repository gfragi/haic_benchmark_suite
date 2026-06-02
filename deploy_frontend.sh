#!/bin/bash
set -e

# Set these variables
IMAGE="ghcr.io/gfragi/haic-frontend:rollback"
NAMESPACE="benchmarking"
DEPLOYMENT="frontend"
DOCKERFILE="Dockerfile.frontend"
CONTEXT="."  # project root

# echo "🔐 Ensuring you're logged in to GHCR..."
# echo "If not already logged in, run: docker login ghcr.io"
# # (You can auto-login here if you want, but usually it's done once manually.)

# 1. Ensure buildx builder exists and is active
if ! docker buildx inspect haic-builder >/dev/null 2>&1; then
  echo "🧱 Creating buildx builder 'haic-builder'..."
  docker buildx create --name haic-builder --use
  docker buildx inspect --bootstrap
else
  echo "🧱 Using existing buildx builder 'haic-builder'..."
  docker buildx use haic-builder
fi

# 2. Build & push multi-arch image
echo "🔨 Building and pushing multi-arch Docker image..."
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f "$DOCKERFILE" \
  -t "$IMAGE" \
  "$CONTEXT" \
  --push

# 3. Trigger Kubernetes rollout restart (if kubectl is configured)
if kubectl cluster-info >/dev/null 2>&1; then
  echo "♻️ Restarting Kubernetes deployment..."
  kubectl rollout restart deployment "$DEPLOYMENT" -n "$NAMESPACE"

  echo "⏳ Waiting for rollout to complete..."
  kubectl rollout status deployment "$DEPLOYMENT" -n "$NAMESPACE"

  echo "✅ Frontend redeployed successfully!"
else
  echo "⚠️ kubectl not available or cluster not accessible. Multi-arch image pushed successfully to GHCR."
fi
