"""
Tests for the FastAPI gateway.

These tests use FastAPI’s built‑in TestClient to verify that the root endpoint
returns the expected response.  More comprehensive tests for the user
endpoints would require mocking Supabase responses and are beyond the scope of
this template.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_read_root() -> None:
    """Ensure the root endpoint returns a JSON message."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Gateway is working"}