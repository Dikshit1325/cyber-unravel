import pytest
from fastapi.testclient import TestClient
from main import app
from backend.tests.conftest import auth_headers, INVESTIGATOR

client = TestClient(app)

def test_unfiltered_anomalies():
    response = client.get("/api/anomalies", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "summary" in data
    assert "anomalies" in data
    assert data["total"] == len(data["anomalies"])
    summary = data["summary"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_severity_filter():
    response = client.get("/api/anomalies?severity=CRITICAL", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["anomalies"])
    for a in data["anomalies"]:
        assert a["severity"] == "CRITICAL"
    summary = data["summary"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_min_score_filter():
    response = client.get("/api/anomalies?min_score=80", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["anomalies"])
    for a in data["anomalies"]:
        score = a.get("score") if "score" in a else a.get("correlation_score")
        assert score >= 80
    summary = data["summary"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_combined_filter():
    response = client.get("/api/anomalies?severity=CRITICAL&min_score=80", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["anomalies"])
    summary = data["summary"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_entity_filter():
    unfiltered = client.get("/api/anomalies", headers=auth_headers(INVESTIGATOR)).json()
    valid_entity = None
    for a in unfiltered["anomalies"]:
        if a.get("entity_ids"):
            valid_entity = a["entity_ids"][0]
            break
    assert valid_entity is not None

    response = client.get(f"/api/anomalies?entity_id={valid_entity}", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["anomalies"])
    for a in data["anomalies"]:
        assert valid_entity in a["entity_ids"]
    summary = data["summary"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_anomaly_type_filter():
    response = client.get("/api/anomalies?anomaly_type=SHARED_IP", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["anomalies"])
    for a in data["anomalies"]:
        assert a["anomaly_type"] == "SHARED_IP"
    summary = data["summary"]
    assert summary["network"] == data["total"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_empty_filter_result():
    response = client.get("/api/anomalies?anomaly_type=NON_EXISTENT_TYPE", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "total": 0,
        "summary": {
            "financial": 0,
            "telecom": 0,
            "network": 0,
            "cross_domain": 0,
        },
        "anomalies": [],
    }

def test_multiple_filters():
    response = client.get("/api/anomalies?severity=HIGH&min_score=50&source=telecom", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["anomalies"])
    summary = data["summary"]
    total_summary = (
        summary["financial"]
        + summary["telecom"]
        + summary["network"]
        + summary["cross_domain"]
    )
    assert total_summary == data["total"]

def test_invalid_sort_param():
    response = client.get("/api/anomalies?sort=invalid_sort", headers=auth_headers(INVESTIGATOR))
    assert response.status_code == 400
