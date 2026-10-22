def test_list_tasks_starts_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Write CI pipeline", "description": "Add automated checks"},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Write CI pipeline"
    assert task["completed"] is False
    assert task["id"] > 0

    fetched = client.get(f"/tasks/{task['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == task["id"]


def test_create_task_strips_whitespace(client):
    response = client.post("/tasks", json={"title": "  Valid title  "})
    assert response.status_code == 201
    assert response.json()["title"] == "Valid title"


def test_create_task_rejects_blank_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_rejects_unknown_fields(client):
    response = client.post("/tasks", json={"title": "Valid", "admin": True})
    assert response.status_code == 422


def test_create_task_rejects_long_title(client):
    response = client.post("/tasks", json={"title": "x" * 201})
    assert response.status_code == 422


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Original", "completed": False})
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated", "completed": True},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["completed"] is True


def test_update_task_rejects_empty_update(client):
    created = client.post("/tasks", json={"title": "Original"})
    response = client.patch(f"/tasks/{created.json()['id']}", json={})
    assert response.status_code == 422


def test_update_missing_task_returns_404(client):
    response = client.patch("/tasks/999", json={"title": "Updated"})
    assert response.status_code == 404


def test_update_task_rejects_blank_title(client):
    created = client.post("/tasks", json={"title": "Original"})
    response = client.patch(f"/tasks/{created.json()['id']}", json={"title": "  "})
    assert response.status_code == 422


def test_update_task_rejects_null_fields(client):
    created = client.post("/tasks", json={"title": "Original"})
    response = client.patch(f"/tasks/{created.json()['id']}", json={"description": None})
    assert response.status_code == 422


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Delete me"})
    task_id = created.json()["id"]
    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_missing_task_returns_404(client):
    assert client.delete("/tasks/999").status_code == 404


def test_list_tasks_pagination(client):
    for number in range(3):
        client.post("/tasks", json={"title": f"Task {number}"})
    response = client.get("/tasks?limit=2&offset=1")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_invalid_pagination_is_rejected(client):
    assert client.get("/tasks?limit=0").status_code == 422
