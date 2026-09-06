from __future__ import annotations

from typing import Any

import networkx as nx
import pandas as pd


# ============================================================
# NODE ID HELPERS
# ============================================================

def person_node(person_id: str) -> str:
    return f"person:{person_id}"


def phone_node(phone: str) -> str:
    return f"phone:{phone}"


def bank_node(account: str) -> str:
    return f"bank:{account}"


def ip_node(ip_address: str) -> str:
    return f"ip:{ip_address}"


def social_node(social_id: str) -> str:
    return f"social:{social_id}"

def social_event_node(social_event_id: str) -> str:
    return f"social_event:{social_event_id}"


# ============================================================
# CREATE EMPTY GRAPH
# ============================================================

def create_graph() -> nx.MultiDiGraph:
    """
    Create an empty investigation graph.
    """

    return nx.MultiDiGraph()


# ============================================================
# ADD PERSON NODES
# ============================================================

def add_person_nodes(
    G: nx.MultiDiGraph,
    persons: pd.DataFrame,
) -> None:
    """
    Add PERSON nodes and their known identifiers.
    """

    for _, row in persons.iterrows():

        person_id = str(row["person_id"]).strip()

        G.add_node(
            person_node(person_id),
            node_type="PERSON",
            entity_id=person_id,
            name=str(row["name"]),
            age=int(row["age"]),
        )


# ============================================================
# ADD IDENTITY NODES AND OWNERSHIP EDGES
# ============================================================

def add_identity_relationships(
    G: nx.MultiDiGraph,
    persons: pd.DataFrame,
) -> None:
    """
    Add PHONE, BANK, IP and SOCIAL nodes.

    Relationships:

        PERSON --USES--> PHONE
        PERSON --OWNS--> BANK
        PERSON --USES--> IP
        PERSON --HAS_SOCIAL--> SOCIAL
    """

    for _, row in persons.iterrows():

        person_id = str(row["person_id"]).strip()

        # --------------------------------------------------------
        # PHONE
        # --------------------------------------------------------

        phone = str(row["phone"]).strip()

        G.add_node(
            phone_node(phone),
            node_type="PHONE",
            entity_id=phone,
        )

        G.add_edge(
            person_node(person_id),
            phone_node(phone),
            relationship="USES",
            source="persons.csv",
        )

        # --------------------------------------------------------
        # BANK ACCOUNT
        # --------------------------------------------------------

        bank_account = str(
            row["bank_account"]
        ).strip()

        G.add_node(
            bank_node(bank_account),
            node_type="BANK",
            entity_id=bank_account,
        )

        G.add_edge(
            person_node(person_id),
            bank_node(bank_account),
            relationship="OWNS",
            source="persons.csv",
        )

        # --------------------------------------------------------
        # PERSON'S KNOWN IP
        # --------------------------------------------------------

        ip_address = str(
            row["ip_address"]
        ).strip()

        G.add_node(
            ip_node(ip_address),
            node_type="IP",
            entity_id=ip_address,
        )

        G.add_edge(
            person_node(person_id),
            ip_node(ip_address),
            relationship="USES",
            source="persons.csv",
        )

        # --------------------------------------------------------
        # SOCIAL ACCOUNT
        # --------------------------------------------------------

        social_id = str(
            row["social_id"]
        ).strip()

        G.add_node(
            social_node(social_id),
            node_type="SOCIAL",
            entity_id=social_id,
        )

        G.add_edge(
            person_node(person_id),
            social_node(social_id),
            relationship="HAS_SOCIAL",
            source="persons.csv",
        )


# ============================================================
# ADD CDR RELATIONSHIPS
# ============================================================

def add_cdr_edges(
    G: nx.MultiDiGraph,
    cdr: pd.DataFrame,
) -> None:
    """
    Add communication relationships from CDR.

    Example:

        P001 --CALLED--> P002
    """

    for _, row in cdr.iterrows():

        caller = str(row["caller"]).strip()
        receiver = str(row["receiver"]).strip()

        source_id = str(row["cdr_id"]).strip()

        timestamp = row["timestamp"]

        duration = float(
            row["duration_seconds"]
        )

        edge_data: dict[str, Any] = {
            "relationship": "CALLED",
            "timestamp": timestamp,
            "duration_seconds": duration,
            "source": source_id,
            "source_dataset": "cdr.csv",
        }

        # scenario_tag is retained only as synthetic/demo metadata.
        # It is NOT used as an intelligence feature.
        if "scenario_tag" in row:
            edge_data["scenario_tag"] = str(
                row["scenario_tag"]
            )

        G.add_edge(
            person_node(caller),
            person_node(receiver),
            **edge_data,
        )


