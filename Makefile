# HAIC Benchmark Suite - Development Commands
.PHONY: help setup dev prod test clean docker-build docker-up docker-down

# Default target
help: ## Show this help message
	@echo "HAIC Benchmark Suite - Development Commands"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Setup commands
setup: ## Initial project setup
	@echo "Setting up HAIC Benchmark Suite..."
	cp .env.development .env
	@echo "✅ Environment configured for development"

setup-prod: ## Setup for production
	@echo "Setting up for production..."
	cp .env.production .env
	@echo "⚠️  Remember to set production environment variables!"
	@echo "✅ Production environment configured"

# Development commands
dev: ## Start development environment
	@echo "Starting development environment..."
	cp .env.development .env
	docker compose up -d
	@echo "✅ Development environment starting..."
	@echo "📊 Services:"
	@echo "  - Backend API:    http://localhost:8000"
	@echo "  - Frontend UI:    http://localhost:8080"
	@echo "  - MinIO Console:  http://localhost:9001"
	@echo "  - Database:       localhost:5432"
	@echo ""
	@echo "📋 Useful commands:"
	@echo "  make logs         - View service logs"
	@echo "  make shell        - Access backend container"
	@echo "  make test         - Run tests"
	@echo "  make stop         - Stop services"

backend-dev: ## Start only backend service for development
	@echo "Starting backend service..."
	cp .env.development .env
	docker compose up -d backend db minio
	@echo "✅ Backend service starting..."

prod: ## Start production-like environment
	@echo "Starting production environment..."
	cp .env.production .env
	docker compose -f docker compose.yml up -d
	@echo "✅ Production environment starting..."

# Testing commands
test: ## Run all tests
	@echo "Running tests..."
	docker compose exec backend python -W ignore::DeprecationWarning -W ignore::PendingDeprecationWarning -W ignore::MovedIn20Warning -W ignore::UserWarning -m pytest tests/ -v --disable-warnings

test-unit: ## Run fast unit tests (SQLite + mocks, no Docker needed)
	@echo "Running unit tests (no Docker)..."
	cd backend && ../bench-env/bin/python -W ignore::DeprecationWarning \
		-m pytest tests/ \
		--ignore=tests/test_live_integration.py \
		--ignore=tests/test_config.py \
		--ignore=tests/test_evaluation_result.py \
		--ignore=tests/test_logs_and_evaluate.py \
		--ignore=tests/test_evaluate.py \
		--ignore=tests/test_log.py \
		-v --disable-warnings

test-live: ## Run live integration tests against ephemeral Docker stack
	@echo "Starting ephemeral test stack..."
	docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --build
	@echo "Waiting for backend to be healthy..."
	@timeout 90 bash -c '\
		until curl -sf http://localhost:8000/meta/health | python3 -c \
			"import sys,json; h=json.load(sys.stdin); sys.exit(0 if h[\"db_ok\"] and h[\"minio_ok\"] else 1)" \
			2>/dev/null; do \
			echo "  waiting..."; sleep 5; \
		done' || (docker compose -f docker-compose.yml -f docker-compose.test.yml down --volumes; exit 1)
	@echo "Stack is healthy. Running live tests..."
	docker compose -f docker-compose.yml -f docker-compose.test.yml \
		exec backend python -m pytest tests/test_live_integration.py -v --disable-warnings; \
	EXIT_CODE=$$?; \
	docker compose -f docker-compose.yml -f docker-compose.test.yml down --volumes; \
	exit $$EXIT_CODE

test-all: ## Run unit tests then live integration tests
	@echo "=== Phase 1: Unit tests ==="
	$(MAKE) test-unit
	@echo ""
	@echo "=== Phase 2: Live integration tests ==="
	$(MAKE) test-live

