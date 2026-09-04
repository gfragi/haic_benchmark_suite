#!/usr/bin/env bash
# migrate_sus_data_extract.sh
#
# Step 1 of 2 (see migrate_sus_data_load.py for step 2).
#
# Extracts every row from DEV's `surveys` table as a JSON file, including
# survey_id/configuration_id/schema_id - fields GET /api/v1/survey/raw does
# NOT expose (it's an analytics export, not a data round-trip). This still
# needs a direct SQL read against dev, whatever form that takes for you.
#
# WHERE TO RUN THIS: wherever you can reach dev's postgres - your own
# machine (port-forward or a direct connection string), or `kubectl exec`
# into dev's postgres pod if you have that. Not prod - this only reads dev.
#
# Fill in DEV_PSQL below, then run:
#   ./scripts/migrate_sus_data_extract.sh
# It writes surveys_dev_export.json in the current directory.

set -euo pipefail

# ---- TODO: fill this in --------------------------------------------------
# However you connect to DEV's postgres. Examples:
#   psql "postgresql://haic_user:PASSWORD@localhost:5432/haic_benchmark"   (after: kubectl port-forward svc/postgres 5432:5432 -n benchmarking, against your DEV context)
#   -- or, if you do have exec on dev too, replace this whole array with:
#   kubectl exec -n benchmarking <dev-postgres-pod> -- psql -U haic_user -d haic_benchmark
DEV_PSQL=(psql "postgresql://TODO_USER:TODO_PASSWORD@TODO_HOST:5432/TODO_DB")

OUT_FILE="surveys_dev_export.json"

"${DEV_PSQL[@]}" -t -A -c "
  SELECT json_agg(row_to_json(t))
  FROM (
    SELECT survey_id, user_id, timestamp, pilot_tag, app_version, ai_model_version,
           schema_id, tam_sus_responses, ethics_responses, domain_specific, configuration_id
    FROM surveys
    ORDER BY timestamp
  ) t;
" > "$OUT_FILE"

count=$(python3 -c "import json; print(len(json.load(open('$OUT_FILE'))))")
echo "Wrote $count rows to $OUT_FILE"
echo "Next: kubectl cp $OUT_FILE <prod-namespace>/<prod-backend-pod>:/tmp/surveys_dev_export.json"
