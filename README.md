# HAIC Benchmark Suite

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

A comprehensive platform for evaluating Human-AI Collaboration (HAIC) systems through simulation, metrics computation, and interactive benchmarking.

## 🎯 What is HAIC Benchmark Suite?

The HAIC Benchmark Suite is an end-to-end platform for evaluating and benchmarking Human-AI collaborative systems. It combines realistic simulation environments, comprehensive metrics computation, and interactive evaluation tools to help researchers and practitioners assess the effectiveness of AI systems working alongside humans.

- **🤖 Pilot reference environments**: example pilot scenarios (healthcare, manufacturing, energy, smart cities, smart ticketing) plus log-driven evaluation support
- **📊 Comprehensive Metrics**: core HAIC interaction metrics (F, D, HCL, Tr, A, S, EL, EfficiencyScore) plus extensible metrics
- **🔬 Evaluation workflow**: reproducible benchmarking runs + exports for analysis/visualization
- **🌐 Web Interface**: Interactive dashboard for configuring, running, and analyzing evaluations
- **⚡ Background evaluation**: async runs with progress tracking (when enabled)
- **📈 Extensible Framework**: Plugin architecture for adding new domains and metrics
- **🎯 Fairness Analysis**: Built-in bias detection and fairness evaluation tools
- **📝 Survey System**: SUS and ethics surveys with automatic aggregation and analysis
- **🏗️ Environment Builder**: Custom scenario generation and environment management
- **🔄 Simulator Integration**: Direct simulation run management and result processing
- **📊 Advanced Reporting**: Time-series analytics, comparative analysis, and automated reporting
- **👥 Collaboration Metrics**: Multi-user interaction analysis and team performance metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Pilot Data/Sim  │    │    Metrics      │    │    Backend      │
│ (logs + sims)   │───▶│ (metrics_core)  │───▶│   (FastAPI)     │
│                 │    │                 │    │                 │
│ • Pilot logs    │    │ • Core HAIC     │    │ • REST API      │
│ • Optional sims │    │ • Optional ext. │    │ • DB + MinIO    │
│ • JSON export   │    │ • Aggregations  │    │ • Auth (opt.)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Results       │    │   Analysis      │
│   (Vue.js)      │    │   (MinIO)       │    │   (Charts)      │
│                 │    │                 │    │                 │
│ • Config UI     │    │ • Log Storage   │    │ • Metrics Viz   │
│ • Results Dash  │    │ • Export/Import │    │ • Comparisons   │
│ • Real-time Mon │    │ • Versioning    │    │ • Reports       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧪 Testing & Validation

### Quick Backend Verification

```bash
cd backend
PYTHONPATH=. pytest -q
```

### Test Categories

#### Unit Tests (No External Dependencies)
Perfect for development and CI/CD:
```bash
cd backend && PYTHONPATH=. pytest tests/test_data_evaluation.py -v
```

#### Integration Tests (Full Stack)
Requires Docker infrastructure:
```bash
make dev    # Start all services
make test   # Run comprehensive tests
```

#### Manual Testing
```bash
make test-backend  # Test simulation integration
make test-smoke    # Quick health checks
```

### Testing Documentation
- **[Backend Testing Guide](backend/TESTING_README.md)** - Complete testing instructions
- **[Frontend Testing](frontend/TESTING_README.md)** - Frontend-specific tests
- **[Performance Guide](frontend/PERFORMANCE_GUIDE.md)** - Performance monitoring

## 🎭 Pilot Implementations

### 1. **Healthcare - CT Scan Diagnosis**

**Scenario**: AI-assisted radiology diagnosis with human expert review
- **Agents**: Radiologist Assistant (AI), Voice Support Bot (AI), Human Radiologist
- **Tasks**: Image viewing, window leveling, marking findings, final reporting
- **Metrics Focus**: Diagnostic accuracy, human-AI agreement, intervention rates

### 2. **Healthcare - Oncology (Neuro-Symbolic)**

**Scenario**: NS model-based cancer diagnosis with multi-stage human review
- **Agents**: NS AI Model, Explainability Tool (XAI), ML Engineer, Clinical Expert
- **Tasks**: Training, inference, explainability generation, human review
- **Metrics Focus**: Trust calibration, explainability effectiveness, review efficiency