# ============================================================
# ADD TRANSACTION RELATIONSHIPS
# ============================================================

def add_transaction_edges(
    G: nx.MultiDiGraph,
    transactions: pd.DataFrame,
) -> None:
    """
    Add bank transfer relationships.

    Example:

        A001 --TRANSFERRED--> A002
    """

    for _, row in transactions.iterrows():

        sender = str(
            row["sender_account"]
        ).strip()

        receiver = str(
            row["receiver_account"]
        ).strip()

        source_id = str(
            row["transaction_id"]
        ).strip()

        timestamp = row["timestamp"]

        amount = float(
            row["amount"]
        )

        edge_data: dict[str, Any] = {
            "relationship": "TRANSFERRED",
            "amount": amount,
            "timestamp": timestamp,
            "channel": str(row["channel"]),
            "source": source_id,
            "source_dataset": "transactions.csv",
        }

        # Synthetic/demo metadata only.
        if "scenario_tag" in row:
            edge_data["scenario_tag"] = str(
                row["scenario_tag"]
            )

        G.add_edge(
            bank_node(sender),
            bank_node(receiver),
            **edge_data,
        )


# ============================================================
# ADD IPDR RELATIONSHIPS
# ============================================================

def add_ipdr_edges(
    G: nx.MultiDiGraph,
    ipdr: pd.DataFrame,
) -> None:
    """
    Add IP activity relationships.

    This is especially useful for shared IP detection.

    Example:

        P001 --USES--> 203.0.113.77
        P002 --USES--> 203.0.113.77
    """

    for _, row in ipdr.iterrows():

        person_id = str(
            row["person_id"]
        ).strip()

        ip_address = str(
            row["ip_address"]
        ).strip()

        source_id = str(
            row["ipdr_id"]
        ).strip()

        timestamp = row["timestamp"]

        duration = float(
            row["session_duration_seconds"]
        )

        edge_data: dict[str, Any] = {
            "relationship": "USES",
            "timestamp": timestamp,
            "session_duration_seconds": duration,
            "device_id": str(row["device_id"]),
            "source": source_id,
            "source_dataset": "ipdr.csv",
        }

        if "scenario_tag" in row:
            edge_data["scenario_tag"] = str(
                row["scenario_tag"]
            )

        # Make sure IP node exists.
        G.add_node(
            ip_node(ip_address),
            node_type="IP",
            entity_id=ip_address,
        )

        G.add_edge(
            person_node(person_id),
            ip_node(ip_address),
            **edge_data,
        )


# ============================================================
# ADD SOCIAL EDGES
# ============================================================

def add_social_edges(
    G: nx.MultiDiGraph,
    social: pd.DataFrame,
) -> None:
    """
    Add social activity relationships.

    Example:

        P001 --PERFORMED_SOCIAL_ACTIVITY--> SOC_EVT0001
    """

    if social is None or social.empty:
        return

    for _, row in social.iterrows():

        person_id = str(
            row["person_id"]
        ).strip()

        event_id = str(
            row["social_event_id"]
        ).strip()

        if pd.isna(row["social_event_id"]) or not event_id:
            continue

        timestamp = row["timestamp"]

        edge_data: dict[str, Any] = {
            "relationship": "PERFORMED_SOCIAL_ACTIVITY",
            "timestamp": timestamp,
            "platform": str(row["platform"]),
            "activity_type": str(row["activity_type"]),
            "source": event_id,
            "source_dataset": "social.csv",
        }

        if "scenario_tag" in row:
            edge_data["scenario_tag"] = str(
                row["scenario_tag"]
            )

        # Make sure SOCIAL_EVENT node exists
        G.add_node(
            social_event_node(event_id),
            node_type="SOCIAL_EVENT",
            entity_id=event_id,
            platform=str(row["platform"]),
            activity_type=str(row["activity_type"]),
            timestamp=timestamp,
        )

        G.add_edge(
            person_node(person_id),
            social_event_node(event_id),
            **edge_data,
        )


