from fastapi.testclient import TestClient

from app.main import app


def test_asset_crud() -> None:
    with TestClient(app) as client:
        response = client.post("/assets", json={"name": "api-host"})
        assert response.status_code == 201
        assert response.json()["name"] == "api-host"
        assert client.get("/assets").status_code == 200
