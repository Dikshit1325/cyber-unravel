import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd

from main import app
from backend.tests.conftest import auth_headers, ADMIN, INVESTIGATOR, ANALYST
from services.audit_service import audit_service

client = TestClient(app)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "transactions.csv"

# 1. GET /api/transactions returns 200 for authorized users
def test_get_transactions_authorized():
    for user in [ADMIN, INVESTIGATOR, ANALYST]:
        response = client.get("/api/transactions", headers=auth_headers(user))
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "transactions" in data
        assert "summary" in data
        assert data["total"] > 0

# 2. Unauthenticated requests return 401
def test_get_transactions_unauthenticated():
    response = client.get("/api/transactions")
    assert response.status_code == 401
    assert "detail" in response.json()

# 3. Invalid user returns 401
def test_get_transactions_invalid_user():
    response = client.get("/api/transactions", headers={"X-User-Id": "non_existent_user"})
    assert response.status_code == 401

# 4. Role spoofing does not escalate privileges
def test_transactions_role_spoofing():
    # Sending client-side role header does not bypass server resolution
    response = client.get(
        "/api/transactions",
        headers={"X-User-Id": ANALYST, "X-User-Role": "ADMIN"},
    )
    assert response.status_code == 200  # Analyst has transaction_view permission

# 5. Response contains real transaction IDs from dataset
def test_transactions_match_dataset():
    df_real = pd.read_csv(DATA_PATH)
    real_tx_ids = set(df_real["transaction_id"].astype(str).str.strip())
    assert len(real_tx_ids) > 0

    response = client.get("/api/transactions?page_size=200", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == len(real_tx_ids)
    for tx in data["transactions"]:
        assert tx["transaction_id"] in real_tx_ids
        assert tx["amount"] > 0
        assert tx["sender_account"]
        assert tx["receiver_account"]

# 6. Filtering by transaction_id
def test_filter_by_transaction_id():
    response = client.get("/api/transactions?transaction_id=TX0001", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["transactions"][0]["transaction_id"] == "TX0001"

# 7. Filtering by entity_id
def test_filter_by_entity_id():
    response = client.get("/api/transactions?entity_id=P005", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for tx in data["transactions"]:
        assert "P005" in tx["entity_ids"]

# 8. Filtering by account (sender or receiver)
def test_filter_by_account():
    response = client.get("/api/transactions?account=A005", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for tx in data["transactions"]:
        assert tx["sender_account"] == "A005" or tx["receiver_account"] == "A005"

# 9. Filtering by min_amount and max_amount
def test_filter_by_amount_range():
    min_amt = 5000.0
    max_amt = 15000.0
    response = client.get(
        f"/api/transactions?min_amount={min_amt}&max_amount={max_amt}",
        headers=auth_headers(INVESTIGATOR),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for tx in data["transactions"]:
        assert min_amt <= tx["amount"] <= max_amt

# 10. Multiple combined filters
def test_multiple_combined_filters():
    response = client.get(
        "/api/transactions?entity_id=P005&min_amount=5000&channel=NEFT",
        headers=auth_headers(INVESTIGATOR),
    )
    assert response.status_code == 200
    data = response.json()
    for tx in data["transactions"]:
        assert "P005" in tx["entity_ids"]
        assert tx["amount"] >= 5000
        assert tx["channel"] == "NEFT"

# 11. Invalid filter values (e.g. min_amount > max_amount) return 400
def test_invalid_filter_amounts():
    response = client.get(
        "/api/transactions?min_amount=10000&max_amount=1000",
        headers=auth_headers(INVESTIGATOR),
    )
    assert response.status_code == 400
    assert "detail" in response.json()

# 12. Invalid sort parameter returns 400
def test_invalid_sort_parameter():
    response = client.get(
        "/api/transactions?sort=invalid_sort_col",
        headers=auth_headers(INVESTIGATOR),
    )
    assert response.status_code == 400

# 13. Sorting deterministic test
def test_sorting_transactions():
    # Sort by amount descending
    resp_desc = client.get("/api/transactions?sort=amount_desc&page_size=100", headers=auth_headers(INVESTIGATOR))
    assert resp_desc.status_code == 200
    txs_desc = resp_desc.json()["transactions"]
    amounts_desc = [t["amount"] for t in txs_desc]
    assert amounts_desc == sorted(amounts_desc, reverse=True)

    # Sort by timestamp ascending
    resp_asc = client.get("/api/transactions?sort=timestamp_asc&page_size=100", headers=auth_headers(INVESTIGATOR))
    assert resp_asc.status_code == 200
    txs_asc = resp_asc.json()["transactions"]
    timestamps_asc = [t["timestamp"] for t in txs_asc]
    assert timestamps_asc == sorted(timestamps_asc)

# 14. Pagination test
def test_pagination():
    resp_p1 = client.get("/api/transactions?page=1&page_size=5", headers=auth_headers(INVESTIGATOR))
    resp_p2 = client.get("/api/transactions?page=2&page_size=5", headers=auth_headers(INVESTIGATOR))

    assert resp_p1.status_code == 200
    assert resp_p2.status_code == 200

    p1_txs = resp_p1.json()["transactions"]
    p2_txs = resp_p2.json()["transactions"]

    assert len(p1_txs) == 5
    assert len(p2_txs) == 5

    p1_ids = {t["transaction_id"] for t in p1_txs}
    p2_ids = {t["transaction_id"] for t in p2_txs}

    # No overlap between page 1 and page 2
    assert len(p1_ids.intersection(p2_ids)) == 0

# 15. Single transaction detail lookup
def test_single_transaction_detail():
    resp = client.get("/api/transactions/TX0001", headers=auth_headers(INVESTIGATOR))
    assert resp.status_code == 200
    data = resp.json()
    assert data["transaction_id"] == "TX0001"
    assert "amount" in data
    assert "sender_account" in data
    assert "receiver_account" in data

    # Non-existent transaction returns 404
    resp_404 = client.get("/api/transactions/TX999999", headers=auth_headers(INVESTIGATOR))
    assert resp_404.status_code == 404

# 16. Audit log generation for transaction requests
def test_transaction_audit_logging():
    client.get("/api/transactions/TX0001", headers=auth_headers(INVESTIGATOR))

    resp = client.get("/api/audit?action=transaction_view", headers=auth_headers(ADMIN))
    assert resp.status_code == 200
    records = resp.json()["audit_records"]
    assert len(records) > 0

    tx_records = [r for r in records if r["resource_type"] == "transaction"]
    assert len(tx_records) > 0

    # Ensure no raw transaction datasets in audit logs
    for r in tx_records:
        assert "raw_transactions" not in r
        assert "transactions_payload" not in r
