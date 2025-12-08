# HAIC Benchmark Suite

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

A comprehensive platform for evaluating Human-AI Collaboration (HAIC) systems through simulation, metrics computation, and interactive benchmarking.

## 🎯 What is HAIC Benchmark Suite?

The HAIC Benchmark Suite is an end-to-end platform for evaluating and benchmarking Human-AI collaborative systems. It combines realistic simulation environments, comprehensive metrics computation, and interactive evaluation tools to help researchers and practitioners assess the effectiveness of AI systems working alongside humans.

### Key Features

- **🤖 Realistic Simulations**: 6 complete pilot implementations across healthcare, manufacturing, energy, transportation, and urban planning domains
- **📊 Comprehensive Metrics**: HAIC-specific metrics (Fluency, Delegation, Human-Centered Learning, Trust, Autonomy, Surprise, Efficiency) plus traditional ML metrics
- **🔬 Scientific Evaluation**: Research-grade benchmarking with statistical analysis and visualization
- **🌐 Web Interface**: Interactive dashboard for configuring, running, and analyzing evaluations
- **⚡ Real-time Processing**: Background evaluation with progress tracking and notifications
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
│   Simulations   │    │    Metrics      │    │    Backend      │
│  (haic_sim_mvp) │───▶│ (metrics_core)  │───▶│   (FastAPI)     │
│                 │    │                 │    │                 │
│ • 6 Pilot Impl. │    │ • HAIC Metrics  │    │ • REST API      │
│ • Decision Logs │    │ • ML Metrics    │    │ • DB Storage    │
│ • Scenario Gen  │    │ • Real-time Comp│    │ • User Mgmt     │
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

The project includes automated testing tools to ensure everything is working correctly:

```bash
# Run the backend verification script
./test_backend.sh

# Expected output:
# ✅ Project structure looks good
# ✅ Virtual environment activated
# ✅ haic_env_builder package available
# ✅ Unit tests passed
# 🎉 Backend is ready for development!
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

### 5. **Smart Cities - Traffic Optimization**
**Scenario**: AI traffic management with human oversight
- **Agents**: Traffic Optimizer (AI), City Controller (Human), Sensor Network
- **Tasks**: Signal timing, congestion prediction, incident response
- **Metrics Focus**: Traffic flow efficiency, emergency response, user satisfaction

### 6. **Smart Ticketing - Public Transport**
**Scenario**: AI demand prediction for transport optimization
- **Agents**: Route Optimizer (AI), Dispatch Controller (Human), Passenger Interface
- **Tasks**: Demand forecasting, route planning, real-time adjustments
- **Metrics Focus**: On-time performance, passenger satisfaction, resource utilization

## 📊 HAIC Metrics Framework

### Core HAIC Metrics (F, D, HCL, Tr, A, S, EL)

| Metric | Name | Description | Scale | Direction |
|--------|------|-------------|-------|-----------|
| **F** | Fluency | Interactions per minute | 0-∞ | Higher better |
| **D** | Delegation | Average human decision time | 0-∞ seconds | Lower better |
| **HCL** | Human-Centered Learning | Efficiency within time constraints | 0-1 | Higher better |
| **Tr** | Trust | System reliability and appropriate autonomy | 0-1 | Higher better |
| **A** | Autonomy | Appropriate AI decision-making | 0-1 | Balanced |
| **S** | Surprise | Unexpected system behavior | 0-1 | Lower better |
| **EL** | Efficiency/Latency | End-to-end response times | 0-∞ seconds | Lower better |

### Additional Metrics
- **Traditional ML**: Accuracy, Precision, Recall, F1-Score
- **Interaction Quality**: Human-AI Agreement, Intervention Rates, Override Patterns
- **User Experience**: Satisfaction Scores, Cognitive Load, Trust Levels
- **System Performance**: Throughput, Resource Utilization, Error Rates

## 🧪 Testing & Quality Assurance

### Comprehensive Testing Guide
For detailed testing instructions covering both development and production environments, see:
- **[TESTING_README.md](TESTING_README.md)** - Complete testing guide
- **[frontend/TESTING_README.md](frontend/TESTING_README.md)** - Frontend-specific testing
- **[frontend/PERFORMANCE_GUIDE.md](frontend/PERFORMANCE_GUIDE.md)** - Performance monitoring

### Quick Test Commands
```bash
# Development environment testing
make dev && make health && cd frontend && npm run test:all

# Production smoke tests
make test-smoke

# Backend integration tests
make test-backend

# Frontend performance analysis
cd frontend && npm run build -- --analyze
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+ (for frontend testing)
- Docker & Docker Compose
- PostgreSQL & MinIO (via Docker)
- Keycloak (for authentication)

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/haic_benchmark_suite.git
cd haic_benchmark_suite
```

### 2. Start Infrastructure
```bash
docker-compose up -d
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

### 4. Run Simulations
```bash
# Generate sample evaluation data
cd haic_sim_mvp
python tools/run_dataset_experiment.py --config configs/ct_demo.json

# Compute metrics from simulation logs
python tools/run_metrics.py --log results/ct_demo_*.json
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

metrics = compute_metrics(decisions, rt_max=5.0)
# Returns: {"F": 1.2, "D": 3.0, "HCL": 0.4, ...}
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