### 3. **Manufacturing - Quality Control**

**Scenario**: AI vision systems for defect detection with human verification
- **Agents**: Quality Inspector (AI), Human Reviewer, System Orchestrator
- **Tasks**: Part inspection, defect classification, acceptance/rejection
- **Metrics Focus**: False positive reduction, human effort savings, throughput

### 4. **Smart Energy - Grid Management**

**Scenario**: AI-powered fault detection in electrical grids
- **Agents**: Digital Twin (AI), Human Operator, Alert System
- **Tasks**: Load balancing, fault prediction, emergency response
- **Metrics Focus**: Response time, safety incidents, predictive accuracy

### 5. **Smart Cities - Administrative Workflow (Applications)**

**Scenario**: AI-assisted administrative workflows with optional human verification (e.g., applications review)
- **Actors**: Citizen/User, AI Evaluator, Human Operator, Municipal Workflow System
- **Tasks**: Submission → AI evaluation → optional operator verification/correction → final decision
- **Metrics Focus**: AI latency (`latency_ms`), human effort (`duration_s`), agreement via derived `correct`, and breakdowns by model/app version


### 6. **Smart Ticketing - AIOps Ticket Solver (Active Learning)**

**Scenario**: Automated ticket dispatching/resolution with Active Learning + Human-in-the-loop labeling
- **Actors**: End User (ticket submitter), AI Triage/Resolver (AL + HC-XAI), Human Expert (label/verify), Ticketing System (workflow)
- **Tasks**: Ticket intake → AI proposal/triage → human labeling/verification (when needed) → model update
- **Metrics Focus**: AI latency (`latency_ms`), human effort (`duration_s`), interaction frequency (F), trust/quality via derived `correct` (Tr), and longitudinal improvements (A)

## 📊 HAIC Metrics Framework

### Core HAIC Interaction Metrics (computed from logs)

| Metric | Name | What it measures (log-derived) | Scale | Direction |
|--------|------|---------------------------------|-------|-----------|
| **F** | Interaction Frequency | Agent actions per minute within the session window. | 0–∞ | Higher (within comparable runs) |
| **D** | Mean Action Duration | Mean per-action time using `duration_s` (human) or `latency_ms/1000` (AI) when available. | 0–∞ seconds | Lower better |
| **HCL** | Human Cognitive Load (proxy) | Normalized human response-time proxy: `1 − min(mean_human_rt / rt_max_human_s, 1)`. Higher means faster responses (lower inferred load). | 0–1 | Higher better |
| **Tr** | Trust / Reliability (proxy) | Error-adjusted reliability from labeled outcomes: `1 − (errors / labeled)` using `correct=false` and/or explicit `event_type=error`. | 0–1 | Higher better |
| **A** | Adaptability | Normalized change in labeled correctness over the session (early vs late), bounded (e.g., `tanh`). | -1 to 1 | Higher better (positive = improving) |
| **S** | Similarity (Human–Surrogate) | Similarity between observed and surrogate behavior (KL-based similarity or action-match fallback). | 0–1 | Higher better |
| **EL** | Efficiency Loss | Relative time loss vs baseline: `(T − baseline_s) / baseline_s` (when baseline is provided). | 0–∞ | Lower better |
| **EfficiencyScore** | Composite Efficiency | Smoothed efficiency score derived from `EL` with optional penalties/bonuses (e.g., off-role actions, progress events). | 0–1 | Higher better |


### Additional Metrics (optional / pilot-specific)

- **Outcome/ML metrics**: Accuracy/Precision/Recall, when ground truth or audit labels exist
- **Interaction diagnostics**: acceptance/override rates, disagreement patterns (requires `correct` or explicit labels)
- **System performance**: throughput, resource utilization, error events (requires relevant telemetry fields)


## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+ (for frontend testing)
- Docker & Docker Compose
- PostgreSQL & MinIO (via Docker)
- Keycloak (for authentication, if enabled in your deployment)

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/haic_benchmark_suite.git
cd haic_benchmark_suite
```

### 2. Start Infrastructure
```bash
docker compose up -d
```

### 2a. Start the full local stack with a frontend

Backend, Postgres, and MinIO always start. Choose the frontend with Compose profiles:

```bash
# Vue frontend on http://localhost:8080
docker compose --profile vue up -d --build

# React frontend on http://localhost:3000
docker compose --profile react up -d --build

# Both frontends at once
docker compose --profile vue --profile react up -d --build
```

Useful local endpoints:

```bash
# FastAPI docs
http://localhost:8000/api/docs

# MinIO console
http://localhost:9001
```

### 3. Install Dependencies
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install

# Metrics Core
pip install -e packages/metrics_core
```

### 4. (Optional) Run simulations / generate sample data
```bash
# Optional: generate sample evaluation logs (if you use the included sim tools)
cd haic_sim_mvp
python tools/run_dataset_experiment.py --config configs/ct_demo.json
```

### 5. Start Backend
```bash
cd backend
python main.py
# API available at http://localhost:8000/api/docs
```

### 6. Start Frontend
```bash
cd frontend
npm run serve
# UI available at http://localhost:8080
```

## 📋 Usage Scenarios

### Scenario 1: Research Evaluation
**Goal**: Compare different AI models in a healthcare setting
1. Configure CT diagnosis pilot with different AI models
2. Run simulations with varying human expertise levels
3. Compare HAIC metrics across model configurations
4. Generate research reports with statistical analysis

### Scenario 2: System Optimization
**Goal**: Optimize human-AI team performance
1. Set up manufacturing quality control scenario
2. Adjust AI confidence thresholds and human review policies
3. Measure impact on throughput and error rates
4. Find optimal balance between automation and human oversight

### Scenario 3: Training and Education
**Goal**: Train practitioners on AI collaboration patterns
1. Use interactive scenarios with real-time feedback
2. Show how different intervention strategies affect outcomes
3. Provide personalized recommendations for human-AI collaboration

### Scenario 4: Compliance and Safety
**Goal**: Ensure AI systems meet safety and regulatory requirements
1. Test edge cases and failure modes in simulation
2. Validate human oversight procedures
3. Generate audit trails and compliance reports

### Scenario 5: Product Development
**Goal**: Design better human-AI interfaces
1. A/B test different UI designs and interaction patterns
2. Measure user satisfaction and cognitive load
3. Optimize workflows for specific domains

## 🔧 API Reference

### Core Endpoints

#### Configurations
- `POST /api/v1/configuration/new` - Create evaluation configuration
- `GET /api/v1/configuration` - List all configurations
- `GET /api/v1/configuration/{id}` - Get configuration details
- `PUT /api/v1/configuration/update/{id}` - Update configuration
- `DELETE /api/v1/configuration/delete/{id}` - Delete configuration

#### Logs
- `POST /api/v1/logs/upload` - Upload evaluation logs
- `POST /api/v1/logs/register` - Register individual log entry
- `GET /api/v1/logs/{config_id}` - List logs for configuration
- `DELETE /api/v1/logs/{config_id}/{log_name}` - Delete log

#### Evaluation
- `POST /api/v1/evaluate/{config_id}` - Start evaluation
- `GET /api/v1/evaluate/metrics` - Get available metrics

#### Results
- `GET /api/v1/results/{config_id}` - Get results for configuration
- `GET /api/v1/results/{config_id}/group/{group_name}` - Get grouped results

### Advanced Features

#### Fairness Analysis
- `POST /api/v1/fairness/evaluate/` - Evaluate fairness metrics for predictions

#### Survey System
- `POST /api/v1/survey` - Submit survey response
- `GET /api/v1/survey/aggregate` - Get aggregated survey metrics
- `GET /api/v1/survey/versions` - List app versions with surveys
- `GET /api/v1/survey/summary` - Get survey summary for version
- `GET /api/v1/survey/compare` - Compare survey results between versions
- `GET /api/v1/survey/question-averages` - Get question-level averages

