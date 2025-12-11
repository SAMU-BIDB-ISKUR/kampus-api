import pytest
from unittest.mock import MagicMock, Mock

def test_create_campus(client, mock_db_conn):
    """Test creating a new campus"""
    # Arrange
    campus_data = {
        "name": "Test Kampüs",
        "city": "İstanbul",
        "address": "Test Adresi",
        "established_year": 2020,
        "total_area": 1000.5,
        "student_capacity": 5000
    }
    
    # Mock cursor to return dict-like object
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    
    # Create a mock row that behaves like a dict
    mock_row = {
        "id": 1, 
        **campus_data, 
        "created_at": "2023-01-01T00:00:00", 
        "updated_at": "2023-01-01T00:00:00"
    }
    mock_cursor.fetchone.return_value = mock_row
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)

    # Act
    response = client.post("/api/campuses", json=campus_data)

    # Assert
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["name"] == campus_data["name"]
    assert data["city"] == campus_data["city"]
    assert data["id"] == 1
    mock_cursor.execute.assert_called()
    mock_db_conn.commit.assert_called_once()

def test_get_campuses(client, mock_db_conn):
    """Test retrieving all campuses"""
    # Arrange
    mock_campuses = [
        {"id": 1, "name": "Kampüs 1", "city": "İstanbul", "address": None, "established_year": None, "total_area": None, "student_capacity": None, "created_at": None, "updated_at": None},
        {"id": 2, "name": "Kampüs 2", "city": "Ankara", "address": None, "established_year": None, "total_area": None, "student_capacity": None, "created_at": None, "updated_at": None}
    ]
    
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = mock_campuses
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)

    # Act
    response = client.get("/api/campuses")

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Kampüs 1"
    assert data[1]["name"] == "Kampüs 2"

def test_get_campus_by_id(client, mock_db_conn):
    """Test retrieving a specific campus by ID"""
    # Arrange
    mock_campus = {
        "id": 1, 
        "name": "Kampüs 1", 
        "city": "İstanbul", 
        "address": "Test Adres", 
        "established_year": 2020, 
        "total_area": 1500.0, 
        "student_capacity": 10000, 
        "created_at": "2023-01-01T00:00:00", 
        "updated_at": "2023-01-01T00:00:00"
    }
    
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = mock_campus
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)

    # Act
    response = client.get("/api/campuses/1")

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Kampüs 1"

def test_get_campus_not_found(client, mock_db_conn):
    """Test retrieving a non-existent campus returns 404"""
    # Arrange
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)

    # Act
    response = client.get("/api/campuses/999")

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert "bulunamadı" in response.json()["detail"].lower()

def test_update_campus(client, mock_db_conn):
    """Test updating an existing campus"""
    # Arrange
    mock_campus_existing = {
        "id": 1, 
        "name": "Eski İsim", 
        "city": "İstanbul",
        "address": None,
        "established_year": None,
        "total_area": None,
        "student_capacity": None
    }
    mock_campus_updated = {
        "id": 1, 
        "name": "Yeni İsim", 
        "city": "İstanbul", 
        "address": None, 
        "established_year": None, 
        "total_area": None, 
        "student_capacity": None, 
        "created_at": "2023-01-01T00:00:00", 
        "updated_at": "2023-01-01T12:00:00"
    }
    
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    # First call for find_by_id (check existence), second call for update returning
    mock_cursor.fetchone.side_effect = [mock_campus_existing, mock_campus_updated]
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)
    
    update_data = {"name": "Yeni İsim"}
    
    # Act
    response = client.put("/api/campuses/1", json=update_data)

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["name"] == "Yeni İsim"
    mock_db_conn.commit.assert_called_once()

def test_delete_campus(client, mock_db_conn):
    """Test deleting a campus"""
    # Arrange
    mock_campus = {
        "id": 1, 
        "name": "Silinecek Kampüs", 
        "city": "İstanbul", 
        "address": None, 
        "established_year": None, 
        "total_area": None, 
        "student_capacity": None, 
        "created_at": "2023-01-01T00:00:00", 
        "updated_at": "2023-01-01T00:00:00"
    }
    
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = mock_campus
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)

    # Act
    response = client.delete("/api/campuses/1")

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Silinecek Kampüs"
    mock_db_conn.commit.assert_called_once()

def test_create_campus_with_missing_required_fields(client, mock_db_conn):
    """Test that creating a campus without required fields fails"""
    # Arrange - missing 'city' field
    campus_data = {
        "name": "Test Kampüs"
    }
    
    # Act
    response = client.post("/api/campuses", json=campus_data)

    # Assert
    assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"

def test_get_campuses_filtered_by_city(client, mock_db_conn):
    """Test filtering campuses by city"""
    # Arrange
    mock_campuses = [
        {"id": 1, "name": "Kampüs 1", "city": "İstanbul", "address": None, "established_year": None, "total_area": None, "student_capacity": None, "created_at": None, "updated_at": None}
    ]
    
    mock_cursor = MagicMock()
    mock_db_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = mock_campuses
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=False)

    # Act
    response = client.get("/api/campuses?city=İstanbul")

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    data = response.json()
    assert len(data) == 1
    assert data[0]["city"] == "İstanbul"
