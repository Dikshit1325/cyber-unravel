from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional, Dict, Any, Set
from collections import defaultdict

from services.cache_manager import CacheManager

router = APIRouter(prefix="/api/network", tags=["Network / IPDR"])


def _compute_shared_infrastructure(df_ipdr, resolver):
    """
    Computes mappings of IP -> set of entity IDs and Device -> set of entity IDs
    for shared infrastructure correlation without running heavy anomaly detection.
    """
    ip_entities: Dict[str, Set[str]] = defaultdict(set)
    device_entities: Dict[str, Set[str]] = defaultdict(set)

    if df_ipdr is None or df_ipdr.empty:
        return ip_entities, device_entities

    for _, row in df_ipdr.iterrows():
        p_id = str(row.get("person_id", "")).strip()
        ip = str(row.get("ip_address", "")).strip()
        dev = str(row.get("device_id", "")).strip()

        person = resolver.resolve(p_id) if resolver else None
        entity_id = person["person_id"] if person else (p_id if p_id.startswith("P") else None)

        if entity_id:
            if ip:
                ip_entities[ip].add(entity_id)
            if dev:
                device_entities[dev].add(entity_id)

    return ip_entities, device_entities


@router.get("/", response_model=None)
def get_network_records(
    ipdr_id: Optional[str] = Query(None, description="Filter by exact IPDR record ID"),
    record_id: Optional[str] = Query(None, description="Alias for ipdr_id"),
    entity_id: Optional[str] = Query(None, description="Filter by associated entity ID (e.g. P001)"),
    person_id: Optional[str] = Query(None, description="Alias for entity_id"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    source_ip: Optional[str] = Query(None, description="Alias for ip_address"),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum session duration in seconds"),
    max_duration: Optional[int] = Query(None, ge=0, description="Maximum session duration in seconds"),
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

    target_id = ipdr_id or record_id
    target_entity = entity_id or person_id
    target_ip = ip_address or source_ip

    data, resolver, _ = CacheManager().get_data()
    df_ipdr = data.get("ipdr")

    if df_ipdr is None or df_ipdr.empty:
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "summary": {
                "total_records": 0,
                "total_duration_seconds": 0,
                "avg_duration_seconds": 0.0,
                "unique_entities": 0,
                "unique_ips": 0,
                "unique_devices": 0,
                "shared_ip_count": 0,
                "shared_device_count": 0,
                "high_priority_count": 0,
            },
            "records": [],
        }

    ip_entities, device_entities = _compute_shared_infrastructure(df_ipdr, resolver)

    records: List[Dict[str, Any]] = []
    for _, row in df_ipdr.iterrows():
        r_id = str(row["ipdr_id"]).strip()
        p_id = str(row["person_id"]).strip()
        ip = str(row["ip_address"]).strip()
        dev = str(row["device_id"]).strip()
        ts = str(row["timestamp"]).strip()
        dur = int(row["session_duration_seconds"]) if row["session_duration_seconds"] is not None else 0
        tag = str(row.get("scenario_tag", "NORMAL")).strip()

        person = resolver.resolve(p_id) if resolver else None
        resolved_entity_id = person["person_id"] if person else (p_id if p_id.startswith("P") else None)
        entity_name = person["name"] if person else None

        shared_ip_entities = sorted(list(ip_entities.get(ip, set()) - ({resolved_entity_id} if resolved_entity_id else set())))
        shared_dev_entities = sorted(list(device_entities.get(dev, set()) - ({resolved_entity_id} if resolved_entity_id else set())))
        is_shared_ip = len(ip_entities.get(ip, set())) > 1
        is_shared_device = len(device_entities.get(dev, set())) > 1

        mins = dur // 60
        secs = dur % 60
        dur_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

        record = {
            "ipdr_id": r_id,
            "record_id": r_id,
            "person_id": p_id,
            "entity_id": resolved_entity_id,
            "entity_ids": [resolved_entity_id] if resolved_entity_id else [],
            "entity_name": entity_name,
            "ip_address": ip,
            "source_ip": ip,
            "device_id": dev,
            "timestamp": ts,
            "session_duration_seconds": dur,
            "duration_seconds": dur,
            "duration_formatted": dur_str,
            "scenario_tag": tag,
            "is_shared_ip": is_shared_ip,
            "is_shared_device": is_shared_device,
            "shared_ip_entities": shared_ip_entities,
            "shared_device_entities": shared_dev_entities,
            "shared_ip_count": len(ip_entities.get(ip, set())),
            "shared_device_count": len(device_entities.get(dev, set())),
        }
        records.append(record)

    # Apply filters
    filtered = records
    if target_id:
        cleaned = target_id.strip().upper()
        filtered = [r for r in filtered if r["ipdr_id"].upper() == cleaned]
    if target_entity:
        cleaned = target_entity.strip().upper()
        filtered = [r for r in filtered if (r["entity_id"] and r["entity_id"].upper() == cleaned) or r["person_id"].upper() == cleaned]
    if target_ip:
        cleaned = target_ip.strip().lower()
        filtered = [r for r in filtered if cleaned in r["ip_address"].lower()]
    if device_id:
        cleaned = device_id.strip().upper()
        filtered = [r for r in filtered if cleaned in r["device_id"].upper()]
    if min_duration is not None:
        filtered = [r for r in filtered if r["session_duration_seconds"] >= min_duration]
    if max_duration is not None:
        filtered = [r for r in filtered if r["session_duration_seconds"] <= max_duration]
    if start_time:
        filtered = [r for r in filtered if r["timestamp"] >= start_time]
    if end_time:
        filtered = [r for r in filtered if r["timestamp"] <= end_time]
    if scenario_tag and scenario_tag != "All":
        cleaned = scenario_tag.strip().upper()
        filtered = [r for r in filtered if r["scenario_tag"].upper() == cleaned]

    # Sorting
    if sort == "timestamp_asc":
        filtered.sort(key=lambda r: (r["timestamp"], r["ipdr_id"]))
    elif sort == "duration_desc":
        filtered.sort(key=lambda r: (-r["session_duration_seconds"], r["timestamp"], r["ipdr_id"]))
    elif sort == "duration_asc":
        filtered.sort(key=lambda r: (r["session_duration_seconds"], r["timestamp"], r["ipdr_id"]))
    else:  # timestamp_desc default
        filtered.sort(key=lambda r: (r["timestamp"], r["ipdr_id"]), reverse=True)

    # Summary metrics
    total_count = len(filtered)
    total_duration = sum(r["session_duration_seconds"] for r in filtered)
    avg_duration = round(total_duration / total_count, 2) if total_count else 0.0
    unique_entities = len({r["entity_id"] for r in filtered if r["entity_id"]})
    unique_ips = len({r["ip_address"] for r in filtered if r["ip_address"]})
    unique_devices = len({r["device_id"] for r in filtered if r["device_id"]})
    shared_ip_cnt = sum(1 for r in filtered if r["is_shared_ip"])
    shared_dev_cnt = sum(1 for r in filtered if r["is_shared_device"])
    high_priority_cnt = sum(1 for r in filtered if r["scenario_tag"].upper() != "NORMAL")

    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged = filtered[start_idx:end_idx]

    summary = {
        "total_records": total_count,
        "total_duration_seconds": total_duration,
        "avg_duration_seconds": avg_duration,
        "unique_entities": unique_entities,
        "unique_ips": unique_ips,
        "unique_devices": unique_devices,
        "shared_ip_count": shared_ip_cnt,
        "shared_device_count": shared_dev_cnt,
        "high_priority_count": high_priority_cnt,
    }

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "summary": summary,
        "records": paged,
    }


