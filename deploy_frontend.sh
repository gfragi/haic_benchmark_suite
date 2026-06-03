#!/bin/bash
set -e

# Set these variables
IMAGE="ghcr.io/gfragi/haic-frontend:rollback"
NAMESPACE="benchmarking"
DEPLOYMENT="frontend"
CONTEXT="."  # project root

DEFAULT_DOCKERFILE="Dockerfile.frontend"
DOCKERFILE_OPTIONS=("Dockerfile.frontend" "Dockerfile.frontend-react")

choose_dockerfile() {
  local provided_dockerfile="$1"

  if [[ -n "$provided_dockerfile" ]]; then
    if [[ ! -f "$provided_dockerfile" ]]; then
      echo "❌ Dockerfile '$provided_dockerfile' not found."
      exit 1
    fi
    DOCKERFILE="$provided_dockerfile"
    return
  fi

  echo "Select the frontend Dockerfile to deploy:"
  for i in "${!DOCKERFILE_OPTIONS[@]}"; do
    local option="${DOCKERFILE_OPTIONS[$i]}"
    local marker=""
    if [[ "$option" == "$DEFAULT_DOCKERFILE" ]]; then
      marker=" (default)"
    fi
    echo "  $((i + 1)). $option$marker"
  done

  read -r -p "Enter choice [1-${#DOCKERFILE_OPTIONS[@]}] (default: 1): " dockerfile_choice
  dockerfile_choice="${dockerfile_choice:-1}"

  if ! [[ "$dockerfile_choice" =~ ^[0-9]+$ ]] || (( dockerfile_choice < 1 || dockerfile_choice > ${#DOCKERFILE_OPTIONS[@]} )); then
    echo "❌ Invalid choice: $dockerfile_choice"
    exit 1
  fi

  DOCKERFILE="${DOCKERFILE_OPTIONS[$((dockerfile_choice - 1))]}"
}

choose_dockerfile "$1"

echo "🔐 Ensuring you're logged in to GHCR..."
echo "If not already logged in, run: docker login ghcr.io"
echo "📦 Using Dockerfile: $DOCKERFILE"
# (You can auto-login here if you want, but usually it's done once manually.)

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
