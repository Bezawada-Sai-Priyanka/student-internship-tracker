import pytest

import app as tracker


@pytest.fixture
def client(tmp_path, monkeypatch):
    database = str(tmp_path / "test.db")
    monkeypatch.setattr(tracker, "DATABASE", database)
    tracker.init_db()

    tracker.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret"
    )

    with tracker.app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Internship Tracker" in response.data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_add_student(client):
    response = client.post("/add", data={
        "student_name": "Asha",
        "student_email": "asha@example.com",
        "company": "Tech Startup",
        "role": "Python Intern",
        "status": "Applied"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Asha" in response.data
    assert b"Tech Startup" in response.data


def test_reject_invalid_status(client):
    response = client.post("/add", data={
        "student_name": "Asha",
        "student_email": "asha@example.com",
        "company": "Tech Startup",
        "role": "Python Intern",
        "status": "Unknown"
    }, follow_redirects=True)

    assert b"Invalid internship status." in response.data
