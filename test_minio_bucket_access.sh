#!/usr/bin/env bash
# Tests whether the benchmarking-suite service account's token (from the same
# gateway our backend authenticates to) actually has read access to a given
# MinIO bucket - i.e. reproduces exactly what the backend's poll does,
# without needing kubectl/backend access.
set -euo pipefail

AUTH_URL="https://humaine-minio-api.euprojects.net/auth/auth"
S3_ENDPOINT="https://s3-minio.humaine-horizon.eu"

read -rp "Service account username [benchmarking-suite-service]: " MINIO_USER
MINIO_USER="${MINIO_USER:-benchmarking-suite-service}"
read -rsp "Service account password: " MINIO_PASS
echo

read -rp "Bucket to test [smart-healthcare-diabetes-models]: " BUCKET
BUCKET="${BUCKET:-smart-healthcare-diabetes-models}"

echo
echo "== Step 1: requesting a token from $AUTH_URL =="
TOKEN_RESPONSE=$(curl -s -X POST "$AUTH_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=${MINIO_USER}" \
  --data-urlencode "password=${MINIO_PASS}")

TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || true)

if [ -z "$TOKEN" ]; then
  echo "FAILED to obtain a token. Raw response:"
  echo "$TOKEN_RESPONSE"
  exit 1
fi

echo "Got token: ${TOKEN:0:20}...(truncated)"
echo

echo "== Step 2: listing bucket '$BUCKET' with that token =="
curl -s -H "Authorization: Bearer $TOKEN" \
  "${S3_ENDPOINT}/${BUCKET}?list-type=2" | tee /tmp/minio_bucket_test_response.xml

echo
echo "== Result =="
if grep -q "<ListBucketResult" /tmp/minio_bucket_test_response.xml 2>/dev/null; then
  echo "SUCCESS - the token has read access to this bucket."
elif grep -q "AccessDenied" /tmp/minio_bucket_test_response.xml 2>/dev/null; then
  echo "ACCESS DENIED - confirmed, the token does not have read access to this bucket."
else
  echo "UNEXPECTED RESPONSE - see output above."
fi
