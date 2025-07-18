from fastapi import Depends, FastAPI
from app.routers import logs, configuration, evaluate, reporting, log_generator, fairness, env_builder, simulator
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi.middleware.cors import CORSMiddleware
from .utils.keycloak_utils import decode_jwt_token

from app.routers import results
from app.routers import survey

from app.utils.database import engine
from app.models.survey import Survey

from app.utils.database import Base

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Human-AI Benchmark Suite",
    description="An application to evaluate Human-AI collaboration.",
    version="1.0.0",
)
security = HTTPBearer()


origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",# The URL of the frontend
    "http://frontend:8080",  # The URL of the frontend
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(survey.router , prefix="/survey", tags=["Survey"])
app.include_router(fairness.router, prefix="/fairness", tags=["Fairness"])
app.include_router(env_builder.router, prefix="/env", tags=["Environment Builder"])
app.include_router(simulator.router, prefix="/simulator", tags=["Simulator"])



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_jwt_token(token)
    # You could map this payload to a user model or simply return the payload
    return payload

@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "You have accessed a protected route!",
        "user": current_user
    }


