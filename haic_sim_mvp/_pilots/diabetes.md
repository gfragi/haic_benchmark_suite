# Smart Healthcare (NS/Healthentia) — Integration & Logging Spec (v0)

Scope. Define the environment config, logging contract, and Node‑RED/Kubeflow hooks for the Neuro‑Symbolic oncology pipeline (Healthentia + NS backend + XAI + two‑step review).

## Environment Configuration

Use this as a reference/demo script aligned with your platform schema. Adjust as needed for your specific deployment environment.

```yaml
{
"sim_id": "pilot_ns_v0",
"environment": {
"id": "NS_ENV",
"class": "base.Environment",
"attributes": { "task": "ns_oncology_review", "domain": "healthcare" }
},
"agents": [
{ "id": "SYS", "class": "base.Agent", "model": "system",
"affordances": ["input_create","notify"] },
{ "id": "NSAI", "class": "base.Agent", "model": "ai",
"affordances": ["train","inference","explain"] },
{ "id": "XAI", "class": "base.Agent", "model": "ai_tool",
"affordances": ["generate_xai"] },
{ "id": "MLE", "class": "base.Agent", "model": "human",
"affordances": ["review","accept","reject","annotate"] },
{ "id": "EXP", "class": "base.Agent", "model": "human",
"affordances": ["review","accept","reject","annotate"] },
{ "id": "REG", "class": "base.Agent", "model": "system",
"affordances": ["register_model","store_artifacts"] }
],
"objects": [
{ "id": "Img", "class": "base.Object",
"attributes": {"kind":"medical_image"},
"affordances": ["provide"] },
{ "id": "Mdl", "class": "base.Object",
"attributes": {"kind":"ns_model"},
"affordances": ["store","download"] },
{ "id": "XaiArt", "class": "base.Object",
"attributes": {"kind":"xai_artifact"},
"affordances": ["store","view"] }
],
"script": [
{ "t": 0.0, "agent": "SYS", "action": "input_create", "object": "Img",
"effect": {"image_id":"IMG001","cohort":{"cancer_type":"breast","stage":"II"}} },
{ "t": 1.2, "agent": "NSAI", "action": "train", "object": "Mdl",
"effect": {"model_uri":"minio://bucket/models/ns/mdl_001","metrics":{"auc":0.86}},
"latency_ms": 950 },
{ "t": 2.2, "agent": "XAI", "action": "generate_xai", "object": "XaiArt",
"effect": {"technique":"shap","top_features":["tumor_size","age","rule:RS12"],
"artifact_uri":"minio://bucket/xai/IMG001.png"},
"latency_ms": 840 },
{ "t": 5.0, "agent": "SYS", "action": "notify", "object": "Mdl",
"effect": {"role":"ml_engineer","presigned_url_id":"psu_abc123"} },
{ "t": 14.0, "agent": "MLE", "action": "review", "object": "Mdl",
"effect": {"decision":"accept","note":"metrics & XAI consistent"}, "duration_s": 8.2 },
{ "t": 20.0, "agent": "REG", "action": "register_model", "object": "Mdl",
"effect": {"model_id":"mdl_20251017_09","version":"1.0.0","registry":"mlflow"} },
{ "t": 26.0, "agent": "SYS", "action": "notify", "object": "Mdl",
"effect": {"role":"expert","presigned_url_id":"psu_def456"} },
{ "t": 35.0, "agent": "EXP", "action": "review", "object": "Mdl",
"effect": {"decision":"accept","note":"rules align with protocol"}, "duration_s": 7.5, "correct": true }
]
}
```

## Data Model (session + interactions)

- `sim_id` = `ns_healthentia` (app discriminator)

- `session_id` = 1 clinician session (login/working window)

- `interaction_id` = the case unit (e.g., `image_id`, propagated through the flow)

- `decisions[]` entries carry `interaction_id` + `t`|timestamp, `actor_type`, `action`, optional `duration_s`|latency_ms, `payload{}`, and optional `correct`.

**Group fields for slicing**: `cancer_type`, `stage`, `site_id`, `age_bucket`. Use buckets/pseudonyms; no raw PII.


## Event Catalog (what to emit)

- `initial_input_provided` — image/data received (include `image_id`, `cohort`)

- `model_trained` or `ai_response` — model output (metrics, URI, `latency_ms`)

- `xai_generated` — explanation artifact (top features, artifact URI, `latency_ms`)

- `human_review_notified` — presigned URL / channel

- `human_review_performed` — `{decision: accept|reject, note}` + `duration_s`; set correct once audited

- `model_registered` — registry + version (if applicable)



## Metrics Mapping

- `F`: event density over session (interactions/min)

- `D`: mean `duration_s` on human reviews

- `HCL`: 1 − min(`duration_s`/`rt_max`, `1`) with `rt_max=30`

- `Tr`: acceptance/rejection rates; correctness when audited

- `EL`: AI latencies + overall cycle timings

- `Fairness`: by `cancer_type/stage/site_id/age_bucket`