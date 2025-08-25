# HAIC Env Builder + Simulator (Backend)

A modular backend to define **Human–AI collaboration** scenarios as YAML, run fast **simulations**, and produce **metrics** JSON files that the Benchmark Suite can store, visualize, and compare.

**You can:**

- Generate a scenario config (`/api/env/generate_config`)
- List/load configs (`/api/env/list_configs`, `/api/env/load_config`)
- Run a simulation (`/api/simulator/simulate`)
- List/load metrics artifacts (`/api/simulator/list`, `/api/simulator/load`)


## Where things live

- Configs: `haic_env_builder/configs/*.yaml`
- Metrics: `metrics/*_metrics_YYYYMMDD_HHMMSS.json`

See `quickstart.md` to run your first sim in 3 minutes.
