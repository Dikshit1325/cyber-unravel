from fastapi.testclient import TestClient
from main import app
from backend.tests.conftest import auth_headers, INVESTIGATOR, ADMIN, ANALYST

client = TestClient(app)


def test_network_unauthenticated():
    response = client.get("/api/network/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication"


def test_network_invalid_user():
    response = client.get("/api/network/", headers={"X-User-Id": "nonexistent_user"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user"


def test_network_list_success():
    response = client.get("/api/network/", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "summary" in data
    assert "records" in data
    assert data["total"] > 0
    assert len(data["records"]) > 0
    assert "total_records" in data["summary"]
    assert "unique_ips" in data["summary"]
    assert "unique_devices" in data["summary"]


def test_network_pagination():
    response = client.get("/api/network/?page=1&page_size=5", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["records"]) <= 5


def test_network_filter_by_entity():
    response = client.get("/api/network/?entity_id=P001", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    for rec in data["records"]:
        assert rec["entity_id"] == "P001" or rec["person_id"] == "P001"


def test_network_detail_success():
    # First get a valid record ID
    list_res = client.get("/api/network/?page_size=1", headers=auth_headers(INVESTIGATOR))
    assert list_res.status_code == 200
    records = list_res.json()["records"]
    assert len(records) > 0
    target_id = records[0]["ipdr_id"]

    # Now fetch detail
    detail_res = client.get(f"/api/network/{target_id}", headers=auth_headers(INVESTIGATOR))
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["ipdr_id"] == target_id
    assert "ip_address" in detail
    assert "device_id" in detail
    assert "session_duration_seconds" in detail


def test_network_detail_not_found():
    response = client.get("/api/network/NONEXISTENT_IPDR_999", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 404


def test_network_audit_logging():
    # Make a successful request
    client.get("/api/network/?page_size=2", headers=auth_headers(INVESTIGATOR))

    # Verify audit log
    audit_res = client.get("/api/audit/?action=network_view", headers=auth_headers(ADMIN))
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    records = audit_data["audit_records"]
    assert any(r["action"] == "network_view" and r["status"] == "SUCCESS" for r in records)
