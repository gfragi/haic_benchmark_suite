# Quickstart (3 minutes)

## 0) Run the backend

```bash
PYTHONPATH=backend uvicorn app.main:app --reload

# Swagger at http://localhost:8000/api/docs
```

## 1) List configs

```bash
curl -X GET "http://localhost:8000/api/env/list_configs"
| jq
# => { "available_configs": ["CT_Scan_Diagnosis_env.yaml", "Kitchen_Toy_env.yaml", ...] }
```

## 2) (Optional) Generate a new config

```bash
curl -X POST "http://localhost:8000/api/env/generate_config" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "CT Scan Diagnosis",
    "task_parameters": {"image_type":"CT","urgency":"high","report_required":true},
    "agent_definitions": [
      {"name":"RadiologistAssistant","capabilities":["classify","highlight","summarize"],"modality":"text"},
      {"name":"VoiceSupportBot","capabilities":["speak","respond"],"modality":"audio"}
    ],
    "profile_definitions": [
      {"id":"user123","skill_level":"expert","role":"radiologist"},
      {"id":"user456","skill_level":"novice","role":"technician"}
    ]
  }'
# => { "message":"Environment config generated", "path":"haic_env_builder/configs/CT_Scan_Diagnosis_env.yaml" }
```


## 3) Run a simulation

```bash
curl -X POST "http://localhost:8000/api/env/generate_config" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "CT Scan Diagnosis",
    "task_parameters": {"image_type":"CT","urgency":"high","report_required":true},
    "agent_definitions": [
      {"name":"RadiologistAssistant","capabilities":["classify","highlight","summarize"],"modality":"text"},
      {"name":"VoiceSupportBot","capabilities":["speak","respond"],"modality":"audio"}
    ],
    "profile_definitions": [
      {"id":"user123","skill_level":"expert","role":"radiologist"},
      {"id":"user456","skill_level":"novice","role":"technician"}
    ]
  }'
# => { "message":"Environment config generated", "path":"haic_env_builder/configs/CT_Scan_Diagnosis_env.yaml" }
```

## 4) List metrics artifacts

```bash
curl -s "http://localhost:8000/api/simulator/list" | jq
# => { "files": ["CT_Scan_Diagnosis_metrics_20250724_180410.json", ...] }

curl -s "http://localhost:8000/api/simulator/load?file=CT_Scan_Diagnosis_metrics_20250724_180410.json" | jq
# => { "metrics": { ...full content... } }
```