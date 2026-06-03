# Makefile Guide — HAIC Benchmark Suite

Run `make help` at any time to see a one-line summary of every target.

---

## Prerequisites

| Tool | Purpose |
|---|---|
| Docker Desktop | All `docker-*`, `dev`, `test-live` targets |
| `bench-env/` venv | `make test-unit` (created by `pip install -r backend/requirements.txt`) |
| `curl`, `python3` | `make test-smoke`, `make health` |
| `jq` | `make health` (optional — falls back to raw JSON) |

---

## Workflow: first-time setup

```bash
make setup        # copies .env.development → .env
make dev          # starts all services (Docker required)
make db-seed      # seeds core metric definitions
```

Services started by `make dev`:

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| Frontend UI | http://localhost:8080 |
| MinIO Console | http://localhost:9001 |
| PostgreSQL | localhost:5432 |

---

## Testing

### Unit tests — no Docker needed

```bash
make test-unit
```

Runs the fast in-memory test suite (SQLite + mocked MinIO) directly with the
local `bench-env` Python interpreter. Takes ~0.5 s.

Covers:
- `test_data_evaluation.py` — pure metric logic
- `test_hardening_piece2.py` — API hardening (404/400/500 shapes)
- `test_piece3_schema.py` — schema bridge / validation warnings
- `test_e2e_smoke.py` — full register → evaluate → results pipeline (in-memory)

### Live integration tests — Docker required

```bash
make test-live
```

Spins up an **ephemeral** Docker stack (`docker-compose.test.yml` overlay):
- Fresh tmpfs Postgres (`haic_test` database)
- MinIO with `haic-test` bucket
- Backend image rebuilt from source

Health-checks the backend at `http://localhost:8000/meta/health` (waits up to
90 s for `db_ok` and `minio_ok` to both be `true`), then runs
`tests/test_live_integration.py` inside the container.

The stack is torn down automatically (with `--volumes`) whether tests pass or
fail.

### Run both phases

```bash
make test-all     # test-unit then test-live
```

### Quick smoke check (stack already running)

```bash
make test-smoke   # checks /meta/health + frontend reachability
make health       # same but with per-service detail via jq
```

---

## Docker management

| Command | What it does |
|---|---|
| `make docker-build` | Rebuilds all images (`--no-cache`) |
| `make docker-up` | Starts all services (no rebuild) |
| `make docker-down` / `make stop` | Stops all services |
| `make logs` | Tails logs for all services |
| `make logs-backend` | Tails backend logs only |
| `make shell` | Opens bash in the backend container |
| `make shell-db` | Opens psql in the database container |
| `make status` | Shows container status (`docker compose ps`) |

---

## Database

```bash
make db-migrate   # runs alembic upgrade head inside the backend container
make db-seed      # POSTs to /api/v1/meta/seed/core-metrics
```

`DATABASE_URL` is read from the environment (set in `.env`). The
`alembic/env.py` reads `DATABASE_URL` at migration time, so you can also
override it directly:

```bash
DATABASE_URL=postgresql://haic_user:changeme123@localhost:5432/haic_benchmark \
  cd backend && alembic upgrade head
```

---

## Environment files

| File | Used by |
|---|---|
| `.env.development` | `make setup` / `make dev` (copied to `.env`) |
| `.env.production` | `make setup-prod` (copied to `.env`) |
| `.env` | Active config read by Docker Compose and the backend |

Never commit `.env` — it is in `.gitignore`.

---

## Cleanup

```bash
make clean        # stops containers, removes volumes, prunes dangling images
make clean-all    # same but also removes all built images (full reset)
```

---

## Code quality

```bash
make lint         # flake8 + black --check (inside backend container)
make format       # black + isort in-place (inside backend container)
```

---

## Known issues / notes

- `make status` and `make shell-db` have a typo (`docke` instead of `docker`)
  in the Makefile — run `docker compose ps` and
  `docker compose exec db psql -U haic_user -d haic_benchmark` directly until
  fixed.
- `make test-smoke` is defined twice in the Makefile; Make uses the second
  definition (simple curl, no health-JSON parsing).
- `make test-unit` uses `bench-env/bin/python` (the project venv). If that
  venv doesn't exist, create it with:
  ```bash
  python3 -m venv bench-env
  bench-env/bin/pip install -r backend/requirements.txt
  ```
