from __future__ import annotations
import json
import streamlit as st

from affordance_library import affordance_to_dict, Affordance
from templates import make_pilot_contract, make_sample_log_template, FIELD_HELP
from validators import extract_actions_from_logs, validate_logs_against_contract
from exporters import export_onboarding_zip
import streamlit.components.v1 as components
from pathlib import Path

def render_svg(svg_path: str, height: int = 1000):
    svg = Path(svg_path).read_text()
    components.html(svg, height=height, scrolling=False)

st.set_page_config(page_title="Pilot Onboarding Wizard")


# ---------- Helpers ----------
def _init_state():
    ss = st.session_state
    ss.setdefault("pilot_info", {
        "pilot_tag": "applications",
        "sim_id": "pilot_apps_v1",
        "domain": "smart-cities",
        "task": "application_review",
        "app_version": "apps_v1.0.0",
        "ai_model_version": "novo-2025-12",
    })
    ss.setdefault("actors", [])
    ss.setdefault("objects", [])
    ss.setdefault("selected_affordances", [])  # list of dicts with key/label/timing/actor_types
    ss.setdefault("action_map", {})
    ss.setdefault("sample_logs_blob", None)
    ss.setdefault("derive_correct_rules_text", "[]")
    ss.setdefault("rt_limits", {"rt_max_ai_ms": 20000, "rt_max_human_s": 30})


def _safe_json_load(txt: str):
    try:
        return json.loads(txt)
    except Exception:
        return None


def _sync_actor_affordances_from_selected():
    """
    Auto-assign actor affordances based on actor.type and affordance.actor_types.
    - Keeps only affordances that still exist in selected_affordances
    - Assigns all applicable selected affordances to each actor
    """
    ss = st.session_state
    selected = ss.get("selected_affordances") or []
    actors = ss.get("actors") or []

    if not selected or not actors:
        # still normalize structure a bit
        for a in actors:
            a.setdefault("affordances", [])
        ss["actors"] = actors
        return

    # key -> affordance dict
    by_key = {a.get("key"): a for a in selected if isinstance(a, dict) and a.get("key")}

    for actor in actors:
        actor_type = str(actor.get("type") or "")
        applicable_keys = []
        for k, aff in by_key.items():
            actor_types = aff.get("actor_types") or []
            if actor_type in actor_types:
                applicable_keys.append(k)

        # stable ordering for UI (optional)
        applicable_keys = sorted(set(applicable_keys))
        actor["affordances"] = applicable_keys

    ss["actors"] = actors


def _actors_table_view():
    """
    Make the actors table more readable: show counts + preview.
    """
    out = []
    for a in st.session_state["actors"]:
        affs = a.get("affordances") or []
        preview = ", ".join(affs[:3]) + (f" (+{len(affs)-3})" if len(affs) > 3 else "")
        out.append({
            "id": a.get("id"),
            "type": a.get("type"),
            "role": a.get("role"),
            "affordances_count": len(affs),
            "affordances_preview": preview,
        })
    return out

def render_svg(svg_path: str, height: int = 1050):
    """
    Render an SVG file inline in Streamlit with responsive scaling.
    """
    try:
        svg = Path(svg_path).read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"Could not load SVG: {e}")
        return

    html = f"""
    <style>
      svg {{ width: 100%; height: auto; }}
    </style>
    <div style="display:flex; justify-content:center;">
      <div style="width:100%; max-width:820px;">
        {svg}
      </div>
    </div>
    """
    components.html(html, height=height, scrolling=False)



_init_state()

st.title("Pilot Onboarding Wizard v0.2")
st.caption("Build a pilot environment contract + map log actions to affordances + validate + export package.")

# Sidebar steps
step = st.sidebar.radio(
    "Steps",
    ["📘 How logs become metrics", "1) Pilot Info", "2) Actors", "3) Objects", "4) Affordances", "5) Upload Logs", "6) Action Mapping", "7) Rules (optional)", "8) Validate & Export"],
    index=0
)

with st.sidebar.expander('Show mapping diagram', expanded=False):
    render_svg('haic_env_logs_metrics_diagram.svg', height=1020)

