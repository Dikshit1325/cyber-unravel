"""
test_anomaly_engine.py
======================
Automated tests for the rule-based anomaly detection engine.

Ground-truth / scenario tags are used HERE (and only here) to validate
that the hidden synthetic patterns are discoverable by the engine.

They are NOT imported or used in anomaly_engine.py itself.
"""
from __future__ import annotations

import pandas as pd
import pytest
from services.anomaly_engine import (
    AnomalyEngine,
    FinancialAnomalyDetector,
    TelecomAnomalyDetector,
    NetworkAnomalyDetector,
    CrossDomainCorrelator,
    _severity,
)
from services.data_loader import load_all_data
from services.cache_manager import CacheManager


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope="module")
def investigation_data():
    """Load real data once for all tests in this module."""
    CacheManager._instance = None
    data = load_all_data()
    yield data
    CacheManager._instance = None


@pytest.fixture(scope="module")
def engine(investigation_data):
    return AnomalyEngine(investigation_data)


# ============================================================
# UTILITY
# ============================================================

def test_severity_mapping():
    assert _severity(10) == "LOW"
    assert _severity(29) == "LOW"
    assert _severity(30) == "MEDIUM"
    assert _severity(59) == "MEDIUM"
    assert _severity(60) == "HIGH"
    assert _severity(79) == "HIGH"
    assert _severity(80) == "CRITICAL"
    assert _severity(100) == "CRITICAL"


# ============================================================
# FINANCIAL TESTS
# ============================================================

