from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from services.data_loader import load_all_data
from services.entity_resolution import EntityResolver
from services.graph_engine import build_investigation_graph


router = APIRouter(
    prefix="/api",
    tags=["Investigation Graph"],
)

# ============================================================
# GET CASE
# ============================================================

@router.get("/case")
def get_case():
    """
    Return summary information for the demo investigation case.
    """

    data, _, graph = get_investigation_data()

    persons = data["persons"]
    cdr = data["cdr"]
    transactions = data["transactions"]
    ipdr = data["ipdr"]
    social = data["social"]

    return {
        "case_id": "CASE-2026-1024",
        "case_name": "Online Financial Fraud",
        "status": "ACTIVE",
        "priority": "HIGH",

        "summary": {
            "persons": len(persons),
            "calls": len(cdr),
            "transactions": len(transactions),
            "ipdr_events": len(ipdr),
            "social_events": len(social),
            "graph_nodes": graph.number_of_nodes(),
            "graph_edges": graph.number_of_edges(),
        },

        "incident_date": "2026-09-01",

        "description": (
            "Synthetic investigation involving telecom, "
            "financial, IPDR, and social-media activity."
        ),
    }







# ============================================================
# LOAD DATA + BUILD GRAPH
# ============================================================

from services.cache_manager import CacheManager

def get_investigation_data():
    """
    Load all datasets, create the entity resolver,
    and build the investigation graph.

    Returns:
        data, resolver, graph
    """
    return CacheManager().get_data()


# ============================================================
# HELPER — JSON SAFE VALUES
# ============================================================

def json_safe(value: Any) -> Any:
    """
    Convert pandas/numpy/datetime values
    into JSON-compatible Python values.
    """

    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value


# ============================================================
# GET COMPLETE GRAPH
# ============================================================

@router.get("/graph")
def get_graph():
    """
    Return the complete investigation graph.

    Response contains:
        nodes
        edges
        node_count
        edge_count
    """

    _, _, graph = get_investigation_data()

    nodes = []

    for node_id, attributes in graph.nodes(data=True):

        node = {
            "id": node_id,
        }

        for key, value in attributes.items():
            node[key] = json_safe(value)

        nodes.append(node)

    edges = []

    for source, target, key, attributes in graph.edges(
        keys=True,
        data=True,
    ):

        edge = {
            "id": f"{source}-{key}-{target}",
            "source": source,
            "target": target,
        }

        for attribute, value in attributes.items():
            edge[attribute] = json_safe(value)

        edges.append(edge)

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


# ============================================================
# GET ENTITY
# ============================================================

@router.get("/entity/{entity_id}")
def get_entity(entity_id: str):
    """
    Return complete information about an entity.

    The supplied identifier can be:
        P001
        PH001
        A001
        SOC001
        DEV001
        IP address
    """

    data, resolver, graph = get_investigation_data()

    entity = resolver.resolve(entity_id)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity not found: {entity_id}",
        )

    person_id = entity["person_id"]

    # --------------------------------------------------------
    # Find direct PERSON -> PERSON relationships
    # --------------------------------------------------------

    connections = []

    person_node = f"person:{person_id}"

    if person_node in graph:

        for _, target, attributes in graph.out_edges(
            person_node,
            data=True,
        ):

            target_type = graph.nodes[target].get(
                "node_type"
            )

            if target_type != "PERSON":
                continue

            connections.append(
                {
                    "entity": graph.nodes[target].get(
                        "entity_id"
                    ),
                    "relationship": attributes.get(
                        "relationship"
                    ),
                }
            )

    return {
        "entity_id": entity["person_id"],
        "name": entity["name"],
        "age": json_safe(entity["age"]),
        "phones": [
            entity["phone"]
        ],
        "bank_accounts": [
            entity["bank_account"]
        ],
        "ip_addresses": [
            entity["ip_address"]
        ],
        "social_accounts": [
            entity["social_id"]
        ],
        "device_ids": [
            entity["device_id"]
        ],
        "connections": connections,
    }


# ============================================================
# GET ENTITY SUMMARY
# ============================================================

