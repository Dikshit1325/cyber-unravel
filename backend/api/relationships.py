"""
GET /api/relationships

Returns hidden relationships derived from the investigation graph.
Uses existing graph_engine and cache_manager logic — no mock data.

Security: Protected by AuthAuditMiddleware (relationship_view action).
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Query

from services.cache_manager import CacheManager
from services.graph_engine import person_node


router = APIRouter(prefix="/api", tags=["Relationships"])


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy/datetime values to JSON-safe Python types."""
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


@router.get("/relationships")
def get_relationships(
    entity_id: Optional[str] = Query(
        None,
        description="Filter: only return relationships involving this entity ID (person ID like P001).",
    ),
    limit: int = Query(20, ge=1, le=100, description="Page size (1–100)."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
):
    """Return hidden relationships derived from the investigation graph.

    Relationships are extracted from the pre-built NetworkX investigation graph
    (built by CacheManager using real CDR, transaction, IPDR, and social data).

    Results are ordered deterministically: by edge weight/count descending,
    then by relationship ID ascending.

    Supports optional filtering by entity_id (matches source or target person node).
    """
    _, resolver, graph = CacheManager().get_data()

    # Build a person_id -> name lookup from the resolver for richer labels
    person_name: dict[str, str] = {}
    for node_id, attrs in graph.nodes(data=True):
        if attrs.get("node_type") == "PERSON":
            pid = attrs.get("entity_id", "")
            person_name[pid] = attrs.get("name", pid)

    # Build a collapsed relationship index: (src_person, rel_type, tgt_person) -> agg dict
    # We only surface PERSON-to-PERSON edges (CALLED, TRANSFERRED via person lookup)
    # plus direct PERSON -> PERSON edges like CALLED from CDR.
    rel_index: dict[str, dict] = {}

    for src, tgt, attrs in graph.edges(data=True):
        src_attrs = graph.nodes.get(src, {})
        tgt_attrs = graph.nodes.get(tgt, {})

        src_type = src_attrs.get("node_type", "")
        tgt_type = tgt_attrs.get("node_type", "")

        # Only surface relationships between PERSON nodes (CALLED edges)
        if src_type != "PERSON" or tgt_type != "PERSON":
            continue

        src_pid = src_attrs.get("entity_id", src)
        tgt_pid = tgt_attrs.get("entity_id", tgt)
        rel_type = attrs.get("relationship", "UNKNOWN")

        key = f"{src_pid}__{rel_type}__{tgt_pid}"

        if key not in rel_index:
            rel_index[key] = {
                "id": key,
                "source": src_pid,
                "source_name": person_name.get(src_pid, src_pid),
                "target": tgt_pid,
                "target_name": person_name.get(tgt_pid, tgt_pid),
                "type": rel_type,
                "observations": 0,
                "first_seen": None,
                "last_seen": None,
                "source_dataset": attrs.get("source_dataset", ""),
            }

        rel_index[key]["observations"] += 1

        ts = _json_safe(attrs.get("timestamp"))
        if ts:
            entry = rel_index[key]
            if entry["first_seen"] is None or ts < entry["first_seen"]:
                entry["first_seen"] = ts
            if entry["last_seen"] is None or ts > entry["last_seen"]:
                entry["last_seen"] = ts

    relationships = list(rel_index.values())

    # Optional entity_id filter — show only rows where source or target matches
    if entity_id:
        relationships = [
            r for r in relationships
            if r["source"] == entity_id or r["target"] == entity_id
        ]

    # Deterministic ordering: most-observed first, then by ID
    relationships.sort(key=lambda r: (-r["observations"], r["id"]))

    total = len(relationships)
    page = relationships[offset: offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "relationships": page,
    }
