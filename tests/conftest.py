import pytest
import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Add root directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import app, get_db_connection

# Mock Database Connection
@pytest.fixture
def mock_db_conn():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

# Override Dependency
@pytest.fixture
def client(mock_db_conn):
    def override_get_db_connection():
        yield mock_db_conn

    app.dependency_overrides[get_db_connection] = override_get_db_connection
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
