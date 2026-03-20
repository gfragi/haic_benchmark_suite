## __Backend Architecture Overview__

The __Human-AI Benchmark Suite__ backend is a __FastAPI-based application__ designed to evaluate Human-AI collaboration by managing configurations, processing logs, computing metrics, and generating evaluation results.

### __Core Technology Stack__

- __Framework__: FastAPI (Python web framework)
- __Database__: PostgreSQL with SQLAlchemy ORM
- __Object Storage__: MinIO (for storing logs and results)
- __Migrations__: Alembic
- __Authentication__: Keycloak integration
- __Async Support__: asyncpg, aiohttp

### __Architecture Pattern__

The backend follows a __layered architecture__:

1. __Models__ (`app/models/`): Database entities (EvaluationConfig, LogEntry, MetricDefinition, Survey, Results)
2. __Routers__ (`app/routers/`): API endpoint definitions for different features
3. __Services__ (`app/services/`): Business logic (evaluation, metrics computation, reporting)
4. __Utils__ (`app/utils/`): Shared utilities (database connection, MinIO, authentication)
5. __Schemas__ (`app/schemas/`): Pydantic models for request/response validation

### __Key Features__

__1. Evaluation System__

- Creates evaluation configurations specifying model types and metrics
- Accepts log uploads via MinIO
- Processes logs in background tasks to compute metrics
- Groups results by AI model version for comparison
- Supports multiple metric categories: Effectiveness, Efficiency, Adaptability, Collaboration, Trust, and Robustness

__2. Log Management__

- Ingests interaction logs from Human-AI systems
- Validates and normalizes log formats
- Stores logs in MinIO for scalable storage
- Supports both single session and batch uploads

__3. Metrics & Reporting__

- Computes 20+ metrics across 6 pillars
- Aggregates results across sessions
- Time-series analysis for tracking improvements
- Generates detailed evaluation reports

__4. Environment Builder & Simulator__

- Modular environment configuration via YAML
- Simulates Human-AI collaboration scenarios
- Generates synthetic logs for testing

__5. Survey System__

- Manages survey schemas and question sets
- Collects qualitative feedback on Human-AI interactions

__6. Fairness Evaluation__

- Integrates fairness metrics for bias detection
- Supports demographic parity and equalized odds analysis

### __API Structure__ (`/api/v1/`)

- `/logs` - Log ingestion
- `/configuration` - Evaluation configuration CRUD
- `/evaluate` - Trigger evaluations
- `/results` - Retrieve evaluation results
- `/survey` - Survey management
- `/fairness` - Fairness metrics
- `/env` - Environment builder
- `/simulator` - Run simulations
- `/collab-metrics` - Collaboration-specific metrics

### __Data Flow__

1. User creates evaluation config via API
2. Uploads logs (JSON) which are stored in MinIO
3. Background task processes logs, computing metrics per session
4. Results are aggregated by AI model version
5. Results stored back to MinIO + metadata in PostgreSQL
6. Frontend fetches and visualizes results

The backend is production-ready with Docker support, Kubernetes manifests, and comprehensive error handling.
