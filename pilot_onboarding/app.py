from __future__ import annotations
import json
import streamlit as st

from affordance_library import get_default_affordances, affordance_to_dict, Affordance
from templates import make_pilot_contract, make_sample_log_template, FIELD_HELP
from validators import extract_actions_from_logs, validate_logs_against_contract
from exporters import export_onboarding_zip


st.set_page_config(page_title="Pilot Onboarding Wizard", layout="wide")

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
    ss.setdefault("selected_affordances", [])  # list of dicts with key/label/timing
    ss.setdefault("action_map", {})
    ss.setdefault("sample_logs_blob", None)
    ss.setdefault("derive_correct_rules_text", "[]")
    ss.setdefault("rt_limits", {"rt_max_ai_ms": 20000, "rt_max_human_s": 30})


def _safe_json_load(txt: str):
    try:
        return json.loads(txt)
    except Exception as e:
        return None


_init_state()

st.title("Pilot Onboarding Wizard")
st.caption("Build a pilot environment contract + map log actions to affordances + validate + export package.")

# Sidebar steps
step = st.sidebar.radio(
    "Steps",
    ["1) Pilot Info", "2) Actors", "3) Objects", "4) Affordances", "5) Upload Logs", "6) Action Mapping", "7) Rules (optional)", "8) Validate & Export"],
    index=0
)

# ---------- Step 1 ----------
if step == "1) Pilot Info":
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
        st.session_state["rt_limits"]["rt_max_ai_ms"] = st.number_input("rt_max_ai_ms", value=int(st.session_state["rt_limits"]["rt_max_ai_ms"]), step=1000)
        st.session_state["rt_limits"]["rt_max_human_s"] = st.number_input("rt_max_human_s", value=int(st.session_state["rt_limits"]["rt_max_human_s"]), step=1)

    st.info("Tip: pilot_tag + sim_id are used as stable identifiers. app_version / ai_model_version help comparisons.")

# ---------- Step 2 ----------
elif step == "2) Actors":
    st.subheader("Actors")
    st.caption("Define who acts in the pilot: humans, AI, and system components (e.g., workflow engine, HMI).")

    with st.form("add_actor"):
        colA, colB, colC = st.columns(3)
        with colA:
            actor_id = st.text_input("actor id", value="OP")
        with colB:
            actor_type = st.selectbox("type", ["human", "ai", "system"], help=FIELD_HELP["actor_type"], index=0)
        with colC:
            role = st.text_input("role", value="operator")

        submitted = st.form_submit_button("Add actor")
        if submitted:
            st.session_state["actors"].append({
                "id": actor_id.strip(),
                "type": actor_type,
                "role": role.strip(),
                "affordances": []
            })
            st.success(f"Added actor {actor_id}")

    if st.session_state["actors"]:
        st.write("Current actors:")
        st.dataframe(st.session_state["actors"], use_container_width=True)
    else:
        st.warning("No actors yet.")

# ---------- Step 3 ----------
elif step == "3) Objects":
    st.subheader("Objects")
    st.caption("Define what the actors act upon (application, ticket, image, job, grid_state, etc.).")

    with st.form("add_object"):
        colA, colB = st.columns(2)
        with colA:
            obj_id = st.text_input("object id", value="APP", )
        with colB:
            kind = st.text_input("kind", value="application")

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

    # show library and pick
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
    colR1, colR2 = st.columns([1,4])
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
            picked.append({
                "key": c_key.strip(),
                "label": c_label.strip(),
                "actor_types": c_actor,
                "timing": c_timing,
                "description": c_desc.strip()
            })
        
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

            # persist so it shows next time
            add_custom_affordance(Affordance(**new_aff))
            st.success("Saved custom affordance to library (local).")

    # merge picked with existing selected
    # keep unique by key
    existing = {a["key"]: a for a in st.session_state["selected_affordances"]}
    for a in picked:
        existing[a["key"]] = a
    st.session_state["selected_affordances"] = list(existing.values())

    st.write("Selected affordances:")
    if st.session_state["selected_affordances"]:
        st.dataframe(st.session_state["selected_affordances"], use_container_width=True)
    else:
        st.warning("No affordances selected yet.")

# ---------- Step 5 ----------
elif step == "5) Upload Logs":
    st.subheader("Upload or paste sample logs")
    st.caption("Upload one representative JSON log. We will extract discovered actions from it.")

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
                # remove mapping (means action must equal affordance key)
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

    # Build contract
    derive_rules = _safe_json_load(st.session_state["derive_correct_rules_text"])
    if derive_rules is None:
        derive_rules = None

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

    # Validation
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

    # sample log template
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

    # Export zip
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