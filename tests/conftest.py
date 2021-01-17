import pytest
from src.flaskapp.api import app

@pytest.fixture
def client():
    """Pytest fixture to mock API requests."""
    app.config["TESTING"] = True
    _client = app.test_client()
    return _client
