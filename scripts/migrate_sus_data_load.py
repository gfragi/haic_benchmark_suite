#!/usr/bin/env python3
"""
migrate_sus_data_load.py

Step 2 of 2 (see migrate_sus_data_extract.sh for step 1).

Loads surveys exported from dev into prod via POST /api/v1/survey - the
same endpoint the app itself uses, so each row goes through the real
validation and gives a clean per-row error instead of a raw SQL failure.
configuration_id is a plain autoincrement int (not portable across
environments as-is) - CONFIG_ID_MAP below remaps it per row before POSTing.

WHERE TO RUN THIS: your own machine, or anywhere with network access to
prod's API - prod is directly reachable, so no kubectl/pod-exec needed for
this step (or the extract step, now that GET /survey/export exists).

  python3 scripts/migrate_sus_data_extract.sh https://dev-api.example.org
  python3 scripts/migrate_sus_data_load.py https://prod-api.example.org --dry-run
  python3 scripts/migrate_sus_data_load.py https://prod-api.example.org

Stdlib only (json/urllib) - nothing to install.
"""
import json
import sys
import urllib.error
import urllib.request

EXPORT_FILE = "surveys_dev_export.json"

# ---- TODO: fill this in --------------------------------------------------
# dev configuration_id -> prod configuration_id. Every dev id present in
# the export should be listed here; see UNMAPPED_ACTION for what happens
# to rows whose id isn't.
CONFIG_ID_MAP = {
    # 2: 8,
    # 3: 9,
}

# "null" -> submit with configuration_id = null (row kept, link dropped)
# "skip" -> don't submit that row at all
# "fail" -> abort the whole run on the first unmapped id
UNMAPPED_ACTION = "null"

# schema_id links to survey_question_sets. Only carry it across if that
# same schema_id already exists in prod's survey_question_sets - otherwise
# the submission fails schema validation. Default: drop it (submit as
# null), since the raw SUS/ethics answers don't depend on it. Note:
# schema_id has no DB-level foreign key (see backend/app/models/survey.py) -
# the risk is app-level validation at POST time, not a constraint violation.
DROP_SCHEMA_ID = True


def remap_config_id(dev_id):
    if dev_id is None:
        return None, True
    if dev_id in CONFIG_ID_MAP:
        return CONFIG_ID_MAP[dev_id], True
    if UNMAPPED_ACTION == "null":
        return None, True
    if UNMAPPED_ACTION == "skip":
        return None, False
    raise SystemExit(f"Unmapped configuration_id {dev_id} and UNMAPPED_ACTION='fail' - aborting.")


def post_survey(api_base, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/survey", data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return True, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return False, e.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        return False, str(e)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(f"Usage: {sys.argv[0]} <prod-api-base-url, e.g. https://prod-api.example.org/api/v1> [--dry-run]")
    api_base = args[0]
    dry_run = "--dry-run" in sys.argv

    with open(EXPORT_FILE) as f:
        rows = json.load(f)
    print(f"Loaded {len(rows)} rows from {EXPORT_FILE}")

    ok, failed, skipped = 0, [], []
    for row in rows:
        config_id, keep = remap_config_id(row.get("configuration_id"))
        if not keep:
            skipped.append(row["survey_id"])
            continue

        payload = {
            "survey_id": row["survey_id"],
            "user_id": row["user_id"],
            "timestamp": row["timestamp"],
            "pilot_tag": row["pilot_tag"],
            "app_version": row.get("app_version"),
            "ai_model_version": row.get("ai_model_version"),
            "tam_sus_responses": row["tam_sus_responses"],
            "ethics_responses": row["ethics_responses"],
            "domain_specific": row.get("domain_specific"),
            "configuration_id": config_id,
            "schema_id": None if DROP_SCHEMA_ID else row.get("schema_id"),
        }

        if dry_run:
            print(f"[dry-run] would POST survey_id={payload['survey_id']} configuration_id={config_id}")
            ok += 1
            continue

        success, result = post_survey(api_base, payload)
        if success:
            ok += 1
        else:
            failed.append((row["survey_id"], result))
            print(f"FAILED survey_id={row['survey_id']}: {result}")

    print()
    print(f"Done. {ok} succeeded, {len(failed)} failed, {len(skipped)} skipped (unmapped configuration_id).")
    if failed:
        print("Failed survey_ids:", [f[0] for f in failed])
    if skipped:
        print("Skipped survey_ids (unmapped configuration_id):", skipped)


if __name__ == "__main__":
    main()
