import os, sys, json, io, time, importlib
from pathlib import Path
import streamlit as st
import pandas as pd

# --- Paths: app at repo root, engine inside haic_sim_mvp/ ---
ROOT = Path(__file__).resolve().parent          # repo root
PKG_ROOT = ROOT / "haic_sim_mvp"                # where engine/ lives
sys.path.insert(0, str(ROOT))                   # allow 'haic_sim_mvp' import
sys.path.insert(0, str(PKG_ROOT))               # (defensive)

# --- MVP imports using package-qualified paths ---
from haic_sim_mvp.engine.run_sim import run_from_config
from haic_sim_mvp.engine.datasets import load_csv, make_script_from_dataset
from haic_sim_mvp.engine.policies import ThresholdPolicy, L2DPolicy
from haic_sim_mvp.engine.evaluate import compute_metrics as base_metrics

# HAIC pillars bridge
try:
    from haic_sim_mvp.engine.metrics_bridge import haic_metrics_for_log
    HAVE_HAIC = True
    HAIC_ERR = None
except Exception as e:
    HAVE_HAIC = False
    HAIC_ERR = str(e)

st.set_page_config(page_title="HAIC MVP", layout="wide")
st.title("HAIC MVP — Human–AI Collaboration Simulator")

mb = importlib.import_module("haic_sim_mvp.engine.metrics_bridge")
haic_metrics_for_log = mb.haic_metrics_for_log
HAVE_HAIC = getattr(mb, "_CM", None) is not None
HAIC_ERR = None if HAVE_HAIC else "No metrics module loaded"

with st.sidebar:
    st.header("Settings")

    default_results = PKG_ROOT / "results" if (PKG_ROOT / "results").exists() else ROOT / "results"
    results_dir = st.text_input("Results directory", value=str(default_results))
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    st.markdown("---")
    st.caption("HAIC metrics module (optional)")
    metrics_mod = st.text_input(
        "Module path",
        value=os.environ.get("HAIC_METRICS_MODULE", "metrics_core.interaction_metrics"),
        help="e.g., metrics_core.interaction_metrics",
    )
    if st.button("Load metrics module"):
        os.environ["HAIC_METRICS_MODULE"] = metrics_mod
        mb = importlib.reload(mb)                         # re-resolve inside the bridge
        haic_metrics_for_log = mb.haic_metrics_for_log    # refresh callable
        HAVE_HAIC = getattr(mb, "_CM", None) is not None
        HAIC_ERR = None if HAVE_HAIC else f"Could not import: {metrics_mod}"

    if HAVE_HAIC:
        st.success("HAIC pillars: enabled")
    else:
        st.warning(f"HAIC pillars unavailable. {HAIC_ERR or ''}")


tab_view, tab_exp, tab_script = st.tabs(["📄 View Log", "🧪 Run Dataset A/B", "🧰 Scripted Run"])

# ---------- TAB 1: VIEW LOG ----------
with tab_view:
    st.subheader("View an existing MVP results JSON")
    uploaded = st.file_uploader("Upload results JSON", type=["json"], key="log_upload")
    if uploaded:
        log = json.load(uploaded)
        st.success("Loaded log.")
        # quick meta
        meta_cols = st.columns(4)
        meta_cols[0].metric("sim_id", log.get("sim_id", ""))
        meta_cols[1].metric("env_id", log.get("env_id", ""))
        meta_cols[2].metric("#steps", len(log.get("decisions", [])))
        meta_cols[3].metric("#agents", len(log.get("agents", {})))

        # base metrics (accuracy / latency / defer)
        base = base_metrics(log)
        mcols = st.columns(5)
        mcols[0].metric("accuracy", f"{base.get('accuracy', 0):.2f}" if base.get("accuracy") is not None else "–")
        mcols[1].metric("AI acc", f"{base.get('ai_accuracy', 0):.2f}" if base.get("ai_accuracy") is not None else "–")
        mcols[2].metric("Human acc", f"{base.get('human_accuracy', 0):.2f}" if base.get("human_accuracy") is not None else "–")
        mcols[3].metric("defer rate", f"{base.get('defer_rate', 0):.2f}" if base.get("defer_rate") is not None else "–")
        mcols[4].metric("avg latency (ms)", f"{base.get('avg_latency_ms', 0):.0f}")

        # HAIC pillars
        if HAVE_HAIC:
            pillars = haic_metrics_for_log(log)
            st.markdown("#### HAIC Pillars")
            pcols = st.columns(8)
            for i, k in enumerate(["F","D","HCL","Tr","A","S","EL","EfficiencyScore"]):
                pcols[i].metric(k, f"{pillars.get(k, 0):.2f}")
        else:
            st.info("Install metrics package (see sidebar) to compute HAIC pillars.")

        # decisions table + simple charts
        st.markdown("#### Decisions")
        df = pd.DataFrame(log.get("decisions", []))
        # compact view
        show_cols = [c for c in ["t","agent_id","action","object_id","latency_ms","correct","effect"] if c in df.columns]
        st.dataframe(df[show_cols] if show_cols else df, use_container_width=True, height=320)

        # charts
        st.markdown("#### Charts")
        c1, c2 = st.columns(2)
        if "latency_ms" in df.columns and "t" in df.columns:
            c1.line_chart(df[["t","latency_ms"]].set_index("t"))
        counts = df.groupby("agent_id")["action"].count().reset_index(name="count") if "agent_id" in df else None
        if counts is not None and not counts.empty:
            counts = counts.set_index("agent_id")
            c2.bar_chart(counts)

