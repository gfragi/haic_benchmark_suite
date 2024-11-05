from fastapi import FastAPI
from app.routers import logs, configuration, evaluate, reporting, log_generator

from fastapi.middleware.cors import CORSMiddleware

from app.routers import results

app = FastAPI(
    title="Human-AI Benchmark Suite",
    description="An application to evaluate Human-AI collaboration.",
    version="1.0.0",
)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080", # The URL of the frontend
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
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(configuration.router, prefix="/configuration", tags=["Configuration"])
app.include_router(evaluate.router, prefix="/evaluate", tags=["Evaluation"])
app.include_router(results.router, prefix="/results", tags=["Results"])
app.include_router(reporting.router, prefix="/reporting", tags=["Reporting"])
app.include_router(log_generator.router, prefix="/log-generator", tags=["Log Generator"])

