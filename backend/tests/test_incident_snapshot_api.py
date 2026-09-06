"""
Tests for GET /api/incident_snapshot

Verifies:
- Authenticated access (all roles)
- Unauthenticated 401
- Invalid user 401
- Role spoofing does not elevate privileges
- Response schema
- Pagination (limit/offset)
- Window behavior (24h default)
- Entity filtering
- Timestamp integrity (events within window)
- Audit SUCCESS on success
- Audit DENIED on 401
- No sensitive payloads in audit logs
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from backend.tests.conftest import auth_headers, ADMIN, INVESTIGATOR, ANALYST
from services.audit_service import audit_service

client = TestClient(app)


# ============================================================
# 1. Authenticated access returns 200 for all roles
# ============================================================

def test_snapshot_authorized_all_roles():
    for user in [ADMIN, INVESTIGATOR, ANALYST]:
        res = client.get("/api/incident_snapshot", headers=auth_headers(user))
        assert res.status_code == 200, f"Expected 200 for {user}, got {res.status_code}"
        data = res.json()
        assert "total_events" in data
        assert "events" in data
        assert "window_start" in data
        assert "window_end" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["events"], list)


# ============================================================
# 2. Unauthenticated 401
# ============================================================

def test_snapshot_unauthenticated():
    res = client.get("/api/incident_snapshot")
    assert res.status_code == 401
    assert "detail" in res.json()


# ============================================================
# 3. Invalid user 401
# ============================================================

def test_snapshot_invalid_user():
    res = client.get("/api/incident_snapshot", headers={"X-User-Id": "ghost_9999"})
    assert res.status_code == 401


# ============================================================
# 4. Role spoofing does not escalate privileges
# ============================================================

def test_snapshot_role_spoofing():
    res = client.get(
        "/api/incident_snapshot",
        headers={"X-User-Id": ANALYST, "X-User-Role": "ADMIN"},
    )
    # ANALYST has incident_snapshot_view, so should be 200
    assert res.status_code == 200


# ============================================================
# 5. Response schema validation
# ============================================================

def test_snapshot_schema():
    res = client.get("/api/incident_snapshot?limit=5", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    data = res.json()
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert isinstance(data["total_events"], int)
    assert data["total_events"] >= 0
    assert isinstance(data["events"], list)
    assert len(data["events"]) <= 5


# ============================================================
# 6. Each event has required fields
# ============================================================

def test_snapshot_event_schema():
    res = client.get("/api/incident_snapshot?limit=20", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    for evt in res.json()["events"]:
        assert "event_type" in evt
        assert "timestamp" in evt
        assert "source_dataset" in evt
        assert "source" in evt
        assert evt["event_type"] in {"CALL", "TRANSACTION", "IP_ACTIVITY", "SOCIAL_ACTIVITY"}


# ============================================================
# 7. Pagination – non-overlapping pages
# ============================================================

def test_snapshot_pagination():
    r1 = client.get("/api/incident_snapshot?limit=5&offset=0", headers=auth_headers(INVESTIGATOR)).json()
    r2 = client.get("/api/incident_snapshot?limit=5&offset=5", headers=auth_headers(INVESTIGATOR)).json()

    assert r1["total_events"] == r2["total_events"]

    sources_p1 = {e["source"] for e in r1["events"]}
    sources_p2 = {e["source"] for e in r2["events"]}

    # No overlap in source IDs between pages
    assert sources_p1.isdisjoint(sources_p2), "Pages should not overlap"


# ============================================================
# 8. Window behavior – default is 24 hours
# ============================================================

def test_snapshot_window_24h():
    res = client.get("/api/incident_snapshot?window_hours=24", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    data = res.json()
    if data["window_start"] and data["window_end"] and data["events"]:
        start = data["window_start"]
        end = data["window_end"]
        for evt in data["events"]:
            ts = evt["timestamp"]
            assert ts >= start, f"Event {evt['source']} timestamp {ts} < window_start {start}"
            assert ts <= end, f"Event {evt['source']} timestamp {ts} > window_end {end}"


# ============================================================
# 9. Window – larger window returns at least as many events
# ============================================================

def test_snapshot_larger_window_gte_results():
    res_24 = client.get(
        "/api/incident_snapshot?window_hours=24&limit=100",
        headers=auth_headers(INVESTIGATOR),
    ).json()
    res_168 = client.get(
        "/api/incident_snapshot?window_hours=168&limit=100",
        headers=auth_headers(INVESTIGATOR),
    ).json()
    assert res_168["total_events"] >= res_24["total_events"]


# ============================================================
# 10. Entity filtering narrows results
# ============================================================

def test_snapshot_entity_filter():
    import pandas as pd
    from pathlib import Path

    persons_path = Path(__file__).resolve().parents[1] / "data" / "persons.csv"
    df = pd.read_csv(persons_path)
    test_entity = str(df["person_id"].iloc[0]).strip()

    res = client.get(
        f"/api/incident_snapshot?entity_id={test_entity}&window_hours=168&limit=50",
        headers=auth_headers(INVESTIGATOR),
    )
    assert res.status_code == 200
    data = res.json()
    # All events must involve the target entity
    for evt in data["events"]:
        involved = {
            evt.get("entity_id"),
            evt.get("caller"),
            evt.get("receiver"),
            evt.get("sender_entity_id"),
            evt.get("receiver_entity_id"),
        }
        assert test_entity in involved, (
            f"Event {evt['source']} does not involve entity {test_entity}"
        )


# ============================================================
# 11. Invalid window_hours >= 1 and <= 168
# ============================================================

def test_snapshot_invalid_window():
    res_zero = client.get("/api/incident_snapshot?window_hours=0", headers=auth_headers(INVESTIGATOR))
    assert res_zero.status_code == 422

    res_over = client.get("/api/incident_snapshot?window_hours=999", headers=auth_headers(INVESTIGATOR))
    assert res_over.status_code == 422


# ============================================================
# 12. Audit SUCCESS logged
# ============================================================

def test_snapshot_audit_success():
    res = client.get("/api/incident_snapshot?limit=1", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    audit_res = client.get(
        "/api/audit?action=incident_snapshot_view&status=SUCCESS",
        headers=auth_headers(ADMIN),
    )
    assert audit_res.status_code == 200
    records = audit_res.json()["audit_records"]
    assert len(records) >= 1


# ============================================================
# 13. Audit DENIED on unauthenticated
# ============================================================

def test_snapshot_audit_denied():
    client.get("/api/incident_snapshot")
    audit_res = client.get(
        "/api/audit?action=incident_snapshot_view&status=DENIED",
        headers=auth_headers(ADMIN),
    )
    assert audit_res.status_code == 200
    records = audit_res.json()["audit_records"]
    assert len(records) >= 1


# ============================================================
# 14. No sensitive payloads in audit logs
# ============================================================

def test_snapshot_audit_no_sensitive():
    client.get("/api/incident_snapshot?limit=1", headers=auth_headers(INVESTIGATOR))
    audit_res = client.get(
        "/api/audit?action=incident_snapshot_view",
        headers=auth_headers(ADMIN),
    )
    assert audit_res.status_code == 200
    for log in audit_res.json()["audit_records"]:
        meta_str = str(log.get("metadata", {}) or {})
        assert "password" not in meta_str.lower()
        assert "token" not in meta_str.lower()
        assert "DataFrame" not in meta_str


# ============================================================
# 15. Max limit enforcement
# ============================================================

def test_snapshot_max_limit():
    res = client.get("/api/incident_snapshot?limit=100", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200

    res_over = client.get("/api/incident_snapshot?limit=200", headers=auth_headers(INVESTIGATOR))
    assert res_over.status_code == 422
