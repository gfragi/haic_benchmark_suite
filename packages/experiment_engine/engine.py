"""
engine.py

HAICExperimentEngine: orchestrates the multi-model cross-comparison
experiment flow (extract -> predict -> fit -> compare) described in the
Step 2 task. A standalone module - no backend/app imports. It talks to the
experiment_* tables (created in Step 1) through a SQLAlchemy Session,
reflecting them via SQLAlchemy Core (sa.Table(autoload_with=...)) rather
than importing the ORM model classes from backend/app/models/experiments.py,
so this package stays usable outside the FastAPI app.

Scope note: phase_0 (AI-frequency extraction) and phase_2 (real-matrix
fitting) are written against the Smart City pilot's own log/action
vocabulary (payload.ai_decision/payload.op_decision, the ai_accept/
ai_reject/ai_flag canon), matching this task's own smoke test and its
literal example return shapes. A later step would need to make that
mapping configurable per-domain the way the "Bring Your Own Data" fit-model
endpoint does, if this engine is to run outside the SC pilot.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import sqlalchemy as sa


def _find_project_root() -> Path:
    """Same haic_env_builder/+packages/ sibling-check used throughout this
    repo (see backend/app/routers/simulator.py) - works both in a local
    checkout and inside the backend container, where the backend/ wrapper
    directory doesn't exist."""
    here = Path(__file__).resolve()
    for cand in here.parents:
        if (cand / "haic_env_builder").is_dir() and (cand / "packages").is_dir():
            return cand
    return here.parents[2] if len(here.parents) >= 3 else here.parents[-1]


PROJECT_ROOT = _find_project_root()
for _p in (PROJECT_ROOT / "packages" / "surrogate", PROJECT_ROOT / "packages" / "metrics_core", PROJECT_ROOT / "scripts"):
    _p_str = str(_p)
    if _p.is_dir() and _p_str not in sys.path:
        sys.path.insert(0, _p_str)

from surrogate.markov import MarkovSurrogate  # noqa: E402
from metrics_core.interaction_metrics import compute_metrics  # noqa: E402
import fit_markov  # noqa: E402

RT_MAX_S = 300.0
AI_LATENCY_MS = 45000.0
SMOOTH_EPSILON_DEFAULT = 0.005

# SC pilot canon - see module docstring's scope note.
AI_ACTION_MAP = {"Accepted": "ai_accept", "Rejected": "ai_reject", "Flagged for verification": "ai_flag"}
OP_ACTION_MAP = {
    "Accepted": "op_accept", "Rejected": "op_reject",
    "Accepted after verification": "op_accept_verified", "Rejected after verification": "op_reject_verified",
    "Fixed & accepted": "op_fix_accept",
}
ACCEPT_ACTIONS = ["op_accept", "op_accept_verified", "op_fix_accept"]

MODEL_STATUS_ORDER = ["registered", "ai_extracted", "fitted", "predicted", "revealed"]

H1_ERROR_THRESHOLD_PCT = 15.0
H2_S_THRESHOLD = 0.80
H3_ERROR_THRESHOLD = 0.10


# ---------------------------------------------------------------------------
# Analytical metric helpers - closed-form expected values computed directly
# from a fitted model's aggregate.{transition_matrix,duration_stats,
# ai_action_frequency}, without running the surrogate or touching raw
# session data. Used by phase_3's Step A ("real" metrics from model_b's
# matrix) and Step C (H3's structural decomposition).
# ---------------------------------------------------------------------------

def _smooth_row(row: Optional[Dict[str, float]], op_actions: List[str], eps: float) -> Optional[Dict[str, float]]:
    if row is None:
        return None
    smoothed = {op: row.get(op, 0.0) + eps for op in op_actions}
    total = sum(smoothed.values())
    return {op: v / total for op, v in smoothed.items()}


def _accept_mass(row: Optional[Dict[str, float]], accept_actions: List[str]) -> Optional[float]:
    if row is None:
        return None
    return sum(row.get(a, 0.0) for a in accept_actions)


def _analytical_tr(freq: Dict[str, float], matrix: Dict[str, Optional[Dict[str, float]]], accept_actions: List[str]) -> Optional[float]:
    """E[Tr] = sum_i freq[i] * accept_mass(row_i), renormalized over the AI
    actions that actually have a fitted row (mirrors correct = op_action in
    accept_actions, averaged over the AI-action distribution)."""
    total_w, tr = 0.0, 0.0
    for ai, f in freq.items():
        if f <= 0:
            continue
        mass = _accept_mass(matrix.get(ai), accept_actions)
        if mass is None:
            continue
        tr += f * mass
        total_w += f
    return (tr / total_w) if total_w > 0 else None


