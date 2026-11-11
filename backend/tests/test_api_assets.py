from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_asset_crud() -> None:
    name = f"api-host-{uuid4().hex}"
    with TestClient(app) as client:
        response = client.post("/assets", json={"name": name})
        assert response.status_code == 201
        assert response.json()["name"] == name
        assert client.get("/assets").status_code == 200