if step == "📘 How logs become metrics":
    st.subheader("How your pilot logs become dashboard metrics")
    st.caption("This diagram explains how your workflow, logs, and metrics connect.")

    render_svg(
        "haic_env_logs_metrics_diagram.svg",
        height=850
    )

    st.info(
        "This mapping is the foundation of comparability across pilots. "
        "If actors, actions, and timing are present, evaluation works — "
        "payload details remain fully pilot-owned."
    )
    
# ---------- Step 1 ----------

elif step == "1) Pilot Info":
    st.subheader("Pilot metadata")
    info = st.session_state["pilot_info"]

    c1, c2 = st.columns(2)
    with c1:
        info["pilot_tag"] = st.text_input("pilot_tag", info["pilot_tag"], help=FIELD_HELP["pilot_tag"])
        info["sim_id"] = st.text_input("sim_id", info["sim_id"], help=FIELD_HELP["sim_id"])
        info["domain"] = st.text_input("domain", info["domain"], help=FIELD_HELP["domain"])
        info["task"] = st.text_input("task", info["task"], help=FIELD_HELP["task"])
    with c2:
        info["app_version"] = st.text_input("app_version (optional)", info.get("app_version", ""), help=FIELD_HELP["app_version"])
        info["ai_model_version"] = st.text_input("ai_model_version (optional)", info.get("ai_model_version", ""), help=FIELD_HELP["ai_model_version"])
        st.session_state["rt_limits"]["rt_max_ai_ms"] = st.number_input(
            "rt_max_ai_ms", value=int(st.session_state["rt_limits"]["rt_max_ai_ms"]), step=1000, help=FIELD_HELP["rt_max_ai_ms"]
        )
        st.session_state["rt_limits"]["rt_max_human_s"] = st.number_input(
            "rt_max_human_s", value=int(st.session_state["rt_limits"]["rt_max_human_s"]), step=1, help=FIELD_HELP["rt_max_human_s"]
        )

    st.info("Tip: pilot_tag + sim_id are used as stable identifiers. app_version / ai_model_version help comparisons.")

# ---------- Step 2 ----------
elif step == "2) Actors":
    st.subheader("Actors")
    st.caption("Define who acts in the pilot: humans, AI, and system components (e.g., workflow engine, HMI).")

    with st.form("add_actor"):
        colA, colB, colC = st.columns(3)
        with colA:
            actor_id = st.text_input("actor id", value="OP", help=FIELD_HELP["actor_id"])
        with colB:
            actor_type = st.selectbox("type", ["human", "ai", "system"], help=FIELD_HELP["actor_type"], index=0)
        with colC:
            role = st.text_input("role", value="operator", help=FIELD_HELP["role"])
        submitted = st.form_submit_button("Add actor")
        if submitted:
            st.session_state["actors"].append({
                "id": actor_id.strip(),
                "type": actor_type,
                "role": role.strip(),
                "affordances": []
            })
            _sync_actor_affordances_from_selected()
            st.success(f"Added actor {actor_id}")

    if st.session_state["actors"]:
        st.write("Current actors:")
        st.dataframe(_actors_table_view(), use_container_width=True)
        if st.session_state["selected_affordances"]:
            st.caption("Affordances are auto-assigned based on actor type and selected affordances.")
        else:
            st.caption("Select affordances in Step 4 to auto-populate actor affordances.")
    else:
        st.warning("No actors yet.")

# ---------- Step 3 ----------
elif step == "3) Objects":
    st.subheader("Objects")
    st.caption("Define what the actors act upon (application, ticket, image, job, grid_state, etc.).")

    with st.form("add_object"):
        colA, colB = st.columns(2)
        with colA:
            obj_id = st.text_input("object id", value="APP", help=FIELD_HELP["object_id"])
        with colB:
            kind = st.text_input("kind", value="application", help=FIELD_HELP["object_kind"])

        submitted = st.form_submit_button("Add object")
        if submitted:
            st.session_state["objects"].append({
                "id": obj_id.strip(),
                "kind": kind.strip(),
                "attributes": {}
            })
            st.success(f"Added object {obj_id}")

    if st.session_state["objects"]:
        st.write("Current objects:")
        st.dataframe(st.session_state["objects"], use_container_width=True)
    else:
        st.warning("No objects yet.")