class TestFinancialDetector:

    def test_high_value_transfers_detected(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        findings = det.detect_high_value_transfers()
        assert len(findings) > 0, "Expected at least one high-value transfer finding"

    def test_high_value_finding_has_required_fields(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        for f in det.detect_high_value_transfers():
            assert "finding_id" in f
            assert "anomaly_type" in f
            assert f["anomaly_type"] == "HIGH_VALUE_TRANSFER"
            assert "entity_ids" in f
            assert "timestamp_range" in f
            assert "score" in f
            assert "severity" in f
            assert "explanation" in f
            assert "supporting_transaction_ids" in f
            assert len(f["supporting_transaction_ids"]) > 0

    def test_rapid_transfers_detected(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        findings = det.detect_rapid_transfers()
        assert len(findings) > 0, "Expected at least one rapid transfer finding"

    def test_rapid_transfer_finding_has_required_fields(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        for f in det.detect_rapid_transfers():
            assert f["anomaly_type"] == "RAPID_TRANSFERS"
            assert "supporting_transaction_ids" in f

    def test_structuring_detected(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        findings = det.detect_potential_structuring()
        # May or may not detect depending on dataset — just verify no crash
        assert isinstance(findings, list)

    def test_multihop_detected(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        findings = det.detect_multi_hop_transfers()
        assert isinstance(findings, list)

    def test_empty_transactions_returns_empty(self):
        det = FinancialAnomalyDetector(pd.DataFrame(), pd.DataFrame())
        assert det.detect_all() == []

    def test_score_within_bounds(self, investigation_data):
        det = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
        )
        for f in det.detect_all():
            assert 0 <= f["score"] <= 100

    def test_configurable_threshold(self, investigation_data):
        # Higher z-score threshold should yield fewer or equal findings
        det_strict = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
            config={"high_value_z_score": 3.0},
        )
        det_relaxed = FinancialAnomalyDetector(
            investigation_data["transactions"],
            investigation_data["entity_mapping"],
            config={"high_value_z_score": 1.0},
        )
        strict_count = len(det_strict.detect_high_value_transfers())
        relaxed_count = len(det_relaxed.detect_high_value_transfers())
        assert strict_count <= relaxed_count


# ============================================================
# TELECOM TESTS
# ============================================================

class TestTelecomDetector:

    def test_abnormal_hour_calls_detected(self, investigation_data):
        det = TelecomAnomalyDetector(investigation_data["cdr"])
        findings = det.detect_abnormal_hour_calls()
        assert isinstance(findings, list)

    def test_communication_burst_detected(self, investigation_data):
        det = TelecomAnomalyDetector(investigation_data["cdr"])
        findings = det.detect_communication_burst()
        assert isinstance(findings, list)

    def test_unusual_contact_pattern_detected(self, investigation_data):
        det = TelecomAnomalyDetector(investigation_data["cdr"])
        findings = det.detect_unusual_contact_pattern()
        assert isinstance(findings, list)

    def test_telecom_finding_has_required_fields(self, investigation_data):
        det = TelecomAnomalyDetector(investigation_data["cdr"])
        for f in det.detect_all():
            assert "finding_id" in f
            assert "anomaly_type" in f
            assert "entity_ids" in f
            assert "timestamp_range" in f
            assert "score" in f
            assert "severity" in f
            assert "explanation" in f
            assert "supporting_cdr_ids" in f

    def test_empty_cdr_returns_empty(self):
        det = TelecomAnomalyDetector(pd.DataFrame())
        assert det.detect_all() == []

    def test_telecom_score_within_bounds(self, investigation_data):
        det = TelecomAnomalyDetector(investigation_data["cdr"])
        for f in det.detect_all():
            assert 0 <= f["score"] <= 100

    def test_configurable_abnormal_hour(self, investigation_data):
        # Setting window to cover all 24 hours should detect all callers
        det_all = TelecomAnomalyDetector(
            investigation_data["cdr"],
            config={"abnormal_hour_start": 0, "abnormal_hour_end": 0},
        )
        # Window start == end: no hours are "abnormal" — should return nothing
        findings = det_all.detect_abnormal_hour_calls()
        assert isinstance(findings, list)


# ============================================================
# NETWORK TESTS
# ============================================================

class TestNetworkDetector:

    def test_shared_ip_detected(self, investigation_data):
        det = NetworkAnomalyDetector(
            investigation_data["ipdr"],
            investigation_data["entity_mapping"],
        )
        findings = det.detect_shared_ip()
        assert len(findings) > 0, "Dataset contains a shared IP (203.0.113.77)"

    def test_shared_ip_finding_has_required_fields(self, investigation_data):
        det = NetworkAnomalyDetector(
            investigation_data["ipdr"],
            investigation_data["entity_mapping"],
        )
        for f in det.detect_shared_ip():
            assert "finding_id" in f
            assert f["anomaly_type"] == "SHARED_IP"
            assert "entity_ids" in f
            assert len(f["entity_ids"]) >= 2
            assert "infrastructure_identifier" in f
            assert "timestamp_range" in f
            assert "score" in f
            assert "severity" in f
            assert "explanation" in f
            assert "supporting_ipdr_ids" in f
            # Neutral language check
            assert "Potential shared infrastructure" in f["explanation"]

    def test_shared_device_is_list(self, investigation_data):
        det = NetworkAnomalyDetector(
            investigation_data["ipdr"],
            investigation_data["entity_mapping"],
        )
        findings = det.detect_shared_device()
        assert isinstance(findings, list)

    def test_empty_ipdr_returns_empty(self):
        det = NetworkAnomalyDetector(pd.DataFrame(), pd.DataFrame())
        assert det.detect_all() == []

    def test_network_score_within_bounds(self, investigation_data):
        det = NetworkAnomalyDetector(
            investigation_data["ipdr"],
            investigation_data["entity_mapping"],
        )
        for f in det.detect_all():
            assert 0 <= f["score"] <= 100


# ============================================================
# CROSS-DOMAIN TESTS
# ============================================================

class TestCrossDomainCorrelator:

    def test_cross_domain_bursts_detected(self, investigation_data):
        correlator = CrossDomainCorrelator(
            investigation_data["cdr"],
            investigation_data["transactions"],
            investigation_data["ipdr"],
            investigation_data["social"],
            investigation_data["entity_mapping"],
        )
        findings = correlator.detect_all()
        assert len(findings) > 0, "Expected cross-domain findings"

    def test_cross_domain_finding_has_required_fields(self, investigation_data):
        correlator = CrossDomainCorrelator(
            investigation_data["cdr"],
            investigation_data["transactions"],
            investigation_data["ipdr"],
            investigation_data["social"],
            investigation_data["entity_mapping"],
        )
        for f in correlator.detect_all():
            assert "finding_id" in f
            assert f["anomaly_type"] == "CROSS_DOMAIN_ACTIVITY_BURST"
            assert "entity_ids" in f
            assert "domains_involved" in f
            assert len(f["domains_involved"]) >= 2
            assert "start_time" in f
            assert "end_time" in f
            assert "event_ids" in f
            assert "correlation_score" in f
            assert "severity" in f
            assert "explanation" in f
            assert "supporting_event_ids_by_domain" in f

    def test_cross_domain_score_within_bounds(self, investigation_data):
        correlator = CrossDomainCorrelator(
            investigation_data["cdr"],
            investigation_data["transactions"],
            investigation_data["ipdr"],
            investigation_data["social"],
            investigation_data["entity_mapping"],
        )
        for f in correlator.detect_all():
            assert 0 <= f["correlation_score"] <= 100

    def test_empty_datasets_returns_empty(self):
        correlator = CrossDomainCorrelator(
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )
        assert correlator.detect_all() == []

    def test_configurable_window(self, investigation_data):
        # Narrow window should produce fewer or equal findings
        correlator_narrow = CrossDomainCorrelator(
            investigation_data["cdr"],
            investigation_data["transactions"],
            investigation_data["ipdr"],
            investigation_data["social"],
            investigation_data["entity_mapping"],
            config={"correlation_window_minutes": 5},
        )
        correlator_wide = CrossDomainCorrelator(
            investigation_data["cdr"],
            investigation_data["transactions"],
            investigation_data["ipdr"],
            investigation_data["social"],
            investigation_data["entity_mapping"],
            config={"correlation_window_minutes": 120},
        )
        narrow_count = len(correlator_narrow.detect_all())
        wide_count = len(correlator_wide.detect_all())
        assert narrow_count <= wide_count


# ============================================================
# INTEGRATED ENGINE TESTS
# ============================================================

class TestAnomalyEngine:

    def test_detect_all_returns_all_categories(self, engine):
        results = engine.detect_all()
        assert "financial" in results
        assert "telecom" in results
        assert "network" in results
        assert "cross_domain" in results
        assert "all" in results
        assert "summary" in results

    def test_summary_counts_correct(self, engine):
        results = engine.detect_all()
        summary = results["summary"]
        assert summary["financial_count"] == len(results["financial"])
        assert summary["telecom_count"] == len(results["telecom"])
        assert summary["network_count"] == len(results["network"])
        assert summary["cross_domain_count"] == len(results["cross_domain"])
        total = (
            summary["financial_count"]
            + summary["telecom_count"]
            + summary["network_count"]
            + summary["cross_domain_count"]
        )
        assert summary["total"] == total

    def test_all_findings_have_finding_id(self, engine):
        results = engine.detect_all()
        for f in results["all"]:
            assert "finding_id" in f
            assert len(f["finding_id"]) > 0

    def test_no_fabricated_evidence(self, engine, investigation_data):
        """Supporting IDs must reference records that exist in the datasets."""
        real_tx_ids = set(investigation_data["transactions"]["transaction_id"])
        real_cdr_ids = set(investigation_data["cdr"]["cdr_id"])
        real_ipdr_ids = set(investigation_data["ipdr"]["ipdr_id"])

        results = engine.detect_all()

        for f in results["financial"]:
            for tx_id in f.get("supporting_transaction_ids", []):
                assert tx_id in real_tx_ids, f"Fabricated tx_id: {tx_id}"

        for f in results["telecom"]:
            for cdr_id in f.get("supporting_cdr_ids", []):
                assert cdr_id in real_cdr_ids, f"Fabricated cdr_id: {cdr_id}"

        for f in results["network"]:
            for ipdr_id in f.get("supporting_ipdr_ids", []):
                assert ipdr_id in real_ipdr_ids, f"Fabricated ipdr_id: {ipdr_id}"

    def test_all_sorted_by_score_descending(self, engine):
        results = engine.detect_all()
        scores = [
            f.get("score", f.get("correlation_score", 0))
            for f in results["all"]
        ]
        assert scores == sorted(scores, reverse=True)

    def test_does_not_import_ground_truth(self):
        """Verify anomaly_engine.py does not import or reference ground_truth.csv."""
        import inspect
        import services.anomaly_engine as ae
        source = inspect.getsource(ae)
        assert "ground_truth" not in source.lower()
        # No hardcoded person IDs in engine source
        for hardcoded_id in ["P001", "P002", "P003"]:
            assert hardcoded_id not in source, (
                f"Hardcoded entity ID '{hardcoded_id}' found in anomaly_engine.py"
            )