@router.get("/entity/{entity_id}/summary")
def get_entity_summary(
    entity_id: str,
    recent_limit: int = 5,
):
    """
    Return a unified summary of an entity across all domains:
    accounts, transactions, communications, network/IPDR, and anomalies.
    """
    data, resolver, graph = get_investigation_data()

    entity = resolver.resolve(entity_id)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity not found: {entity_id}",
        )

    person_id = entity["person_id"]
    bank_account = entity["bank_account"]

    # Transactions
    transactions_df = data.get("transactions")
    tx_list = []
    if transactions_df is not None and not transactions_df.empty:
        matched_tx = transactions_df[
            (transactions_df["sender_account"] == bank_account)
            | (transactions_df["receiver_account"] == bank_account)
        ].head(recent_limit)
        for _, row in matched_tx.iterrows():
            tx_list.append({
                "transaction_id": str(row["transaction_id"]),
                "sender_account": str(row["sender_account"]),
                "receiver_account": str(row["receiver_account"]),
                "amount": json_safe(row["amount"]),
                "timestamp": json_safe(row["timestamp"]),
                "channel": str(row["channel"]),
                "scenario_tag": str(row.get("scenario_tag", "NORMAL")),
            })

    # Communications / CDR
    cdr_df = data.get("cdr")
    comm_list = []
    if cdr_df is not None and not cdr_df.empty:
        matched_cdr = cdr_df[
            (cdr_df["caller"] == person_id)
            | (cdr_df["receiver"] == person_id)
        ].head(recent_limit)
        for _, row in matched_cdr.iterrows():
            comm_list.append({
                "cdr_id": str(row["cdr_id"]),
                "caller": str(row["caller"]),
                "receiver": str(row["receiver"]),
                "timestamp": json_safe(row["timestamp"]),
                "duration_seconds": json_safe(row["duration_seconds"]),
                "scenario_tag": str(row.get("scenario_tag", "NORMAL")),
            })

    # Network / IPDR
    ipdr_df = data.get("ipdr")
    ipdr_list = []
    if ipdr_df is not None and not ipdr_df.empty:
        matched_ipdr = ipdr_df[ipdr_df["person_id"] == person_id].head(recent_limit)
        for _, row in matched_ipdr.iterrows():
            ipdr_list.append({
                "ipdr_id": str(row["ipdr_id"]),
                "ip_address": str(row["ip_address"]),
                "device_id": str(row["device_id"]),
                "timestamp": json_safe(row["timestamp"]),
                "session_duration_seconds": json_safe(row["session_duration_seconds"]),
                "scenario_tag": str(row.get("scenario_tag", "NORMAL")),
            })

    # Anomalies
    from services.anomaly_engine import AnomalyEngine
    engine = AnomalyEngine(data)
    all_findings = engine.detect_all().get("all", [])
    related_anomalies = [
        f for f in all_findings if person_id in f.get("entity_ids", [])
    ][:recent_limit]

    return {
        "entity_id": person_id,
        "name": entity["name"],
        "age": json_safe(entity["age"]),
        "accounts": [entity["bank_account"]],
        "phones": [entity["phone"]],
        "ip_addresses": [entity["ip_address"]],
        "social_accounts": [entity["social_id"]],
        "device_ids": [entity["device_id"]],
        "transactions": tx_list,
        "communications": comm_list,
        "network": ipdr_list,
        "anomalies": related_anomalies,
    }


# ============================================================
# GET ENTITY CONNECTIONS
# ============================================================

@router.get("/entity/{entity_id}/connections")
def get_entity_connections(entity_id: str):
    """
    Return all direct graph connections for an entity.

    Accepted identifiers include:
        P001
        PH001
        A001
        SOC001
        DEV001
        10.10.1.11
    """

    # IMPORTANT:
    # get_investigation_data() returns:
    # (data, resolver, graph)
    #
    # Therefore we unpack the tuple instead of doing:
    # data["resolver"]
    # data["graph"]

    _, resolver, graph = get_investigation_data()

    # --------------------------------------------------------
    # Resolve supplied identifier to PERSON
    # --------------------------------------------------------

    entity = resolver.resolve(entity_id)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{entity_id}' not found",
        )

    person_id = entity["person_id"]

    person_node = f"person:{person_id}"

    if person_node not in graph:
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{entity_id}' not found in graph",
        )

    connections = []

    # ========================================================
    # OUTGOING RELATIONSHIPS
    # ========================================================

    for _, target, edge_data in graph.out_edges(
        person_node,
        data=True,
    ):

        target_attributes = graph.nodes[target]

        connection = {
            "entity_id": target,
            "entity_type": target_attributes.get(
                "node_type"
            ),
            "relationship": edge_data.get(
                "relationship"
            ),
            "direction": "outgoing",
            "source": edge_data.get(
                "source"
            ),
            "source_dataset": edge_data.get(
                "source_dataset"
            ),
        }

        # Preserve useful event metadata
        for field in [
            "timestamp",
            "duration_seconds",
            "session_duration_seconds",
            "amount",
            "channel",
            "scenario_tag",
        ]:

            if field in edge_data:

                connection[field] = json_safe(
                    edge_data[field]
                )

        connections.append(connection)

    # ========================================================
    # INCOMING RELATIONSHIPS
    # ========================================================

    for source, _, edge_data in graph.in_edges(
        person_node,
        data=True,
    ):

        source_attributes = graph.nodes[source]

        connection = {
            "entity_id": source,
            "entity_type": source_attributes.get(
                "node_type"
            ),
            "relationship": edge_data.get(
                "relationship"
            ),
            "direction": "incoming",
            "source": edge_data.get(
                "source"
            ),
            "source_dataset": edge_data.get(
                "source_dataset"
            ),
        }

        for field in [
            "timestamp",
            "duration_seconds",
            "session_duration_seconds",
            "amount",
            "channel",
            "scenario_tag",
        ]:

            if field in edge_data:

                connection[field] = json_safe(
                    edge_data[field]
                )

        connections.append(connection)

    return {
        "entity_id": person_id,
        "count": len(connections),
        "connections": connections,
    }


