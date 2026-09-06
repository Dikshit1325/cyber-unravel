from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime

from services.cache_manager import CacheManager
from services.anomaly_engine import AnomalyEngine

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])

def _parse_iso(dt_str: str) -> datetime:
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid datetime format: {dt_str}")

@router.get("/", response_model=None)
def get_anomalies(
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly_type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum anomaly score"),
    source: Optional[str] = Query(None, description="Filter by source/domain where applicable"),
    start_time: Optional[str] = Query(None, description="ISO start timestamp for filter range"),
    end_time: Optional[str] = Query(None, description="ISO end timestamp for filter range"),
    sort: Optional[str] = Query("score_desc", description="Sorting: currently only 'score_desc' supported"),
):
    # Retrieve cached data using CacheManager (Phase 1)
    cache = CacheManager()
    data, _, _ = cache.get_data()
    engine = AnomalyEngine(data)
    results = engine.detect_all()
    all_findings = results["all"]

    # Category ID sets for filtered summary mapping
    fin_ids = {id(f) for f in results.get("financial", [])}
    tel_ids = {id(f) for f in results.get("telecom", [])}
    net_ids = {id(f) for f in results.get("network", [])}
    cd_ids = {id(f) for f in results.get("cross_domain", [])}

    # Apply filters
    filtered: List[dict] = []
    for f in all_findings:
        if anomaly_type and f.get("anomaly_type") != anomaly_type:
            continue
        if entity_id and entity_id not in f.get("entity_ids", []):
            continue
        if severity and f.get("severity", "").lower() != severity.lower():
            continue
        score_val = f.get("score") if "score" in f else f.get("correlation_score")
        if min_score is not None and (score_val is None or score_val < min_score):
            continue
        if source:
            src_match = False
            if "source" in f and f["source"] == source:
                src_match = True
            if "domains_involved" in f and source in f["domains_involved"]:
                src_match = True
            if not src_match:
                continue
        if start_time or end_time:
            tr = f.get("timestamp_range", {})
            if not tr:
                continue
            range_start = _parse_iso(tr.get("start"))
            range_end = _parse_iso(tr.get("end"))
            if start_time:
                filter_start = _parse_iso(start_time)
                if range_end < filter_start:
                    continue
            if end_time:
                filter_end = _parse_iso(end_time)
                if range_start > filter_end:
                    continue
        filtered.append(f)

    # Sorting – default by descending score / correlation_score
    if sort == "score_desc":
        filtered.sort(key=lambda x: x.get("score") if "score" in x else x.get("correlation_score", 0), reverse=True)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sort parameter")

    # Summary counts per category based on FILTERED results
    summary = {
        "financial": sum(1 for f in filtered if id(f) in fin_ids),
        "telecom": sum(1 for f in filtered if id(f) in tel_ids),
        "network": sum(1 for f in filtered if id(f) in net_ids),
        "cross_domain": sum(1 for f in filtered if id(f) in cd_ids),
    }

    response = {
        "total": len(filtered),
        "summary": summary,
        "anomalies": filtered,
    }
    return response
