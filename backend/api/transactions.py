from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime

from services.cache_manager import CacheManager

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

def _parse_timestamp(dt_str: str) -> str:
    # Normalize timestamp string for filtering/comparison
    return dt_str.strip()

@router.get("/", response_model=None)
def get_transactions(
    transaction_id: Optional[str] = Query(None, description="Filter by exact transaction ID"),
    entity_id: Optional[str] = Query(None, description="Filter by associated entity ID (e.g. P001)"),
    account: Optional[str] = Query(None, description="Filter by sender or receiver account"),
    sender: Optional[str] = Query(None, description="Filter by sender account"),
    receiver: Optional[str] = Query(None, description="Filter by receiver account"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum transaction amount"),
    start_time: Optional[str] = Query(None, description="Filter start timestamp"),
    end_time: Optional[str] = Query(None, description="Filter end timestamp"),
    channel: Optional[str] = Query(None, description="Filter by channel/type (NEFT, UPI, IMPS, RTGS)"),
    scenario_tag: Optional[str] = Query(None, description="Filter by scenario tag (NORMAL, etc.)"),
    sort: Optional[str] = Query("timestamp_desc", description="Sorting: timestamp_desc, timestamp_asc, amount_desc, amount_asc"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Page size"),
):
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_amount cannot be greater than max_amount",
        )

    allowed_sorts = ["timestamp_desc", "timestamp_asc", "amount_desc", "amount_asc"]
    if sort and sort not in allowed_sorts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameter. Allowed values: {', '.join(allowed_sorts)}",
        )

    # Load cached investigation data
    data, resolver, _ = CacheManager().get_data()
    df_tx = data.get("transactions")

    if df_tx is None or df_tx.empty:
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "summary": {
                "total_volume": 0.0,
                "high_value_count": 0,
                "unique_accounts": 0,
                "filtered_count": 0,
            },
            "transactions": [],
        }

    # Build enriched transaction records
    records: List[Dict[str, Any]] = []
    for _, row in df_tx.iterrows():
        tx_id = str(row["transaction_id"]).strip()
        sender_acc = str(row["sender_account"]).strip()
        receiver_acc = str(row["receiver_account"]).strip()
        amount = float(row["amount"])
        timestamp = str(row["timestamp"]).strip()
        tx_channel = str(row["channel"]).strip()
        tag = str(row.get("scenario_tag", "NORMAL")).strip()

        # Correlate sender and receiver with entity resolver
        sender_person = resolver.resolve(sender_acc)
        receiver_person = resolver.resolve(receiver_acc)

        sender_entity_id = sender_person["person_id"] if sender_person else None
        receiver_entity_id = receiver_person["person_id"] if receiver_person else None
        sender_name = sender_person["name"] if sender_person else None
        receiver_name = receiver_person["name"] if receiver_person else None

        entity_ids = [e for e in [sender_entity_id, receiver_entity_id] if e]

        record = {
            "transaction_id": tx_id,
            "id": tx_id,
            "timestamp": timestamp,
            "sender_account": sender_acc,
            "receiver_account": receiver_acc,
            "sender": sender_acc,
            "receiver": receiver_acc,
            "sender_name": sender_name,
            "receiver_name": receiver_name,
            "sender_entity_id": sender_entity_id,
            "receiver_entity_id": receiver_entity_id,
            "amount": amount,
            "channel": tx_channel,
            "type": tx_channel,
            "scenario_tag": tag,
            "priority": "HIGH" if tag != "NORMAL" else "NORMAL",
            "status": "Requires Review" if tag != "NORMAL" else "Cleared",
            "case_id": "CASE-2026-1024",
            "caseId": "CASE-2026-1024",
            "currency": "INR",
            "entity_ids": entity_ids,
        }
        records.append(record)

    # Apply filters
    filtered: List[Dict[str, Any]] = []
    for t in records:
        if transaction_id and t["transaction_id"].lower() != transaction_id.strip().lower():
            continue
        if entity_id and entity_id.strip() not in t["entity_ids"]:
            continue
        if account:
            acc_clean = account.strip().lower()
            if t["sender_account"].lower() != acc_clean and t["receiver_account"].lower() != acc_clean:
                continue
        if sender and t["sender_account"].lower() != sender.strip().lower():
            continue
        if receiver and t["receiver_account"].lower() != receiver.strip().lower():
            continue
        if min_amount is not None and t["amount"] < min_amount:
            continue
        if max_amount is not None and t["amount"] > max_amount:
            continue
        if start_time and t["timestamp"] < start_time.strip():
            continue
        if end_time and t["timestamp"] > end_time.strip():
            continue
        if channel and channel.strip().upper() != "ALL" and t["channel"].upper() != channel.strip().upper():
            continue
        if scenario_tag and scenario_tag.strip().upper() != "ALL" and t["scenario_tag"].upper() != scenario_tag.strip().upper():
            continue

        filtered.append(t)

    # Apply sorting
    if sort == "timestamp_desc":
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    elif sort == "timestamp_asc":
        filtered.sort(key=lambda x: x["timestamp"], reverse=False)
    elif sort == "amount_desc":
        filtered.sort(key=lambda x: (x["amount"], x["timestamp"]), reverse=True)
    elif sort == "amount_asc":
        filtered.sort(key=lambda x: (x["amount"], x["timestamp"]), reverse=False)

    total_count = len(filtered)
    total_volume = sum(t["amount"] for t in filtered)
    high_value_count = sum(1 for t in filtered if t["amount"] >= 10000 or t["scenario_tag"] != "NORMAL")
    unique_accounts = len(set(t["sender_account"] for t in filtered) | set(t["receiver_account"] for t in filtered))

    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_transactions = filtered[start_idx:end_idx]

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "summary": {
            "total_volume": total_volume,
            "high_value_count": high_value_count,
            "unique_accounts": unique_accounts,
            "filtered_count": total_count,
        },
        "transactions": paged_transactions,
    }

