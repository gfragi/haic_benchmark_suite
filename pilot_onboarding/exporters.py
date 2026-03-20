from __future__ import annotations
from typing import Dict, Any
import io
import json
import zipfile


def _json_bytes(data: Dict[str, Any]) -> bytes:
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def make_readme_md(contract: Dict[str, Any], action_map: Dict[str, str]) -> str:
    sim_id = contract.get("sim_id", "")
    pilot_tag = contract.get("pilot_tag", "")
    env = contract.get("environment", {}) or {}
    domain = env.get("domain", "")
    task = env.get("task", "")

    lines = []
    lines.append(f"# Pilot Onboarding Package — {pilot_tag}\n")
    lines.append("This package aligns pilot logs with the environment contract so the HAIC benchmarking platform can compute metrics consistently.\n")
    lines.append("## Quick checklist\n")
    lines.append("- Each event has: `actor_type`, `action`, `timestamp`, `interaction_id`\n")
    lines.append("- AI events include `latency_ms` when applicable\n")
    lines.append("- Human events include `duration_s` when applicable\n")
    lines.append("- Every log `action` maps to an environment `affordance` (directly or via `action_map.json`)\n")

    lines.append("## Environment contract\n")
    lines.append(f"- **sim_id:** `{sim_id}`\n")
    lines.append(f"- **pilot_tag:** `{pilot_tag}`\n")
    lines.append(f"- **domain:** `{domain}`\n")
    lines.append(f"- **task:** `{task}`\n")

    lines.append("## Action mapping (aliases)\n")
    if action_map:
        lines.append("| Pilot log action | Mapped affordance |\n")
        lines.append("|---|---|\n")
        for k, v in action_map.items():
            lines.append(f"| `{k}` | `{v}` |\n")
    else:
        lines.append("_No aliases defined. Actions must match affordance keys directly._\n")

    lines.append("\n## Notes\n")
    lines.append("- Payload fields are domain-specific and treated as opaque by the platform.\n")
    lines.append("- Agreement (`correct`) can be derived using `derive_correct_rules.json` if provided.\n")

    return "".join(lines)


def export_onboarding_zip(
    *,
    contract: Dict[str, Any],
    action_map: Dict[str, str],
    derive_correct_rules: Any,
    sample_log_template: Dict[str, Any],
    validation_report: Dict[str, Any],
) -> bytes:
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("pilot_env_contract.json", _json_bytes(contract))
        z.writestr("action_map.json", _json_bytes(action_map or {}))
        if derive_correct_rules is not None:
            z.writestr("derive_correct_rules.json", _json_bytes({"derive_correct_rules": derive_correct_rules}))
        z.writestr("sample_log_template.json", _json_bytes(sample_log_template))
        z.writestr("validation_report.json", _json_bytes(validation_report))
        z.writestr("README.md", make_readme_md(contract, action_map).encode("utf-8"))
    return buff.getvalue()