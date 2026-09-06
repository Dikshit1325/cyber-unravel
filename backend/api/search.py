import re
from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Dict, Any, Optional

from services.cache_manager import CacheManager

router = APIRouter(prefix="/api/search", tags=["Search"])

# Mapping of domain to display name and route template
DOMAIN_CONFIG = {
    "entity": {
        "type": "Entity",
        "fields": ["person_id", "name", "phone", "bank_account", "social_id", "ip_address", "device_id"],
        "route": lambda id: f"/entities/{id}",
    },
    "account": {
        "type": "Account",
        "fields": ["bank_account"],
        "route": lambda id: f"/entities/{id}",
    },
    "phone": {
        "type": "Phone",
        "fields": ["phone"],
        "route": lambda id: f"/entities/{id}",
    },
    "ip_address": {
        "type": "IP Address",
        "fields": ["ip_address"],
        "route": lambda id: f"/entities/{id}",
    },
    "device": {
        "type": "Device",
        "fields": ["device_id"],
        "route": lambda id: f"/entities/{id}",
    },
    "transaction": {
        "type": "Transaction",
        "fields": ["transaction_id", "sender_account", "receiver_account"],
        "route": lambda id: f"/transactions/{id}",
    },
    "communication": {
        "type": "Communication",
        "fields": ["cdr_id", "caller", "receiver"],
        "route": lambda id: f"/communications/{id}",
    },
    "network": {
        "type": "Network",
        "fields": ["ipdr_id", "person_id", "ip_address"],
        "route": lambda id: f"/network/{id}",
    },
    "anomaly": {
        "type": "Anomaly",
        "fields": ["anomaly_id", "anomaly_type", "entity_ids"],
        "route": lambda id: f"/anomalies/{id}",
    },
}

def _matches(record: Dict[str, Any], query: str, fields: List[str]) -> bool:
    q = query.lower()
    for f in fields:
        val = record.get(f)
        if val is None:
            continue
        if isinstance(val, (list, set, tuple)):
            if any(q in str(item).lower() for item in val):
                return True
        else:
            if q in str(val).lower():
                return True
    return False

@router.get("/", response_model=None)
def search(
    q: str = Query(..., min_length=1, description="Search query string"),
    domain: Optional[str] = Query(None, description="Optional domain filter (entity, account, phone, ip_address, device, transaction, communication, network, anomaly)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Result offset for pagination"),
):
    if not q:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query parameter 'q' is required")

    data, resolver, _ = CacheManager().get_data()

    results: List[Dict[str, Any]] = []

    def add_result(id_val: str, domain_key: str, title: str, subtitle: str, entity_id: Optional[str] = None):
        cfg = DOMAIN_CONFIG[domain_key]
        results.append({
            "id": id_val,
            "type": cfg["type"],
            "title": title,
            "subtitle": subtitle,
            "entity_id": entity_id,
            "route": cfg["route"](id_val),
        })

    # Entities (persons)
    persons_df = data.get("persons")
    if persons_df is not None and not persons_df.empty:
        for _, row in persons_df.iterrows():
            rec = {col: row[col] for col in DOMAIN_CONFIG["entity"]["fields"] if col in row}
            if _matches(rec, q, DOMAIN_CONFIG["entity"]["fields"]):
                pid = str(row["person_id"]).strip()
                add_result(
                    id_val=pid,
                    domain_key="entity",
                    title=str(row.get("name", "")).strip(),
                    subtitle=f"Person {pid}",
                    entity_id=pid,
                )

        # Accounts, Phones, IPs, Devices derived from persons
        for _, row in persons_df.iterrows():
            pid = str(row["person_id"]).strip()
            # Account
            acc = str(row.get("bank_account", "")).strip()
            if acc and _matches({"bank_account": acc}, q, ["bank_account"]):
                add_result(acc, "account", acc, f"Account of {pid}", pid)
            # Phone
            phone = str(row.get("phone", "")).strip()
            if phone and _matches({"phone": phone}, q, ["phone"]):
                add_result(phone, "phone", phone, f"Phone of {pid}", pid)
            # IP address
            ip = str(row.get("ip_address", "")).strip()
            if ip and _matches({"ip_address": ip}, q, ["ip_address"]):
                add_result(ip, "ip_address", ip, f"IP of {pid}", pid)
            # Device
            dev = str(row.get("device_id", "")).strip()
            if dev and _matches({"device_id": dev}, q, ["device_id"]):
                add_result(dev, "device", dev, f"Device of {pid}", pid)

    # Transactions
    tx_df = data.get("transactions")
    if tx_df is not None and not tx_df.empty:
        for _, row in tx_df.iterrows():
            rec = {col: row[col] for col in DOMAIN_CONFIG["transaction"]["fields"] if col in row}
            if _matches(rec, q, DOMAIN_CONFIG["transaction"]["fields"]):
                tid = str(row["transaction_id"]).strip()
                title = f"{row.get('sender_account','').strip()} → {row.get('receiver_account','').strip()}"
                subtitle = f"{row.get('amount','')} {row.get('currency','INR')}"
                add_result(tid, "transaction", title, subtitle)

    # Communications (CDR)
    cdr_df = data.get("cdr")
    if cdr_df is not None and not cdr_df.empty:
        for _, row in cdr_df.iterrows():
            rec = {col: row[col] for col in DOMAIN_CONFIG["communication"]["fields"] if col in row}
            if _matches(rec, q, DOMAIN_CONFIG["communication"]["fields"]):
                cid = str(row["cdr_id"]).strip()
                title = f"{row.get('caller','').strip()} → {row.get('receiver','').strip()}"
                subtitle = str(row.get("timestamp", ""))
                add_result(cid, "communication", title, subtitle)

    # Network (IPDR)
    ipdr_df = data.get("ipdr")
    if ipdr_df is not None and not ipdr_df.empty:
        for _, row in ipdr_df.iterrows():
            rec = {col: row[col] for col in DOMAIN_CONFIG["network"]["fields"] if col in row}
            if _matches(rec, q, DOMAIN_CONFIG["network"]["fields"]):
                nid = str(row["ipdr_id"]).strip()
                title = str(row.get("person_id", ""))
                subtitle = f"IP {row.get('ip_address','').strip()}"
                add_result(nid, "network", title, subtitle)

    # Anomalies (use engine)
    from services.anomaly_engine import AnomalyEngine
    engine = AnomalyEngine(data)
    all_findings = engine.detect_all().get("all", [])
    for f in all_findings:
        if _matches(f, q, DOMAIN_CONFIG["anomaly"]["fields"]):
            aid = f.get("anomaly_id") or f.get("id") or f.get("source") or "unknown"
            title = f.get("anomaly_type", "Anomaly")
            subtitle = f"Severity {f.get('severity','')}, score {f.get('score') or f.get('correlation_score','')}"
            add_result(str(aid), "anomaly", title, subtitle)

    # Optional domain filter
    if domain:
        dk = domain.lower()
        if dk not in DOMAIN_CONFIG:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid domain filter: {domain}")
        results = [r for r in results if r["type"].lower().replace(' ', '_') == dk]

    # Deterministic ordering
    results.sort(key=lambda x: (x["type"].lower(), x["id"]))

    total = len(results)
    sliced = results[offset: offset + limit]

    return {"total": total, "limit": limit, "offset": offset, "results": sliced}
