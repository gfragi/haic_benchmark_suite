// frontend/src/utils/insightsUtil.js

function rag(value, bands, higherIsBetter = true) {
  const v = Number(value) || 0;
  const [y, g] = bands;
  if (higherIsBetter) {
    if (v >= g) return ["🟢", "strong"];
    if (v >= y) return ["🟡", "ok"];
    return ["🔴", "weak"];
  } else {
    if (v <= y) return ["🟢", "low"];
    if (v <= g) return ["🟡", "moderate"];
    return ["🔴", "high"];
  }
}

function b(html) {
  // wrap a label in <strong>…</strong> so v-html renders it bold
  return `<strong>${html}</strong>`;
}

export function summarizeRunBrief(result = {}) {
  const decs = result.decisions || [];
  const N = decs.length;

  let T = 0;
  if (N >= 2) {
    const t0 = Number(decs[0]?.t) || 0;
    const t1 = Number(decs[N - 1]?.t) || t0;
    T = Math.max(0, t1 - t0);
  }

  const m = result.metrics || {};
  const F = Number(m.F || 0);
  const H = Number(m.HCL || 0);
  const Tr = Number(m.Tr || 0);
  const ES = Number(m.EfficiencyScore || 0);
  const EL = Number(m.EL || 0);

  const task = result.task || "Scenario";
  const env = result.environment || "env";

  let s = `${task} (${env}): ${N} actions in ~${T.toFixed(
    1
  )}s · pace ${F.toFixed(1)}/min · efficiency ${ES.toFixed(2)} (EL=${EL.toFixed(
    2
  )}) · accuracy ${Tr.toFixed(2)} · responsiveness ${H.toFixed(2)}.`;

  // add-ons
  const A = Number(m.A || 0);
  const S = Number(m.S || 0);
  const off = decs.filter((d) => d.off_role_action).length / (N || 1);
  const prog = decs.filter((d) => {
    const et = String(d.event_type || "").toLowerCase();
    return et === "progress" || et === "checklist_progress";
  }).length;

  const adds = [];
  if (A > 0.05) adds.push("improving over time");
  else if (A < -0.05) adds.push("degrading over time");
  if (S >= 0.8) adds.push("aligned with surrogate");
  else if (S <= 0.5) adds.push("diverging from surrogate");
  if (off > 0.1) adds.push("frequent off-role actions");
  if (prog > 0) adds.push(`${prog} progress ticks`);

  if (adds.length) s += " " + adds.join("; ") + ".";
  return s;
}

export function deriveAuxRates(result = {}) {
  const decs = result.decisions || [];
  const N = decs.length;
  const off = decs.filter((d) => d.off_role_action).length;
  const offRate = N ? off / N : 0;

  let T = 0;
  if (N >= 2) {
    const t0 = Number(decs[0]?.t) || 0;
    const t1 = Number(decs[N - 1]?.t) || t0;
    T = Math.max(0, t1 - t0);
  }

  const prog = decs.filter((d) => {
    const et = String(d.event_type || "").toLowerCase();
    return et === "progress" || et === "checklist_progress";
  }).length;

  const progPerSec = T > 0 ? prog / T : 0;
  return { offrole_rate: offRate, progress_per_sec: progPerSec };
}

export function interpretMetrics(metrics = {}, aux = {}) {
  const F = Number(metrics.F || 0);
  const D = Number(metrics.D || 0);
  const H = Number(metrics.HCL || 0);
  const Tr = Number(metrics.Tr || 0);
  const A = Number(metrics.A || 0);
  const S = Number(metrics.S || 0);
  const EL = Number(metrics.EL || 0);
  const ES = Number(metrics.EfficiencyScore || 0);

  const off = Number(aux.offrole_rate || 0);
  const progPS = Number(aux.progress_per_sec || 0);

  const out = [];

  // Pace
  {
    const [pEmoji, pLabel] = rag(F, [5, 15], true);
    out.push(
      `${pEmoji} ${b("Pace")} (${F.toFixed(1)}/min): ${pLabel} activity level.`
    );
  }

  // Duration (lower better)
  {
    const [dE, dL] = rag(D, [0.2, 0.5], false);
    out.push(`${dE} ${b("Action duration")} (D=${D.toFixed(2)}s): ${dL}.`);
  }

  // Responsiveness
  {
    const [hE, hL] = rag(H, [0.6, 0.8], true);
    out.push(
      `${hE} ${b("Responsiveness")} (HCL=${H.toFixed(
        2
      )}): ${hL} reaction speed.`
    );
  }

  // Accuracy (Tr)
  {
    const [aE, aL] = rag(Tr, [0.9, 0.97], true);
    out.push(`${aE} ${b("Accuracy")} (Tr=${Tr.toFixed(2)}): ${aL} error rate.`);
  }

  // Adaptability
  if (A >= 0.1) {
    out.push(`🟢 ${b("Adaptability")} (A=+${A.toFixed(2)}): learning trend.`);
  } else if (A <= -0.1) {
    out.push(`🔴 ${b("Adaptability")} (A=${A.toFixed(2)}): degrading trend.`);
  } else {
    out.push(`🟡 ${b("Adaptability")} (A=${A.toFixed(2)}): stable.`);
  }

  // Surrogate alignment
  {
    const [sE] = rag(S, [0.5, 0.8], true);
    if (S >= 0.8)
      out.push(
        `${sE} ${b("Surrogate alignment")} (S=${S.toFixed(2)}): high agreement.`
      );
    else if (S <= 0.5)
      out.push(
        `${sE} ${b("Surrogate alignment")} (S=${S.toFixed(2)}): diverging.`
      );
    else
      out.push(
        `${sE} ${b("Surrogate alignment")} (S=${S.toFixed(2)}): partial match.`
      );
  }

  // Policy conformity (off-role)
  {
    const [oE, oL] = rag(off, [0.05, 0.1], false);
    out.push(
      `${oE} ${b("Policy conformity")} (off-role ${(off * 100).toFixed(
        1
      )}%): ${oL}.`
    );
  }

  // Task progress
  if (progPS > 0) {
    out.push(`🟢 ${b("Task progress")}: ${progPS.toFixed(2)} ticks/sec.`);
  } else {
    out.push(`🟡 ${b("Task progress")}: no explicit ticks.`);
  }

  // Efficiency
  {
    const [eE, eL] = rag(ES, [0.6, 0.8], true);
    out.push(
      `${eE} ${b("Efficiency")} (score=${ES.toFixed(2)}, EL=${EL.toFixed(
        2
      )}): ${eL}.`
    );
  }

  return out;
}
