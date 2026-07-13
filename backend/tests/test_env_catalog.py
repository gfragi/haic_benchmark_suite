from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.env_catalog import router


def _client(tmp_path, monkeypatch):
    monkeypatch.setenv("HAIC_CONFIG_DIR", str(tmp_path))
    app = FastAPI()
    app.include_router(router, prefix="/envs")
    return TestClient(app)


def _env_doc(env_id="Test_Env", sim_id="test_sim"):
    return {
        "sim_id": sim_id,
        "environment": {
            "id": env_id,
            "class": "base.Environment",
            "attributes": {"task": "classification", "domain": "test"},
        },
        "agents": [],
        "objects": [],
        "script": [],
    }


def test_add_replace_and_remove_env(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    create = client.post("/envs", json=_env_doc())
    assert create.status_code == 201
    assert create.json()["id"] == "Test_Env"

    get_created = client.get("/envs/Test_Env")
    assert get_created.status_code == 200
    assert get_created.json()["sim_id"] == "test_sim"

    replacement = _env_doc(sim_id="updated_sim")
    replace = client.put("/envs/Test_Env", json=replacement)
    assert replace.status_code == 200

    get_replaced = client.get("/envs/Test_Env")
    assert get_replaced.status_code == 200
    assert get_replaced.json()["sim_id"] == "updated_sim"

    remove = client.delete("/envs/Test_Env")
    assert remove.status_code == 204

    get_removed = client.get("/envs/Test_Env")
    assert get_removed.status_code == 404


def test_add_env_rejects_duplicate_id(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    assert client.post("/envs", json=_env_doc()).status_code == 201

    duplicate = client.post("/envs", json=_env_doc())
    assert duplicate.status_code == 409


def test_replace_env_requires_matching_body_id(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    assert client.post("/envs", json=_env_doc()).status_code == 201

    mismatch = client.put("/envs/Test_Env", json=_env_doc(env_id="Other_Env"))
    assert mismatch.status_code == 400
