## Smart Healthcare (NS/Healthentia) — Agents



| ID       | Role                        | `model`   | `actor_type` in logs | Affordances                              | What it represents                     |
| -------- | --------------------------- | --------- | -------------------- | ---------------------------------------- | -------------------------------------- |
| **SYS**  | Orchestrator / Data service | `system`  | `system`             | `input_create`, `notify`                 | Ingests inputs; sends notifications.   |
| **NSAI** | Neuro-symbolic model        | `ai`      | `ai`                 | `train`, `inference`, `explain`          | Training/inference component.          |
| **XAI**  | Explainability tool         | `ai_tool` | `ai`                 | `generate_xai`                           | SHAP/LIME/etc. artifact generation.    |
| **MLE**  | ML engineer reviewer        | `human`   | `human`              | `review`, `accept`, `reject`, `annotate` | First human review.                    |
| **EXP**  | Clinical expert reviewer    | `human`   | `human`              | `review`, `accept`, `reject`, `annotate` | Second human review.                   |
| **REG**  | Model registry              | `system`  | `system`             | `register_model`, `store_artifacts`      | Registers versions & stores artifacts. |


## Action ↔ Log mapping (Healthcare)
| Env `action`       | Log `action` / `event_type`          | Typical payload keys                                        |
| ------------------ | ------------------------------------ | ----------------------------------------------------------- |
| `input_create`     | `initial_input_provided`             | `image_id`, `cohort{cancer_type,stage}`, `site_id?`         |
| `train`            | `model_trained` *(or `ai_response`)* | `model_uri`, `metrics{...}`, `latency_ms`                   |
| `generate_xai`     | `xai_generated`                      | `technique`, `top_features[]`, `artifact_uri`, `latency_ms` |
| `notify`           | `human_review_notified`              | `role`, `method`, `presigned_url_id`                        |
| `review` (MLE/EXP) | `human_review_performed`             | `decision`, `note`, `duration_s`, `correct?`                |
| `register_model`   | `model_registered`                   | `model_id`, `version`, `registry`                           |
