from fastapi import FastAPI
from app.routers import logs, evaluation_config, evaluate, evaluation_result, reporting

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Human-AI Benchmark Suite",
    description="An application to evaluate Human-AI collaboration.",
    version="1.0.0",
)

origins = [
    "http://localhost:8080",  # The URL of the frontend
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Import and include your routers
app.include_router(logs.router, prefix="/logs", tags=["logs"])
app.include_router(evaluation_config.router, prefix="/evaluation", tags=["evaluation_config"])
app.include_router(evaluate.router, prefix="/evaluate", tags=["evaluation"])
app.include_router(evaluation_result.router, prefix="/results", tags=["evaluation_result"])
app.include_router(reporting.router, prefix="/reporting", tags=["reporting"])

