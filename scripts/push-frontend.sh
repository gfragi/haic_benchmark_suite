#!/bin/bash

set -e

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | xargs)
else
  echo ".env file not found!"
  exit 1
fi

# Log in to GitHub Container Registry
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

# Build the frontend image
docker build -f Dockerfile.frontend -t "$FRONTEND_IMAGE" .

# Push to GitHub Container Registry
docker push "$FRONTEND_IMAGE"

echo "✅ Frontend image pushed successfully to $FRONTEND_IMAGE"


# chmod +x scripts/push-frontend.sh
# ./scripts/push-frontend.sh