#### Environment Management
- `GET /api/v1/envs` - List all available environments
- `GET /api/v1/envs/{env_id}` - Get environment details
- `GET /api/v1/envs/{env_id}/blocks` - Get environment blocks
- `POST /api/v1/env/generate_config` - Generate custom environment config
- `GET /api/v1/env/list_configs` - List environment configurations
- `GET /api/v1/env/load_config` - Load environment configuration

#### Simulation Management
- `GET /api/v1/simulator/runs` - List simulation runs
- `GET /api/v1/simulator/runs/{file}` - Get specific simulation run
- `GET /api/v1/simulator/runs_by_task` - Get runs filtered by task/prefix

#### Reporting & Analytics
- `GET /api/v1/reporting/time-series-data` - Get time series analytics
- `GET /api/v1/reporting/aggregate-by-date` - Get date-based aggregations
- `POST /api/v1/reporting/generate-report` - Generate comprehensive report

#### Collaboration Metrics
- `POST /api/v1/collab-metrics/collab/compute` - Compute collaboration metrics
- `GET /api/v1/collab-metrics/collab/from-run/{run_id}` - Get metrics for run
- `GET /api/v1/collab-metrics/collab/from-artifact` - Get metrics from artifact

#### Log Generator
- `GET /api/v1/log-generator/download` - Download generated logs
- `POST /api/v1/log-generator/generate` - Generate synthetic logs

### Meta & System Endpoints
- `GET /meta/health` - System health check
- `GET /meta/version` - Version information
- `POST /meta/seed/core-metrics` - Seed core metrics definitions

### Simulation API

```python
from haic_sim_mvp.engine.run_sim import run_from_config

# Run a simulation
config = {
    "environment": {"env_id": "CT_Diagnosis"},
    "agents": [{"entity_id": "AI_Radiologist", "model": "ai"}],
    "script": [
        {"t": 1, "agent": "AI_Radiologist", "object": "scan_001", "action": "classify"}
    ]
}

log_path = run_from_config(config)
```

### Metrics API

```python
from packages.metrics_core.interaction_metrics import compute_metrics

# Compute HAIC metrics
decisions = [
    {"agent": "ai", "action": "classify", "latency_ms": 150, "correct": True},
    {"agent": "human", "action": "review", "latency_ms": 3000, "correct": True}
]

metrics = compute_metrics(decisions=decisions, rt_max=5.0)  # rt_max is a normalization bound (seconds)
# For pilot-specific bounds, use values like rt_max_human_s / rt_max_ai_ms in your evaluation config, and pass the relevant bound here.
# Returns: {"F": ..., "D": ..., "HCL": ..., "Tr": ..., "A": ..., "S": ..., "EL": ..., "EfficiencyScore": ...}
```

## 📈 Results and Visualization

### Interactive Dashboard
- Real-time evaluation progress
- Comparative metric visualizations
- Scenario configuration builder
- Historical results analysis

### Export Formats
- JSON metrics data
- CSV decision logs
- PDF reports with charts
- Raw simulation data

### Analysis Tools
- Statistical significance testing
- Correlation analysis
- Trend identification
- Anomaly detection

## 🤝 Contributing

### Adding New Pilots
1. Create pilot specification in `haic_sim_mvp/_pilots/`
2. Implement environment config in `haic_sim_mvp/configs/`
3. Build agent logic in `haic_sim_mvp/user_plugins/`
4. Add test scenarios and sample data

### Extending Metrics
1. Add metric functions to `packages/metrics_core/`
2. Update metric schemas and validation
3. Add visualization components to frontend
4. Update API documentation

### Improving Simulations
1. Enhance agent decision-making logic
2. Add more realistic timing distributions
3. Implement complex interaction patterns
4. Validate against real-world data

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- Uses [Vue.js](https://vuejs.org/) for the frontend interface
- Metrics computation powered by custom HAIC metrics framework
- Simulation engine inspired by multi-agent systems research

## 📞 Support

- **Documentation**: [Full API Docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/haic_benchmark_suite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/haic_benchmark_suite/discussions)

---

**HAIC Benchmark Suite** - Advancing Human-AI Collaboration through rigorous evaluation and benchmarking.