# ============================================================
# GET ENTITY TIMELINE
# ============================================================

@router.get("/entity/{entity_id}/timeline")
def get_entity_timeline(
    entity_id: str,
):
    """
    Return chronological activity for an entity.

    Sources:
        CDR
        Transactions
        IPDR
        Social
    """

    data, resolver, _ = get_investigation_data()

    entity = resolver.resolve(entity_id)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity not found: {entity_id}",
        )

    person_id = entity["person_id"]
    bank_account = entity["bank_account"]

    events = []

    # ========================================================
    # CDR EVENTS
    # ========================================================

    cdr = data["cdr"]

    person_calls = cdr[
        (cdr["caller"] == person_id)
        | (cdr["receiver"] == person_id)
    ]

    for _, row in person_calls.iterrows():

        caller = str(row["caller"])
        receiver = str(row["receiver"])

        if caller == person_id:
            direction = "OUTGOING"
            other_person = receiver
        else:
            direction = "INCOMING"
            other_person = caller

        events.append(
            {
                "event_type": "CALL",
                "direction": direction,
                "timestamp": json_safe(
                    row["timestamp"]
                ),
                "related_entity": other_person,
                "duration_seconds": json_safe(
                    row["duration_seconds"]
                ),
                "source": str(
                    row["cdr_id"]
                ),
                "source_dataset": "cdr.csv",
                "scenario_tag": str(
                    row["scenario_tag"]
                ),
            }
        )

    # ========================================================
    # TRANSACTION EVENTS
    # ========================================================

    transactions = data["transactions"]

    person_transactions = transactions[
        (
            transactions["sender_account"]
            == bank_account
        )
        |
        (
            transactions["receiver_account"]
            == bank_account
        )
    ]

    for _, row in person_transactions.iterrows():

        sender = str(
            row["sender_account"]
        )

        receiver = str(
            row["receiver_account"]
        )

        if sender == bank_account:
            direction = "OUTGOING"
            related_account = receiver
        else:
            direction = "INCOMING"
            related_account = sender

        events.append(
            {
                "event_type": "TRANSACTION",
                "direction": direction,
                "timestamp": json_safe(
                    row["timestamp"]
                ),
                "related_account": related_account,
                "amount": json_safe(
                    row["amount"]
                ),
                "channel": str(
                    row["channel"]
                ),
                "source": str(
                    row["transaction_id"]
                ),
                "source_dataset": "transactions.csv",
                "scenario_tag": str(
                    row["scenario_tag"]
                ),
            }
        )

    # ========================================================
    # IPDR EVENTS
    # ========================================================

    ipdr = data["ipdr"]

    person_ipdr = ipdr[
        ipdr["person_id"] == person_id
    ]

    for _, row in person_ipdr.iterrows():

        events.append(
            {
                "event_type": "IP_ACTIVITY",
                "direction": "ACTIVITY",
                "timestamp": json_safe(
                    row["timestamp"]
                ),
                "ip_address": str(
                    row["ip_address"]
                ),
                "device_id": str(
                    row["device_id"]
                ),
                "session_duration_seconds": json_safe(
                    row["session_duration_seconds"]
                ),
                "source": str(
                    row["ipdr_id"]
                ),
                "source_dataset": "ipdr.csv",
                "scenario_tag": str(
                    row["scenario_tag"]
                ),
            }
        )

    # ========================================================
    # SOCIAL EVENTS
    # ========================================================

    social = data["social"]

    person_social = social[
        social["person_id"] == person_id
    ]

    for _, row in person_social.iterrows():

        events.append(
            {
                "event_type": "SOCIAL_ACTIVITY",
                "direction": "ACTIVITY",
                "timestamp": json_safe(
                    row["timestamp"]
                ),
                "platform": str(
                    row["platform"]
                ),
                "activity_type": str(
                    row["activity_type"]
                ),
                "source": str(
                    row["social_event_id"]
                ),
                "source_dataset": "social.csv",
                "scenario_tag": str(
                    row["scenario_tag"]
                ),
            }
        )

    # ========================================================
    # SORT CHRONOLOGICALLY
    # ========================================================

    events.sort(
        key=lambda event: event["timestamp"]
    )

    return {
        "entity_id": person_id,
        "timeline": events,
        "count": len(events),
    }