def _analytical_hcl(freq: Dict[str, float], duration_stats: Dict[str, Optional[dict]], rt_max: float = RT_MAX_S) -> Optional[float]:
    """E[HCL] = clip01(1 - E[duration]/rt_max), matching
    interaction_metrics.compute_metrics()'s HCL formula in expectation."""
    total_w, mean_rt = 0.0, 0.0
    for ai, f in freq.items():
        if f <= 0:
            continue
        stats = duration_stats.get(ai)
        if stats is None:
            continue
        mean_rt += f * stats["mean"]
        total_w += f
    if total_w <= 0:
        return None
    mean_rt /= total_w
    return max(0.0, min(1.0, 1.0 - (mean_rt / rt_max if rt_max > 0 else 1.0)))


def _analytical_f(freq: Dict[str, float], duration_stats: Dict[str, Optional[dict]], ai_latency_ms: float = AI_LATENCY_MS) -> Optional[float]:
    """E[F] (interactions/minute) = 2 events per item / (E[time per item]/60).
    E[time per item] = fixed AI latency (the same constant MarkovSurrogate
    itself always uses - real per-model AI latency isn't part of a fitted
    haic.markov_model.v1 file) + E[human duration]. This is an
    approximation flagged via the caller's returned *_note field, not a
    literal replay of real event timestamps."""
    total_w, mean_human = 0.0, 0.0
    for ai, f in freq.items():
        if f <= 0:
            continue
        stats = duration_stats.get(ai)
        if stats is None:
            continue
        mean_human += f * stats["mean"]
        total_w += f
    if total_w <= 0:
        return None
    mean_human /= total_w
    mean_time_per_item = (ai_latency_ms / 1000.0) + mean_human
    if mean_time_per_item <= 0:
        return None
    return 2.0 / (mean_time_per_item / 60.0)


def _jsd(p: Dict[str, float], q: Dict[str, float], eps: float = 1e-10) -> float:
    """Jensen-Shannon divergence (log base 2) over the union of both dicts'
    keys (generalized from validate_surrogate.py's same-keyset version,
    since two independently-fitted models' op_actions vocabularies can
    legitimately differ)."""
    keys = set(p) | set(q)
    pf = {k: p.get(k, 0.0) for k in keys}
    qf = {k: q.get(k, 0.0) for k in keys}
    m = {k: 0.5 * (pf[k] + qf[k]) for k in keys}

    def kl(a: Dict[str, float], b: Dict[str, float]) -> float:
        return sum(a[k] * math.log2((a[k] + eps) / (b[k] + eps)) for k in keys)

    return 0.5 * kl(pf, m) + 0.5 * kl(qf, m)


def _err_pct(pred: Optional[float], real: Optional[float]) -> Optional[float]:
    if pred is None or real is None or real == 0:
        return None
    return abs(pred - real) / abs(real) * 100.0


