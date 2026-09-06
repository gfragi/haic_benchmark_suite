#!/usr/bin/env bash
# migrate_sus_data_extract.sh
#
# Step 1 of 2 (see migrate_sus_data_load.py for step 2).
#
# Extracts every survey row from DEV via the new GET /survey/export
# endpoint (backend/app/routers/survey.py) - a plain HTTP GET, no DB
# credentials or kubectl access needed. Unlike GET /survey/raw (analytics
# export), this includes survey_id/configuration_id/schema_id, so each row
# can be POSTed back as-is by migrate_sus_data_load.py.
#
# Requires the new /export endpoint to actually be deployed to the dev
# cluster first - it doesn't exist there until this branch's backend image
# is rolled out.
#
# WHERE TO RUN THIS: wherever you can reach dev's API over HTTP (your own
# machine is fine if dev is reachable, same as prod).
#
#   ./scripts/migrate_sus_data_extract.sh https://dev-api.example.org
#
# Optionally restrict to one pilot (matches GET /survey/export's own
# pilot_tag query param - same convention as /raw, /aggregate, /comments):
#   ./scripts/migrate_sus_data_extract.sh https://dev-api.example.org radiology_demo

set -euo pipefail

DEV_API_BASE="${1:?Usage: $0 <dev-api-base-url, e.g. https://dev-api.example.org/api/v1> [pilot_tag]}"
PILOT_TAG="${2:-}"
OUT_FILE="surveys_dev_export.json"

URL="${DEV_API_BASE%/}/survey/export"
if [[ -n "$PILOT_TAG" ]]; then
  URL="${URL}?pilot_tag=${PILOT_TAG}"
fi

curl -sf "$URL" -o "$OUT_FILE"

count=$(python3 -c "import json; print(len(json.load(open('$OUT_FILE'))))")
echo "Wrote $count rows to $OUT_FILE"
echo "Next: python3 scripts/migrate_sus_data_load.py <prod-api-base-url> [--dry-run]"
