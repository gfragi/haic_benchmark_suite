#!/bin/bash

# Exit immediately if a command fails
set -e

# Set these variables
IMAGE="ghcr.io/gfragi/haic-frontend:latest"
NAMESPACE="benchmarking"
DEPLOYMENT="frontend"
DOCKERFILE="Dockerfile.frontend"
CONTEXT="."  # path to your frontend root

# 1. Build the Docker image
echo "🔨 Building Docker image..."
docker build -f $DOCKERFILE -t $IMAGE $CONTEXT

# 2. Push to GitHub Container Registry
echo "📤 Pushing image to GHCR..."
docker push $IMAGE

# 3. Trigger Kubernetes rollout restart
echo "♻️ Restarting Kubernetes deployment..."
kubectl rollout restart deployment $DEPLOYMENT -n $NAMESPACE

# 4. Wait for rollout to finish
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment $DEPLOYMENT -n $NAMESPACE

echo "✅ Frontend redeployed successfully!"
