import api from "./axios";
export async function fetchSurveyAggregatesByPilot(pilotTag) {
  const { data } = await api.get("/survey/aggregate", {
    params: { pilot_tag: pilotTag }, // adjust if your param name differs
  });
  return data || {};
}

/** Convenience small helpers */
export function computeDeltas(a, b) {
  // a & b are metric objects from the aggregate response
  const safe = (x) => (typeof x === "number" && !Number.isNaN(x) ? x : 0);
  const delta = {
    sus: safe(b.avg_sus) - safe(a.avg_sus),
    ethics: safe(b.avg_ethics) - safe(a.avg_ethics),
  };
  return {
    delta,
    aCount: a.count || 0,
    bCount: b.count || 0,
    // quick “likely meaningful” hint via CI non-overlap
    susLikelyMeaningful: !intervalsOverlap(
      a.avg_sus,
      a.sus_ci95,
      b.avg_sus,
      b.sus_ci95
    ),
    ethicsLikelyMeaningful: !intervalsOverlap(
      a.avg_ethics,
      a.ethics_ci95,
      b.avg_ethics,
      b.ethics_ci95
    ),
  };
}

function intervalsOverlap(m1, ci1, m2, ci2) {
  if ([m1, ci1, m2, ci2].some((v) => typeof v !== "number")) return true;
  const a1 = m1 - ci1,
    b1 = m1 + ci1;
  const a2 = m2 - ci2,
    b2 = m2 + ci2;
  return Math.max(a1, a2) <= Math.min(b1, b2);
}
