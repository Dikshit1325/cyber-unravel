from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["Lead"])

@router.get("/lead")
def get_lead():
    """Return the most critical anomaly as an actionable lead"""
    from services.cache_manager import CacheManager
    from services.anomaly_engine import AnomalyEngine
    data, _, _ = CacheManager().get_data()
    engine = AnomalyEngine(data)
    anomalies = engine.detect_all()["all"]
    # Define severity ranking
    severity_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    # Sort descending by severity rank, then by score
    sorted_anoms = sorted(
        anomalies,
        key=lambda a: (
            severity_rank.get(str(a.get("severity", "MEDIUM")).upper(), 2),
            a.get("score") if a.get("score") is not None else a.get("correlation_score", 0),
        ),
        reverse=True,
    )
    if not sorted_anoms:
        raise HTTPException(status_code=404, detail="No anomalies available for lead")
    top = sorted_anoms[0]
    finding_id = top.get("finding_id") or top.get("id") or "ANO-01"
    title = top.get("title") or (str(top.get("anomaly_type", "Suspicious Pattern")).replace("_", " ").title())
    subtitle = top.get("explanation") or top.get("subtitle") or ""
    entity_id = top.get("entity_ids", [None])[0] if top.get("entity_ids") else None
    return {
        "id": finding_id,
        "type": "Anomaly",
        "title": title,
        "subtitle": subtitle,
        "entity_id": entity_id,
        "route": "/anomalies",
    }