# ---------- Step 4 ----------
elif step == "4) Affordances":
    st.subheader("Affordances")
    st.caption("Pick canonical interaction types (affordances). Log actions will map to these.")

    from affordance_library import get_affordances_merged, add_custom_affordance, reset_custom_affordances
    lib = get_affordances_merged()

    picked = []
    st.write("Select affordances from the library:")
    for group, items in lib.items():
        with st.expander(group, expanded=True):
            for a in items:
                key = f"aff_{group}_{a.key}"
                checked = st.checkbox(f"{a.key} — {a.label} ({a.timing})", value=False, key=key)
                if checked:
                    picked.append(affordance_to_dict(a))

    # custom add
    st.divider()
    st.write("Add a custom affordance (optional):")
    colR1, colR2 = st.columns([1, 4])
    with colR1:
        if st.button("Reset custom library"):
            reset_custom_affordances()
            st.warning("Custom affordances cleared. Reload page to refresh.")

    with st.form("add_custom_aff"):
        c1, c2, c3 = st.columns(3)
        with c1:
            c_key = st.text_input("key", value="custom_action")
            c_label = st.text_input("label", value="Custom Action")
        with c2:
            c_actor = st.multiselect("actor types", ["human", "ai", "system"], default=["system"])
        with c3:
            c_timing = st.selectbox("timing expectation", ["none", "ai_latency_ms", "human_duration_s"], index=0)
        c_desc = st.text_input("description", value="")
        ok = st.form_submit_button("Add custom affordance")
        if ok:
            new_aff = {
                "key": c_key.strip(),
                "label": c_label.strip(),
                "actor_types": c_actor,
                "timing": c_timing,
                "description": c_desc.strip(),
                "group": "Custom"
            }
            picked.append(new_aff)
            add_custom_affordance(Affordance(**new_aff))
            st.success("Saved custom affordance to library (local).")

    # merge picked with existing selected (unique by key)
    existing = {a["key"]: a for a in st.session_state["selected_affordances"] if isinstance(a, dict) and a.get("key")}
    for a in picked:
        if isinstance(a, dict) and a.get("key"):
            existing[a["key"]] = a
    st.session_state["selected_affordances"] = list(existing.values())

    # IMPORTANT: sync actor affordances whenever selected affordances change
    _sync_actor_affordances_from_selected()

    st.write("Selected affordances:")
    if st.session_state["selected_affordances"]:
        st.dataframe(st.session_state["selected_affordances"], use_container_width=True)
        if st.session_state["actors"]:
            st.caption("Actors have been updated automatically based on the selected affordances.")
    else:
        st.warning("No affordances selected yet.")

# ---------- Step 5 ----------
elif step == "5) Upload Logs":
    st.subheader("Upload or paste sample logs")
    st.caption("Upload one representative JSON log. We will extract discovered actions from it.")
    # with st.expander("Visual guide: How your pilot maps to metrics", expanded=True):
    #     st.write(
    #         "This diagram explains how your pilot workflow, environment definition, "
    #         "and logs are interpreted to compute metrics. "
    #         "You do NOT need to change your business logic — only describe it once."
    #     )

    #     render_svg(
    #         str(Path(__file__).resolve().parent / "haic_env_logs_metrics_diagram.svg")
    #     )


    st.markdown("""
    **Minimum checklist before uploading logs:**
    - Each event has: `actor_type`, `action`, `timestamp`, `interaction_id`
    - AI actions include `latency_ms` (when applicable)
    - Human actions include `duration_s` (when applicable)
    - Actions either match affordances or are mapped in Step 6
    """)

    up = st.file_uploader("Upload JSON log file", type=["json"])
    if up is not None:
        try:
            blob = json.loads(up.read().decode("utf-8"))
            st.session_state["sample_logs_blob"] = blob
            st.success("Loaded JSON log successfully.")
        except Exception as e:
            st.error(f"Failed to parse JSON: {e}")

    st.write("Or paste JSON:")
    pasted = st.text_area("Paste JSON", height=200, value="")
    if st.button("Load pasted JSON"):
        blob = _safe_json_load(pasted)
        if blob is None:
            st.error("Invalid JSON.")
        else:
            st.session_state["sample_logs_blob"] = blob
            st.success("Loaded pasted JSON successfully.")

    if st.session_state["sample_logs_blob"] is not None:
        actions = sorted(list(extract_actions_from_logs(st.session_state["sample_logs_blob"])))
        st.info(f"Discovered actions: {len(actions)}")
        st.code("\n".join(actions[:200]) if actions else "(none)")

