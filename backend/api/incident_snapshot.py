"""
GET /api/incident_snapshot

Returns a focused incident window — events from all entities within
the requested time window (default: last 24 hours of data).

Uses existing timeline/event data loaded by CacheManager. No mock data.

Security: Protected by AuthAuditMiddleware (incident_snapshot_view action).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Query

from services.cache_manager import CacheManager


router = APIRouter(prefix="/api", tags=["Incident Snapshot"])


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy/datetime values to JSON-safe Python types."""
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


@router.get("/incident_snapshot")
def get_incident_snapshot(
    entity_id: Optional[str] = Query(
        None,
        description="Filter to a specific entity (person ID like P001). "
                    "If omitted, all entities are included.",
    ),
    window_hours: int = Query(
        24,
        ge=1,
        le=168,  # Max 7 days
        description="Number of hours to look back from the latest event timestamp. "
                    "Default 24, max 168 (7 days).",
    ),
    limit: int = Query(20, ge=1, le=100, description="Page size (1–100)."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
):
    """Return an incident window snapshot across all (or one) entity.

    Events are collected from CDR, Transactions, IPDR, and Social datasets.
    The window is computed from the LATEST available event timestamp, not
    from the current wall-clock time (because this is synthetic demo data).

    Results are sorted chronologically (newest first for easy review).
    """
    data, resolver, _ = CacheManager().get_data()

    # Build a person_id -> name lookup from persons table
    persons = data["persons"]
    person_name: dict[str, str] = {}
    person_ids: list[str] = []
    for _, row in persons.iterrows():
        pid = str(row["person_id"]).strip()
        name = str(row["name"]).strip()
        person_name[pid] = name
        person_ids.append(pid)

    # If entity_id is given, resolve it via resolver to a canonical person_id
    target_person_id: Optional[str] = None
    if entity_id:
        resolved = resolver.resolve(entity_id)
        if resolved:
            target_person_id = resolved["person_id"]

    # ----------------------------------------------------------------
    # Collect all events from CDR / Transactions / IPDR / Social
    # ----------------------------------------------------------------
    all_events: list[dict] = []

    cdr = data["cdr"]
    transactions = data["transactions"]
    ipdr = data["ipdr"]
    social = data["social"]

    # -- CDR events ---------------------------------------------------
    for _, row in cdr.iterrows():
        caller = str(row["caller"]).strip()
        receiver = str(row["receiver"]).strip()

        relevant_pids = {caller, receiver}
        if target_person_id and target_person_id not in relevant_pids:
            continue

        ts = _json_safe(row["timestamp"])

        all_events.append({
            "event_type": "CALL",
            "timestamp": ts,
            "source_dataset": "cdr.csv",
            "source": str(row["cdr_id"]),
            "caller": caller,
            "caller_name": person_name.get(caller, caller),
            "receiver": receiver,
            "receiver_name": person_name.get(receiver, receiver),
            "duration_seconds": _json_safe(row["duration_seconds"]),
            "entity_id": caller,  # primary actor
        })

    # -- Transaction events ------------------------------------------
    # Map bank_account -> person_id for enrichment
    account_to_person: dict[str, str] = {}
    for _, row in persons.iterrows():
        pid = str(row["person_id"]).strip()
        acc = str(row["bank_account"]).strip()
        account_to_person[acc] = pid

    for _, row in transactions.iterrows():
        sender_acc = str(row["sender_account"]).strip()
        receiver_acc = str(row["receiver_account"]).strip()

        sender_pid = account_to_person.get(sender_acc, sender_acc)
        receiver_pid = account_to_person.get(receiver_acc, receiver_acc)

        relevant_pids = {sender_pid, receiver_pid}
        if target_person_id and target_person_id not in relevant_pids:
            continue

        ts = _json_safe(row["timestamp"])

        all_events.append({
            "event_type": "TRANSACTION",
            "timestamp": ts,
            "source_dataset": "transactions.csv",
            "source": str(row["transaction_id"]),
            "sender": sender_acc,
            "sender_entity_id": sender_pid,
            "sender_name": person_name.get(sender_pid, sender_acc),
            "receiver": receiver_acc,
            "receiver_entity_id": receiver_pid,
            "receiver_name": person_name.get(receiver_pid, receiver_acc),
            "amount": _json_safe(row["amount"]),
            "channel": str(row["channel"]),
            "entity_id": sender_pid,
        })

    # -- IPDR events -------------------------------------------------
    for _, row in ipdr.iterrows():
        pid = str(row["person_id"]).strip()
        if target_person_id and pid != target_person_id:
            continue

        ts = _json_safe(row["timestamp"])

        all_events.append({
            "event_type": "IP_ACTIVITY",
            "timestamp": ts,
            "source_dataset": "ipdr.csv",
            "source": str(row["ipdr_id"]),
            "entity_id": pid,
            "entity_name": person_name.get(pid, pid),
            "ip_address": str(row["ip_address"]),
            "device_id": str(row["device_id"]),
            "session_duration_seconds": _json_safe(row["session_duration_seconds"]),
        })

    # -- Social events -----------------------------------------------
    for _, row in social.iterrows():
        pid = str(row["person_id"]).strip()
        if target_person_id and pid != target_person_id:
            continue

        ts = _json_safe(row["timestamp"])

        all_events.append({
            "event_type": "SOCIAL_ACTIVITY",
            "timestamp": ts,
            "source_dataset": "social.csv",
            "source": str(row["social_event_id"]),
            "entity_id": pid,
            "entity_name": person_name.get(pid, pid),
            "platform": str(row["platform"]),
            "activity_type": str(row["activity_type"]),
        })

    # ----------------------------------------------------------------
    # Compute window: use the latest event timestamp as reference
    # so the demo data always shows a meaningful window.
    # ----------------------------------------------------------------
    timestamps = [e["timestamp"] for e in all_events if e.get("timestamp")]

    if not timestamps:
        return {
            "entity_id": entity_id,
            "case_id": "CASE-2026-1024",
            "window_start": None,
            "window_end": None,
            "total_events": 0,
            "events": [],
            "limit": limit,
            "offset": offset,
        }

    # Sort ISO strings — works because they are comparable lexicographically
    window_end_str = max(timestamps)
    window_start_str = None

    # Parse the max timestamp to compute start
    try:
        # Handle both offset-aware and naive datetimes from isoformat
        end_dt = datetime.fromisoformat(window_end_str.replace("Z", "+00:00"))
        from datetime import timedelta
        start_dt = end_dt - timedelta(hours=window_hours)
        window_start_str = start_dt.isoformat()
    except Exception:
        # Fallback: string comparison (ISO format is lexicographically sortable)
        window_start_str = None

    # Filter events to the window
    if window_start_str:
        all_events = [
            e for e in all_events
            if e.get("timestamp") and e["timestamp"] >= window_start_str
        ]

    # Sort newest first (reverse chronological for incident review)
    all_events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

    total = len(all_events)
    page = all_events[offset: offset + limit]

    return {
        "entity_id": entity_id,
        "case_id": "CASE-2026-1024",
        "window_start": window_start_str,
        "window_end": window_end_str,
        "total_events": total,
        "events": page,
        "limit": limit,
        "offset": offset,
    }
