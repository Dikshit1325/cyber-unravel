# backend/api/entities.py
"""Entity API routes.
Provides endpoint for retrieving entity details and a unified summary.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any

from services.entity_resolution import EntityResolver
from services.cache_manager import CacheManager
from services.transaction_analysis import TransactionEngine
from services.communication_analysis import CommunicationEngine
from services.ipdr_analysis import IPDRAnalysisEngine
from services.anomaly_engine import AnomalyEngine
from services.audit_service import audit_logger

router = APIRouter(prefix="/api/entity", tags=["Entity"])

# Existing endpoint to get full entity details
@router.get("/{entity_id}", response_model=Dict[str, Any])
async def get_entity(entity_id: str):
    # Resolve entity information
    resolver = EntityResolver()
    entity = resolver.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity

# New unified summary endpoint
@router.get("/{entity_id}/summary", response_model=Dict[str, Any])
async def get_entity_summary(
    entity_id: str,
    recent_limit: int = Query(5, ge=1, le=20, description="Number of recent items per domain"),
):
    """Return a concise summary of an entity across all domains.
    Includes counts and recent activity slices for accounts, transactions,
    communications, network/IPDR, and anomalies.
    """
    # Resolve core entity info
    resolver = EntityResolver()
    entity = resolver.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

    # Cache manager to obtain raw data for analysis engines
    cache = CacheManager()
    data, _, _ = cache.get_data()

    # Prepare summary sections
    summary: Dict[str, Any] = {
        "entity": entity,
        "accounts": [],
        "transactions": [],
        "communications": [],
        "network": [],
        "anomalies": [],
    }

    # Accounts – already part of entity object
    summary["accounts"] = entity.get("bank_accounts", [])[:recent_limit]

    # Transactions – filter by entity_id
    tx_engine = TransactionEngine(data)
    txs = tx_engine.get_by_entity(entity_id, limit=recent_limit)
    summary["transactions"] = txs

    # Communications – filter by entity_id
    comm_engine = CommunicationEngine(data)
    comms = comm_engine.get_by_entity(entity_id, limit=recent_limit)
    summary["communications"] = comms

    # Network/IPDR – filter by entity_id
    ipdr_engine = IPDRAnalysisEngine(data)
    ipdrs = ipdr_engine.get_by_entity(entity_id, limit=recent_limit)
    summary["network"] = ipdrs

    # Anomalies – filter by entity_id
    anomaly_engine = AnomalyEngine(data)
    anomalies_all = anomaly_engine.detect_all()["all"]
    related_anomalies = [a for a in anomalies_all if entity_id in a.get("entity_ids", [])][:recent_limit]
    summary["anomalies"] = related_anomalies

    # Audit the request (resource_type = entity_summary)
    audit_logger.log(
        action="read",
        resource_type="entity_summary",
        resource_id=entity_id,
        status="success",
        user_id="{{user_id}}",  # placeholder – actual user resolved in middleware
    )

    return summary
