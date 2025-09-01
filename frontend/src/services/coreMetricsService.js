import api from "./axios";

export async function computeCoreV1(
  runId,
  { rt_max = 5.0, baseline_s = null } = {}
) {
  const params = new URLSearchParams();
  params.set("rt_max", rt_max);
  if (baseline_s !== null && baseline_s !== undefined)
    params.set("baseline_s", baseline_s);

  const { data } = await api.post(
    `/collab-metrics/collab/from-artifact/${encodeURIComponent(
      runId
    )}?${params.toString()}`
  );
  // backend returns { artifact, ref }; we’ll use artifact directly
  return data.artifact;
}
