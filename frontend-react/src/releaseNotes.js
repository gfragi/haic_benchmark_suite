// Manually maintained release notes, shown on the public /releases page.
// Add a new entry at the top of RELEASES for each release - date/version
// here drives the version number shown in the app header (AppShell.jsx).
// Copy in commit messages / PR summaries as convenient; this isn't wired to
// git automatically.

export const RELEASES = [
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