class HAICExperimentEngine:
    """
    db_connection: a SQLAlchemy Session bound to the same database as the
    backend app (matches app.utils.database.SessionLocal's pattern - the
    engine reflects the experiment_* tables from whatever engine that
    session is bound to, rather than importing their ORM classes).
    """

    def __init__(self, db_connection, model_registry_path: Optional[str] = None):
        self.db = db_connection
        self.model_registry_path = model_registry_path

        bind = self.db.get_bind() if hasattr(self.db, "get_bind") else self.db
        metadata = sa.MetaData()
        self.t_runs = sa.Table("experiment_runs", metadata, autoload_with=bind)
        self.t_models = sa.Table("experiment_models", metadata, autoload_with=bind)
        self.t_results = sa.Table("experiment_results", metadata, autoload_with=bind)

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _get_experiment(self, experiment_id) -> dict:
        row = self.db.execute(sa.select(self.t_runs).where(self.t_runs.c.id == experiment_id)).mappings().first()
        if row is None:
            raise ValueError(f"Experiment {experiment_id} not found")
        return dict(row)

    def _get_model(self, experiment_id, model_id: str) -> dict:
        row = self.db.execute(
            sa.select(self.t_models).where(
                self.t_models.c.experiment_id == experiment_id, self.t_models.c.model_id == model_id,
            )
        ).mappings().first()
        if row is None:
            raise ValueError(f"Model '{model_id}' not registered in experiment {experiment_id}")
        return dict(row)

    def _get_target_models(self, experiment_id) -> List[dict]:
        rows = self.db.execute(
            sa.select(self.t_models).where(
                self.t_models.c.experiment_id == experiment_id, self.t_models.c.role == "target",
            )
        ).mappings().all()
        return [dict(r) for r in rows]

    def _update_model(self, experiment_id, model_id: str, **values) -> None:
        values["updated_at"] = datetime.now(timezone.utc)
        self.db.execute(
            sa.update(self.t_models)
            .where(self.t_models.c.experiment_id == experiment_id, self.t_models.c.model_id == model_id)
            .values(**values)
        )
        self.db.commit()

    def _all_targets_at_least(self, experiment_id, status: str) -> bool:
        min_rank = MODEL_STATUS_ORDER.index(status)
        targets = self._get_target_models(experiment_id)
        if not targets:
            return False
        return all(MODEL_STATUS_ORDER.index(t["status"]) >= min_rank for t in targets)

    @staticmethod
    def _load_json(path: str) -> dict:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def _save_json(path: str, data: dict) -> None:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # phase 0 - AI-frequency extraction (operator data untouched)
    # ------------------------------------------------------------------

    def phase_0_extract_ai_freq(self, experiment_id, model_id: str, log_file_path: str) -> dict:
        events = fit_markov._flatten_events(self._load_json(log_file_path))
        ai_events = [e for e in events if e.get("actor_type") == "ai"]

        interaction_ids = set()
        raw_counts: Dict[str, int] = {}
        for e in ai_events:
            iid = e.get("interaction_id")
            if iid is not None:
                interaction_ids.add(iid)
            raw = fit_markov._get_path(e, "payload.ai_decision")
            canon = AI_ACTION_MAP.get(raw)
            if canon is not None:
                raw_counts[canon] = raw_counts.get(canon, 0) + 1

        # ai_reject/ai_flag are fractions of the *reviewed* subset only
        # (excluding ai_accept from the denominator), matching the fitted
        # model's own ai_action_frequency convention (ai_accept: 0.0,
        # reject/flag summing to 1.0) - ai_accept structurally never
        # reaches an operator in this domain, so its fitted transition_matrix
        # row is null. Computing reject/flag as fractions of the *total*
        # population instead would give ai_accept nonzero sampling weight in
        # ai_freq_override, and _sample_op_action() would then fall back to
        # a uniform-random operator decision for every such draw - a
        # fabricated decision for an interaction that, in reality, never
        # produces one. n_ai_accept is reported separately as a raw count,
        # not folded into the probability distribution.
        n_reviewed = raw_counts.get("ai_reject", 0) + raw_counts.get("ai_flag", 0)
        freq = {
            "ai_accept": 0.0,
            "ai_reject": (raw_counts.get("ai_reject", 0) / n_reviewed) if n_reviewed else 0.0,
            "ai_flag": (raw_counts.get("ai_flag", 0) / n_reviewed) if n_reviewed else 0.0,
        }

        result = {
            "ai_reject": freq["ai_reject"],
            "ai_flag": freq["ai_flag"],
            "n_sessions": len(interaction_ids),
            "n_ai_accept": raw_counts.get("ai_accept", 0),
        }

        self._update_model(experiment_id, model_id, ai_action_frequency=freq, status="ai_extracted")
        return result

    # ------------------------------------------------------------------
    # phase 1 - blind prediction (source surrogate + target AI frequency)
    # ------------------------------------------------------------------

    def phase_1_blind_predict(self, experiment_id, target_model_id: str) -> dict:
        experiment = self._get_experiment(experiment_id)
        source_model = self._get_model(experiment_id, experiment["source_model_id"])
        target_model = self._get_model(experiment_id, target_model_id)

        if MODEL_STATUS_ORDER.index(target_model["status"]) < MODEL_STATUS_ORDER.index("ai_extracted"):
            raise ValueError(
                f"Target model '{target_model_id}' must be at least 'ai_extracted' "
                f"(run phase_0_extract_ai_freq first) - currently '{target_model['status']}'"
            )
        if not source_model.get("fitted_model_path"):
            raise ValueError(f"Source model '{source_model['model_id']}' has no fitted_model_path")

        surrogate = MarkovSurrogate(model_path=source_model["fitted_model_path"], persona="aggregate", seed=42)
        sessions = surrogate.generate_batch(
            n_sessions=experiment["n_sessions"], n_items=experiment["n_items"],
            rt_max_s=RT_MAX_S, ai_freq_override=target_model["ai_action_frequency"],
        )

        per_session = [
            compute_metrics(decisions=s["decisions"], T=None, baseline_s=None, rt_max=RT_MAX_S)
            for s in sessions
        ]

        def _summary(metric: str) -> tuple[Optional[float], Optional[float]]:
            values = [s[metric] for s in per_session if s.get(metric) is not None]
            if not values:
                return None, None
            arr = np.array(values, dtype=float)
            return float(arr.mean()), float(arr.std())

        pred_tr, pred_tr_std = _summary("Tr")
        pred_hcl, pred_hcl_std = _summary("HCL")
        pred_el, pred_el_std = _summary("EL")  # None: no baseline_s configured, matching validate_surrogate.py Part B
        pred_f, pred_f_std = _summary("F")

        sealed_at = datetime.now(timezone.utc)
        self.db.execute(
            sa.insert(self.t_results).values(
                experiment_id=experiment_id,
                model_a_id=source_model["model_id"],
                model_b_id=target_model["model_id"],
                comparison_type="predicted_vs_real",
                pred_Tr=pred_tr, pred_Tr_std=pred_tr_std,
                pred_HCL=pred_hcl, pred_HCL_std=pred_hcl_std,
                pred_EL=pred_el, pred_EL_std=pred_el_std,
                pred_F=pred_f, pred_F_std=pred_f_std,
            )
        )
        self._update_model(experiment_id, target_model_id, status="predicted")

        if self._all_targets_at_least(experiment_id, "predicted"):
            self.db.execute(sa.update(self.t_runs).where(self.t_runs.c.id == experiment_id).values(sealed_at=sealed_at, status="predicted"))
        self.db.commit()

        predictions = {
            "model_a_id": source_model["model_id"], "model_b_id": target_model["model_id"],
            "pred_Tr": pred_tr, "pred_Tr_std": pred_tr_std,
            "pred_HCL": pred_hcl, "pred_HCL_std": pred_hcl_std,
            "pred_EL": pred_el, "pred_EL_std": pred_el_std,
            "pred_F": pred_f, "pred_F_std": pred_f_std,
            "n_sessions": len(sessions), "sealed_at": sealed_at.isoformat(),
        }
        print("=== PREDICTIONS SEALED ===")
        print("Do not reveal target model operator data yet.")
        return predictions

    # ------------------------------------------------------------------
    # phase 2 - fit the real matrix from actual operator logs (reveal)
    # ------------------------------------------------------------------

    def phase_2_fit_real_matrix(self, experiment_id, model_id: str, log_file_path: str) -> dict:
        experiment = self._get_experiment(experiment_id)
        data = self._load_json(log_file_path)

        model = fit_markov.fit_model({
            "input_data": data,
            "source_label": log_file_path,
            "domain": experiment["domain"],
            "ai_action_field": "payload.ai_decision",
            "human_action_field": "payload.op_decision",
            "ai_actor_value": "ai",
            "human_actor_value": "human",
            "ai_action_map": AI_ACTION_MAP,
            "op_action_map": OP_ACTION_MAP,
            "accept_actions": ACCEPT_ACTIONS,
            "group_by": "payload.op_id",
        })

        model_path = f"data/{experiment_id}_{model_id}_markov_model.json"
        self._save_json(model_path, model)

        self._update_model(experiment_id, model_id, fitted_model_path=model_path, status="revealed")

        if self._all_targets_at_least(experiment_id, "revealed"):
            self.db.execute(
                sa.update(self.t_runs).where(self.t_runs.c.id == experiment_id)
                .values(revealed_at=datetime.now(timezone.utc), status="revealed")
            )
            self.db.commit()

        return model

    # ------------------------------------------------------------------
    # phase 3 - compare predictions (sealed) vs reality (revealed)
    # ------------------------------------------------------------------

    def phase_3_compare(self, experiment_id, model_a_id: str, model_b_id: str) -> dict:
        model_a = self._get_model(experiment_id, model_a_id)
        model_b = self._get_model(experiment_id, model_b_id)

        # "status >= 'fitted'" doesn't literally apply to the source model -
        # it's registered with a fitted_model_path up front and its status
        # legitimately stays 'registered' (it's never a phase_0/1/2 target).
        # "Has a matrix" is the actual requirement, so that's what's checked.
        if not model_a.get("fitted_model_path"):
            raise ValueError(f"Model '{model_a_id}' has no fitted matrix (fitted_model_path is empty)")
        if model_b["status"] != "revealed" or not model_b.get("fitted_model_path"):
            raise ValueError(f"Model '{model_b_id}' must be 'revealed' (run phase_2_fit_real_matrix first)")

        fitted_a = self._load_json(model_a["fitted_model_path"])
        fitted_b = self._load_json(model_b["fitted_model_path"])

        matrix_a = fitted_a["aggregate"]["transition_matrix"]
        matrix_b = fitted_b["aggregate"]["transition_matrix"]
        duration_stats_b = fitted_b["aggregate"]["duration_stats"]
        freq_b = fitted_b["aggregate"]["ai_action_frequency"]
        accept_actions_b = fitted_b["accept_actions"]

        # ---- Step A: prediction error (real, computed analytically from
        # model_b's fitted matrix - no surrogate, no raw session replay) ----
        real_tr = _analytical_tr(freq_b, matrix_b, accept_actions_b)
        real_hcl = _analytical_hcl(freq_b, duration_stats_b)
        real_el = None  # no baseline_s available generically - see pred_EL note
        real_f = _analytical_f(freq_b, duration_stats_b)

        existing = self.db.execute(
            sa.select(self.t_results).where(
                self.t_results.c.experiment_id == experiment_id,
                self.t_results.c.model_a_id == model_a_id,
                self.t_results.c.model_b_id == model_b_id,
                self.t_results.c.comparison_type == "predicted_vs_real",
            )
        ).mappings().first()
        if existing is None:
            raise ValueError(
                f"No predicted_vs_real result row for ({model_a_id} -> {model_b_id}) - "
                f"run phase_1_blind_predict first"
            )
        existing = dict(existing)

        err_tr = _err_pct(existing["pred_Tr"], real_tr)
        err_hcl = _err_pct(existing["pred_HCL"], real_hcl)
        err_el = _err_pct(existing["pred_EL"], real_el)
        err_f = _err_pct(existing["pred_F"], real_f)

        # ---- Step B: cross-model surrogate similarity ----
        op_actions_a = fitted_a["op_actions"]
        op_actions_b = fitted_b["op_actions"]
        common_ai_actions = sorted(set(matrix_a) & set(matrix_b))
        s_per_action: Dict[str, float] = {}
        for ai in common_ai_actions:
            row_a = _smooth_row(matrix_a.get(ai), op_actions_a, SMOOTH_EPSILON_DEFAULT)
            row_b = _smooth_row(matrix_b.get(ai), op_actions_b, SMOOTH_EPSILON_DEFAULT)
            if row_a is None or row_b is None:
                continue
            s_per_action[ai] = 1.0 - math.sqrt(max(0.0, _jsd(row_a, row_b)))
        s_cross = float(np.mean(list(s_per_action.values()))) if s_per_action else None

        # ---- Step C: hypothesis verdicts ----
        h1 = (err_tr is not None and err_hcl is not None and err_tr < H1_ERROR_THRESHOLD_PCT and err_hcl < H1_ERROR_THRESHOLD_PCT)
        h2 = (s_cross is not None and s_cross > H2_S_THRESHOLD)

        matrix_a_smoothed = {ai: _smooth_row(row, op_actions_a, SMOOTH_EPSILON_DEFAULT) for ai, row in matrix_a.items()}
        accept_actions_a = fitted_a["accept_actions"]
        pred_tr_structural = _analytical_tr(freq_b, matrix_a_smoothed, accept_actions_a)
        h3 = (
            pred_tr_structural is not None and real_tr not in (None, 0)
            and abs(pred_tr_structural - real_tr) / abs(real_tr) < H3_ERROR_THRESHOLD
        )

        self.db.execute(
            sa.update(self.t_results).where(self.t_results.c.id == existing["id"]).values(
                real_Tr=real_tr, real_HCL=real_hcl, real_EL=real_el, real_F=real_f,
                err_Tr_pct=err_tr, err_HCL_pct=err_hcl, err_EL_pct=err_el, err_F_pct=err_f,
                S_cross=s_cross, S_cross_per_action=s_per_action,
                h1_supported=h1, h2_supported=h2, h3_supported=h3,
                updated_at=datetime.now(timezone.utc),
            )
        )

        worst_action = min(s_per_action, key=s_per_action.get) if s_per_action else None
        notes = (
            f"Rows differ most on '{worst_action}' (S={s_per_action[worst_action]:.3f})"
            if worst_action else "No shared ai_actions between the two matrices"
        )
        self.db.execute(
            sa.insert(self.t_results).values(
                experiment_id=experiment_id, model_a_id=model_a_id, model_b_id=model_b_id,
                comparison_type="matrix_vs_matrix",
                S_cross=s_cross, S_cross_per_action=s_per_action, notes=notes,
            )
        )
        self.db.commit()

        result = {
            "model_a_id": model_a_id, "model_b_id": model_b_id,
            "pred_Tr": existing["pred_Tr"], "real_Tr": real_tr, "err_Tr_pct": err_tr,
            "pred_HCL": existing["pred_HCL"], "real_HCL": real_hcl, "err_HCL_pct": err_hcl,
            "pred_EL": existing["pred_EL"], "real_EL": real_el, "err_EL_pct": err_el,
            "pred_F": existing["pred_F"], "real_F": real_f, "err_F_pct": err_f,
            "S_cross": s_cross, "S_cross_per_action": s_per_action,
            "h1_supported": h1, "h2_supported": h2, "h3_supported": h3,
            "pred_Tr_structural": pred_tr_structural,
        }

        def _f(v):
            return f"{v:.3f}" if v is not None else "N/A"

        def _pct(v):
            return f"{v:.1f}%" if v is not None else "N/A"

        print(f"=== COMPARISON: {model_a_id} → {model_b_id} ===")
        print(f"Metric | Predicted | Real   | Error%")
        print(f"Tr     | {_f(existing['pred_Tr']):<9} | {_f(real_tr):<6} | {_pct(err_tr)}")
        print(f"HCL    | {_f(existing['pred_HCL']):<9} | {_f(real_hcl):<6} | {_pct(err_hcl)}")
        print(f"EL     | {_f(existing['pred_EL']):<9} | {_f(real_el):<6} | {_pct(err_el)}")
        print(f"F      | {_f(existing['pred_F']):<9} | {_f(real_f):<6} | {_pct(err_f)}")
        print()
        print(f"Cross-model S({model_a_id}→{model_b_id}): {_f(s_cross)}")
        for ai, v in s_per_action.items():
            print(f"  {ai}: {v:.3f}")
        print()
        print(f"H1 (frequency transfer):   {'SUPPORTED' if h1 else 'REJECTED'}  [err_Tr={_pct(err_tr)}, err_HCL={_pct(err_hcl)}]")
        print(f"H2 (matrix stability):     {'SUPPORTED' if h2 else 'REJECTED'}  [S={_f(s_cross)}, threshold={H2_S_THRESHOLD}]")
        structural_err = (
            abs(pred_tr_structural - real_tr) / abs(real_tr) * 100
            if pred_tr_structural is not None and real_tr else None
        )
        print(f"H3 (regime decomposition): {'SUPPORTED' if h3 else 'REJECTED'}  [structural_err={_pct(structural_err)}]")

        return result

    # ------------------------------------------------------------------
    # orchestration
    # ------------------------------------------------------------------

    def run_full_experiment(self, experiment_id) -> dict:
        """Assumes all models are already registered with log_file_paths
        set. Runs phase_0 + phase_1 for every target model, then stops -
        predictions are sealed but operator data is not yet touched."""
        predictions = {}
        for target in self._get_target_models(experiment_id):
            self.phase_0_extract_ai_freq(experiment_id, target["model_id"], target["log_file_path"])
            predictions[target["model_id"]] = self.phase_1_blind_predict(experiment_id, target["model_id"])

        print("=== ALL PREDICTIONS SEALED ===")
        print("Ready to reveal. Call reveal_and_compare() when ready.")
        return predictions

    def reveal_and_compare(self, experiment_id) -> dict:
        """Second half - fits each target's real matrix, then compares
        every (source, target) pair. Call only after run_full_experiment()."""
        experiment = self._get_experiment(experiment_id)
        results = {}
        for target in self._get_target_models(experiment_id):
            self.phase_2_fit_real_matrix(experiment_id, target["model_id"], target["log_file_path"])

        for target in self._get_target_models(experiment_id):
            results[target["model_id"]] = self.phase_3_compare(
                experiment_id, experiment["source_model_id"], target["model_id"],
            )
        return results
