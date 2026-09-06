from fastapi.testclient import TestClient
from main import app
from backend.tests.conftest import auth_headers, INVESTIGATOR

client = TestClient(app)

def test_get_graph():
    response = client.get("/api/graph", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "node_count" in data
    assert "edge_count" in data
    assert data["node_count"] > 0
    assert data["edge_count"] > 0

def test_get_entity():
    response = client.get("/api/entity/P001", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "P001"
    assert data["name"] == "Aarav Mehta"
    assert "PH001" in data["phones"]
    assert "A001" in data["bank_accounts"]
    assert "SOC001" in data["social_accounts"]

def test_get_entity_connections():
    response = client.get("/api/entity/P001/connections", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "P001"
    assert data["count"] > 0
    relationships = [
        connection["relationship"]
        for connection in data["connections"]
    ]
    assert "USES" in relationships
    assert "OWNS" in relationships

def test_get_entity_timeline():
    response = client.get("/api/entity/P001/timeline", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "P001"
    assert data["count"] > 0
    event_types = [
        event["event_type"]
        for event in data["timeline"]
    ]
    assert "CALL" in event_types
    assert "TRANSACTION" in event_types
    assert "IP_ACTIVITY" in event_types
    assert "SOCIAL_ACTIVITY" in event_types

def test_get_entity_summary():
    response = client.get("/api/entity/P001/summary", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "P001"
    assert data["name"] == "Aarav Mehta"
    assert "accounts" in data
    assert "transactions" in data
    assert "communications" in data
    assert "network" in data
    assert "anomalies" in data
    assert isinstance(data["transactions"], list)
    assert isinstance(data["communications"], list)
    assert isinstance(data["network"], list)

def test_get_entity_summary_not_found():
    response = client.get("/api/entity/NONEXISTENT_999/summary", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 404

def test_get_entity_summary_unauthenticated():
    response = client.get("/api/entity/P001/summary")
    assert response.status_code == 401