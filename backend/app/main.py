# main.py
from fastapi import FastAPI, APIRouter
from app.routers import logs, configuration, evaluate, reporting, log_generator, meta, metrics
from app.routers import fairness, env_builder, simulator, results, survey
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Human-AI Benchmark Suite",
    description="An application to evaluate Human-AI collaboration.",
    version="2.0.1",
    docs_url="/api/docs",            # optional
    openapi_url="/api/openapi.json", # optional
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v1", )

api.include_router(logs.router,           prefix="/logs",          tags=["Logs"])
api.include_router(configuration.router,  prefix="/configuration", tags=["Configuration"])
api.include_router(evaluate.router,       prefix="/evaluate",      tags=["Evaluation"])
api.include_router(results.router,        prefix="/results",       tags=["Results"])
api.include_router(reporting.router,      prefix="/reporting",     tags=["Reporting"])
api.include_router(log_generator.router,  prefix="/log-generator", tags=["Log Generator"])
api.include_router(survey.router,         prefix="/survey",        tags=["Survey"])
api.include_router(fairness.router,       prefix="/fairness",      tags=["Fairness"])
api.include_router(env_builder.router,    prefix="/env", tags=["Environment Builder"])
api.include_router(simulator.router,      prefix="/simulator", tags=["Simulator"])
api.include_router(metrics.router,        prefix="/metrics", tags=["Metrics"])
app.include_router(meta.router,           prefix="/meta", tags=["Meta"])

app.include_router(api)
