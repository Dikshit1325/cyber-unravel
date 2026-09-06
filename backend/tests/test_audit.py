import pytest
from fastapi.testclient import TestClient
from main import app
from backend.tests.conftest import auth_headers, ADMIN, INVESTIGATOR, ANALYST
from services.audit_service import audit_service

client = TestClient(app)

# 1. Missing authentication header → 401 Unauthorized
def test_no_headers_returns_401():
    response = client.get("/api/audit")
    assert response.status_code == 401
    assert "detail" in response.json()

# 2. Valid ADMIN → allowed
def test_valid_admin_allowed():
    response = client.get("/api/audit", headers=auth_headers(ADMIN))
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "audit_records" in data

# 3. Valid INVESTIGATOR → allowed
def test_valid_investigator_allowed():
    response = client.get("/api/audit", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "audit_records" in data

# 4. Valid ANALYST → allowed for permitted endpoints
def test_valid_analyst_permitted_endpoints():
    # Analyst can view anomalies and graph
    resp_anomalies = client.get("/api/anomalies", headers=auth_headers(ANALYST))
    assert resp_anomalies.status_code == 200

    resp_graph = client.get("/api/graph", headers=auth_headers(ANALYST))
    assert resp_graph.status_code == 200

    resp_entity = client.get("/api/entity/P001", headers=auth_headers(ANALYST))
    assert resp_entity.status_code == 200

# 5. ANALYST → /api/audit → 403 Forbidden
def test_analyst_audit_forbidden():
    response = client.get("/api/audit", headers=auth_headers(ANALYST))
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

# 6. Spoofed X-User-Role → must NOT grant unauthorized privileges
def test_spoofed_user_role_blocked():
    # Analyst tries to spoof ADMIN role via header
    spoofed_headers = {
        "X-User-Id": ANALYST,
        "X-User-Role": "ADMIN",
    }
    response = client.get("/api/audit", headers=spoofed_headers)
    # Role must be resolved from server-side AuthService, resulting in 403
    assert response.status_code == 403

# 7. Denied request generates audit record with status="DENIED"
def test_denied_request_generates_audit_record():
    # Send an unauthorized request
    client.get("/api/audit", headers=auth_headers(ANALYST))

    # Query audit log as admin
    resp = client.get("/api/audit?status=DENIED", headers=auth_headers(ADMIN))
    assert resp.status_code == 200
    records = resp.json()["audit_records"]
    assert len(records) > 0

    # Verify at least one denied record for analyst_01
    denied_for_analyst = [
        r for r in records if r["user_id"] == ANALYST and r["status"] == "DENIED"
    ]
    assert len(denied_for_analyst) > 0
    record = denied_for_analyst[0]
    assert record["action"] == "audit_view"
    assert record["resource_type"] == "audit"
    assert "resource_id" in record

# 8. Successful request generates audit record with complete schema
def test_successful_request_generates_audit_record():
    client.get("/api/entity/P001", headers=auth_headers(INVESTIGATOR))

    resp = client.get("/api/audit?user_id=investigator_01", headers=auth_headers(ADMIN))
    assert resp.status_code == 200
    records = resp.json()["audit_records"]
    assert len(records) > 0

    entity_records = [
        r for r in records if r["resource_id"] == "P001" and r["status"] == "SUCCESS"
    ]
    assert len(entity_records) > 0
    rec = entity_records[0]

    # Required schema checks
    required_fields = [
        "audit_id",
        "timestamp",
        "user_id",
        "role",
        "action",
        "endpoint",
        "resource_type",
        "resource_id",
        "status",
    ]
    for field in required_fields:
        assert field in rec

    assert rec["resource_type"] == "entity"
    assert rec["resource_id"] == "P001"
    assert rec["role"] == "INVESTIGATOR"

# 9. Audit privacy: sensitive data should not be present in audit records
def test_audit_privacy_no_sensitive_payloads():
    resp = client.get("/api/audit", headers=auth_headers(ADMIN))
    assert resp.status_code == 200
    records = resp.json()["audit_records"]

    forbidden_keys = {"password", "token", "raw_cdr", "raw_ipdr", "transactions_payload"}
    for r in records:
        for key in forbidden_keys:
            assert key not in r
            if "metadata" in r and r["metadata"]:
                assert key not in r["metadata"]

# 10. Audit filters (action, user_id, status)
def test_audit_filters():
    # Filter by action
    resp = client.get("/api/audit?action=graph_view", headers=auth_headers(ADMIN))
    assert resp.status_code == 200
    for rec in resp.json()["audit_records"]:
        assert rec["action"] == "graph_view"

    # Filter by user_id
    resp_user = client.get(f"/api/audit?user_id={ADMIN}", headers=auth_headers(ADMIN))
    assert resp_user.status_code == 200
    for rec in resp_user.json()["audit_records"]:
        assert rec["user_id"] == ADMIN
