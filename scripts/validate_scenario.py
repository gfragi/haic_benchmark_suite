"""
validate_scenario.py

Standalone CLI validator for HAIC scenario JSON files (haic.scenario.v1),
against data/haic_scenario_schema.json and the vocabulary in
data/haic_ontology.json.

Usage:
    python scripts/validate_scenario.py path/to/scenario.json

Dependencies: jsonschema (pip install jsonschema --break-system-packages)

--- Last run output (against a scenario extracted from the sc_permit_review
    template in data/haic_ontology.json) ---

Scenario is VALID.

  Domain:          Smart City
  Template:        sc_permit_review (Smart City — Permit review) [declared]
  Surrogate tier:  1 - Markov chain (First-order Markov chain fitted from real pilot logs)
  Sessions:        10 sessions x 164 items = 1640 items
  Estimated decisions: 3280 (n_items * n_sessions * 2)

  Metrics requested:
    Tr    Trust proxy                      - requires: correct                      [OK]
    HCL   Human-centeredness               - requires: duration_s, rt_max_s         [OK]
    EL    Effort loss                      - requires: duration_s, baseline_s       [OK]
    F     Interaction frequency            - requires: timestamps                   [OK]
    S     Surrogate similarity             - requires: surrogate_probs              [OK]

  Personas in use:
    from_data  (Fitted from pilot data) - agent(s): operator

  Agents:
    ai_system     (ai1      ) role=ai_system
    surrogate     (operator ) role=surrogate  persona=from_data  fitted_model=data/sc_markov_model.json

Note: "template" was resolved from the scenario's own declared `template`
field, hence "[declared]" rather than "[exact match]" - the exact-match
fallback path (matching domain/surrogate_tier/rt_max_s/n_items/n_sessions
against every ontology template) only runs when no `template` field is
present at all.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ONTOLOGY_PATH = "data/haic_ontology.json"
SCHEMA_PATH = "data/haic_scenario_schema.json"


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def explain(error) -> str:
    """A friendlier one-line explanation for a jsonschema ValidationError -
    jsonschema's own messages for contains/allOf failures ("None of [...]
    are valid under the given schema") aren't very actionable on their own."""
    validator = error.validator
    if validator == "required":
        return f"missing required field(s): {', '.join(error.message.split(chr(39))[1::2]) or error.message}"
    if validator == "enum":
        return f"'{error.instance}' is not a recognized value - allowed: {error.validator_value}"
    if validator == "const":
        return f"'{error.instance}' must be exactly '{error.validator_value}'"
    if validator == "minItems":
        return f"needs at least {error.validator_value} item(s), got {len(error.instance)}"
    if validator == "type":
        return f"expected type {error.validator_value}, got {type(error.instance).__name__}"
    if validator in ("allOf", "contains", "anyOf"):
        return (
            "agents array doesn't satisfy a structural requirement - needs at least one "
            "ai_system agent and at least one human_operator/surrogate agent"
            + (", and (since surrogate_tier >= 1) at least one surrogate agent with a non-empty fitted_model" if validator == "allOf" else "")
        )
    return error.message


def field_path(error) -> str:
    path = list(error.absolute_path)
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in path) if path else "$ (root)"


def validate(scenario: dict, schema: dict) -> list:
    validator = Draft7Validator(schema)
    return sorted(validator.iter_errors(scenario), key=lambda e: list(e.absolute_path))


def find_template(scenario: dict, ontology: dict) -> tuple[str | None, bool]:
    """Return (template_id, exact_match) - prefers an explicit `template`
    field on the scenario, else looks for an ontology template whose
    domain/surrogate_tier/rt_max_s/n_items/n_sessions match exactly."""
    templates = ontology.get("templates", [])
    if scenario.get("template"):
        return scenario["template"], False

    for t in templates:
        if (
            t.get("domain") == scenario.get("domain")
            and t.get("surrogate_tier") == scenario.get("surrogate_tier")
            and t.get("rt_max_s") == scenario.get("rt_max_s")
            and t.get("n_items") == scenario.get("n_items")
            and t.get("n_sessions") == scenario.get("n_sessions")
        ):
            return t["id"], True
    return None, False


def print_summary(scenario: dict, ontology: dict) -> None:
    by_id = {"domains": {}, "metric_families": {}, "surrogate_tiers": {}, "persona_archetypes": {}, "agent_roles": {}, "templates": {}}
    for key in by_id:
        for item in ontology.get(key, []):
            by_id[key][item["id"]] = item

    print("Scenario is VALID.")
    print()

    domain = by_id["domains"].get(scenario["domain"], {})
    print(f"  Domain:          {domain.get('label', scenario['domain'])}")

    template_id, exact = find_template(scenario, ontology)
    if template_id:
        t = by_id["templates"].get(template_id, {})
        tag = "[exact match]" if exact else "[declared]"
        print(f"  Template:        {template_id} ({t.get('label', '?')}) {tag}")
    else:
        print("  Template:        none (custom scenario)")

    tier = by_id["surrogate_tiers"].get(scenario["surrogate_tier"], {})
    print(f"  Surrogate tier:  {scenario['surrogate_tier']} - {tier.get('label', '?')} ({tier.get('description', '')})")

    n_items, n_sessions = scenario["n_items"], scenario["n_sessions"]
    print(f"  Sessions:        {n_sessions} sessions x {n_items} items = {n_items * n_sessions} items")
    print(f"  Estimated decisions: {n_items * n_sessions * 2} (n_items * n_sessions * 2)")
    print()

    # Which fields are plausibly available, to flag metrics missing inputs.
    available = {"correct", "duration_s", "rt_max_s", "timestamps", "sequence_order"}
    if scenario.get("baseline_s") is not None:
        available.add("baseline_s")
    if scenario["surrogate_tier"] >= 1:
        available.add("surrogate_probs")

    print("  Metrics requested:")
    for metric_id in scenario["metrics"]:
        m = by_id["metric_families"].get(metric_id, {})
        requires = m.get("requires", [])
        missing = [r for r in requires if r not in available]
        status = "[OK]" if not missing else f"[MISSING: {', '.join(missing)}]"
        print(f"    {metric_id:<5} {m.get('label', '?'):<32} - requires: {', '.join(requires):<28} {status}")
    print()

    personas: dict[str, list[str]] = {}
    for agent in scenario["agents"]:
        p = agent.get("persona")
        if p:
            personas.setdefault(p, []).append(agent["id"])
    if personas:
        print("  Personas in use:")
        for p, agent_ids in personas.items():
            label = by_id["persona_archetypes"].get(p, {}).get("label", p)
            print(f"    {p}  ({label}) - agent(s): {', '.join(agent_ids)}")
    else:
        print("  Personas in use: none declared")
    print()

    print("  Agents:")
    for agent in scenario["agents"]:
        extras = "".join(f"  {k}={v}" for k, v in agent.items() if k not in ("id", "role"))
        print(f"    {agent['role']:<13} ({agent['id']:<9}) role={agent['role']}{extras}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_scenario.py path/to/scenario.json", file=sys.stderr)
        sys.exit(1)

    scenario_path = sys.argv[1]
    ontology = load_json(ONTOLOGY_PATH)
    schema = load_json(SCHEMA_PATH)
    scenario = load_json(scenario_path)

    errors = validate(scenario, schema)
    if errors:
        print(f"Scenario is INVALID ({len(errors)} error(s)).\n")
        for e in errors:
            print(f"  {field_path(e)}")
            print(f"    {explain(e)}")
        sys.exit(1)

    print_summary(scenario, ontology)
    sys.exit(0)


if __name__ == "__main__":
    main()
