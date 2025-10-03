# streamlit_app.py
import os, sys, json, importlib
from pathlib import Path
import streamlit as st
import pandas as pd

# ---------- paths & imports ----------
ROOT = Path(__file__).resolve().parent
PKG_ROOT = ROOT / "haic_sim_mvp"
sys.path.insert(0, str(PKG_ROOT))

from haic_sim_mvp.engine.run_sim import run_from_config
from haic_sim_mvp.engine.datasets import load_csv, make_script_from_dataset
from haic_sim_mvp.engine.policies import ThresholdPolicy, L2DPolicy
from haic_sim_mvp.engine.evaluate import compute_metrics as base_metrics

# --- YAML/JSON helpers ---
import json, io, difflib
from pathlib import Path
import pandas as pd

def _normalize_step(s: dict) -> dict:
    s = dict(s or {})
    # common aliases
    if "obj" in s and "object" not in s:
        s["object"] = s.pop("obj")
    # types
    if "t" in s:
        try: s["t"] = int(s["t"])
        except: pass
    if "latency_ms" in s and s["latency_ms"] is not None:
        try: s["latency_ms"] = int(s["latency_ms"])
        except: pass
    if "correct" in s and isinstance(s["correct"], str):
        s["correct"] = s["correct"].lower() in {"1","true","yes","y"}
    return s

def _steps_to_df(steps: list[dict]) -> pd.DataFrame:
    rows = []
    for s in steps or []:
        s = _normalize_step(s)
        rows.append({
            "t": s.get("t", 1),
            "agent": s.get("agent",""),
            "action": s.get("action",""),
            "object": s.get("object",""),
            "latency_ms": s.get("latency_ms"),
            "correct": s.get("correct", None),
            "effect_json": json.dumps(s.get("effect", None), ensure_ascii=False)
        })
    if not rows:
        rows = [{"t":1,"agent":"","action":"","object":"","latency_ms":None,"correct":None,"effect_json":"null"}]
    df = pd.DataFrame(rows).sort_values("t")
    return df

def _df_to_steps(df) -> list[dict]:
    """Convert an edited data_editor frame back to a list of script steps."""
    import pandas as pd
    out: list[dict] = []

    # 1) Normalize input into a DataFrame
    if df is None:
        return out
    if not isinstance(df, pd.DataFrame):
        try:
            df = pd.DataFrame(df)
        except Exception:
            return out

    # 2) Ensure columns exist
    for col in ["t", "agent", "action", "object", "latency_ms", "correct", "effect_json"]:
        if col not in df.columns:
            df[col] = None

    # 3) Sort safely by t (create sequence if t is all NaN)
    if df["t"].isna().all():
        df["t"] = range(1, len(df) + 1)
    df2 = df.sort_values("t", kind="stable", na_position="first")

    # 4) Row → step
    for _, r in df2.iterrows():
        # effect json
        eff = None
        txt = (r.get("effect_json") or "").strip()
        if txt:
            try:
                eff = json.loads(txt)
            except Exception:
                eff = {"raw": txt}  # keep whatever was typed

        # latency
        lat = r.get("latency_ms")
        if pd.isna(lat):
            lat = None
        else:
            try:
                lat = int(lat)
            except Exception:
                lat = None

        # t
        tval = r.get("t")
        try:
            tval = int(tval)
        except Exception:
            tval = len(out) + 1

        step = {
            "t": tval,
            "agent": (r.get("agent") or "").strip(),
            "action": (r.get("action") or "").strip(),
            "object": (r.get("object") or "").strip(),
            "latency_ms": lat,
        }

        c = r.get("correct")
        if c is not None and not pd.isna(c):
            step["correct"] = bool(c)
        if eff is not None:
            step["effect"] = eff

        out.append(step)

    return out

try:
    import yaml  # PyYAML
except Exception:
    yaml = None

REQUIRED_KEYS = ["environment", "agents", "objects", "script"]

def to_yaml(cfg: dict) -> str:
    if yaml is None:
        return "# Install PyYAML for YAML export\n" + json.dumps(cfg, indent=2)
    # Safe, readable dump; keep keys order if possible
    return yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True)

def to_json(cfg: dict) -> str:
    return json.dumps(cfg, indent=2, ensure_ascii=False)

