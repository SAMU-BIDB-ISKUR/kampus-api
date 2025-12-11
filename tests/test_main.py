import pytest

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Üniversite Kampüs ve Bina API'ye hoş geldiniz",
        "docs": "/docs",
        "version": "1.0.0"
    }
