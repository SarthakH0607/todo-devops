import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_home_page(client):
    assert client.get("/").status_code == 200


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_create_task(client):
    r = client.post("/api/tasks", json={"title": "Learn DevOps"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Learn DevOps"


def test_create_task_without_title(client):
    assert client.post("/api/tasks", json={}).status_code == 400


def test_get_tasks(client):
    client.post("/api/tasks", json={"title": "Task A"})
    r = client.get("/api/tasks")
    assert r.status_code == 200
    assert len(r.get_json()) >= 1


def test_update_task(client):
    tid = client.post("/api/tasks", json={"title": "Old"}).get_json()["id"]
    r = client.put(f"/api/tasks/{tid}", json={"title": "New", "done": True})
    assert r.status_code == 200
    assert r.get_json()["title"] == "New"
    assert r.get_json()["done"] is True


def test_delete_task(client):
    tid = client.post("/api/tasks", json={"title": "Temp"}).get_json()["id"]
    assert client.delete(f"/api/tasks/{tid}").status_code == 200
    assert client.delete(f"/api/tasks/{tid}").status_code == 404


def test_metrics_endpoint(client):
    assert client.get("/metrics").status_code == 200