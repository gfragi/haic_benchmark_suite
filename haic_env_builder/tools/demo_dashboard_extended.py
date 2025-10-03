
from __future__ import annotations
import json, sys, os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, date

import streamlit as st
import pandas as pd
import altair as alt
import yaml

# ---------- bootstrap: add repo root (directory that contains haic_env_builder/) ----------
def _add_repo_root_to_syspath():
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "haic_env_builder").exists():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return p
    cwd = Path.cwd()
    if (cwd / "haic_env_builder").exists() and str(cwd) not in sys.path:
        sys.path.insert(0, str(cwd))
    return cwd

REPO_ROOT = _add_repo_root_to_syspath()

from haic_env_builder.utils.simulation_runner import simulate_environment
from metrics_core.interaction_metrics import compute_metrics_by_agent
from haic_env_builder.utils.insights import summarize_run_brief, interpret_metrics, derive_aux_rates

CONFIG_DIR = (REPO_ROOT / "haic_env_builder" / "configs").resolve()
RUNS_DIR = (REPO_ROOT / "runs").resolve()
RUNS_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="HAIC Simulator Dashboard", page_icon="🧪", layout="wide")
alt.data_transformers.disable_max_rows()

# ================================ helpers ====================================
@st.cache_data
def list_configs() -> List[str]:
    return sorted([p.name for p in CONFIG_DIR.glob("*.yaml")])


@st.cache_data
def infer_env_options_from_configs() -> list[str]:
    options = set()
    for yp in CONFIG_DIR.glob("*.yaml"):
        try:
            data = yaml.safe_load(yp.read_text(encoding="utf-8"))
            env = (data or {}).get("task_parameters", {}).get("environment")
            if isinstance(env, str) and env.strip():
                options.add(env.strip())
        except Exception:
            pass
    if not options:
        options = {"ct_scan", "overcooked_cram", "radiologist_task"}
    return sorted(options)


def _scan_runs() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for p in sorted(RUNS_DIR.glob("*.json")):
        try:
            with p.open("r", encoding="utf-8") as f:
                head = json.loads(f.read(4096))
            task = head.get("task") or head.get("task_name") or "unknown"
        except Exception:
            task = "unknown"
        stat = p.stat()
        rows.append({
            "file": p.name,
            "task": task,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "size_kb": round(stat.st_size / 1024, 1)
        })
    df = pd.DataFrame(rows).sort_values("modified", ascending=False, kind="stable").reset_index(drop=True)
    return df

@st.cache_data(show_spinner=False)
def list_runs_cached(_nonce: int) -> pd.DataFrame:
    # nonce invalidates cache when we create/rename/delete
    return _scan_runs()

def refresh_runs():
    st.session_state['runs_nonce'] = st.session_state.get('runs_nonce', 0) + 1

def read_run(file_name: str) -> Dict[str, Any]:
    p = (RUNS_DIR / file_name).resolve()
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def run_sim_by_config_name(name: str, seed: Optional[int]) -> Dict[str, Any]:
    cfg_path = (CONFIG_DIR / name).resolve()
    if not cfg_path.exists():
        st.error(f"Config not found: {name}")
        st.stop()
    result = simulate_environment(str(cfg_path), seed=seed)
    refresh_runs()
    return result

def run_sim_by_yaml_text(yaml_text: str, seed: Optional[int]) -> Dict[str, Any]:
    tmp_path = CONFIG_DIR / "_pasted.yaml"
    tmp_path.write_text(yaml_text, encoding="utf-8")
    try:
        result = simulate_environment(str(tmp_path), seed=seed)
        refresh_runs()
        return result
    finally:
        try: tmp_path.unlink()
        except Exception: pass