# ---------- TAB 2: DATASET A/B ----------
with tab_exp:
    st.subheader("Run dataset-driven experiment")
    csv_up = st.file_uploader("Upload dataset CSV (ai_prob, ground_truth)", type=["csv"], key="csv_upload")
    colA, colB, colC = st.columns(3)
    mode = colA.selectbox("Policy mode", ["baseline","l2d"], index=1)
    threshold = colB.slider("Threshold (baseline)", 0.0, 1.0, 0.5, 0.01, disabled=(mode!="baseline"))
    tau = colC.slider("Tau (L2D-like)", 0.0, 1.0, 0.7, 0.01, disabled=(mode!="l2d"))
    human_acc = st.slider("Human accuracy", 0.5, 1.0, 0.9, 0.01)

    run_btn = st.button("Run experiment")
    if run_btn and csv_up is not None:
        # read CSV bytes into a temp fileless DataFrame
        df = pd.read_csv(csv_up)
        rows = df.to_dict(orient="records")

        # configure experiment
        cfg = {
            "sim_id": f"exp_{mode}",
            "environment": {"id":"HAIC_Exp","class":"base.Environment","attributes":{"task":"classification"}},
            "agents": [
                {"id":"AI","class":"base.Agent","model":"ai","affordances":["classify"]},
                {"id":"H","class":"base.Agent","model":"human","affordances":["classify"]},
            ],
            "objects": [{"id": f"O{i+1}","class":"base.Object","attributes":{"row":i+1},"affordances":["classify"]}
                        for i in range(len(rows))],
            "script": []
        }
        policy = ThresholdPolicy(threshold=threshold) if mode == "baseline" else L2DPolicy(tau=tau)
        script = make_script_from_dataset(rows, ai_agent_id="AI", human_agent_id="H",
                                          ai_policy=policy, positive_label="positive",
                                          human_accuracy=human_acc)
        cfg["script"] = script

        # run & show
        out_path = run_from_config(cfg, results_dir=results_dir)
        st.success(f"Run complete → {out_path}")
        log = json.loads(Path(out_path).read_text(encoding="utf-8"))

        base = base_metrics(log)
        mcols = st.columns(5)
        mcols[0].metric("accuracy", f"{base.get('accuracy', 0):.2f}" if base.get("accuracy") is not None else "–")
        mcols[1].metric("AI acc", f"{base.get('ai_accuracy', 0):.2f}" if base.get("ai_accuracy") is not None else "–")
        mcols[2].metric("Human acc", f"{base.get('human_accuracy', 0):.2f}" if base.get("human_accuracy") is not None else "–")
        mcols[3].metric("defer rate", f"{base.get('defer_rate', 0):.2f}" if base.get("defer_rate") is not None else "–")
        mcols[4].metric("avg latency (ms)", f"{base.get('avg_latency_ms', 0):.0f}")

        if HAVE_HAIC:
            pillars = haic_metrics_for_log(log)
            pcols = st.columns(8)
            for i, k in enumerate(["F","D","HCL","Tr","A","S","EL","EfficiencyScore"]):
                pcols[i].metric(k, f"{pillars.get(k, 0):.2f}")

        # downloads
        st.download_button("Download log JSON", data=json.dumps(log, indent=2),
                           file_name=Path(out_path).name, mime="application/json")

# ---------- TAB 3: SCRIPTED RUN ----------
with tab_script:
    st.subheader("Run a scripted config JSON")
    cfg_up = st.file_uploader("Upload config JSON", type=["json"], key="cfg_upload")
    if st.button("Run scripted") and cfg_up is not None:
        cfg = json.load(cfg_up)
        out_path = run_from_config(cfg, results_dir=results_dir)
        st.success(f"Run complete → {out_path}")
        log = json.loads(Path(out_path).read_text(encoding="utf-8"))

        base = base_metrics(log)
        mcols = st.columns(5)
        mcols[0].metric("accuracy", f"{base.get('accuracy', 0):.2f}" if base.get("accuracy") is not None else "–")
        mcols[1].metric("AI acc", f"{base.get('ai_accuracy', 0):.2f}" if base.get("ai_accuracy") is not None else "–")
        mcols[2].metric("Human acc", f"{base.get('human_accuracy', 0):.2f}" if base.get("human_accuracy") is not None else "–")
        mcols[3].metric("defer rate", f"{base.get('defer_rate', 0):.2f}" if base.get("defer_rate") is not None else "–")
        mcols[4].metric("avg latency (ms)", f"{base.get("avg_latency_ms", 0):.0f}")
        if HAVE_HAIC:
            pillars = haic_metrics_for_log(log)
            pcols = st.columns(8)
            for i, k in enumerate(["F","D","HCL","Tr","A","S","EL","EfficiencyScore"]):
                pcols[i].metric(k, f"{pillars.get(k, 0):.2f}")
