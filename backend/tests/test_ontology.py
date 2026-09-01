from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.ontology import router


def _client():
    app = FastAPI()
    app.include_router(router, prefix="/ontology")
    return TestClient(app)


def test_get_ontology_contains_expected_keys():
    client = _client()

    response = client.get("/ontology")

    assert response.status_code == 200
    body = response.json()
    assert "domains" in body
    assert "metric_families" in body


def test_get_ontology_templates():
    client = _client()

    response = client.get("/ontology/templates")

    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)
    assert any(t["id"] == "sc_permit_review" for t in templates)
