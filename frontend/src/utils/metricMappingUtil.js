// src/utils/metricMappingUtil.js
export const CORE_METRIC_META = {
  F: {
    label: "F (interactions/min)",
    pillar: "Interaction / Collaboration",
    fmt: (x) => x?.toFixed(2),
  },
  D: {
    label: "D (avg action duration, s)",
    pillar: "Performance / Efficiency",
    fmt: (x) => x?.toFixed(2),
  },
  HCL: {
    label: "HCL (human-centeredness)",
    pillar: "Human-Centeredness",
    fmt: (x) => `${Math.round((x || 0) * 100)}%`,
  },
  Tr: {
    label: "Tr (trust proxy)",
    pillar: "Trust / Transparency",
    fmt: (x) => `${Math.round((x || 0) * 100)}%`,
  },
  A: {
    label: "A (adaptability)",
    pillar: "Adaptability",
    fmt: (x) => x?.toFixed(2),
  },
  S: {
    label: "S (similarity)",
    pillar: "Similarity (Surrogates)",
    fmt: (x) => `${Math.round((x || 0) * 100)}%`,
  },
  EL: {
    label: "EL (effort loss)",
    pillar: "Performance / Efficiency",
    fmt: (x) => `${((x || 0) * 100).toFixed(1)}%`,
  },
  EfficiencyScore: {
    label: "Efficiency Score",
    pillar: "Performance / Efficiency",
    fmt: (x) => `${Math.round((x || 0) * 100)}%`,
  },
};