def split_metrics_bounded_open(metrics: Dict[str, float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Heuristically split metrics into bounded [-1,1] vs open range.
    If |value| <= 1.05 -> bounded; else open. Returns (bounded_df, open_df)."""
    items = [(k, float(v)) for k, v in (metrics or {}).items()]
    if not items:
        return pd.DataFrame(columns=["metric","value"]), pd.DataFrame(columns=["metric","value"])
    bounded = [(k,v) for k,v in items if abs(v) <= 1.05]
    openrng = [(k,v) for k,v in items if abs(v) > 1.05]
    return (pd.DataFrame(bounded, columns=["metric","value"]),
            pd.DataFrame(openrng, columns=["metric","value"]))

def plot_metric_groups(metrics: Dict[str, float]):
    bdf, odf = split_metrics_bounded_open(metrics)
    # Open-range first if present
    if not odf.empty:
        st.markdown("**Open-range metrics** (absolute scale)")
        bar_chart_shared(odf, log_scale=False)
    if not bdf.empty:
        st.markdown("**Bounded metrics** (−1 to 1)")
        chart = alt.Chart(bdf).mark_bar().encode(
            x=alt.X("metric:N", sort=None, title=None),
            y=alt.Y("value:Q", title=None, scale=alt.Scale(domain=[-1,1])),
            tooltip=["metric","value"]
        )
        st.altair_chart(chart, use_container_width=True)


def metric_glossary_note():
    with st.expander("How to read these metrics", expanded=True):
        st.markdown("""
**Effort Loss (EL)** – How much slower the task is vs a baseline.  
If baseline = 100s and the actual run = 120s, then **EL = 0.20** → 20% slower (lower is better).

**Mean Duration (D)** – Average time per interaction (seconds).  
If three actions take 0.9s, 1.1s, 1.0s → **D = 1.0s**. High values suggest workflow bottlenecks.

**Interaction Frequency (F)** – Interactions per minute (collaboration density).  
30 events over 10 minutes → **F = 3 / min**. Too low may imply poor engagement; too high may imply inefficiency.

**Human‑Centeredness (HCL)** – Proxy for cognitive load / responsiveness (0–1).  
If average human reaction = 1.2s and max allowed = 5.0s → **HCL = 0.76**. Higher means smoother human interaction.

**Trust Proxy (Tr)** – How often humans accept or validate AI suggestions (0–1).  
If 37/40 are correct → **Tr = 0.925**. Lower values mean frequent overrides or errors.

**Adaptability (A)** – Improvement trend during the session (−1..1).  
If early accuracy = 0.6 and late accuracy = 0.9 → **A = 0.5** (50% improvement). Negative means deterioration.

**Surrogate Similarity (S)** – How closely a surrogate replicates human behaviour (0–1).  
If distributions overlap 90% → **S = 0.9**. Higher means surrogates are reliable stand‑ins.
        """)


def metrics_to_df(metrics: Dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame([(k, float(v)) for k, v in metrics.items()], columns=["metric","value"])

def decisions_to_df(decisions: List[Dict[str, Any]]) -> pd.DataFrame:
    cols = [
        "t","agent","actor_type","action","proposed_action","correct","ai_suggested","human_accepted",
        "successful_outcome","unsafe_event","manual_intervention","off_role_action","latency_ms","duration_s",
        "event_type","reward","profile"
    ]
    rows = []
    for d in decisions or []:
        row = {c: d.get(c) for c in cols}
        prof = row.get("profile") or {}
        if isinstance(prof, dict):
            row["profile_id"] = prof.get("profile_id")
            row["profile_role"] = prof.get("role")
            row["profile_skill"] = prof.get("skill_level")
        rows.append(row)
    df = pd.DataFrame(rows).sort_values(by=["t","agent"], kind="stable")
    return df


def bar_chart_shared(dfm: pd.DataFrame, log_scale: bool = False):
    if dfm is None or dfm.empty: 
        st.info("No metrics to show.")
        return
    yscale = alt.Scale(type='log') if log_scale else alt.Scale(type='linear')
    chart = alt.Chart(dfm).mark_bar().encode(
        x=alt.X("metric:N", sort=None, title=None),
        y=alt.Y("value:Q", title=None, scale=yscale),
        tooltip=["metric","value"]
    )
    st.altair_chart(chart, use_container_width=True)

def bar_chart_facet(dfm: pd.DataFrame):
    if dfm is None or dfm.empty:
        st.info("No metrics to show.")
        return
    chart = alt.Chart(dfm).mark_bar().encode(
        y=alt.Y("value:Q", title=None),
        x=alt.X("metric:N", sort=None, title=None),
        column=alt.Column("metric:N", header=alt.Header(labelAngle=0)),
        tooltip=["metric","value"]
    ).resolve_scale(y='independent')
    st.altair_chart(chart, use_container_width=True)

# old (kept for backward compatibility)
def bar_chart(dfm: pd.DataFrame):
    if dfm is None or dfm.empty: return
    chart = alt.Chart(dfm).mark_bar().encode(
        x=alt.X("metric:N", sort=None, title=None),
        y=alt.Y("value:Q", title=None),
        tooltip=["metric","value"]
    )
    st.altair_chart(chart, use_container_width=True)

def comparison_chart(df: pd.DataFrame):
    if df.empty: return
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("metric:N", sort=None, title=None),
        y=alt.Y("value:Q"),
        color="run:N",
        column=alt.Column("metric:N", header=alt.Header(labelAngle=0)),
        tooltip=["run","metric","value"]
    ).resolve_scale(y='independent')
    st.altair_chart(chart, use_container_width=True)

def timeline_chart(df: pd.DataFrame):
    if df is None or df.empty or "t" not in df.columns: return
    pts = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X("t:Q", title="time (s)"),
        y=alt.Y("agent:N", title="agent"),
        shape=alt.Shape("actor_type:N"),
        tooltip=["t","agent","actor_type","action","proposed_action","correct","latency_ms","duration_s"]
    ).interactive()
    st.altair_chart(pts, use_container_width=True)

def progress_chart(df: pd.DataFrame):
    if df is None or df.empty or "event_type" not in df.columns: return
    prog = df[df["event_type"].isin(["checklist_progress","progress","task_progress"])]
    if prog.empty: return
    ticks = alt.Chart(prog).mark_tick().encode(
        x=alt.X("t:Q", title="time (s)"),
        y=alt.value(0),
        tooltip=["t","event_type","reward"]
    )
    st.altair_chart(ticks, use_container_width=True)

def show_result_payload(result: Dict[str, Any], show_by_agent: bool = True, show_json: bool = False):
    st.subheader("Metrics")
    plot_metric_groups(result.get("metrics", {}))
    metric_glossary_note()

    with st.expander("Summary & Insights", expanded=True):
        st.write(summarize_run_brief(result))
        aux = derive_aux_rates(result)
        bullets = interpret_metrics(result.get("metrics", {}), **aux)
        for b in bullets: st.markdown(f"- {b}")
        st.caption(f"Saved to: {result.get('log_path')}")

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

# ================================ UI ====================================
st.title("HAIC Simulator • Dashboard")
st.caption("Run scenarios, browse previous runs, and visualize metrics")

tabs = st.tabs(["▶️ Run Simulation", "📁 Browse Runs", "🧱 Builder (paste YAML)"])

# --- Run Simulation tab ---
with tabs[0]:
    with st.sidebar:
        st.header("Run settings")
        configs = list_configs()
        seed = st.number_input("Seed (optional)", value=123, step=1, format="%d")
        show_by_agent = st.checkbox("Show metrics by agent", value=True)
        show_json = st.checkbox("Show raw JSON", value=False)
    if not configs:
        st.error("No configs found in haic_env_builder/configs")
    else:
        cfg = st.selectbox("Config", configs, index=0)
        run_btn = st.button("Run Simulation 🚀", use_container_width=True)
        if run_btn:
            with st.spinner("Simulating..."):
                result = run_sim_by_config_name(cfg, int(seed))
            st.success(f"Done: {result.get('task')} | env={result.get('environment','n/a')} | hash={result.get('config_hash','n/a')}")
            show_result_payload(result, show_by_agent, show_json)
        else:
            st.info("Pick a config and click **Run Simulation**.")

# --- Browse Runs tab ---
with tabs[1]:
    nonce = st.session_state.get('runs_nonce', 0)
    runs_df = list_runs_cached(nonce)

    if runs_df.empty:
        st.info("No runs found in /runs yet. Execute a simulation first.")
    else:
        # Filters row
        colf1, colf2, colf3 = st.columns([1,1,2])
        with colf1:
            task_choices = ["(all)"] + sorted([t for t in runs_df["task"].unique() if isinstance(t, str)])
            sel_task = st.selectbox("Task", task_choices, index=0)
        with colf2:
            dates = runs_df["modified"].dt.date
            dmin, dmax = dates.min(), dates.max()
            drange = st.date_input("Date range", value=(dmin, dmax))
            if isinstance(drange, tuple) and len(drange)==2:
                start, end = drange
            else:
                start, end = dmin, dmax
        with colf3:
            search = st.text_input("Search filename", value="")

        df_f = runs_df.copy()
        if sel_task != "(all)":
            df_f = df_f[df_f["task"] == sel_task]
        df_f = df_f[(df_f["modified"].dt.date >= start) & (df_f["modified"].dt.date <= end)]
        if search.strip():
            df_f = df_f[df_f["file"].str.contains(search.strip(), case=False, na=False)]

        st.subheader("Runs")
        st.dataframe(df_f, use_container_width=True, height=320)

        # Actions row: open, rename, delete
        colA, colB, colC, colD = st.columns([1,1,1,2])
        with colA:
            sel_file = st.selectbox("Select run", df_f["file"].tolist(), index=0 if not df_f.empty else None, key="sel_file")
            open_btn = st.button("Open", use_container_width=True)
        with colB:
            new_name = st.text_input("Rename to", value="", placeholder="new_name.json")
            rename_btn = st.button("Rename", use_container_width=True)
        with colC:
            delete_btn = st.button("Delete", use_container_width=True, type="secondary")
        with colD:
            compare_files = st.multiselect("Compare (pick 2–6)", df_f["file"].tolist(), default=df_f["file"].tolist()[:2])
            compare_btn = st.button("Compare Metrics", use_container_width=True)

        # Handle file operations
        if sel_file:
            if open_btn:
                try:
                    result = read_run(sel_file)
                    st.session_state['browse_loaded'] = (sel_file, result)
                except Exception as e:
                    st.error(f"Failed to read {sel_file}: {e}")

            if rename_btn and new_name.strip():
                src = RUNS_DIR / sel_file
                dst = RUNS_DIR / new_name.strip()
                if dst.exists():
                    st.warning("A file with that name already exists.")
                else:
                    try:
                        src.rename(dst)
                        st.success(f"Renamed to {dst.name}")
                        refresh_runs()
                    except Exception as e:
                        st.error(f"Rename failed: {e}")

            if delete_btn:
                try:
                    (RUNS_DIR / sel_file).unlink()
                    st.success(f"Deleted {sel_file}")
                    st.session_state.pop('browse_loaded', None)
                    refresh_runs()
                except Exception as e:
                    st.error(f"Delete failed: {e}")

        # Show loaded run
        loaded = st.session_state.get('browse_loaded')
        if loaded:
            sel_file_loaded, result = loaded
            st.subheader(f"Run: {sel_file_loaded}")
            st.caption(f"Task: {result.get('task')} | env={result.get('environment','n/a')} | config_hash={result.get('config_hash','n/a')}")
            show_result_payload(result, show_by_agent=True, show_json=False)

        # Comparison
        if compare_btn and compare_files:
            rows = []
            for f in compare_files:
                try:
                    r = read_run(f)
                    for m, v in (r.get("metrics") or {}).items():
                        rows.append({"run": f, "metric": m, "value": float(v)})
                except Exception as e:
                    st.warning(f"Skip {f}: {e}")
            cmp_df = pd.DataFrame(rows)
            if cmp_df.empty:
                st.info("No comparable metrics found.")
            else:
                st.subheader("Metrics Comparison")
                comparison_chart(cmp_df)


# --- Builder tab ---
with tabs[2]:
    subtabs = st.tabs(["Visual Builder", "Paste YAML"])

    # -------- Visual Builder --------
    with subtabs[0]:
        st.markdown("Build a config with controls, preview YAML, then **Run** or **Save**.")
        with st.form("builder_form", clear_on_submit=False):
            col1, col2 = st.columns([2,1])
            with col1:
                task_name = st.text_input("Environment Name", value="My Environment")
                task_version = st.text_input("Version", value="v1")
            with col2:
                seed_b = st.number_input("Seed (optional)", value=123, step=1, format="%d")

            env_opts = infer_env_options_from_configs()
            environment = st.selectbox("Environment", env_opts, index=0)
            with st.expander("Metrics & Timing"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    rt_max = st.slider("rt_max (s, human reaction cap)", 0.1, 10.0, 5.0, 0.1)
                with c2:
                    baseline_s = st.number_input("baseline_s (s, optional)", value=0.0, step=0.1, help="Benchmark total time; if 0, omitted.")
                with c3:
                    dt = st.slider("dt (simulation step)", 0.01, 1.0, 0.1, 0.01)

            with st.expander("Environment parameters (JSON)", expanded=False):
                env_params_text = st.text_area("env_params", value="{}", height=100,
                    help="Provide JSON dict for environment-specific params.")
            try:
                env_params = {} if not env_params_text.strip() else json.loads(env_params_text)
                env_ok = True
            except Exception as e:
                env_ok = False
                st.warning(f"env_params JSON parse error: {e}")

            st.markdown("**Agents**")
            default_agents = [
                {"id": "hu1", "name": "Radiologist", "type": "human", "profile": "default"},
                {"id": "ai1", "name": "AI Assistant", "type": "ai", "profile": "gpt"},
            ]
            agents_df = st.data_editor(
                pd.DataFrame(default_agents),
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "type": st.column_config.SelectboxColumn("type", options=["human","ai"]),
                },
                key="agents_editor",
            )

            st.markdown("**Profiles**")
            default_profiles = [
                {"id": "default", "type": "human", "parameters": "{}"},
                {"id": "gpt", "type": "ai", "parameters": "{}"},
            ]
            profiles_df = st.data_editor(
                pd.DataFrame(default_profiles),
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "type": st.column_config.SelectboxColumn("type", options=["human","ai"]),
                },
                key="profiles_editor",
            )
            records_agents = pd.DataFrame(agents_df).fillna("").to_dict(orient="records")
            agent_defs = [
                    {
                        "id": (str(r.get("id", "")).strip() or f"ag{i+1}"),
                        "name": (str(r.get("name", "")).strip() or f"Agent {i+1}"),
                        "type": r.get("type", "human"),
                        "profile": r.get("profile", "default"),
                    }
                    for i, r in enumerate(records_agents)
                ]

            records_profiles = pd.DataFrame(profiles_df).fillna("").to_dict(orient="records")

            def _parse_params(val):
                if isinstance(val, dict):
                    return val
                s = str(val).strip()
                return json.loads(s) if s else {}

            profile_defs = [
                {
                    "id": (str(r.get("id", "")).strip() or f"p{i+1}"),
                    "type": r.get("type", "human"),
                    "parameters": _parse_params(r.get("parameters", "{}")),
                }
                for i, r in enumerate(records_profiles)
            ]

            # Build config dict
            cfg_dict = {
                "task_name": task_name,
                "task_description": task_version,
                "task_parameters": {
                    "environment": environment,
                    "env_params": env_params if env_ok else {},
                    "dt": float(dt),
                    "rt_max": float(rt_max),
                    "baseline_s": None if baseline_s == 0 else float(baseline_s),
                },
                "agent_definitions": agent_defs,
                "profile_definitions": profile_defs,
            }

            yaml_preview = yaml.safe_dump(cfg_dict, sort_keys=False, allow_unicode=True)

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                run_from_ui = st.form_submit_button("Run 🚀", use_container_width=True)
            with col_btn2:
                save_cfg = st.form_submit_button("Save Config", use_container_width=True)
        st.subheader("YAML Preview")
        st.code(yaml_preview, language="yaml")
        st.download_button(
            "Download YAML",
            yaml_preview,
            file_name="config.yaml",
            mime="text/yaml",
            use_container_width=True,
        )


        # Actions after form submit
        if run_from_ui:
            if not env_ok:
                st.error("Please fix env_params JSON first.")
            else:
                with st.spinner("Simulating from built config..."):
                    # Persist to a temp and run
                    tmp_path = CONFIG_DIR / "_ui_built.yaml"
                    tmp_path.write_text(yaml_preview, encoding="utf-8")
                    result = simulate_environment(str(tmp_path), seed=int(seed_b))
                    try: tmp_path.unlink()
                    except Exception: pass
                st.success(f"Done: {result.get('task')} | env={result.get('environment','n/a')}")
                show_result_payload(result, show_by_agent=True, show_json=False)

        if save_cfg:
            fname = f"{task_name.replace(' ','_')}_{task_version}.yaml"
            out = CONFIG_DIR / fname
            out.write_text(yaml_preview, encoding="utf-8")
            st.success(f"Saved to configs: {out.name}")

    # -------- Paste YAML (unchanged, kept as fallback) --------
    with subtabs[1]:
        st.markdown("Paste a full config YAML and run it. The YAML should include `task_name`, `task_parameters`, `agent_definitions`, and `profile_definitions`.")
        seed_b2 = st.number_input("Seed (optional)", value=123, step=1, format="%d", key="builder_seed_paste")
        default_yaml = """\
task_name: My Environment
task_description: v1
task_parameters:
  environment: ct_scan
  env_params: {}
  dt: 0.1
  rt_max: 5
  baseline_s: null
agent_definitions:
  - id: human1
    name: Radiologist
    type: human
    profile: default
  - id: ai1
    name: AI Assistant
    type: ai
    profile: gpt
profile_definitions:
  - id: default
    type: human
    parameters: {}
  - id: gpt
    type: ai
    parameters: {}
"""
        yaml_text = st.text_area("Config YAML", value=default_yaml, height=300, label_visibility="visible")
        colA, colB = st.columns([1,1])
        with colA:
            run_from_yaml_btn = st.button("Run with this YAML 🚀", use_container_width=True)
        with colB:
            try:
                yaml.safe_load(yaml_text)
                st.success("YAML looks valid.")
            except Exception as e:
                st.warning(f"YAML parse warning: {e}")

        if run_from_yaml_btn:
            with st.spinner("Simulating from pasted YAML..."):
                result = run_sim_by_yaml_text(yaml_text, int(seed_b2))
            st.success(f"Done: {result.get('task')} | env={result.get('environment','n/a')} | hash={result.get('config_hash','n/a')}")
            show_result_payload(result, show_by_agent=True, show_json=False)
