import os
import pytest
from unittest import mock
from api import create_app


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"FLASK_ENV": "development"}):
        yield


@pytest.fixture
def app():
    """
    Create a flask app for testing
    """
    os.environ['FLASK_ENV'] = "testing"
    print("env: ", os.environ.get("ENV_VAR"))
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    """
    Create a flask test client
    :param app: Flask app
    """
    return app.test_client()
