"""
Tests for GET /api/relationships

Verifies:
- Authenticated access (all roles)
- Unauthenticated 401
- Invalid user 401
- Role spoofing does not elevate privileges
- Response schema
- Pagination (limit/offset)
- Deterministic ordering
- Entity filtering
- Audit SUCCESS on success
- Audit DENIED on 401/403
- No sensitive payloads in audit logs
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from main import app
from backend.tests.conftest import auth_headers, ADMIN, INVESTIGATOR, ANALYST
from services.audit_service import audit_service

client = TestClient(app)


# ============================================================
# 1. Authenticated access returns 200 for all roles
# ============================================================

def test_relationships_authorized_all_roles():
    for user in [ADMIN, INVESTIGATOR, ANALYST]:
        res = client.get("/api/relationships", headers=auth_headers(user))
        assert res.status_code == 200, f"Expected 200 for {user}, got {res.status_code}"
        data = res.json()
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "relationships" in data
        assert isinstance(data["relationships"], list)


# ============================================================
# 2. Unauthenticated 401
# ============================================================

def test_relationships_unauthenticated():
    res = client.get("/api/relationships")
    assert res.status_code == 401
    assert "detail" in res.json()


# ============================================================
# 3. Invalid user 401
# ============================================================

def test_relationships_invalid_user():
    res = client.get("/api/relationships", headers={"X-User-Id": "unknown_ghost_user"})
    assert res.status_code == 401


# ============================================================
# 4. Role spoofing does not escalate privileges
# ============================================================

def test_relationships_role_spoofing():
    # Sending client-side X-User-Role header must NOT bypass server-side role resolution
    res = client.get(
        "/api/relationships",
        headers={"X-User-Id": ANALYST, "X-User-Role": "ADMIN"},
    )
    # ANALYST has relationship_view, so should be 200 regardless of spoofed header
    assert res.status_code == 200


# ============================================================
# 5. Response schema validation
# ============================================================

def test_relationships_schema():
    res = client.get("/api/relationships?limit=5", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    data = res.json()
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert data["total"] >= 0
    for rel in data["relationships"]:
        assert "id" in rel
        assert "source" in rel
        assert "target" in rel
        assert "type" in rel
        assert "observations" in rel
        assert rel["observations"] >= 1


# ============================================================
# 6. Pagination – limit and offset
# ============================================================

def test_relationships_pagination():
    res_page1 = client.get("/api/relationships?limit=3&offset=0", headers=auth_headers(INVESTIGATOR))
    res_page2 = client.get("/api/relationships?limit=3&offset=3", headers=auth_headers(INVESTIGATOR))

    assert res_page1.status_code == 200
    assert res_page2.status_code == 200

    p1 = res_page1.json()
    p2 = res_page2.json()

    # Same total on both pages
    assert p1["total"] == p2["total"]

    # No overlap in IDs
    ids_p1 = {r["id"] for r in p1["relationships"]}
    ids_p2 = {r["id"] for r in p2["relationships"]}
    assert ids_p1.isdisjoint(ids_p2), "Pages should not overlap"


# ============================================================
# 7. Deterministic ordering – same result on repeated call
# ============================================================

def test_relationships_deterministic():
    r1 = client.get("/api/relationships?limit=10", headers=auth_headers(INVESTIGATOR)).json()
    r2 = client.get("/api/relationships?limit=10", headers=auth_headers(INVESTIGATOR)).json()
    ids1 = [r["id"] for r in r1["relationships"]]
    ids2 = [r["id"] for r in r2["relationships"]]
    assert ids1 == ids2, "Order must be deterministic across calls"


# ============================================================
# 8. Entity filtering – entity_id narrows results
# ============================================================

def test_relationships_entity_filter():
    # First fetch without filter to get a valid entity
    res_all = client.get("/api/relationships?limit=5", headers=auth_headers(INVESTIGATOR))
    assert res_all.status_code == 200
    rels = res_all.json()["relationships"]

    if not rels:
        pytest.skip("No relationships found in graph – skipping filter test")

    # Use the source entity from the first result
    entity_id = rels[0]["source"]

    res_filtered = client.get(
        f"/api/relationships?entity_id={entity_id}",
        headers=auth_headers(INVESTIGATOR),
    )
    assert res_filtered.status_code == 200
    filtered = res_filtered.json()["relationships"]

    # Every result must include the entity as source or target
    for r in filtered:
        assert r["source"] == entity_id or r["target"] == entity_id, (
            f"Relationship {r['id']} does not involve entity {entity_id}"
        )


# ============================================================
# 9. Data integrity – relationships reference real entities
# ============================================================

def test_relationships_reference_real_persons():
    from pathlib import Path
    import pandas as pd

    persons_path = Path(__file__).resolve().parents[1] / "data" / "persons.csv"
    persons_df = pd.read_csv(persons_path)
    valid_ids = set(persons_df["person_id"].astype(str).str.strip())

    res = client.get("/api/relationships?limit=50", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    for rel in res.json()["relationships"]:
        assert rel["source"] in valid_ids, f"Source {rel['source']} not in persons"
        assert rel["target"] in valid_ids, f"Target {rel['target']} not in persons"


# ============================================================
# 10. Audit SUCCESS logged on success
# ============================================================

def test_relationships_audit_success():
    # Make a fresh authenticated request and verify a SUCCESS audit record exists
    res = client.get("/api/relationships?limit=1", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    # Use the audit query endpoint to verify audit records
    audit_res = client.get(
        "/api/audit?action=relationship_view&status=SUCCESS",
        headers=auth_headers(ADMIN),
    )
    assert audit_res.status_code == 200
    records = audit_res.json()["audit_records"]
    assert len(records) >= 1


# ============================================================
# 11. Audit DENIED logged on 401
# ============================================================

def test_relationships_audit_denied_unauthenticated():
    client.get("/api/relationships")
    audit_res = client.get(
        "/api/audit?action=relationship_view&status=DENIED",
        headers=auth_headers(ADMIN),
    )
    assert audit_res.status_code == 200
    records = audit_res.json()["audit_records"]
    assert len(records) >= 1


# ============================================================
# 12. No sensitive payloads in audit logs
# ============================================================

def test_relationships_audit_no_sensitive_payload():
    client.get("/api/relationships?limit=1", headers=auth_headers(INVESTIGATOR))
    audit_res = client.get(
        "/api/audit?action=relationship_view",
        headers=auth_headers(ADMIN),
    )
    assert audit_res.status_code == 200
    for log in audit_res.json()["audit_records"]:
        meta_str = str(log.get("metadata", {}) or {})
        assert "password" not in meta_str.lower()
        assert "token" not in meta_str.lower()
        assert "DataFrame" not in meta_str


# ============================================================
# 13. Max limit enforcement
# ============================================================

def test_relationships_max_limit():
    res = client.get("/api/relationships?limit=100", headers=auth_headers(INVESTIGATOR))
    assert res.status_code == 200
    assert res.json()["limit"] == 100

    # limit > 100 should return 422 validation error
    res_over = client.get("/api/relationships?limit=101", headers=auth_headers(INVESTIGATOR))
    assert res_over.status_code == 422
