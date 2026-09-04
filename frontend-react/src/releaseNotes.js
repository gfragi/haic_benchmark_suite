// Manually maintained release notes, shown on the public /releases page.
// Add a new entry at the top of RELEASES for each release - date/version
// here drives the version number shown in the app header (AppShell.jsx).
// Copy in commit messages / PR summaries as convenient; this isn't wired to
// git automatically.

export const RELEASES = [
  {
    version: 'v3.0',
    date: '2026-09-04',
    backend: [
      'Added the blind-prediction multi-model experiment methodology: extract a target model\'s AI-action frequency only (operator responses stay untouched), predict its HAIC metrics using a source model\'s fitted surrogate, seal the predictions with a timestamp before any real data is used, then reveal the target\'s real operator log and compare — with cross-model surrogate similarity (S) and three hypothesis verdicts (H1 frequency transfer, H2 matrix stability, H3 regime decomposition).',
      'Added `experiment_runs`, `experiment_models`, and `experiment_results` tables, and a standalone `HAICExperimentEngine` package with no dependency on the backend app, so the same engine can run outside the API.',
      'Added the full `/experiments` REST surface: create an experiment, register models (by path or direct log upload), extract, predict, reveal, compare, and an assembled results report with a JSON export. Predictions are enforced immutable once sealed — re-predicting an already-sealed model returns 409.',
    ],
    frontend: [
      'Added a third "Multi-model experiment" mode to the Simulate page: a 3-panel stepper (setup → blind predict → reveal & compare) with per-model extraction status chips, a prominently displayed seal timestamp as the experiment\'s scientific-integrity marker, and a predicted-vs-real comparison table with hypothesis verdicts, exportable as JSON.',
    ],
  },
  {
    version: 'v2.4',
    date: '2026-09-03',
    backend: [
      'Migrated the ontology from a static JSON file to Postgres (`ontology_entities`, `scenario_entity_usage`), with full CRUD (`GET/POST/PUT/DELETE /ontology/{entity_type}[/{entity_id}]`), soft-delete only (deprecate, never hard-delete), and per-entity usage tracking recorded automatically on every probabilistic run.',
      'Replaced the Smart-City-only `MarkovSurrogateSC` with a domain-agnostic `MarkovSurrogate` — all action vocabulary now comes from the fitted model file, not hardcoded Python constants.',
      'Added `scripts/fit_markov.py`, a generic Markov-model fitter for any HAIC-format log (configurable field mappings, not hardcoded to the Smart City pilot), and `POST /ontology/fit-model` — upload an interaction log, auto-discover its action vocabulary, and get a fitted surrogate plus a new domain/template registered in the ontology, ready to simulate from immediately.',
    ],
    frontend: [
      'Added a "Bring your own data" flow inside Probabilistic mode: a 3-stage wizard (upload → map fields → fit & simulate) with a live field-mapping preview before anything is submitted.',
      'Simulate page redesigned to surface the platform\'s research grounding: mode cards explaining Scripted vs. Probabilistic, template provenance ("Fitted on 566 sessions · 5 operators" vs. "Custom fit"), a persona accept-rate visualization, and a fidelity callout (predicted vs. real Tr/HCL/F) shown for the validated Smart City domain.',
    ],
  },
  {
    version: 'v2.3',
    date: '2026-09-02',
    backend: [
      'Added `MarkovSurrogateSC`, a first-order Markov surrogate fitted from the real 566-session Smart City pilot log — samples AI/operator decision sequences and response times from the real fitted transition matrix and duration stats, not a scripted replay.',
      'Added the HAIC ontology (`data/haic_ontology.json`): domains, action types, agent roles, persona archetypes, surrogate tiers, metric families, and scenario templates, plus a JSON scenario schema.',
      'Added `POST /simulator/probabilistic` (Tier 0 scripted / Tier 1 Markov chain), with persona archetypes (accept-bias and response-time bias applied on top of the aggregate fit) and automatic baseline resolution for Effort Loss.',
      'Validated the surrogate against the real pilot data it was fitted from: HCL and F land within 1% of real; Tr is ~12% low, traced to sparse data in one AI-action category (n=32) rather than a modelling error.',
    ],
    frontend: [
      'Added a "Probabilistic" mode to the Simulate page\'s Run tab, alongside the existing Scripted mode: template tiles, an ontology-driven configuration form (domain, tier, persona, metrics), a live preview, and scenario JSON export/import.',
    ],
  },
  {
    version: 'v2.2',
    date: '2026-08-31',
    backend: [
      'Added `POST /simulator/simulate-and-ingest` — runs a curated scenario N times via `simulate_environment()`, translates each run into the standard session-log format through a new `sim_bridge` service, and ingests it into a configuration through the same pipeline real pilot uploads use.',
      'Added `GET /simulator/scenarios` — a curated, verified-runnable subset of the bundled scenario configs.',
      'Added scenario-authoring endpoints backing the new "Build Scenario" tab.',
      'Fixed project-root detection for config resolution inside the deployed container, where the `backend/` wrapper directory doesn\'t exist.',
    ],
    frontend: [
      'Added a `/simulate` page: a "Run" tab (pick a scenario, target configuration, and run count; generate & ingest) and a "Build Scenario" tab (define custom scenarios — agents, scripted steps, timings, outcomes — from scratch).',
      'Ingested synthetic sessions evaluate through the same dashboard as real pilot data.',
    ],
  },
  {
    version: 'v2.1.3',
    date: '2026-07-23',
    backend: [
      'Fixed free-text domain-specific question answers being dropped from the results view — the aggregation endpoint computed them but only ever returned a count, discarding the actual text. Nothing was lost in storage; this only affected what was displayed.',
      'Added `GET /survey/raw` — one row per survey submission (SUS/Ethics/domain-specific answers flattened into columns), for analytic export instead of the existing aggregated-only view.',
    ],
    frontend: [
      'Survey detail page now shows free-text domain-specific answers instead of just a response count.',
      'Added an "Export raw responses" CSV button (one row per respondent) alongside the existing aggregated CSV export.',
      'Fixed CSV export not escaping commas/quotes/newlines in cell values — harmless for the old aggregate export, but would have corrupted the new raw export the moment a free-text answer contained a comma.',
    ],
  },
  {
    version: 'v2.1.2',
    date: '2026-07-22',
    backend: [
      'Added `question_position` to survey question sets — domain-specific questions can now be placed before or after SUS/Ethics per schema, instead of a single hardcoded order for everyone.',
      'Configurations now remember the `schema_id` of the question set attached to their survey link, so it stays fixed to what the link was built with instead of silently following "latest for this pilot_tag" if a newer schema is created later.',
      'Added `PATCH /configuration/{id}/schema` to attach/detach a question set from a configuration.',
    ],
    frontend: [
      'Question Set Editor: added a "Domain questions position" toggle (before/after SUS & Ethics), saved with the rest of the question set.',
      'Added a one-click copy icon to each row in the Evaluations list — copies the public survey link without opening the "Build Link" modal.',
    ],
  },
  {
    version: 'v2.1.1',
    date: '2026-07-22',
    backend: [
      'Added `POST /configuration/{id}/purge` — clears a configuration\'s logs, results, and MinIO objects without deleting the configuration itself. Useful for recovering from stale/leftover MinIO data under a reused numeric config id (e.g. a fresh database pointed at old MinIO storage), without needing direct DB or MinIO access.',
    ],
    frontend: [
      'Added a "Purge" action to the Evaluations list, alongside Delete — clears a configuration\'s data while keeping its name, settings, and registered polling sources.',
    ],
  },
  {
    version: 'v2.1',
    date: '2026-07-22',
    backend: [
      'Fixed `pilot_tag`/`ai_model_version`/`app_version`/session timestamps not being read when a partner nests them under `meta.*` instead of the top level — was silently grouping everything under "Unknown".',
      'Fixed a stale/orphaned result row being left behind whenever a version\'s label changes between evaluations (e.g. after the fix above) — re-evaluating now cleans up any version no longer present in the current logs, not just the ones being replaced.',
      'Extended metrics (Confidence, Response Time, Human-AI Agreement Rate) now auto-derive directly from `decisions[]` payloads when a pilot doesn\'t send an explicit `interaction_data` block — no changes needed on partners\' side.',
      'Fixed Human-AI Agreement Rate and Surrogate Similarity (S) both returning a false `0.0` instead of `null`/"not applicable" when there was no comparable data for that pilot.',
      'Added per-session `metric_timeseries` data to evaluation results, powering the new "metric over time" view.',
      'Added pull-based log ingestion: register a MinIO bucket (on the same consortium MinIO, no extra credentials needed) or a partner-owned HTTP endpoint per configuration, polled automatically on a schedule — no manual upload required once set up.',
    ],
    frontend: [
      'Added a "Metric over time" chart to the results dashboard, with a metric picker — shows per-session trends (e.g. is Adaptability actually improving across sessions), not just version-level aggregates.',
      'Version Comparison bar chart and quadrant plots now consistently respect the "Show versions" filter.',
      'Rebuilt the Ingest Logs wizard\'s "Register Endpoint" tab (previously non-functional) into a working MinIO-bucket / HTTP-endpoint registration flow with live poll status, "poll now", and remove.',
    ],
  },
  {
    version: 'v2.0',
    date: '2026-07-17',
    backend: [
      'Implemented `derive_correct_rules` (previously documented but never actually implemented) for deriving trust labels from AI/operator decision pairs.',
      'Fixed cross-version comparability: `baseline_s`/`rt_max` auto-derivation is now computed once globally across all versions in an evaluation, instead of per-version, which was silently breaking apples-to-apples comparison.',
      'Fixed `total_time` to prefer summed per-event durations over wall-clock timestamp span, correcting Effort Loss and Interaction Frequency for pilots with queue-wait gaps between events.',
      'Added `interaction_data` pass-through so Extended Metrics (accuracy/precision/recall/etc.) can now be computed from uploaded logs end-to-end, not just core HAIC metrics.',
      'Fixed re-running evaluation creating duplicate result rows per version — it now replaces the prior result instead of accumulating.',
      'Added a free-text survey comments endpoint and domain-specific question aggregation.',
      'Fixed the `/meta/health` MinIO check to use a bucket-scoped permission check instead of one requiring broad account access.',
    ],
    frontend: [
      'Added Keycloak authentication, with an explicit public-page allowlist for pages that stay reachable without logging in.',
      'Quadrant plots: added a custom axis picker, per-version filtering, and auto-selection of the first plot that actually has data.',
      'Added a live "what if baseline were X" recompute for Effort Loss / Efficiency Score, directly in the browser.',
      'Extended Metrics tab now supports comparing multiple versions at once (grouped bar charts), matching the Core HAIC tab.',
      'Survey detail page: single-version detail breakdown no longer requires picking a second version to compare against.',
      'Added a live Ethics & Trust score to both survey forms, alongside the existing SUS score.',
      'Sidebar reorganized into Pilots / Analysis sections, with public pages labeled.',
    ],
  },
]
