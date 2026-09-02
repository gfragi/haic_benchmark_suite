#!/usr/bin/env python
"""
seed_ontology.py

Seeds the ontology_entities table from data/haic_ontology.json. Idempotent -
safe to re-run (INSERT ... ON CONFLICT (entity_type, entity_id) DO NOTHING).

Run: python scripts/seed_ontology.py
"""
import json
import sys
from pathlib import Path


def _find_project_root() -> Path:
    """Mirrors backend/app/routers/ontology.py's _find_project_root(): checks
    for haic_env_builder/+packages/ as siblings, which resolves correctly both
    from the repo checkout and from inside the backend container (where the
    backend/ wrapper dir doesn't exist - Dockerfile.backend copies
    backend/app -> ./app directly, alongside haic_env_builder/ and packages/)."""
    here = Path(__file__).resolve()
    for cand in here.parents:
        if (cand / "haic_env_builder").is_dir() and (cand / "packages").is_dir():
            return cand
    return here.parents[1]


PROJECT_ROOT = _find_project_root()
BACKEND_DIR = PROJECT_ROOT / "backend"
if (BACKEND_DIR / "app").is_dir() and str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.dialects.postgresql import insert as pg_insert  # noqa: E402

from app.models.ontology import OntologyEntity  # noqa: E402
from app.utils.database import SessionLocal  # noqa: E402

ONTOLOGY_PATH = PROJECT_ROOT / "data" / "haic_ontology.json"

ARRAY_KEY_TO_ENTITY_TYPE = {
    "domains": "domain",
    "action_types": "action_type",
    "agent_roles": "agent_role",
    "persona_archetypes": "persona_archetype",
    "surrogate_tiers": "surrogate_tier",
    "metric_families": "metric_family",
    "templates": "template",
}


def main() -> None:
    ontology = json.loads(ONTOLOGY_PATH.read_text(encoding="utf-8"))
    db = SessionLocal()

    counts = {}
    total_inserted = 0
    total_skipped = 0
    try:
        for array_key, entity_type in ARRAY_KEY_TO_ENTITY_TYPE.items():
            items = ontology.get(array_key, [])
            inserted = 0
            for item in items:
                entity_id = str(item["id"])
                label = item["label"]
                description = item.get("description", "")
                properties = {k: v for k, v in item.items() if k not in ("id", "label", "description")}

                stmt = pg_insert(OntologyEntity).values(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    label=label,
                    description=description,
                    properties=properties,
                    status="active",
                    created_by="system",
                    version=1,
                ).on_conflict_do_nothing(index_elements=["entity_type", "entity_id"])

                result = db.execute(stmt)
                if result.rowcount:
                    inserted += 1
            db.commit()

            counts[entity_type] = inserted
            total_inserted += inserted
            total_skipped += len(items) - inserted

        print("Seed summary:")
        for entity_type, n in counts.items():
            print(f"  {entity_type}: {n} rows")
        print(f"Total: {total_inserted} rows inserted, {total_skipped} skipped (already existed)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
