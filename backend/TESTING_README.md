# Backend Testing Guide

This guide explains how to run the HAIC Benchmark Suite backend tests at different levels.

## Quick Start

### 1. Unit Tests (No External Dependencies)

These tests verify core functionality without requiring databases or external services:

```bash
# From the backend directory
cd backend
source ../bench-env/bin/activate
PYTHONPATH=. pytest tests/test_data_evaluation.py -v
```

**Expected Output:**
```
tests/test_data_evaluation.py::test_calculate_prediction_accuracy PASSED
tests/test_data_evaluation.py::test_calculate_response_time PASSED
```

### 2. Integration Tests (Requires Full Stack)

For comprehensive testing with database and MinIO:

```bash
# Start all services
make dev

# Wait for services to be ready, then run tests
make test
```

Or manually:
```bash
# Start services
docker compose up -d

# Run tests in container
docker compose exec backend python -m pytest tests/ -v --disable-warnings
```

## Test Categories

### Unit Tests (No External Dependencies)
These tests verify core functionality without requiring databases, APIs, or external services:

- **test_data_evaluation.py**: Tests evaluation utility functions
- **Location**: `backend/tests/test_data_evaluation.py`
- **Requirements**: None (just Python environment)
- **Run**: `cd backend && PYTHONPATH=. pytest tests/test_data_evaluation.py`

**Status**: ✅ **WORKING** - All tests pass

### Integration Tests (Require Full Stack)
These tests exercise the complete API and require all services to be running:

- **test_config.py**: API endpoint tests for configuration management
- **test_evaluation_result.py**: Result storage and retrieval APIs
- **test_logs_and_evaluate.py**: Full log processing workflow
- **test_log.py**: Log upload and registration endpoints
- **test_user.py**: User management functionality
- **Requirements**: PostgreSQL, MinIO, Redis, Full FastAPI app
- **Run**: `make dev && docker compose exec backend python -m pytest tests/ -v`

**Status**: ⚠️ **REQUIRES DOCKER** - Need full infrastructure for API testing

### Manual Tests
- **test_refactored_flow.py**: Manual integration test
- **test_integration_with_sim_mvp.py**: Simulation integration
- **Requirements**: Full environment
- **Run**: `make test-backend`

## Environment Setup

### Local Development (Without Docker)

1. **Activate virtual environment:**
   ```bash
   source bench-env/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   cd ../haic_env_builder && pip install -e .
   ```

3. **Set environment variables:**
   ```bash
   cp .env.development .env
   # Edit .env with your local settings
   ```

4. **Run unit tests:**
   ```bash
   cd backend
   PYTHONPATH=. pytest tests/test_data_evaluation.py
   ```

### Docker Development (Recommended)

1. **Start services:**
   ```bash
   make dev
   ```

2. **Run all tests:**
   ```bash
   make test
   ```

3. **Check service health:**
   ```bash
   make health
   ```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`:
- Ensure `PYTHONPATH=.` is set when running from backend directory
- Activate the virtual environment: `source bench-env/bin/activate`
- Install haic_env_builder: `cd haic_env_builder && pip install -e .`

### Database Errors
If tests fail with database connection errors:
- Ensure PostgreSQL is running: `make health`
- Run database migrations: `make db-migrate`
- Check environment variables in `.env`

### Service Unavailable
If MinIO or other services are down:
- Start all services: `make dev`
- Wait 30-60 seconds for services to initialize
- Check logs: `make logs`

## CI/CD Testing

For automated testing, use the Docker-based approach:

```bash
# Build and test
docker compose build
docker compose up -d
docker compose exec backend python -m pytest tests/ --disable-warnings
```

## Test Coverage

Current test coverage includes:
- ✅ Core evaluation functions
- ✅ API endpoints (integration tests)
- ✅ Log processing pipeline
- ✅ Database operations
- ✅ MinIO file storage

## Contributing

When adding new tests:
1. Unit tests should go in `backend/tests/`
2. Use descriptive test names
3. Include docstrings explaining test purpose
4. Mock external dependencies when possible
