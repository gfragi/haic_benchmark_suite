// robust helpers for all current/future response shapes
import api from "./axios";

// // unwrap common backend response shapes
// const unwrap = (payload) => {
//   let x =
//     payload?.simulation_result ??
//     payload?.result ??
//     payload?.run ??
//     payload?.log ??
//     payload?.content ??
//     payload;
//   if (typeof x === "string") {
//     try {
//       x = JSON.parse(x);
//     } catch {
//       /* keep as-is */
//     }
//   }
//   return x;
// };

// function unbox(data) {
//   // accept {simulation_result}, {result}, {run}, {log}, {content}, bare object, or JSON string
//   let x =
//     data?.simulation_result ??
//     data?.result ??
//     data?.run ??
//     data?.log ??
//     data?.content ??
//     data;
//   if (typeof x === "string") {
//     try {
//       x = JSON.parse(x);
//     } catch {
//       /* keep as-is */
//     }
//   }
//   return x;
// }

export async function simulate(configName, seed = "") {
  const params = new URLSearchParams();
  params.set("name", configName);
  if (seed !== "" && seed !== null && seed !== undefined) {
    params.set("seed", String(seed));
  }
  const { data } = await api.post(
    `/v1/simulator/simulate?${params.toString()}`
  );
  // backend returns the full result payload
  return data;
}

export async function listMetrics() {
  const { data } = await api.get(`/v1/simulator/runs`);
  // accept either {files:[...]} or a raw array for safety
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.files)) return data.files;
  if (Array.isArray(data?.available)) return data.available;
  return [];
}
export async function loadMetrics(file) {
  const safe = encodeURIComponent(file);
  const { data } = await api.get(`/v1/simulator/runs/${safe}`);
  // accept either raw result or {result:...}
  return data?.result ?? data;
}