# ============================================================

def build_investigation_graph(
    data: dict[str, pd.DataFrame],
) -> nx.MultiDiGraph:
    """
    Build the complete investigation graph.

    Uses:

        persons
        cdr
        transactions
        ipdr
        social

    """

    G = create_graph()

    persons = data["persons"]
    cdr = data["cdr"]
    transactions = data["transactions"]
    ipdr = data["ipdr"]
    social = data.get("social", pd.DataFrame())

    # --------------------------------------------------------
    # Identity layer
    # --------------------------------------------------------

    add_person_nodes(
        G,
        persons,
    )

    add_identity_relationships(
        G,
        persons,
    )

    # --------------------------------------------------------
    # Activity layer
    # --------------------------------------------------------

    add_cdr_edges(
        G,
        cdr,
    )

    add_transaction_edges(
        G,
        transactions,
    )

    add_ipdr_edges(
        G,
        ipdr,
    )

    add_social_edges(
        G,
        social,
    )

    return G


# ============================================================
# GRAPH SUMMARY
# ============================================================

def get_graph_summary(
    G: nx.MultiDiGraph,
) -> dict[str, int]:
    """
    Return basic graph statistics.
    """

    node_type_counts: dict[str, int] = {}

    for _, attributes in G.nodes(data=True):

        node_type = attributes.get(
            "node_type",
            "UNKNOWN",
        )

        node_type_counts[node_type] = (
            node_type_counts.get(node_type, 0) + 1
        )

    relationship_counts: dict[str, int] = {}

    for _, _, attributes in G.edges(data=True):

        relationship = attributes.get(
            "relationship",
            "UNKNOWN",
        )

        relationship_counts[relationship] = (
            relationship_counts.get(
                relationship,
                0,
            )
            + 1
        )

    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "person_nodes": node_type_counts.get(
            "PERSON",
            0,
        ),
        "phone_nodes": node_type_counts.get(
            "PHONE",
            0,
        ),
        "bank_nodes": node_type_counts.get(
            "BANK",
            0,
        ),
        "ip_nodes": node_type_counts.get(
            "IP",
            0,
        ),
        "social_nodes": node_type_counts.get(
            "SOCIAL",
            0,
        ),
        "called_edges": relationship_counts.get(
            "CALLED",
            0,
        ),
        "transfer_edges": relationship_counts.get(
            "TRANSFERRED",
            0,
        ),
        "uses_edges": relationship_counts.get(
            "USES",
            0,
        ),
        "social_edges": relationship_counts.get(
            "HAS_SOCIAL",
            0,
        ),
    }


# ============================================================
# FIND NODES OF A TYPE
# ============================================================

def get_nodes_by_type(
    G: nx.MultiDiGraph,
    node_type: str,
) -> list[str]:
    """
    Return node IDs belonging to a particular type.
    """

    return [
        node
        for node, attributes
        in G.nodes(data=True)
        if attributes.get("node_type")
        == node_type
    ]


# ============================================================
# DIRECT RELATIONSHIPS
# ============================================================

def get_entity_relationships(
    G: nx.MultiDiGraph,
    node_id: str,
) -> list[dict[str, Any]]:
    """
    Return incoming and outgoing relationships
    for a node.
    """

    if node_id not in G:
        return []

    relationships = []

    # --------------------------------------------------------
    # Outgoing
    # --------------------------------------------------------

    for _, target, attributes in G.out_edges(
        node_id,
        data=True,
    ):

        relationships.append(
            {
                "direction": "OUT",
                "source": node_id,
                "target": target,
                **attributes,
            }
        )

    # --------------------------------------------------------
    # Incoming
    # --------------------------------------------------------

    for source, _, attributes in G.in_edges(
        node_id,
        data=True,
    ):

        relationships.append(
            {
                "direction": "IN",
                "source": source,
                "target": node_id,
                **attributes,
            }
        )

    return relationships