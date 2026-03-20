# HAIC Benchmark Suite - Testing Guide

## Overview
Comprehensive testing infrastructure for both frontend and backend components with support for development and production environments.

## Test Environment Setup

### Development Environment Testing
```bash
# Start development environment
make dev

# Check service health
make health

# Should show:
# Backend: UP (http://localhost:8000)
# Frontend: UP (http://localhost:8080)
# MinIO: UP (http://localhost:9001)
```

### Production Environment Testing
```bash
# Start production environment
make prod

# Check production health
make health

# Run production smoke tests
make test-smoke
```

## Frontend Testing

### Unit Tests (Jest)
```bash
cd frontend

# Run all unit tests
npm run test:unit

# Run with coverage
npm run test:unit:coverage

# Watch mode for development
npm run test:unit:watch

# Run specific test
npm run test:unit -- --testPathPattern=useConfigurationForm
```

### End-to-End Tests (Cypress)
```bash
cd frontend

# Run E2E tests headlessly
npm run test:e2e

# Open Cypress test runner (interactive)
npm run test:e2e:open

# Run specific E2E test
npx cypress run --spec "cypress/e2e/configuration-workflow.cy.js"
```

### Combined Testing
```bash
cd frontend

# Run all frontend tests
npm run test:all

# Run with coverage and E2E
npm run test:unit:coverage && npm run test:e2e
```

### Code Quality
```bash
cd frontend

# Lint and fix
npm run lint
npm run lint:fix

# Format code
npm run format
```

## Backend Testing

### Unit Tests (pytest)
```bash
# Run backend tests
make test

# Run specific backend tests
make test-backend

# Run integration tests
docker-compose exec backend python backend/test_integration_with_sim_mvp.py

# Run tests with specific markers
docker-compose exec backend python -m pytest tests/ -m unit
docker-compose exec backend python -m pytest tests/ -m integration
```

### API Testing
```bash
# Test API endpoints
curl http://localhost:8000/api/v1/meta/health
curl http://localhost:8000/api/v1/configuration
curl http://localhost:8000/api/docs  # OpenAPI documentation
```

### Database Testing
```bash
# Access database shell
make shell-db

# Run migrations
make db-migrate

# Seed test data
make db-seed
```

## External Service Integration Testing

### MinIO Storage Testing
```bash
# Check MinIO health
curl http://localhost:9001/minio/health/live

# Access MinIO console
# URL: http://localhost:9001
# User: minioadmin
# Pass: minioadmin
```

### Keycloak Authentication Testing
```bash
# Test authentication endpoints
# (Configured for development - auto-login for public paths)
curl http://localhost:8080/survey  # Public path
curl http://localhost:8080/        # Protected path (redirects to Keycloak)
```

### Database Integration Testing
```bash
# Test database connectivity
make shell-db

# Check core metrics seeding
curl http://localhost:8000/api/v1/meta/health
```

## Continuous Integration Testing

### GitHub Actions CI/CD
```yaml
name: HAIC Benchmark Suite Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Backend Testing
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run Backend Tests
        run: make test-backend

      # Frontend Testing
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm ci

      - name: Run Frontend Linting
        run: |
          cd frontend
          npm run lint

      - name: Run Frontend Unit Tests
        run: |
          cd frontend
          npm run test:unit:coverage

      - name: Build Frontend
        run: |
          cd frontend
          npm run build
```

## Performance Testing

### Bundle Analysis
```bash
cd frontend

# Analyze production bundle
npm run build -- --analyze

# Check bundle size with custom analyzer
ANALYZE=true npm run build
```

### Runtime Performance Monitoring
```javascript
// In browser developer console (development)
$app.$performance.getSummary()
$app.$performance.exportData()
$app.$performance.clear()
```

### Load Testing
```bash
# Basic load testing with curl
for i in {1..10}; do
  curl -s http://localhost:8000/api/v1/meta/health > /dev/null &
done
wait
```

## Test Data Management

### Development Test Data
```bash
# Seed development database
make db-seed

# Reset development environment
make clean && make dev
```

### Production Test Data
```bash
# Backup production data before testing
# Use separate test database for production testing
make shell-db  # Access production DB
```

## Troubleshooting Common Issues

### Frontend Tests Failing
```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+

# Run tests with verbose output
npm run test:unit -- --verbose
```

### Backend Tests Failing
```bash
# Check database connectivity
make shell-db

# Check backend logs
make logs-backend

# Rebuild backend container
docker-compose build --no-cache backend
```

### E2E Tests Failing
```bash
cd frontend

# Ensure development server is running
npm run serve

# Check if services are healthy
make health

# Run Cypress in interactive mode for debugging
npm run test:e2e:open
```

### Performance Issues
```bash
# Check bundle size
cd frontend && npm run build -- --report

# Monitor memory usage
# Open browser dev tools → Performance tab
# Check network tab for slow requests
```

## Test Coverage Requirements

### Minimum Coverage Thresholds
- **Frontend Unit Tests**: 80% statement coverage
- **Backend Unit Tests**: 85% statement coverage
- **Integration Tests**: All critical user workflows
- **E2E Tests**: All main user journeys

### Coverage Reporting
```bash
# Frontend coverage
cd frontend && npm run test:unit:coverage
# Reports in: frontend/tests/coverage/

# Backend coverage
make test  # pytest with coverage plugin
```

## External Service Dependencies

### Required for Full Testing
- ✅ **PostgreSQL Database**: Core data storage
- ✅ **MinIO Object Storage**: File upload/download
- ✅ **Keycloak IAM**: Authentication (dev auto-login)
- ✅ **Redis** (future): Caching and sessions

### Service Health Checks
```bash
# All services health check
make health

# Individual service checks
curl http://localhost:8000/meta/health     # Backend
curl http://localhost:8080                 # Frontend
curl http://localhost:9001/minio/health/live  # MinIO
```

## Environment-Specific Testing

### Development Environment
- Auto-login for Keycloak (public paths)
- Hot reloading enabled
- Debug logging active
- Test databases with sample data

### Production Environment
- Full authentication required
- Optimized builds (minified)
- Error logging to external services
- Production database with real data

### Staging Environment (Future)
- Mirror of production
- Full authentication
- Performance monitoring
- Load testing environment

---

## Quick Test Commands

### Development Testing
```bash
# Full development test suite
make dev && make health && cd frontend && npm run test:all

# Quick smoke test
make test-smoke
```

### Production Testing
```bash
# Production deployment test
make prod && make health && make test-smoke

# Full production test suite
make prod && sleep 30 && make test && cd frontend && npm run test:all
```

### CI/CD Testing
```bash
# Run all tests (CI environment)
make test-backend && cd frontend && npm run lint && npm run test:unit:coverage
```

This comprehensive testing setup ensures the HAIC Benchmark Suite maintains high quality and reliability across both development and production environments, with full integration testing of all external services.