@router.get("/{transaction_id}", response_model=None)
def get_transaction_by_id(transaction_id: str):
    data, resolver, _ = CacheManager().get_data()
    df_tx = data.get("transactions")

    if df_tx is None or df_tx.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )

    match = df_tx[df_tx["transaction_id"] == transaction_id.strip()]
    if match.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )

    row = match.iloc[0]
    tx_id = str(row["transaction_id"]).strip()
    sender_acc = str(row["sender_account"]).strip()
    receiver_acc = str(row["receiver_account"]).strip()
    amount = float(row["amount"])
    timestamp = str(row["timestamp"]).strip()
    tx_channel = str(row["channel"]).strip()
    tag = str(row.get("scenario_tag", "NORMAL")).strip()

    sender_person = resolver.resolve(sender_acc)
    receiver_person = resolver.resolve(receiver_acc)

    sender_entity_id = sender_person["person_id"] if sender_person else None
    receiver_entity_id = receiver_person["person_id"] if receiver_person else None
    sender_name = sender_person["name"] if sender_person else None
    receiver_name = receiver_person["name"] if receiver_person else None

    entity_ids = [e for e in [sender_entity_id, receiver_entity_id] if e]

    return {
        "transaction_id": tx_id,
        "id": tx_id,
        "timestamp": timestamp,
        "sender_account": sender_acc,
        "receiver_account": receiver_acc,
        "sender": sender_acc,
        "receiver": receiver_acc,
        "sender_name": sender_name,
        "receiver_name": receiver_name,
        "sender_entity_id": sender_entity_id,
        "receiver_entity_id": receiver_entity_id,
        "amount": amount,
        "channel": tx_channel,
        "type": tx_channel,
        "scenario_tag": tag,
        "priority": "HIGH" if tag != "NORMAL" else "NORMAL",
        "status": "Requires Review" if tag != "NORMAL" else "Cleared",
        "case_id": "CASE-2026-1024",
        "caseId": "CASE-2026-1024",
        "currency": "INR",
        "entity_ids": entity_ids,
    }
