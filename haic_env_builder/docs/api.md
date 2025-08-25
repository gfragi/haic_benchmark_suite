# API (Backend)

Base URL: `http://localhost:8000/api`

## Environment Builder

- **POST** `/env/generate_config`
  Body:

  ```json
  {
    "task_name": "CT Scan Diagnosis",
    "task_parameters": {"image_type":"CT","urgency":"high","report_required":true},
    "agent_definitions": [{"name":"...","capabilities":[],"modality":"text"}],
    "profile_definitions": [{"id":"user123","skill_level":"expert","role":"radiologist"}]
  }
    ```

    Response:

    ```json
    { "message": "...", "path": "haic_env_builder/configs/<file>.yaml" }
    ```

- **GET** `/env/list_configs`

    Response:

    ```json
    { "available_configs": ["<file1>.yaml", "<file2>.yaml", ...] }
    ```

- **GET** `/env/load_config?name=A.yaml`
    Response:

    ```json
    { "config": { ... } }
    ```

## Simulator

- **POST** `/simulator/simulate?name=A.yaml[&seed=123]`
   Response:

    ```json
    { "simulation_id": "..." }
    ```

- **GET** `/simulator/list`
   Response:

    ```json
    { "files": ["CT_Scan_Diagnosis_metrics_2025....json", ...] }
    ```

- **GET** `/simulator/load?file=CT_Scan_Diagnosis_metrics_...json`
   Response:

    ```json
    { "metrics": { ...full json... } }
    ```
