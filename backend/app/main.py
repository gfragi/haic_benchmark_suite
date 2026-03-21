# main.py
import os
import logging
from fastapi import FastAPI, APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from app.routers import logs, configuration, evaluate, log_generator, meta
from app.routers import fairness, env_builder, simulator, results, survey, survey_schema, env_catalog, analytics, reporting, collab, interpret
from fastapi.middleware.cors import CORSMiddleware
from app.services.seed_core_metrics import seed_core_definitions
from app.utils.errors import ErrorEnvelope, ErrorDetail

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Human-AI Benchmark Suite",
    description="An application to evaluate Human-AI collaboration.",
    version="2.0.1",
    docs_url="/api/docs",            # optional
    openapi_url="/api/openapi.json", # optional
)

async def on_startup():
    if os.getenv("SEED_CORE_METRICS", "false").lower() in {"1","true","yes","on"}:
        # don’t crash the server if DB isn’t ready—log and continue
        try:
            seed_core_definitions()
        except Exception as e:
            print(f"[core-metrics] Seed skipped due to error: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v1", )

api.include_router(logs.router,           prefix="/logs",           tags=["Logs"])
api.include_router(configuration.router,  prefix="/configuration",  tags=["Configuration"])
api.include_router(evaluate.router,       prefix="/evaluate",       tags=["Evaluation"])
api.include_router(results.router,        prefix="/results",        tags=["Results"])
api.include_router(reporting.router,      prefix="/reporting",      tags=["Reporting"])
# api.include_router(core_metrics.router,   prefix="/core-metrics",  tags=["Core Metrics"])
api.include_router(analytics.router,     prefix="/analytics",    tags=["Analytics"])
api.include_router(log_generator.router,  prefix="/log-generator", tags=["Log Generator"])
api.include_router(survey.router,         prefix="/survey",        tags=["Survey"])
api.include_router(survey_schema.router, prefix="/survey/schemas", tags=["Survey Schemas"])
api.include_router(fairness.router,       prefix="/fairness",      tags=["Fairness"])
api.include_router(env_builder.router,    prefix="/env", tags=["Environment Builder"])
api.include_router(simulator.router,      prefix="/simulator", tags=["Simulator"])
api.include_router(collab.router,        prefix="/collab-metrics", tags=["Collaboration Metrics"])
api.include_router(env_catalog.router,   prefix="/envs", tags=["Environment Catalog"])
api.include_router(interpret.router,     prefix="",      tags=["Interpretation"])

app.include_router(meta.router,           prefix="/meta", tags=["Meta"])

app.include_router(api)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method, request.url.path,
        repr(exc), exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorEnvelope(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred.",
                details={"exception_type": type(exc).__name__},
            )
        ).model_dump(),
    )