# ---------- Step 6 ----------
elif step == "6) Action Mapping":
    st.subheader("Map pilot log actions → affordances")
    st.caption("For each action discovered in logs, select the canonical affordance it corresponds to.")

    if st.session_state["sample_logs_blob"] is None:
        st.warning("Upload/paste logs first.")
    elif not st.session_state["selected_affordances"]:
        st.warning("Select affordances first.")
    else:
        affordance_keys = [a["key"] for a in st.session_state["selected_affordances"]]
        discovered = sorted(list(extract_actions_from_logs(st.session_state["sample_logs_blob"])))

        st.write("Mapping table:")
        for act in discovered:
            current = st.session_state["action_map"].get(act, "")
            choice = st.selectbox(
                f"{act}",
                options=["(direct match / none)"] + affordance_keys,
                index=(affordance_keys.index(current) + 1) if current in affordance_keys else 0
            )
            if choice == "(direct match / none)":
                if act in st.session_state["action_map"]:
                    st.session_state["action_map"].pop(act, None)
            else:
                st.session_state["action_map"][act] = choice

        st.divider()
        st.write("Current action_map:")
        st.json(st.session_state["action_map"])

# ---------- Step 7 ----------
elif step == "7) Rules (optional)":
    st.subheader("Derive 'correct' rules (optional)")
    st.caption("If you want agreement metrics, you can define rules to derive correct=true/false from decisions.")

    st.write("Edit JSON array of rules (simple and pilot-owned). Example:")
    st.code("""[
  { "when": { "ai_decision": "Accepted" }, "set": true },
  { "when": { "ai_decision": "Rejected", "op_decision": "Accepted" }, "set": false }
]""")

    txt = st.text_area("derive_correct_rules", height=220, value=st.session_state["derive_correct_rules_text"])
    st.session_state["derive_correct_rules_text"] = txt

    parsed = _safe_json_load(txt)
    if parsed is None:
        st.error("Invalid JSON rules (must be an array).")
    else:
        st.success("Rules JSON is valid.")
        st.json(parsed)

# ---------- Step 8 ----------
elif step == "8) Validate & Export":
    st.subheader("Validate & Export package")

    info = st.session_state["pilot_info"]

    derive_rules = _safe_json_load(st.session_state["derive_correct_rules_text"])
    if derive_rules is None:
        derive_rules = None

    # ensure actor affordances are synced before building contract
    _sync_actor_affordances_from_selected()

    contract = make_pilot_contract(
        sim_id=info["sim_id"],
        pilot_tag=info["pilot_tag"],
        domain=info["domain"],
        task=info["task"],
        actors=st.session_state["actors"],
        objects=st.session_state["objects"],
        affordances=st.session_state["selected_affordances"],
        action_map=st.session_state["action_map"],
        derive_correct_rules=derive_rules,
        rt_limits=st.session_state["rt_limits"],
    )

    st.write("Pilot environment contract (preview):")
    st.json(contract)

    if st.session_state["sample_logs_blob"] is None:
        st.warning("No sample logs loaded. Validation will be limited.")
        validation_report = {"error": "No sample logs provided."}
    else:
        validation_report = validate_logs_against_contract(
            contract=contract,
            logs_blob=st.session_state["sample_logs_blob"],
            action_map=st.session_state["action_map"],
        )

    st.divider()
    st.subheader("Validation report")
    st.json(validation_report)

    sample_template = make_sample_log_template(
        sim_id=info["sim_id"],
        pilot_tag=info["pilot_tag"],
        app_version=info.get("app_version") or None,
        ai_model_version=info.get("ai_model_version") or None,
        example_actions=(validation_report.get("discovered_actions") or [])[:3] or None
    )

    st.divider()
    st.subheader("Generated sample log template")
    st.json(sample_template)

    zip_bytes = export_onboarding_zip(
        contract=contract,
        action_map=st.session_state["action_map"],
        derive_correct_rules=derive_rules,
        sample_log_template=sample_template,
        validation_report=validation_report,
    )

    st.download_button(
        "Download Pilot Onboarding Package (.zip)",
        data=zip_bytes,
        file_name=f"pilot_onboarding_{info['pilot_tag']}.zip",
        mime="application/zip"
    )

