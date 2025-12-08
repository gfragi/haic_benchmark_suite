#!/bin/bash

# Wait for MinIO to be ready
until curl -f http://localhost:9000/minio/health/live; do
  echo "Waiting for MinIO..."
  sleep 2
done

# Configure mc alias
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create bucket if it doesn't exist
mc mb local/benchmarking-suite --ignore-existing

# Set public access policy
mc anonymous set public local/benchmarking-suite

echo "MinIO bucket initialized successfully"
