#!/bin/bash

# Wait for MinIO to be ready
until curl -f http://localhost:9000/minio/health/live; do
  echo "Waiting for MinIO..."
  sleep 2
done

# Configure mc alias
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create buckets if they don't exist
mc mb local/benchmarking-suite --ignore-existing
mc mb local/haic-test --ignore-existing

# Set public access policy
mc anonymous set public local/benchmarking-suite
mc anonymous set public local/haic-test

echo "MinIO bucket initialized successfully"
