# tests/test_app.py

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_form(client):
    """Test that the web form loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"LLM Evaluation Configuration" in response.data


def test_post_form_bias_fairness(client, monkeypatch):
    """Test submitting the form with bias fairness selected."""

    # Mock run_bias_analysis to return fake data
    monkeypatch.setattr("app.run_bias_analysis", lambda: {"gender": {"disparate_impact_ratio": 0.8}})

    data = {
        "api_url": "https://fake-url.com/score",
        "username": "test_user",
        "password": "test_pass",
        "analysis": "bias_fairness",
    }

    response = client.post("/", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"gender" in response.data
    assert b"disparate_impact_ratio" in response.data
