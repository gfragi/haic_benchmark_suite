from fastapi import APIRouter, Query, HTTPException
from haic_env_builder.utils.simulation_runner import simulate_environment

router = APIRouter()

@router.post("/simulate")
def simulate(name: str = Query(..., description="Config filename (YAML)")):
    config_path = f"haic_env_builder/configs/{name}"
    try:
        result = simulate_environment(config_path)
        return {"simulation_result": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Configuration not found")
