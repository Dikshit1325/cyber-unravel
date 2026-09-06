from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional, Dict, Any

from services.cache_manager import CacheManager

router = APIRouter(prefix="/api/communications", tags=["Communications"])

@router.get("/", response_model=None)
def get_communications(
    communication_id: Optional[str] = Query(None, description="Filter by exact CDR / communication ID"),
    cdr_id: Optional[str] = Query(None, description="Alias for communication_id"),
    entity_id: Optional[str] = Query(None, description="Filter by associated entity ID (e.g. P001)"),
    caller: Optional[str] = Query(None, description="Filter by caller entity or identifier"),
    receiver: Optional[str] = Query(None, description="Filter by receiver entity or identifier"),
    phone: Optional[str] = Query(None, description="Filter by caller or receiver phone number"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum call duration in seconds"),
    max_duration: Optional[int] = Query(None, ge=0, description="Maximum call duration in seconds"),
    start_time: Optional[str] = Query(None, description="Filter start timestamp"),
    end_time: Optional[str] = Query(None, description="Filter end timestamp"),
    scenario_tag: Optional[str] = Query(None, description="Filter by scenario tag (NORMAL, etc.)"),
    sort: Optional[str] = Query("timestamp_desc", description="Sorting: timestamp_desc, timestamp_asc, duration_desc, duration_asc"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Page size"),
):
    if min_duration is not None and max_duration is not None and min_duration > max_duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_duration cannot be greater than max_duration",
        )

    allowed_sorts = ["timestamp_desc", "timestamp_asc", "duration_desc", "duration_asc"]
    if sort and sort not in allowed_sorts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameter. Allowed values: {', '.join(allowed_sorts)}",
        )

    target_id = communication_id or cdr_id

    # Load cached investigation data
    data, resolver, _ = CacheManager().get_data()
    df_cdr = data.get("cdr")

    if df_cdr is None or df_cdr.empty:
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "summary": {
                "total_calls": 0,
                "total_duration_seconds": 0,
                "avg_duration_seconds": 0.0,
                "high_priority_count": 0,
                "unique_contacts": 0,
                "filtered_count": 0,
            },
            "communications": [],
        }

    # Build enriched communication records
    records: List[Dict[str, Any]] = []
    for _, row in df_cdr.iterrows():
        c_id = str(row["cdr_id"]).strip()
        c_caller = str(row["caller"]).strip()
        c_receiver = str(row["receiver"]).strip()
        c_time = str(row["timestamp"]).strip()
        c_duration = int(row["duration_seconds"]) if row["duration_seconds"] is not None else 0
        tag = str(row.get("scenario_tag", "NORMAL")).strip()

        caller_person = resolver.resolve(c_caller)
        receiver_person = resolver.resolve(c_receiver)

        caller_entity_id = caller_person["person_id"] if caller_person else (c_caller if c_caller.startswith("P") else None)
        receiver_entity_id = receiver_person["person_id"] if receiver_person else (c_receiver if c_receiver.startswith("P") else None)

        caller_name = caller_person["name"] if caller_person else None
        receiver_name = receiver_person["name"] if receiver_person else None

        caller_phone = caller_person.get("phone") if caller_person else (c_caller if c_caller.startswith("PH") else None)
        receiver_phone = receiver_person.get("phone") if receiver_person else (c_receiver if c_receiver.startswith("PH") else None)

        entity_ids = [e for e in [caller_entity_id, receiver_entity_id] if e]

        # Duration formatted string
        mins = c_duration // 60
        secs = c_duration % 60
        dur_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

        record = {
            "communication_id": c_id,
            "id": c_id,
            "cdr_id": c_id,
            "caller": c_caller,
            "receiver": c_receiver,
            "from": c_caller,
            "to": c_receiver,
            "caller_entity_id": caller_entity_id,
            "receiver_entity_id": receiver_entity_id,
            "caller_name": caller_name,
            "receiver_name": receiver_name,
            "caller_phone": caller_phone,
            "receiver_phone": receiver_phone,
            "timestamp": c_time,
            "duration_seconds": c_duration,
            "duration": dur_str,
            "channel": "Voice Call",
            "kind": "Voice Call",
            "type": "Voice Call",
            "scenario_tag": tag,
            "priority": "HIGH" if tag != "NORMAL" else "NORMAL",
            "status": "Requires Review" if tag != "NORMAL" else "Normal",
            "case_id": "CASE-2026-1024",
            "caseId": "CASE-2026-1024",
            "entity_ids": entity_ids,
        }
        records.append(record)

    # Apply filters
    filtered: List[Dict[str, Any]] = []
    for c in records:
        if target_id and c["communication_id"].lower() != target_id.strip().lower():
            continue
        if entity_id and entity_id.strip() not in c["entity_ids"]:
            continue
        if caller:
            caller_clean = caller.strip().lower()
            if (
                c["caller"].lower() != caller_clean
                and (not c["caller_entity_id"] or c["caller_entity_id"].lower() != caller_clean)
                and (not c["caller_phone"] or c["caller_phone"].lower() != caller_clean)
            ):
                continue
        if receiver:
            receiver_clean = receiver.strip().lower()
            if (
                c["receiver"].lower() != receiver_clean
                and (not c["receiver_entity_id"] or c["receiver_entity_id"].lower() != receiver_clean)
                and (not c["receiver_phone"] or c["receiver_phone"].lower() != receiver_clean)
            ):
                continue
        if phone:
            phone_clean = phone.strip().lower()
            if (
                (not c["caller_phone"] or c["caller_phone"].lower() != phone_clean)
                and (not c["receiver_phone"] or c["receiver_phone"].lower() != phone_clean)
                and c["caller"].lower() != phone_clean
                and c["receiver"].lower() != phone_clean
            ):
                continue
        if min_duration is not None and c["duration_seconds"] < min_duration:
            continue
        if max_duration is not None and c["duration_seconds"] > max_duration:
            continue
        if start_time and c["timestamp"] < start_time.strip():
            continue
        if end_time and c["timestamp"] > end_time.strip():
            continue
        if scenario_tag and scenario_tag.strip().upper() != "ALL" and c["scenario_tag"].upper() != scenario_tag.strip().upper():
            continue

        filtered.append(c)

    # Apply sorting
    if sort == "timestamp_desc":
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    elif sort == "timestamp_asc":
        filtered.sort(key=lambda x: x["timestamp"], reverse=False)
    elif sort == "duration_desc":
        filtered.sort(key=lambda x: (x["duration_seconds"], x["timestamp"]), reverse=True)
    elif sort == "duration_asc":
        filtered.sort(key=lambda x: (x["duration_seconds"], x["timestamp"]), reverse=False)

    total_count = len(filtered)
    total_duration = sum(c["duration_seconds"] for c in filtered)
    avg_duration = round(total_duration / total_count, 1) if total_count > 0 else 0.0
    high_priority_count = sum(1 for c in filtered if c["priority"] == "HIGH" or c["scenario_tag"] != "NORMAL")
    unique_contacts = len(set(c["caller"] for c in filtered) | set(c["receiver"] for c in filtered))

    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_communications = filtered[start_idx:end_idx]

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "summary": {
            "total_calls": total_count,
            "total_duration_seconds": total_duration,
            "avg_duration_seconds": avg_duration,
            "high_priority_count": high_priority_count,
            "unique_contacts": unique_contacts,
            "filtered_count": total_count,
        },
        "communications": paged_communications,
    }

