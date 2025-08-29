from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Dict, Any, List

import streamlit as st
import pandas as pd
import altair as alt

# ---------- bootstrap: add repo root (directory that contains haic_env_builder/) ----------
def _add_repo_root_to_syspath():
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "haic_env_builder").exists():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return p
    # fallback to current working dir
    cwd = Path.cwd()
    if (cwd / "haic_env_builder").exists() and str(cwd) not in sys.path:
        sys.path.insert(0, str(cwd))
    return cwd

REPO_ROOT = _add_repo_root_to_syspath()
# ------------------------------------------------------------------------------------------

from haic_env_builder.utils.simulation_runner import simulate_environment
from haic_env_builder.utils.metrics import compute_metrics_by_agent
from haic_env_builder.utils.insights import summarize_run_brief, interpret_metrics, derive_aux_rates

CONFIG_DIR = (REPO_ROOT / "haic_env_builder" / "configs").resolve()
METRICS_DIR = (REPO_ROOT / "metrics").resolve()

st.set_page_config(page_title="HAIC Simulator Dashboard", page_icon="🧪", layout="wide")
alt.data_transformers.disable_max_rows()

@st.cache_data
def list_configs() -> List[str]:
    return sorted([p.name for p in CONFIG_DIR.glob("*.yaml")])

def run_sim(name: str, seed: int | None) -> Dict[str, Any]:
    cfg_path = (CONFIG_DIR / name).resolve()
    if not cfg_path.exists():
        st.error(f"Config not found: {name}")
        st.stop()
    return simulate_environment(str(cfg_path), seed=seed)

def metrics_to_df(metrics: Dict[str, float]) -> pd.DataFrame:
    items = [(k, float(v)) for k, v in metrics.items()]
    return pd.DataFrame(items, columns=["metric", "value"])

def decisions_to_df(decisions: List[Dict[str, Any]]) -> pd.DataFrame:
    cols = [
        "t","agent","actor_type","action","proposed_action","correct","ai_suggested","human_accepted",
        "successful_outcome","unsafe_event","manual_intervention","off_role_action","latency_ms","duration_s",
        "event_type","reward","profile"
    ]
    rows = []
    for d in decisions:
        row = {c: d.get(c) for c in cols}
        prof = row.get("profile") or {}
        if isinstance(prof, dict):
            row["profile_id"] = prof.get("profile_id")
            row["profile_role"] = prof.get("role")
            row["profile_skill"] = prof.get("skill_level")
        rows.append(row)
    df = pd.DataFrame(rows).sort_values(by=["t","agent"], kind="stable")
    return df

def bar_chart(dfm: pd.DataFrame):
    chart = alt.Chart(dfm).mark_bar().encode(
        x=alt.X("metric:N", sort=None, title=None),
        y=alt.Y("value:Q", title=None),
        tooltip=["metric","value"]
    )
    st.altair_chart(chart, use_container_width=True)

def timeline_chart(df: pd.DataFrame):
    if "t" not in df.columns:
        return
    pts = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X("t:Q", title="time (s)"),
        y=alt.Y("agent:N", title="agent"),
        shape=alt.Shape("actor_type:N"),
        tooltip=["t","agent","actor_type","action","proposed_action","correct","latency_ms","duration_s"]
    ).interactive()
    st.altair_chart(pts, use_container_width=True)

def progress_chart(df: pd.DataFrame):
    if "event_type" not in df.columns:
        return
    prog = df[df["event_type"].isin(["checklist_progress","progress"])]
    if prog.empty:
        return
    ticks = alt.Chart(prog).mark_tick().encode(
        x=alt.X("t:Q", title="time (s)"),
        y=alt.value(0),
        tooltip=["t","event_type","reward"]
    )
    st.altair_chart(ticks, use_container_width=True)

# -------------- UI ----------------
st.title("HAIC Simulator • Demo Dashboard")
st.caption("Run scenarios, inspect decisions, and visualize metrics")

with st.sidebar:
    st.header("Run settings")
    configs = list_configs()
    if not configs:
        st.error("No configs found in haic_env_builder/configs")
        st.stop()

    cfg = st.selectbox("Config", configs, index=0)
    seed = st.number_input("Seed (optional)", value=123, step=1, format="%d")
    run_btn = st.button("Run Simulation 🚀", use_container_width=True)

    st.markdown("---")
    show_by_agent = st.checkbox("Show metrics by agent", value=True)
    show_json = st.checkbox("Show raw JSON", value=False)

if run_btn:
    with st.spinner("Simulating..."):
        result = run_sim(cfg, int(seed))

    st.success(f"Done: {result.get('task')} | env={result.get('environment','n/a')} | hash={result.get('config_hash','n/a')}")
    st.caption(f"Saved to: {result.get('log_path')}")

 
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("Metrics")
        dfm = metrics_to_df(result.get("metrics", {}))
        bar_chart(dfm)
    with col2:
        st.subheader("Summary")
        st.json(result.get("metrics", {}), expanded=False)
        
        # === Insights ===
    st.subheader("Insights")
    st.write(summarize_run_brief(result))
    aux = derive_aux_rates(result)
    bullets = interpret_metrics(result.get("metrics", {}), **aux)
    for b in bullets:
        st.markdown(f"- {b}")
        
        
    if show_by_agent:
        st.subheader("Metrics by Agent")
        per_agent = compute_metrics_by_agent(result.get("decisions", []))
        for agent, m in per_agent.items():
            st.markdown(f"**{agent}**")
            st.dataframe(metrics_to_df(m), use_container_width=True)

    st.subheader("Decisions")
    dfd = decisions_to_df(result.get("decisions", []))
    st.dataframe(dfd, use_container_width=True, height=420)

    st.subheader("Timeline")
    timeline_chart(dfd)
    progress_chart(dfd)

    st.subheader("Download")
    st.download_button(
        "Download result JSON",
        data=json.dumps(result, indent=2),
        file_name=Path(result.get("log_path","result.json")).name,
        mime="application/json",
        use_container_width=True,
    )
    csv = dfd.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download decisions CSV",
        data=csv,
        file_name="decisions.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if show_json:
        st.subheader("Raw result payload")
        st.json(result, expanded=False)
else:
    st.info("Pick a config and click **Run Simulation**.")
