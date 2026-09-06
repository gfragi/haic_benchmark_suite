#!/usr/bin/env python3
"""
migrate_sus_data_load.py

Step 2 of 2 (see migrate_sus_data_extract.sh for step 1).

Loads surveys exported from another environment via POST /survey/import,
which does the whole batch in one call and resolves each row's
configuration_id itself - by matching the row's pilot_tag against
configurations on the TARGET platform - rather than requiring a manually
maintained dev-id -> prod-id map. A pilot_tag matching exactly one
configuration there resolves automatically; one matching zero or several is
left unlinked and reported back, unless you pass an override for it.

Usage:
  python3 scripts/migrate_sus_data_load.py <target-api-base-url> [export-file] [--dry-run]
  python3 scripts/migrate_sus_data_load.py <target-api-base-url> [export-file] --overrides '{"applications": 8}'

  export-file defaults to surveys_dev_export.json (what
  migrate_sus_data_extract.sh writes).

Stdlib only (json/urllib) - nothing to install.
"""
import json
import sys
import urllib.error
import urllib.request


def main():
    positional = []
    skip_next = False
    for i, a in enumerate(sys.argv[1:], start=1):
        if skip_next:
            skip_next = False
            continue
        if a == "--overrides":
            skip_next = True
            continue
        if not a.startswith("--"):
            positional.append(a)

    if not positional:
        raise SystemExit(
            f"Usage: {sys.argv[0]} <target-api-base-url> [export-file] [--dry-run] "
            f"[--overrides '{{\"pilot_tag\": configuration_id}}']"
        )
    api_base = positional[0]
    export_file = positional[1] if len(positional) > 1 else "surveys_dev_export.json"
    dry_run = "--dry-run" in sys.argv

    overrides = {}
    if "--overrides" in sys.argv:
        idx = sys.argv.index("--overrides")
        overrides = json.loads(sys.argv[idx + 1])

    with open(export_file) as f:
        rows = json.load(f)
    print(f"Loaded {len(rows)} rows from {export_file}")

    body = json.dumps({
        "rows": rows,
        "pilot_tag_config_overrides": overrides,
        "dry_run": dry_run,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/survey/import", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Import request failed: {e.read().decode('utf-8', errors='replace')}")

    print(json.dumps(result, indent=2))

    if result.get("unmatched_pilot_tags"):
        print(f"\nUnmatched pilot_tags (no configuration_id assigned): {result['unmatched_pilot_tags']}")
        print('Re-run with --overrides \'{"tag": config_id}\' to resolve, or create a matching configuration on the target first.')
    if result.get("ambiguous_pilot_tags"):
        print(f"\nAmbiguous pilot_tags (multiple configurations matched, none assigned): {result['ambiguous_pilot_tags']}")
        print("Re-run with --overrides to pick which configuration_id to use for each.")


if __name__ == "__main__":
    main()
