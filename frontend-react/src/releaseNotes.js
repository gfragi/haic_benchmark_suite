// Manually maintained release notes, shown on the public /releases page.
// Add a new entry at the top of RELEASES for each release - date/version
// here drives the version number shown in the app header (AppShell.jsx).
// Copy in commit messages / PR summaries as convenient; this isn't wired to
// git automatically.

export const RELEASES = [
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
