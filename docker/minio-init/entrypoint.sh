#!/bin/bash

# Run the bucket initialization script
/minio-init/init-bucket.sh &

# Start MinIO server
exec minio server /data --console-address ':9001'