test-smoke: ## Quick health check (services must already be running)
	@echo "Running smoke tests..."
	@curl -sf http://localhost:8000/meta/health | python3 -c \
		"import sys,json; h=json.load(sys.stdin); \
		 print('Backend:', '✅ ok' if h['status']=='ok' else '⚠️ degraded'); \
		 print('  DB:', '✅' if h['db_ok'] else '❌'); \
		 print('  MinIO:', '✅' if h['minio_ok'] else '❌')" \
		|| echo "❌ Backend not reachable at :8000"
	@curl -sf http://localhost:8080 > /dev/null && echo "Frontend: ✅ ok" || echo "Frontend: ❌ not reachable"
	
test-backend: ## Test only backend
	@echo "Testing backend..."
	docker compose exec backend python backend/test_refactored_flow.py
	docker compose exec backend python backend/test_integration_with_sim_mvp.py

test-smoke: ## Quick smoke test
	@echo "Running smoke tests..."
	curl -f http://localhost:8000/api/v1/meta/health || echo "Backend not healthy"
	curl -f http://localhost:8080 || echo "Frontend not accessible"

# Docker commands
docker-build: ## Build all Docker images
	@echo "Building Docker images..."
	docker compose build --no-cache

docker-up: ## Start all services
	@echo "Starting services..."
	docker compose up -d

docker-down: ## Stop all services
	@echo "Stopping services..."
	docker compose down

stop: docker-down ## Stop all services (alias for docker-down)

docker-logs: ## View service logs
	docker compose logs -f

docker-shell: ## Access backend container shell
	docker compose exec backend bash

# Database commands
db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	docker compose exec backend alembic upgrade head

db-seed: ## Seed database with core metrics
	@echo "Seeding core metrics..."
	curl -X POST http://localhost:8000/api/v1/meta/seed/core-metrics

# Cleanup commands
clean: ## Clean up containers and volumes
	@echo "Cleaning up..."
	docker compose down -v
	docker system prune -f

clean-all: ## Deep clean including images
	@echo "Deep cleaning..."
	docker compose down -v --rmi all
	docker system prune -f -a

# Utility commands
logs: ## View all service logs
	docker compose logs -f

logs-backend: ## View backend logs only
	docker compose logs -f backend

shell: ## Access backend shell
	docker compose exec backend bash

shell-db: ## Access database shell
	docke compose exec db psql -U haic_user -d haic_benchmark

# Status commands
status: ## Show service status
	@echo "Service Status:"
	@docke compose ps

health: ## Check service health
	@echo "Checking service health..."
	@curl -s http://localhost:8000/meta/health | jq . || echo "Backend: DOWN"
	@curl -s http://localhost:8080 | grep -q "html" && echo "Frontend: UP" || echo "Frontend: DOWN"
	@docker compose exec -T minio curl -s http://localhost:9000/minio/health/live > /dev/null && echo "MinIO: UP" || echo "MinIO: DOWN"
	@docker compose exec -T db pg_isready -U haic_user -d haic_benchmark > /dev/null && echo "Database: UP" || echo "Database: DOWN"

# CI/CD commands
lint: ## Run linting
	@echo "Running linting..."
	docker compose exec backend flake8 backend/app/
	docker compose exec backend black --check backend/app/

format: ## Format code
	@echo "Formatting code..."
	docker compose exec backend black backend/app/
	docker compose exec backend isort backend/app/

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	@echo "📖 API Docs: http://localhost:8000/api/docs"
	@echo "📚 Frontend: http://localhost:8080"

# Simulation commands
sim-demo: ## Run CT demo simulation
	@echo "Running CT demo simulation..."
	docker compose exec backend python -c "
	import sys
	sys.path.append('/haic_sim_mvp')
	from tools.run_metrics import *
	import json
	from pathlib import Path
	results = json.loads(Path('haic_sim_mvp/results/ct_demo_20250918T223109Z.json').read_text())
	metrics = haic_metrics_for_log(results)
	print('HAIC Metrics:', json.dumps(metrics, indent=2))
	"
