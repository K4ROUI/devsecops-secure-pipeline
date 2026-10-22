import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_tasks.db"
    monkeypatch.setattr(main, "DB_PATH", db_path)
    with TestClient(main.app) as test_client:
        yield test_client
