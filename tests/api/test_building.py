import pytest
from unittest.mock import MagicMock

def test_create_building(client, mock_db_conn):
    # Arrange
    building_data = {
        "campus_id": 1,
        "name": "Test Bina",
        "type": "Derslik",
        "floor_count": 5,
        "construction_year": 2021,
        "gross_area": 500.0
    }
    
    mock_cursor = mock_db_conn.cursor.return_value
    # Mock campus check (find_by_id returns something)
    mock_cursor.fetchone.side_effect = [{"id": 1}, {"id": 1, **building_data}]

    # Act
    response = client.post("/api/buildings", json=building_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Bina"
    assert data["campus_id"] == 1

def test_create_building_campus_not_found(client, mock_db_conn):
    # Arrange
    building_data = {
        "campus_id": 999,
        "name": "Test Bina"
    }
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None # Campus not found

    # Act
    response = client.post("/api/buildings", json=building_data)

    # Assert
    assert response.status_code == 404

def test_get_buildings(client, mock_db_conn):
    # Arrange
    mock_buildings = [
        {"id": 1, "campus_id": 1, "name": "Bina 1", "type": None, "floor_count": None, "construction_year": None, "gross_area": None, "created_at": None, "updated_at": None},
        {"id": 2, "campus_id": 1, "name": "Bina 2", "type": None, "floor_count": None, "construction_year": None, "gross_area": None, "created_at": None, "updated_at": None}
    ]
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchall.return_value = mock_buildings

    # Act
    response = client.get("/api/buildings")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_buildings_by_campus(client, mock_db_conn):
    # Arrange
    mock_buildings = [{"id": 1, "campus_id": 1, "name": "Bina 1", "type": None, "floor_count": None, "construction_year": None, "gross_area": None, "created_at": None, "updated_at": None}]
    mock_cursor = mock_db_conn.cursor.return_value
    # First call: check campus exists (returns campus dict)
    # Second call: fetchall buildings
    mock_cursor.fetchone.return_value = {"id": 1}
    mock_cursor.fetchall.return_value = mock_buildings

    # Act
    response = client.get("/api/buildings?campus_id=1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["campus_id"] == 1

def test_get_building_by_id(client, mock_db_conn):
    # Arrange
    mock_building = {"id": 1, "campus_id": 1, "name": "Bina 1", "type": None, "floor_count": None, "construction_year": None, "gross_area": None, "created_at": None, "updated_at": None}
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchone.return_value = mock_building

    # Act
    response = client.get("/api/buildings/1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_update_building(client, mock_db_conn):
    # Arrange
    mock_building_existing = {"id": 1, "campus_id": 1, "name": "Eski Bina"}
    mock_building_updated = {"id": 1, "campus_id": 1, "name": "Yeni Bina", "type": None, "floor_count": None, "construction_year": None, "gross_area": None, "created_at": None, "updated_at": None}
    
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchone.side_effect = [mock_building_existing, mock_building_updated]
    
    update_data = {"name": "Yeni Bina"}
    
    # Act
    response = client.put("/api/buildings/1", json=update_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Yeni Bina"

def test_update_building_campus_id_fail(client, mock_db_conn):
    # Arrange
    mock_building_existing = {"id": 1, "campus_id": 1, "name": "Eski Bina"}
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchone.return_value = mock_building_existing
    
    update_data = {"campus_id": 2} # Trying to change campus_id
    
    # Act
    response = client.put("/api/buildings/1", json=update_data)

    # Assert
    assert response.status_code == 400

def test_delete_building(client, mock_db_conn):
    # Arrange
    mock_building = {"id": 1, "campus_id": 1, "name": "Silinecek Bina", "type": None, "floor_count": None, "construction_year": None, "gross_area": None, "created_at": None, "updated_at": None}
    mock_cursor = mock_db_conn.cursor.return_value
    mock_cursor.fetchone.return_value = mock_building

    # Act
    response = client.delete("/api/buildings/1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