def parse_any(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty input.")
    # Try JSON first (strict), then YAML
    try:
        return json.loads(text)
    except Exception:
        pass
    if yaml is None:
        raise ValueError("Not valid JSON and PyYAML not installed.")
    try:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("Top-level YAML must be a mapping/object.")
        return data
    except Exception as e:
        raise ValueError(f"YAML parse error: {e}")

def validate_cfg(cfg: dict) -> list[str]:
    errs = []
    for k in REQUIRED_KEYS:
        if k not in cfg:
            errs.append(f"Missing required key: '{k}'")
    # Minimal shape checks
    env = cfg.get("environment", {})
    if not isinstance(env, dict) or "id" not in env or "class" not in env:
        errs.append("environment must include 'id' and 'class'.")
    for sec in ("agents", "objects"):
        arr = cfg.get(sec, [])
        if not isinstance(arr, list) or not all(isinstance(x, dict) for x in arr):
            errs.append(f"'{sec}' must be a list of objects.")
        else:
            for i, x in enumerate(arr):
                if "id" not in x or "class" not in x:
                    errs.append(f"{sec}[{i}] must include 'id' and 'class'.")
                if "affordances" in x and not isinstance(x["affordances"], list):
                    errs.append(f"{sec}[{i}].affordances must be a list.")
    steps = cfg.get("script", [])
    if not isinstance(steps, list):
        errs.append("'script' must be a list.")
    else:
        for i, s in enumerate(steps):
            if not all(k in s for k in ("t","agent","action","object")):
                errs.append(f"script[{i}] must have t, agent, action, object.")
    return errs

def unified_diff(a: str, b: str, a_name="current", b_name="loaded") -> str:
    lines = difflib.unified_diff(
        a.splitlines(keepends=True),
        b.splitlines(keepends=True),
        fromfile=a_name, tofile=b_name, n=3
    )
    return "".join(lines)

# ---- A/B comparison helpers ----
from typing import Dict, Any, Tuple, List

def _val(x, default=0.0):
    try:
        return float(x) if x is not None else default
    except Exception:
        return default

def collect_all_metrics(log: dict) -> dict:
    """Merge base metrics + HAIC pillars and guarantee all keys exist."""
    base = base_metrics(log) or {}
    pillars = haic_metrics_for_log(log) or {}
    out = {}
    out.update(base)
    out.update(pillars)
    out = {k: _val(v) for k, v in out.items()}

    # ensure all KPIs & Pillars are present so downstream never KeyErrors
    for _, key, _, _ in KPI_SPECS:
        out.setdefault(key, 0.0)
    for _, key, _, _ in PILLAR_SPECS:
        out.setdefault(key, 0.0)
    # bonus: a few common aliases some logs might have
    if "avg_latency" in out and "avg_latency_ms" not in out:
        out["avg_latency_ms"] = _val(out["avg_latency"])
    return out

# label, key, better('high'|'low'), fmt
KPI_SPECS = [
    ("accuracy",         "accuracy",        "high", "{:.2f}"),
    ("AI acc",           "ai_accuracy",     "high", "{:.2f}"),
    ("Human acc",        "human_accuracy",  "high", "{:.2f}"),
    ("defer rate",       "defer_rate",      "low",  "{:.2f}"),
    ("avg latency (ms)", "avg_latency_ms",  "low",  "{:.0f}"),
    ("EfficiencyScore",  "EfficiencyScore", "high", "{:.2f}"),
]

PILLAR_SPECS = [
    ("F",  "F",  "—",   "{:.2f}"),
    ("D",  "D",  "—",   "{:.2f}"),
    ("HCL","HCL","high","{:.2f}"),
    ("Tr", "Tr", "high","{:.2f}"),
    ("A",  "A",  "high","{:.2f}"),
    ("S",  "S",  "high","{:.2f}"),
    ("EL", "EL", "low", "{:.2f}"),
]

def _delta_color(better: str) -> str:
    return "inverse" if better == "low" else "normal"

def _g(d: dict, key: str) -> float:
    return _val(d.get(key), 0.0)

def _bullet_changes(ma: dict, mb: dict):
    bullets = []
    # Accuracy
    d_acc = _g(mb, "accuracy") - _g(ma, "accuracy")
    if d_acc != 0:
        bullets.append(("✅" if d_acc > 0 else "⚠️") + f" Accuracy {d_acc:+.2f}")
    # Latency (lower is better → show speed gain)
    d_lat_ms = _g(ma, "avg_latency_ms") - _g(mb, "avg_latency_ms")
    if d_lat_ms != 0:
        bullets.append(("🚀" if d_lat_ms > 0 else "🐢") + f" Latency {d_lat_ms:+.0f} ms")
    # Defer rate
    d_def = _g(mb, "defer_rate") - _g(ma, "defer_rate")
    if d_def != 0:
        bullets.append(("👥" if d_def > 0 else "🤖") + f" Defer {d_def:+.2f}")
    return bullets

def render_ab_comparison(log_A, log_B, name_A="Baseline", name_B="L2D-like"):
    ma = collect_all_metrics(log_A)
    mb = collect_all_metrics(log_B)

    # verdict: accuracy → EfficiencyScore → (lower) latency
    a_tuple = (_g(ma, "accuracy"), _g(ma, "EfficiencyScore"), -_g(ma, "avg_latency_ms"))
    b_tuple = (_g(mb, "accuracy"), _g(mb, "EfficiencyScore"), -_g(mb, "avg_latency_ms"))
    verdict = name_B if b_tuple > a_tuple else name_A
    st.success(f"**A/B finished – suggested winner: {verdict}**")

    for line in _bullet_changes(ma, mb):
        st.write(line)
    st.caption("Δ below is **B − A**. Green means better for that metric (e.g., lower is better for latency & defer).")

    # KPIs row
    st.markdown("#### Core KPIs")
    colA, colB = st.columns(2)
    with colA:
        st.markdown(f"**A — {name_A}**")
        kcols = st.columns(len(KPI_SPECS))
        for i, (label, key, better, fmt) in enumerate(KPI_SPECS):
            kcols[i].metric(label, fmt.format(_g(ma, key)))
    with colB:
        st.markdown(f"**B — {name_B}**")
        kcols = st.columns(len(KPI_SPECS))
        for i, (label, key, better, fmt) in enumerate(KPI_SPECS):
            d = _g(mb, key) - _g(ma, key)
            delta_str = f"{d:+.0f}" if "latency" in key else f"{d:+.2f}"
            kcols[i].metric(label, fmt.format(_g(mb, key)), delta=delta_str, delta_color=_delta_color(better))

    # Pillars
    st.markdown("#### HAIC Interaction metrics")
    colA, colB = st.columns(2)
    with colA:
        st.markdown(f"**A — {name_A}**")
        pcols = st.columns(len(PILLAR_SPECS))
        for i, (label, key, better, fmt) in enumerate(PILLAR_SPECS):
            pcols[i].metric(label, fmt.format(_g(ma, key)))
    with colB:
        st.markdown(f"**B — {name_B}**")
        pcols = st.columns(len(PILLAR_SPECS))
        for i, (label, key, better, fmt) in enumerate(PILLAR_SPECS):
            d = _g(mb, key) - _g(ma, key)
            pcols[i].metric(label, fmt.format(_g(mb, key)), delta=f"{d:+.2f}", delta_color=_delta_color(better))



mb = importlib.import_module("haic_sim_mvp.engine.metrics_bridge")  # tolerant lazy loader
haic_metrics_for_log = mb.haic_metrics_for_log
HAVE_HAIC = getattr(mb, "_CM", None) is not None

import textwrap

USER_PLUGINS_DIR = PKG_ROOT / "user_plugins"
USER_PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
(USER_PLUGINS_DIR / "__init__.py").touch(exist_ok=True)

def _parse_json_obj(s: str) -> dict:
    s = (s or "").strip()
    if not s:
        return {}
    try:
        val = json.loads(s)
        return val if isinstance(val, dict) else {}
    except Exception:
        return {}

def _parse_affordances(s: str) -> list[str]:
    return [a.strip() for a in (s or "").split(",") if a.strip()]

def _plugin_skeleton(module_name: str, agent_class: str, object_class: str, enforce_view_before_classify: bool=True) -> str:
    gate = (
        "        if action == 'classify' and obj.entity_id not in viewed:\n"
        "            raise ValueError(\"Agent must 'view' before 'classify'\")\n"
        if enforce_view_before_classify else ""
    )
    return textwrap.dedent(f"""
    from dataclasses import dataclass
    from typing import Optional, Dict, Any
    from haic_sim_mvp.engine.base import Agent, Object

    @dataclass
    class {agent_class}(Agent):
        def act(self, action: str, obj: Object,
                effect: Optional[Dict[str, Any]] = None, t: Optional[int] = None):
            viewed = self.attributes.setdefault("viewed_cases", [])
            if action == "view" and obj.entity_id not in viewed:
                viewed.append(obj.entity_id)
{gate.rstrip()}
            return super().act(action, obj, effect, t)

    @dataclass
    class {object_class}(Object):
        pass
    """).strip() + "\n"


from streamlit.components.v1 import html as st_html

def render_mermaid(code: str, height: int = 260):
    """Inline Mermaid renderer (no extra deps)."""
    try:
        base = st.get_option("theme.base")
    except Exception:
        base = "light"
    theme = "dark" if str(base).lower() == "dark" else "default"
    st_html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <div class="mermaid">
        {code}
        </div>
        <script>
          mermaid.initialize({{ startOnLoad: true, theme: "{theme}" }});
        </script>
        """,
        height=height,
    )


# ---------- streamlit config ----------
st.set_page_config(page_title="HAIC Simulator | MVP", layout="wide")
st.title("Human–AI Collaboration Simulator | MVP")

# ---------- helpers ----------
def list_files(dir_path: Path, suffixes=(".json",), exclude_contains=("_metrics", "_haic_metrics")):
    if not dir_path.exists(): return []
    files = []
    for p in dir_path.rglob("*"):
        if p.is_file() and p.suffix in suffixes and not any(x in p.name for x in exclude_contains):
            files.append(p)
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

def list_csv(dir_path: Path):
    if not dir_path.exists(): return []
    return sorted([p for p in dir_path.rglob("*.csv")], key=lambda p: p.stat().st_mtime, reverse=True)

def show_base_and_haic(log: dict):
    base = base_metrics(log)
    c = st.columns(5)
    c[0].metric("accuracy", f"{(base.get('accuracy') or 0):.2f}" if base.get("accuracy") is not None else "–")
    c[1].metric("AI acc", f"{(base.get('ai_accuracy') or 0):.2f}" if base.get("ai_accuracy") is not None else "–")
    c[2].metric("Human acc", f"{(base.get('human_accuracy') or 0):.2f}" if base.get("human_accuracy") is not None else "–")
    c[3].metric("defer rate", f"{(base.get('defer_rate') or 0):.2f}" if base.get("defer_rate") is not None else "–")
    c[4].metric("avg latency (ms)", f"{(base.get('avg_latency_ms') or 0):.0f}")
    if HAVE_HAIC:
        pillars = haic_metrics_for_log(log) or {}
        p = st.columns(8)
        for i, k in enumerate(["F","D","HCL","Tr","A","S","EL","EfficiencyScore"]):
            p[i].metric(k, f"{pillars.get(k, 0):.2f}")
    else:
        st.info("Install metrics package to see HAIC metrics.")

def show_decisions_table(log: dict):
    df = pd.DataFrame(log.get("decisions", []))
    if df.empty:
        st.write("No decisions to show."); return
    for old, new in [("agent","agent_id"), ("object","object_id")]:
        if old in df.columns and new not in df.columns:
            df[new] = df[old]
    cols = [c for c in ["t","agent_id","action","object_id","latency_ms","correct","effect"] if c in df.columns]
    st.dataframe(df[cols], use_container_width=True, height=360)
    ch = st.columns(2)
    if "latency_ms" in df.columns and "t" in df.columns:
        ch[0].line_chart(df[["t","latency_ms"]].set_index("t"))
    if "agent_id" in df.columns:
        counts = df.groupby("agent_id")["action"].count().rename("count").to_frame()
        ch[1].bar_chart(counts)

# ---------- sidebar (folders only) ----------
with st.sidebar:
    st.header("Folders")
    default_results = (PKG_ROOT / "results") if (PKG_ROOT / "results").exists() else (ROOT / "results")
    default_configs = (PKG_ROOT / "configs") if (PKG_ROOT / "configs").exists() else (ROOT / "configs")
    results_dir = Path(st.text_input("Results dir", value=str(default_results)))
    configs_dir = Path(st.text_input("Configs dir", value=str(default_configs)))
    st.caption("These populate the drop-downs in the tabs.")

tab_overview, tab_builder, tab_run_cfg, tab_run_csv, tab_view,   tab_compare = st.tabs(
    ["🏁 Overview", "📝 Builder", "🧰 Scripted Run", "🧪 Dataset A/B",  "📄 View Result",  "📊 Compare Results", ]
)
# ---------- View existing result (dropdown) ----------
with tab_view:
    st.subheader("View a results JSON")
    result_files = list_files(results_dir)
    choices = [p.relative_to(results_dir).as_posix() for p in result_files]
    sel = st.selectbox("Select result", choices, index=0 if choices else None)
    if sel:
        path = results_dir / sel
        log = json.loads(path.read_text(encoding="utf-8"))
        meta = st.columns(4)
        meta[0].metric("sim_id", log.get("sim_id",""))
        meta[1].metric("env_id", log.get("env_id",""))
        meta[2].metric("#steps", len(log.get("decisions",[])))
        meta[3].metric("#agents", len(log.get("agents",{})))
        show_base_and_haic(log)
        st.download_button("Download JSON", data=json.dumps(log, indent=2),
                           file_name=path.name, mime="application/json")
        st.markdown("#### Decisions")
        show_decisions_table(log)
    else:
        st.info("No results found in the selected folder.")

# ---------- Run scripted config (dropdown) ----------
with tab_run_cfg:
    st.subheader("Run a scripted config JSON")
    cfg_files = list_files(configs_dir, suffixes=(".json",), exclude_contains=("_metrics","_haic"))
    cfg_choices = [p.relative_to(configs_dir).as_posix() for p in cfg_files]
    cfg_sel = st.selectbox("Select config", cfg_choices, index=0 if cfg_choices else None)
    if cfg_sel and st.button("Run selected config"):
        cfg = json.loads((configs_dir / cfg_sel).read_text(encoding="utf-8"))
        out_path = run_from_config(cfg, results_dir=str(results_dir))
        st.success(f"Run complete → {out_path}")
        log = json.loads(Path(out_path).read_text(encoding="utf-8"))
        show_base_and_haic(log)
        st.markdown("#### Decisions")
        show_decisions_table(log)

# ---------- Dataset A/B (dropdown for csv) ----------
with tab_run_csv:
    st.subheader("Run dataset-driven A/B")

    with st.expander("Why this matters / how to judge A vs B"):
        left, right = st.columns([1.5, 1])
        with left:
            st.markdown(
                """
### **What this A/B does**
- **Same dataset, two policies.** Each CSV row (e.g., `ai_prob`, `ground_truth`) becomes a simulated *case*.
- **Baseline (threshold):** if `ai_prob >= threshold` → AI classifies, else Human.
- **L2D-like (defer):** if `ai_prob` is in an uncertainty band (around τ) → defer to Human; otherwise AI.
- Engine executes and logs; we compute **base** and **HAIC interaction** metrics.

### **How to judge A/B**
- Prefer higher **accuracy** without unacceptable **latency** or **defer rate** growth.
- If **L2D** boosts accuracy with a small defer bump → good trade (capacity permitting).
- Watch **HCL** and **EL/EfficiencyScore** for human effort/load.
                """
            )
        with right:
            render_mermaid(
                """
flowchart TD
  CSV[Dataset CSV] --> MAP[Column Mapper]
  MAP --> GEN[Script Generator]
  GEN --> POL{Select Policy}
  POL -->|baseline| BASE[Threshold]
  POL -->|l2d| L2D[L2D-like]
  BASE --> ENG[Engine]
  L2D --> ENG
  ENG --> LOG[Logs] --> MET[Interaction Metrics]
                """,
                height=320
            )

    # Pick CSV
    csv_files = list_csv(configs_dir)
    csv_choices = [p.relative_to(configs_dir).as_posix() for p in csv_files]
    csv_sel = st.selectbox("Select dataset CSV", csv_choices, index=0 if csv_choices else None)

    # Policy knobs
    c1, c2, c3 = st.columns(3)
    threshold = c1.slider("Baseline threshold", 0.0, 1.0, 0.50, 0.01)
    c1.caption("Lower → more AI coverage, fewer deferrals; may hurt accuracy if model is weak.")
    tau = c2.slider("L2D τ (uncertainty band)", 0.50, 0.99, 0.70, 0.01)
    c2.caption("Higher → wider defer band (1-τ, τ) → more human load; can boost accuracy.")
    human_acc = c3.slider("Human accuracy (assumption)", 0.50, 1.00, 0.90, 0.01)
    c3.caption("Used when policy defers to human; tune to your domain.")

    # --- Column mapping + normalization ---
    df_std = None
    if csv_sel:
        raw_df = pd.read_csv(configs_dir / csv_sel, skipinitialspace=True)
        raw_df.columns = [str(c).strip() for c in raw_df.columns]
        lc_map = {c.lower(): c for c in raw_df.columns}

        def pick(*cands):
            for name in cands:
                if name in lc_map:
                    return lc_map[name]
            return None

        # Auto-detect likely columns
        col_prob = pick("ai_prob", "p_ai", "prob", "score", "risk_score")
        col_gt   = pick("ground_truth", "gt", "label", "secure_gt", "target", "y")
        col_ai_l = pick("ai_latency_ms", "ai_compute_ms")
        col_h_l  = pick("human_latency_ms", "human_est_ms")

        st.caption("Map your CSV columns (auto-detected where possible)")
        m1, m2, m3, m4 = st.columns(4)
        prob_col = m1.selectbox(
            "Probability column",
            raw_df.columns,
            index=(raw_df.columns.get_loc(col_prob) if col_prob in raw_df.columns else 0),
        )
        gt_col = m2.selectbox(
            "Ground-truth column",
            raw_df.columns,
            index=(raw_df.columns.get_loc(col_gt) if col_gt in raw_df.columns else 0),
        )
        ai_lat_col = m3.selectbox(
            "AI latency (optional)",
            ["—"] + list(raw_df.columns),
            index=(0 if not col_ai_l else 1 + raw_df.columns.get_loc(col_ai_l)),
        )
        h_lat_col = m4.selectbox(
            "Human latency (optional)",
            ["—"] + list(raw_df.columns),
            index=(0 if not col_h_l else 1 + raw_df.columns.get_loc(col_h_l)),
        )

        # Canonicalize headers for downstream code
        rename = {}
        if prob_col != "ai_prob":          rename[prob_col] = "ai_prob"
        if gt_col   != "ground_truth":     rename[gt_col]   = "ground_truth"
        if ai_lat_col != "—":              rename[ai_lat_col] = "ai_latency_ms"
        if h_lat_col  != "—":              rename[h_lat_col]  = "human_latency_ms"
        df_std = raw_df.rename(columns=rename)

        # --- Coverage preview (uses normalized ai_prob only) ---
        if "ai_prob" in df_std.columns:
            p = pd.to_numeric(df_std["ai_prob"], errors="coerce").clip(0, 1).dropna()
            baseline_ai_cov = float((p >= threshold).mean())
            band_lo, band_hi = (1.0 - tau), tau
            l2d_defer = float(((p > band_lo) & (p < band_hi)).mean())
            l2d_ai_cov = 1.0 - l2d_defer

            pc = st.columns(3)
            pc[0].metric("Baseline: AI coverage (≈)", f"{baseline_ai_cov:.0%}")
            pc[1].metric("L2D: defer rate (≈)", f"{l2d_defer:.0%}")
            pc[2].metric("L2D: AI coverage (≈)", f"{l2d_ai_cov:.0%}")
            st.caption(f"Uncertainty band: ({band_lo:.2f}, {band_hi:.2f}). Preview uses only `ai_prob` distribution.")
        else:
            st.info("CSV preview: **ai_prob** column not found. Map it above to enable coverage preview.")

    st.markdown(
        "> **Rule of thumb:** Lower threshold → more AI, faster; "
        "Higher τ → more human review, potentially higher accuracy but slower."
    )

    # --- Run A/B with the normalized DataFrame ---
    if df_std is not None and st.button("Run A/B now"):
        # Prepare rows (dicts) and basic typing
        rows = df_std.to_dict(orient="records")
        for r in rows:
            r["ai_prob"] = float(pd.to_numeric(r.get("ai_prob", 0), errors="coerce") or 0)

        # Auto-pick positive label from ground_truth values (e.g., 'secure'/'insecure' or 'positive'/'not_positive')
        pos_label = "positive"
        if "ground_truth" in df_std.columns:
            vals = {str(v).strip().lower() for v in df_std["ground_truth"].dropna().unique()}
            if "secure" in vals:            pos_label = "secure"
            elif "positive" in vals:        pos_label = "positive"
            elif vals:                      pos_label = sorted(vals)[0]  # fallback

        # Build shared sim scaffold
        base_cfg = {
            "environment": {"id": "HAIC_Exp", "class": "base.Environment",
                            "attributes": {"task": "classification"}},
            "agents": [
                {"id": "AI", "class": "base.Agent", "model": "ai", "affordances": ["classify"]},
                {"id": "H",  "class": "base.Agent", "model": "human", "affordances": ["classify"]},
            ],
            "objects": [{"id": f"O{i+1}", "class": "base.Object",
                         "attributes": {"row": i+1}, "affordances": ["classify"]}
                        for i in range(len(rows))],
        }

        # A: Baseline
        cfg_A = dict(base_cfg)
        cfg_A["sim_id"] = "exp_baseline"
        cfg_A["script"] = make_script_from_dataset(
            rows, "AI", "H",
            ai_policy=ThresholdPolicy(threshold=threshold),
            positive_label=pos_label,
            human_accuracy=human_acc,
        )
        out_A = run_from_config(cfg_A, results_dir=str(results_dir))
        log_A = json.loads(Path(out_A).read_text(encoding="utf-8"))

        # B: L2D-like
        cfg_B = dict(base_cfg)
        cfg_B["sim_id"] = "exp_l2d"
        cfg_B["script"] = make_script_from_dataset(
            rows, "AI", "H",
            ai_policy=L2DPolicy(tau=tau),
            positive_label=pos_label,
            human_accuracy=human_acc,
        )
        out_B = run_from_config(cfg_B, results_dir=str(results_dir))
        log_B = json.loads(Path(out_B).read_text(encoding="utf-8"))

        # Show side-by-side verdict + metrics
        render_ab_comparison(log_A, log_B, name_A="Baseline", name_B="L2D-like")


# ---------- 📊 Results & Compare ----------
with tab_compare:
    st.subheader("Compare any two results")

    files = list_files(results_dir)
    names = [p.relative_to(results_dir).as_posix() for p in files]

    if len(names) < 2:
        st.info("Need at least two result files to compare.")
    else:
        # ---- initialize our own state BEFORE rendering widgets ----
        if "cmp_left" not in st.session_state or st.session_state["cmp_left"] not in names:
            st.session_state["cmp_left"] = names[0]
        if "cmp_right" not in st.session_state or st.session_state["cmp_right"] not in names \
           or st.session_state["cmp_right"] == st.session_state["cmp_left"]:
            st.session_state["cmp_right"] = names[1 if len(names) > 1 else 0]

        header = st.columns([6, 1])
        with header[1]:
            if st.button("Swap A/B"):
                st.session_state["cmp_left"], st.session_state["cmp_right"] = \
                    st.session_state["cmp_right"], st.session_state["cmp_left"]
                st.rerun()  # safe rerun with new defaults

        # ---- render dropdowns WITHOUT mutating their keys afterwards ----
        left = st.selectbox(
            "Left",
            names,
            index=names.index(st.session_state["cmp_left"]),
        )
        right = st.selectbox(
            "Right",
            names,
            index=names.index(st.session_state["cmp_right"]),
        )
        # persist user changes (these keys are ours, not widget keys)
        if left != st.session_state["cmp_left"]:
            st.session_state["cmp_left"] = left
        if right != st.session_state["cmp_right"]:
            st.session_state["cmp_right"] = right

        # ---- load and render comparison ----
        import json
        from pathlib import Path
        log_A = json.loads((results_dir / left).read_text(encoding="utf-8"))
        log_B = json.loads((results_dir / right).read_text(encoding="utf-8"))

        render_ab_comparison(log_A, log_B, name_A=Path(left).name, name_B=Path(right).name)

        # optional: download compact comparison report
        A_all = collect_all_metrics(log_A)
        B_all = collect_all_metrics(log_B)
        report = {
            "A_file": left, "B_file": right,
            "A_metrics": A_all,
            "B_metrics": B_all,
            "deltas_B_minus_A": {k: B_all.get(k, 0) - A_all.get(k, 0) for k in sorted(set(A_all) | set(B_all))},
        }
        st.download_button(
            "Download comparison JSON",
            data=json.dumps(report, indent=2),
            file_name=f"compare_{Path(left).stem}_vs_{Path(right).stem}.json",
            mime="application/json",
        )


# ---------- Builder (custom config) ----------
with tab_builder:
    # ---------- State & helpers ----------
    if "builder_cfg" not in st.session_state:
        st.session_state["builder_cfg"] = {
            "sim_id": "ct_demo",
            "environment": {"id": "CT_Diagnosis", "class": "base.Environment",
                            "attributes": {"task": "classification", "domain": "medical"}},
            "agents": [
                {"id": "A1", "class": "user_plugins.medical.Radiologist",
                 "model": "human", "affordances": ["view","classify"], "attributes": {"viewed_cases": []}},
                {"id": "A2", "class": "base.Agent",
                 "model": "ai", "affordances": ["classify"], "attributes": {}},
            ],
            "objects": [
                {"id": "O1", "class": "user_plugins.medical.CTImage",
                 "affordances": ["view","classify"], "attributes": {"type":"CT","patient_id":"P001"}}
            ],
            "script": []
        }
    if "builder_ver" not in st.session_state:
        st.session_state["builder_ver"] = 0

    def k(name: str) -> str:
        """Versioned widget keys to avoid 'cannot modify after instantiation' errors."""
        return f"{name}__v{st.session_state['builder_ver']}"

    cfg = st.session_state["builder_cfg"]  # source of truth

    st.subheader("Config & Plugin Builder")

    with st.expander("How this works", expanded=False):
        c1, c2 = st.columns([1.3, 1.4])
        with c1:
            st.markdown(
                """
- **Steps:** *Environment → Agents → Objects → Script → (optional) Plugin → Preview/Save/Run*  
- **Templates:** Radiology creates *(view → AI classify → Human classify)*  
- **Plugin scaffold:** writes `user_plugins/<module>.py` (can enforce “view before classify”)  
- **Save:** config to **configs_dir** · **Run:** log to **results_dir**  
- **Auto-link:** If you scaffold a plugin, Agent 1 / Object 1 are auto-linked
                """
            )
        with c2:
            render_mermaid(
                """
                flowchart LR
                  ENV[Environment] --> AG[Agents]
                  ENV --> OBJ[Objects]
                  AG -- affordances --> SCR[Script]
                  OBJ -- affordances --> SCR
                  SCR --> PLG{Plugin?}
                  PLG --> CFG[Save → configs_dir]
                  CFG --> RUN[Run]
                  RUN --> LOG[Results → results_dir]
                  LOG --> MET[HAIC Metrics]
                """,
                height=260
            )

    # ---------- Multi-step form ----------
    step_tabs = st.tabs(["1) Environment", "2) Agents", "3) Objects", "4) Script", "5) Plugin", "6) Preview / Save"])

    # -- 1) Environment
    with step_tabs[0]:
        col1, col2 = st.columns(2)
        sim_id = col1.text_input("sim_id", value=cfg.get("sim_id","ct_demo"), key=k("sim_id"))
        env_id = col2.text_input("environment.id", value=cfg["environment"].get("id","ENV"), key=k("env_id"))
        col3, col4 = st.columns(2)
        task = col3.text_input("environment.attributes.task", value=cfg["environment"]["attributes"].get("task","classification"), key=k("task"))
        domain = col4.text_input("environment.attributes.domain", value=cfg["environment"]["attributes"].get("domain","medical"), key=k("domain"))

    # -- 2) Agents
    with step_tabs[1]:
        n_agents = st.number_input("How many agents?", 1, 6, value=max(1, len(cfg.get("agents", []))), step=1, key=k("n_agents"))
        agents_specs = []
        for i in range(int(n_agents)):
            defaults = cfg["agents"][i] if i < len(cfg["agents"]) else {
                "id": f"A{i+1}", "class": "base.Agent", "model": "human" if i == 0 else "ai",
                "affordances": ["view","classify"] if i == 0 else ["classify"], "attributes": {}
            }
            st.markdown(f"**Agent {i+1}**")
            ca, cb, cc = st.columns(3)
            a_id = ca.text_input("id", value=defaults["id"], key=k(f"a_{i}_id"))
            a_model = cb.selectbox("model", ["human","ai","surrogate"],
                                   index=["human","ai","surrogate"].index(defaults.get("model","ai")),
                                   key=k(f"a_{i}_model"))
            a_class = cc.text_input("class", value=defaults.get("class","base.Agent"), key=k(f"a_{i}_class"))
            c2a, c2b = st.columns([1,1])
            aff_str = c2a.text_input("affordances (comma-separated)",
                                     value=", ".join(defaults.get("affordances",[])), key=k(f"a_{i}_aff"))
            attrs_str = c2b.text_area("attributes (JSON)", value=json.dumps(defaults.get("attributes",{}), indent=2),
                                      height=90, key=k(f"a_{i}_attrs"))
            agents_specs.append({
                "id": a_id,
                "class": a_class,
                "model": a_model,
                "affordances": _parse_affordances(aff_str),
                "attributes": _parse_json_obj(attrs_str),
            })

    # -- 3) Objects
    with step_tabs[2]:
        n_objs = st.number_input("How many objects?", 1, 50, value=max(1, len(cfg.get("objects", []))), step=1, key=k("n_objs"))
        objs_specs = []
        for i in range(int(n_objs)):
            defaults = cfg["objects"][i] if i < len(cfg["objects"]) else {
                "id": f"O{i+1}", "class": "base.Object",
                "affordances": ["view","classify"], "attributes": {}
            }
            st.markdown(f"**Object {i+1}**")
            co, cp, cq = st.columns(3)
            o_id = co.text_input("id", value=defaults["id"], key=k(f"o_{i}_id"))
            o_class = cp.text_input("class", value=defaults.get("class","base.Object"), key=k(f"o_{i}_class"))
            o_aff = cq.text_input("affordances (comma-separated)",
                                  value=", ".join(defaults.get("affordances",[])), key=k(f"o_{i}_aff"))
            o_attrs = st.text_area("attributes (JSON)", value=json.dumps(defaults.get("attributes",{}), indent=2),
                                   height=80, key=k(f"o_{i}_attrs"))
            objs_specs.append({
                "id": o_id,
                "class": o_class,
                "affordances": _parse_affordances(o_aff),
                "attributes": _parse_json_obj(o_attrs),
            })

# -- 4) Script
with step_tabs[3]:
    # detect if imported config already carries a script
    imported_steps = cfg.get("script", []) or []
    has_imported = len(imported_steps) > 0

    mode = st.radio(
        "Script mode",
        options=["Use imported script", "Generate from template"],
        index=0 if has_imported else 1,
        horizontal=True,
        key=k("script_mode"),
        help="Keep and edit the script that came from the imported config, or generate a template."
    )

    generated_steps = []  # will fill only if template mode

    if mode == "Use imported script":
        st.caption("Edit your script inline. Add/delete rows as needed.")
        df = _steps_to_df(imported_steps)
        edited = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "t": st.column_config.NumberColumn("t", min_value=0, step=1),
                "agent": st.column_config.TextColumn("agent", help="Must match an agent id"),
                "action": st.column_config.TextColumn("action"),
                "object": st.column_config.TextColumn("object", help="Must match an object id"),
                "latency_ms": st.column_config.NumberColumn("latency_ms", min_value=0, step=10, help="Optional"),
                "correct": st.column_config.CheckboxColumn("correct", help="Optional"),
                "effect_json": st.column_config.TextColumn("effect (JSON)", width="large",
                    help='e.g., {"ai_label":"benign","prob":0.82}'),
            },
            hide_index=True,
        )
        # persist the edited script into session so Preview reflects it
        st.session_state["builder_script"] = _df_to_steps(edited)

        # light validation
        missing_ids = []
        agent_ids = {a["id"] for a in agents_specs}
        obj_ids   = {o["id"] for o in objs_specs}
        for s in st.session_state["builder_script"]:
            if s["agent"] and s["agent"] not in agent_ids:
                missing_ids.append(f"agent '{s['agent']}'")
            if s["object"] and s["object"] not in obj_ids:
                missing_ids.append(f"object '{s['object']}'")
        if missing_ids:
            st.warning("Unknown ids in script: " + ", ".join(sorted(set(missing_ids))))

    else:  # Generate from template
        templ = st.selectbox("Template", ["Radiology (view → AI classify → Human classify)", "Empty"],
                             index=0 if not has_imported else 1, key=k("templ"))
        c1, c2, c3 = st.columns(3)
        ai_label = c1.text_input("AI label", value="benign", key=k("ai_label"))
        ai_prob  = c2.number_input("AI prob", 0.0, 1.0, value=0.82, step=0.01, key=k("ai_prob"))
        human_label = c3.text_input("Human label", value="benign", key=k("h_label"))
        d1, d2, d3, d4 = st.columns(4)
        lat_view = d1.number_input("Latency view (ms)", 0, value=1200, step=10, key=k("lat_view"))
        lat_ai   = d2.number_input("Latency AI classify (ms)", 0, value=220, step=10, key=k("lat_ai"))
        lat_h    = d3.number_input("Latency Human classify (ms)", 0, value=950, step=10, key=k("lat_h"))
        correct  = d4.checkbox("Final human step correct", value=True, key=k("correct"))

        if templ.startswith("Radiology") and agents_specs and objs_specs:
            a_human = agents_specs[0]["id"]
            a_ai = agents_specs[1]["id"] if len(agents_specs) > 1 else agents_specs[0]["id"]
            obj = objs_specs[0]["id"]
            generated_steps = [
                {"t": 1, "agent": a_human, "action": "view", "object": obj, "latency_ms": int(lat_view)},
                {"t": 2, "agent": a_ai, "action": "classify", "object": obj,
                 "latency_ms": int(lat_ai), "effect": {"ai_label": ai_label, "prob": float(ai_prob)}},
                {"t": 3, "agent": a_human, "action": "classify", "object": obj,
                 "latency_ms": int(lat_h), "effect": {"human_label": human_label}, "correct": bool(correct)},
            ]
        else:
            generated_steps = []

        # keep in state so preview uses exactly what the user sees
        st.session_state["builder_script"] = generated_steps


    # -- 5) Plugin (optional)
    with step_tabs[4]:
        st.caption("Optional plugin scaffold (keeps the core clean).")
        colp1, colp2, colp3 = st.columns(3)
        module_name = colp1.text_input("Module (user_plugins.<module>)", value="medical", key=k("pl_mod"))
        agent_class_name = colp2.text_input("Agent class name", value="Radiologist", key=k("pl_agent"))
        object_class_name = colp3.text_input("Object class name", value="CTImage", key=k("pl_obj"))
        enforce_gate = st.checkbox("Enforce 'view before classify'", value=True, key=k("pl_gate"))
        write_plugin = st.checkbox("Create/overwrite plugin file and auto-link Agent 1 & Object 1", value=False, key=k("pl_write"))

    # Assemble a preview config from the current widgets (live)
    config_preview = {
        "sim_id": sim_id,
        "environment": {"id": env_id, "class": "base.Environment", "attributes": {"task": task, "domain": domain}},
        "agents": agents_specs,
        "objects": objs_specs,
        "script": []
    }

    config_preview = {
        "sim_id": sim_id,
        "environment": {"id": env_id, "class": "base.Environment",
                        "attributes": {"task": task, "domain": domain}},
        "agents": agents_specs,
        "objects": objs_specs,
        "script": st.session_state.get("builder_script", cfg.get("script", [])),
    }

    # -- 6) Preview / Save / Import
    with step_tabs[5]:
        st.markdown("#### Live Preview")
        cprev1, cprev2 = st.columns([1,1])
        with cprev1:
            st.code(to_yaml(config_preview), language="yaml")
        with cprev2:
            st.code(to_json(config_preview), language="json")

        st.markdown("#### Save / Run")
        col_save1, col_save2, col_save3 = st.columns(3)
        cfg_filename = col_save1.text_input("Config filename", value=f"{sim_id}.json", key=k("fname"))
        run_after_save = col_save2.checkbox("Run after save", value=False, key=k("run_now"))
        overwrite_cfg = col_save3.checkbox("Overwrite if exists", value=False, key=k("overwrite"))

        # Primary action
        if st.button("Save (and Run if selected)", type="primary", key=k("save_btn")):
            # 1) Optional plugin scaffold
            if write_plugin:
                plugin_path = USER_PLUGINS_DIR / f"{module_name.strip()}.py"
                code = _plugin_skeleton(
                    module_name.strip() or "medical",
                    agent_class_name.strip() or "Radiologist",
                    object_class_name.strip() or "CTImage",
                    enforce_view_before_classify=enforce_gate
                )
                plugin_path.write_text(code, encoding="utf-8")
                st.success(f"Plugin written: {plugin_path}")
                # Auto-link Agent 1 / Object 1
                if config_preview["agents"]:
                    config_preview["agents"][0]["class"] = f"user_plugins.{module_name}.{agent_class_name}"
                if config_preview["objects"]:
                    config_preview["objects"][0]["class"] = f"user_plugins.{module_name}.{object_class_name}"

            # 2) Persist config
            tgt = configs_dir / cfg_filename
            if tgt.exists() and not overwrite_cfg:
                st.warning(f"Config exists: {tgt} (enable 'Overwrite' to replace)")
            else:
                tgt.write_text(json.dumps(config_preview, indent=2), encoding="utf-8")
                st.success(f"Config saved: {tgt}")
                # Keep as the active builder_cfg and bump version so widgets re-instantiate safely
                st.session_state["builder_cfg"] = config_preview
                st.session_state["builder_ver"] += 1

                # 3) Optional run
                if run_after_save:
                    out_path = run_from_config(config_preview, results_dir=str(results_dir))
                    st.success(f"Run complete → {out_path}")

        st.divider()
        st.markdown("#### Paste / Import (YAML or JSON)")
        pasted = st.text_area("Paste here", height=200, placeholder="YAML or JSON…", key=k("paste"))
        up = st.file_uploader("…or upload a file", type=["yaml","yml","json"], key=k("upload"))
        col_imp1, col_imp2 = st.columns([1,1])
        with col_imp1:
            if st.button("Parse & Validate", key=k("parse_btn")):
                try:
                    text = pasted
                    if up is not None:
                        text = up.read().decode("utf-8")
                    loaded = parse_any(text)
                    errs = validate_cfg(loaded)
                    if errs:
                        st.error("Validation issues:\n- " + "\n- ".join(errs))
                    else:
                        st.session_state["loaded_cfg"] = loaded
                        st.success("Parsed OK ✅ — click **Apply to form**.")
                except Exception as e:
                    st.error(f"Parse error: {e}")
        with col_imp2:
            if st.button("Apply to form", key=k("apply_btn")):
                loaded = st.session_state.get("loaded_cfg")
                if not loaded:
                    st.warning("Nothing to apply. Parse a config first.")
                else:
                    st.session_state["builder_cfg"] = loaded
                    st.session_state["builder_ver"] += 1  # force fresh widget keys
                    st.success("Applied to form. Re-rendering…")
                    st.rerun()

# ---------- 🏁 Overview ----------
with tab_overview:
    st.subheader("What is this?")

    st.markdown("""
**HAIC Simulation | MVP** is a tiny, extensible simulation core for **Human–AI workflows**:
- Configure **Environment, Agents, Objects, Policies**, then **Run** and **Log**.
- Evaluate with **base metrics** (accuracy, latency, defer) and **HAIC interaction metrics**.
- Extend via **plugins** (domain Agents/Objects) and **policies** — no core changes needed.
""")

    # Architecture diagram
    render_mermaid("""
flowchart LR
  U[User] -->|Builder| C[Config JSON]
  U -->|Plugin| P[user_plugins/*.py]
  P --> R
  C --> R[Runner]
  D[Dataset CSV] --> G[Script Generator]
  G --> R
  PL[Policy: Baseline/L2D/...] --> R
  R --> L[Decision Log JSON]
  L --> M[HAIC Interaction Metrics]
  M --> V[Charts/UI]
""", height=320)

    # Status badges
    from haic_sim_mvp.engine import metrics_bridge as _mb
    have_pillars = _mb._CM is not None
    cols = st.columns(4)
    cols[0].metric("HAIC interaction metrics", "Enabled" if have_pillars else "Disabled",
                   _mb._CM_MODULE or "—")
    cols[1].metric("Configs", len(list_files(configs_dir, suffixes=(".json",), exclude_contains=("_metrics","_haic"))))
    cols[2].metric("Results", len(list_files(results_dir)))
    cols[3].metric("Datasets (CSV)", len(list_csv(configs_dir)))

    # Recent artifacts (quick glance)
    st.markdown("#### Recent artifacts")
    c1, c2 = st.columns(2)
    recent_cfgs = list_files(configs_dir, suffixes=(".json",), exclude_contains=("_metrics","_haic"))[:5]
    recent_logs = list_files(results_dir)[:5]

    with c1:
        st.caption("Configs")
        if recent_cfgs:
            for p in recent_cfgs:
                st.write("•", p.relative_to(configs_dir).as_posix())
        else:
            st.write("_No configs found_")
    with c2:
        st.caption("Results")
        if recent_logs:
            for p in recent_logs:
                st.write("•", p.relative_to(results_dir).as_posix())
        else:
            st.write("_No results yet_")

    # Guided steps (the story you’ll tell)
    st.markdown("""
#### How to use (demo flow)
1) **Builder:** Fill the form to create a config. *(Optionally scaffold a plugin — your Agent/Object classes — which is auto-linked in the config.)*  
2) **Scripted Run:** Pick that config and **Run** → see *interaction metrics** and the **decision table**.
3) **Dataset A/B:** Pick a CSV → choose **Baseline** or **L2D-like** (with slider hints + live coverage preview) → **Run A/B** → compare side-by-side.  
4) **Results & Compare:** Pick any two logs to compare metrics and **Download** the JSONs for backend/CI.
""")