@router.get("/{communication_id}", response_model=None)
def get_communication_by_id(communication_id: str):
    data, resolver, _ = CacheManager().get_data()
    df_cdr = data.get("cdr")

    if df_cdr is None or df_cdr.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Communication {communication_id} not found",
        )

    match = df_cdr[df_cdr["cdr_id"] == communication_id.strip()]
    if match.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Communication {communication_id} not found",
        )

    row = match.iloc[0]
    c_id = str(row["cdr_id"]).strip()
    c_caller = str(row["caller"]).strip()
    c_receiver = str(row["receiver"]).strip()
    c_time = str(row["timestamp"]).strip()
    c_duration = int(row["duration_seconds"]) if row["duration_seconds"] is not None else 0
    tag = str(row.get("scenario_tag", "NORMAL")).strip()

    caller_person = resolver.resolve(c_caller)
    receiver_person = resolver.resolve(c_receiver)

    caller_entity_id = caller_person["person_id"] if caller_person else (c_caller if c_caller.startswith("P") else None)
    receiver_entity_id = receiver_person["person_id"] if receiver_person else (c_receiver if c_receiver.startswith("P") else None)

    caller_name = caller_person["name"] if caller_person else None
    receiver_name = receiver_person["name"] if receiver_person else None

    caller_phone = caller_person.get("phone") if caller_person else (c_caller if c_caller.startswith("PH") else None)
    receiver_phone = receiver_person.get("phone") if receiver_person else (c_receiver if c_receiver.startswith("PH") else None)

    entity_ids = [e for e in [caller_entity_id, receiver_entity_id] if e]

    mins = c_duration // 60
    secs = c_duration % 60
    dur_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

    return {
        "communication_id": c_id,
        "id": c_id,
        "cdr_id": c_id,
        "caller": c_caller,
        "receiver": c_receiver,
        "from": c_caller,
        "to": c_receiver,
        "caller_entity_id": caller_entity_id,
        "receiver_entity_id": receiver_entity_id,
        "caller_name": caller_name,
        "receiver_name": receiver_name,
        "caller_phone": caller_phone,
        "receiver_phone": receiver_phone,
        "timestamp": c_time,
        "duration_seconds": c_duration,
        "duration": dur_str,
        "channel": "Voice Call",
        "kind": "Voice Call",
        "type": "Voice Call",
        "scenario_tag": tag,
        "priority": "HIGH" if tag != "NORMAL" else "NORMAL",
        "status": "Requires Review" if tag != "NORMAL" else "Normal",
        "case_id": "CASE-2026-1024",
        "caseId": "CASE-2026-1024",
        "entity_ids": entity_ids,
    }
