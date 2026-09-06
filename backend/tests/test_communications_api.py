import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd

from main import app
from backend.tests.conftest import auth_headers, ADMIN, INVESTIGATOR, ANALYST
from services.audit_service import audit_service

client = TestClient(app)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "cdr.csv"

# 1. GET /api/communications returns 200 for authorized users (Admin, Investigator, Analyst)
def test_get_communications_authorized():
    for user in [ADMIN, INVESTIGATOR, ANALYST]:
        response = client.get("/api/communications", headers=auth_headers(user))
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "communications" in data
        assert "summary" in data
        assert data["total"] > 0

# 2. Unauthenticated requests return 401
def test_get_communications_unauthenticated():
    response = client.get("/api/communications")
    assert response.status_code == 401
    assert "detail" in response.json()

# 3. Invalid user returns 401
def test_get_communications_invalid_user():
    response = client.get("/api/communications", headers={"X-User-Id": "invalid_user_999"})
    assert response.status_code == 401

# 4 & 5. Analyst can access communication data and role spoofing is blocked
def test_communications_analyst_and_role_spoofing():
    # Analyst has communication_view permission
    resp_analyst = client.get("/api/communications", headers=auth_headers(ANALYST))
    assert resp_analyst.status_code == 200

    # Role spoofing does not escalate
    resp_spoof = client.get(
        "/api/communications",
        headers={"X-User-Id": ANALYST, "X-User-Role": "ADMIN"},
    )
    assert resp_spoof.status_code == 200

# 6. Response schema structure (total, page, page_size, summary, communications)
def test_communications_response_schema():
    response = client.get("/api/communications?page=1&page_size=25", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "summary" in data
    assert "communications" in data
    assert data["page"] == 1
    assert data["page_size"] == 25

    summary = data["summary"]
    assert "total_calls" in summary
    assert "total_duration_seconds" in summary
    assert "avg_duration_seconds" in summary
    assert "high_priority_count" in summary
    assert "unique_contacts" in summary
    assert summary["total_calls"] == data["total"]

# 7. Response records match real records in cdr.csv
def test_communications_match_source_dataset():
    df_real = pd.read_csv(DATA_PATH)
    real_cdr_ids = set(df_real["cdr_id"].astype(str).str.strip())
    assert len(real_cdr_ids) > 0

    response = client.get("/api/communications?page_size=200", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == len(real_cdr_ids)
    for comm in data["communications"]:
        assert comm["communication_id"] in real_cdr_ids
        assert comm["caller"]
        assert comm["receiver"]
        assert comm["duration_seconds"] >= 0

# 8. Filtering by communication_id
def test_filter_by_communication_id():
    response = client.get("/api/communications?communication_id=CDR0001", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["communications"][0]["communication_id"] == "CDR0001"

# 9. Filtering by entity_id
def test_filter_by_entity_id():
    response = client.get("/api/communications?entity_id=P005", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for comm in data["communications"]:
        assert "P005" in comm["entity_ids"]

# 10. Filtering by caller and receiver
def test_filter_by_caller_and_receiver():
    # Filter caller P005
    resp_caller = client.get("/api/communications?caller=P005", headers=auth_headers(INVESTIGATOR))
    assert resp_caller.status_code == 200
    for comm in resp_caller.json()["communications"]:
        assert comm["caller"] == "P005" or comm.get("caller_entity_id") == "P005"

    # Filter receiver P006
    resp_receiver = client.get("/api/communications?receiver=P006", headers=auth_headers(INVESTIGATOR))
    assert resp_receiver.status_code == 200
    for comm in resp_receiver.json()["communications"]:
        assert comm["receiver"] == "P006" or comm.get("receiver_entity_id") == "P006"

# 11. Duration filtering (min_duration and max_duration)
def test_filter_by_duration_range():
    min_dur = 100
    max_dur = 300
    response = client.get(
        f"/api/communications?min_duration={min_dur}&max_duration={max_dur}",
        headers=auth_headers(INVESTIGATOR),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for comm in data["communications"]:
        assert min_dur <= comm["duration_seconds"] <= max_dur

# 12. Invalid duration filter returns 400
def test_invalid_duration_filter():
    response = client.get(
        "/api/communications?min_duration=500&max_duration=100",
        headers=auth_headers(INVESTIGATOR),
    )
    assert response.status_code == 400
    assert "detail" in response.json()

# 13. Sorting tests (timestamp and duration)
def test_sorting_communications():
    # Sort by duration descending
    resp_dur_desc = client.get("/api/communications?sort=duration_desc&page_size=100", headers=auth_headers(INVESTIGATOR))
    assert resp_dur_desc.status_code == 200
    durs_desc = [c["duration_seconds"] for c in resp_dur_desc.json()["communications"]]
    assert durs_desc == sorted(durs_desc, reverse=True)

    # Sort by timestamp ascending
    resp_time_asc = client.get("/api/communications?sort=timestamp_asc&page_size=100", headers=auth_headers(INVESTIGATOR))
    assert resp_time_asc.status_code == 200
    times_asc = [c["timestamp"] for c in resp_time_asc.json()["communications"]]
    assert times_asc == sorted(times_asc)

# 14. Pagination test
def test_communications_pagination():
    resp_p1 = client.get("/api/communications?page=1&page_size=5", headers=auth_headers(INVESTIGATOR))
    resp_p2 = client.get("/api/communications?page=2&page_size=5", headers=auth_headers(INVESTIGATOR))

    assert resp_p1.status_code == 200
    assert resp_p2.status_code == 200

    p1_comms = resp_p1.json()["communications"]
    p2_comms = resp_p2.json()["communications"]

    assert len(p1_comms) == 5
    assert len(p2_comms) == 5

    p1_ids = {c["communication_id"] for c in p1_comms}
    p2_ids = {c["communication_id"] for c in p2_comms}
    assert len(p1_ids.intersection(p2_ids)) == 0

# 15. Single communication detail lookup
def test_single_communication_detail():
    resp = client.get("/api/communications/CDR0001", headers=auth_headers(INVESTIGATOR))
    assert resp.status_code == 200
    data = resp.json()
    assert data["communication_id"] == "CDR0001"
    assert "caller" in data
    assert "receiver" in data
    assert "duration_seconds" in data
    assert "timestamp" in data

    # 404 for non-existent record
    resp_404 = client.get("/api/communications/CDR999999", headers=auth_headers(INVESTIGATOR))
    assert resp_404.status_code == 404

# 16. Audit log generation
def test_communication_audit_logging():
    client.get("/api/communications/CDR0001", headers=auth_headers(INVESTIGATOR))

    resp = client.get("/api/audit?action=communication_view", headers=auth_headers(ADMIN))
    assert resp.status_code == 200
    records = resp.json()["audit_records"]
    assert len(records) > 0

    comm_records = [r for r in records if r["resource_type"] == "communication"]
    assert len(comm_records) > 0

    # Ensure no raw CDR dataset payload in audit log
    for r in comm_records:
        assert "raw_cdr" not in r
        assert "cdr_payload" not in r