@router.get("/{ipdr_id}", response_model=None)
def get_network_record_by_id(ipdr_id: str):
    target = ipdr_id.strip().upper()
    data, resolver, _ = CacheManager().get_data()
    df_ipdr = data.get("ipdr")
    if df_ipdr is None or df_ipdr.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"IPDR record not found: {ipdr_id}")
    ip_entities, device_entities = _compute_shared_infrastructure(df_ipdr, resolver)
    for _, row in df_ipdr.iterrows():
        r_id = str(row["ipdr_id"]).strip()
        if r_id.upper() == target:
            p_id = str(row["person_id"]).strip()
            ip = str(row["ip_address"]).strip()
            dev = str(row["device_id"]).strip()
            ts = str(row["timestamp"]).strip()
            dur = int(row["session_duration_seconds"]) if row["session_duration_seconds"] is not None else 0
            tag = str(row.get("scenario_tag", "NORMAL")).strip()
            person = resolver.resolve(p_id) if resolver else None
            resolved_entity_id = person["person_id"] if person else (p_id if p_id.startswith("P") else None)
            entity_name = person["name"] if person else None
            shared_ip_entities = sorted(list(ip_entities.get(ip, set()) - ({resolved_entity_id} if resolved_entity_id else set())))
            shared_dev_entities = sorted(list(device_entities.get(dev, set()) - ({resolved_entity_id} if resolved_entity_id else set())))
            is_shared_ip = len(ip_entities.get(ip, set())) > 1
            is_shared_device = len(device_entities.get(dev, set())) > 1
            mins = dur // 60
            secs = dur % 60
            dur_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
            return {
                "ipdr_id": r_id,
                "record_id": r_id,
                "person_id": p_id,
                "entity_id": resolved_entity_id,
                "entity_ids": [resolved_entity_id] if resolved_entity_id else [],
                "entity_name": entity_name,
                "ip_address": ip,
                "source_ip": ip,
                "device_id": dev,
                "timestamp": ts,
                "session_duration_seconds": dur,
                "duration_seconds": dur,
                "duration_formatted": dur_str,
                "scenario_tag": tag,
                "is_shared_ip": is_shared_ip,
                "is_shared_device": is_shared_device,
                "shared_ip_entities": shared_ip_entities,
                "shared_device_entities": shared_dev_entities,
                "shared_ip_count": len(ip_entities.get(ip, set())),
                "shared_device_count": len(device_entities.get(dev, set())),
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"IPDR record not found: {ipdr_id}")
