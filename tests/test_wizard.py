from starlette.testclient import TestClient

from copier_formwork.server import create_app


def test_wizard_index() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "Copier Formwork" in response.text


def test_generate_requires_destination() -> None:
    client = TestClient(create_app())
    response = client.post("/api/generate", json={"project_name": "x", "kind": "package"})
    assert response.status_code == 400
    assert "destination" in response.json()["error"]
