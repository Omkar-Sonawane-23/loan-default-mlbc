def test_health_endpoint_returns_200(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "mongodb_connected" in data
    assert "ml_model_loaded" in data
    assert "blockchain_available" in data


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert "academic" in data["disclaimer"].lower()
