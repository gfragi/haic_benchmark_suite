function normalizeBase(b) {
  if (!b) return "";
  const s = String(b).trim();
  if (/^https?:\/\//i.test(s)) return s.replace(/\/+$/, "");
  return (s.startsWith("/") ? s : "/" + s).replace(/\/+$/, "");
}

const SURVEY_EP =
  (typeof import.meta !== "undefined" &&
    import.meta?.env?.VITE_SURVEY_ENDPOINT) ||
  (typeof process !== "undefined" && process.env?.VUE_APP_SURVEY_ENDPOINT) ||
  "";

const INFERRED_HOST = (() => {
  try {
    if (SURVEY_EP && /^https?:\/\//i.test(SURVEY_EP)) {
      const u = new URL(SURVEY_EP);
      return `${u.protocol}//${u.host}`;
    }
  } catch (_e) {
    /* ignore */
  }
  return "";
})();

// 👇 NEW: guess :8000 when running the UI on :8080 in dev
const DEV_GUESS =
  typeof window !== "undefined" &&
  (window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1") &&
  window.location.port === "8080"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "";

const ENV_BASE =
  (typeof import.meta !== "undefined" && import.meta?.env?.VITE_API_BASE) ||
  (typeof process !== "undefined" && process.env?.VUE_APP_API_BASE) ||
  INFERRED_HOST ||
  DEV_GUESS;

const BASE = normalizeBase(ENV_BASE);
const SCHEMAS_BASE =
  (/^https?:\/\//i.test(BASE) ? BASE : "") +
  `${BASE ? "" : ""}/api/v1/survey/schemas`;

// ---- API calls ----
export async function fetchSchemaById(id) {
  const res = await fetch(`${SCHEMAS_BASE}/${encodeURIComponent(id)}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok)
    throw new Error(`Failed to fetch schema ${id} (HTTP ${res.status})`);
  return res.json();
}

export async function fetchLatestSchemaForPilot(pilotTag) {
  const res = await fetch(
    `${SCHEMAS_BASE}?pilot_tag=${encodeURIComponent(pilotTag)}`,
    { headers: { Accept: "application/json" } }
  );
  if (res.status === 404 || res.status === 204) return null;
  if (!res.ok)
    throw new Error(`Failed to fetch pilot schema (HTTP ${res.status})`);
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// 👇 Ensure POST uses the same base (previously it might have used a relative /api path)
export async function createSchema(payload) {
  const res = await fetch(`${SCHEMAS_BASE}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to create schema (HTTP ${res.status})`);
  return res.json(); // { schema_id, ... }
}
