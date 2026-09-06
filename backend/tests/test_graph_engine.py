from services.data_loader import load_all_data
from services.graph_engine import (
    build_investigation_graph,
    get_entity_relationships,
    get_graph_summary,
    get_nodes_by_type,
)


def test_investigation_graph():

    # ============================================================
    # LOAD DATA
    # ============================================================

    data = load_all_data()

    # ============================================================
    # BUILD GRAPH
    # ============================================================

    G = build_investigation_graph(data)

    # ============================================================
    # GRAPH TYPE
    # ============================================================

    assert G.is_multigraph()
    assert G.is_directed()

    # ============================================================
    # IMPORTANT PERSON NODES
    # ============================================================

    assert "person:P001" in G
    assert "person:P002" in G
    assert "person:P003" in G

    # ============================================================
    # IDENTITY NODES
    # ============================================================

    assert "phone:PH001" in G
    assert "bank:A001" in G
    assert "ip:10.10.1.11" in G
    assert "social:SOC001" in G

    # ============================================================
    # PERSON -> PHONE
    # ============================================================

    phone_edges = G.get_edge_data(
        "person:P001",
        "phone:PH001",
    )

    assert phone_edges is not None

    assert any(
        edge["relationship"] == "USES"
        for edge in phone_edges.values()
    )

    # ============================================================
    # PERSON -> BANK
    # ============================================================

    bank_edges = G.get_edge_data(
        "person:P001",
        "bank:A001",
    )

    assert bank_edges is not None

    assert any(
        edge["relationship"] == "OWNS"
        for edge in bank_edges.values()
    )

    # ============================================================
    # PERSON -> SOCIAL
    # ============================================================

    social_edges = G.get_edge_data(
        "person:P001",
        "social:SOC001",
    )

    assert social_edges is not None

    assert any(
        edge["relationship"] == "HAS_SOCIAL"
        for edge in social_edges.values()
    )

    # ============================================================
    # CDR RELATIONSHIP
    # ============================================================

    called_edges = G.get_edge_data(
        "person:P001",
        "person:P002",
    )

    assert called_edges is not None

    assert any(
        edge["relationship"] == "CALLED"
        for edge in called_edges.values()
    )

    # ============================================================
    # CDR PROVENANCE
    # ============================================================

    found_call = False

    for edge in called_edges.values():

        if edge["relationship"] != "CALLED":
            continue

        if edge["source_dataset"] != "cdr.csv":
            continue

        if edge["source"] == "CDR0111":

            found_call = True

            assert edge["duration_seconds"] == 261
            assert (
                str(edge["timestamp"])
                .startswith("2026-09-01 18:02")
            )

    assert found_call

    # ============================================================
    # TRANSACTION RELATIONSHIP
    # ============================================================

    transfer_edges = G.get_edge_data(
        "bank:A001",
        "bank:A002",
    )

    assert transfer_edges is not None

    assert any(
        edge["relationship"] == "TRANSFERRED"
        for edge in transfer_edges.values()
    )

    # ============================================================
    # TRANSACTION PROVENANCE
    # ============================================================

    found_transaction = False

    for edge in transfer_edges.values():

        if edge["relationship"] != "TRANSFERRED":
            continue

        if edge["source"] != "TX0121":
            continue

        found_transaction = True

        assert edge["amount"] == 100000
        assert edge["source_dataset"] == (
            "transactions.csv"
        )

        assert (
            str(edge["timestamp"])
            .startswith("2026-09-01 18:15")
        )

    assert found_transaction

    # ============================================================
    # SHARED INCIDENT IP
    # ============================================================

    assert "ip:203.0.113.77" in G

    p001_ip_edges = G.get_edge_data(
        "person:P001",
        "ip:203.0.113.77",
    )

    p002_ip_edges = G.get_edge_data(
        "person:P002",
        "ip:203.0.113.77",
    )

    p003_ip_edges = G.get_edge_data(
        "person:P003",
        "ip:203.0.113.77",
    )

    assert p001_ip_edges is not None
    assert p002_ip_edges is not None
    assert p003_ip_edges is not None

    # ============================================================
    # NODE TYPE CHECKS
    # ============================================================

    assert (
        G.nodes["person:P001"]["node_type"]
        == "PERSON"
    )

    assert (
        G.nodes["phone:PH001"]["node_type"]
        == "PHONE"
    )

    assert (
        G.nodes["bank:A001"]["node_type"]
        == "BANK"
    )

    assert (
        G.nodes["ip:10.10.1.11"]["node_type"]
        == "IP"
    )

    assert (
        G.nodes["social:SOC001"]["node_type"]
        == "SOCIAL"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    summary = get_graph_summary(G)

    assert summary["nodes"] > 0
    assert summary["edges"] > 0
    assert summary["person_nodes"] == 10
    assert summary["phone_nodes"] == 10
    assert summary["bank_nodes"] == 10
    assert summary["social_nodes"] == 10

    # ============================================================
    # NODE FILTER
    # ============================================================

    person_nodes = get_nodes_by_type(
        G,
        "PERSON",
    )

    assert len(person_nodes) == 10

    # ============================================================
    # RELATIONSHIP QUERY
    # ============================================================

    relationships = get_entity_relationships(
        G,
        "person:P001",
    )

    assert len(relationships) > 0

    assert any(
        relationship["relationship"] == "CALLED"
        for relationship in relationships
    )

    print(
        "\n✓ INVESTIGATION GRAPH TEST PASSED"
    )

def test_social_graph_integration():
    import pandas as pd
    from services.graph_engine import create_graph, add_person_nodes, add_social_edges

    G = create_graph()
    
    persons_df = pd.DataFrame([
        {"person_id": "P001", "name": "Alice", "age": 30, "phone": "", "bank_account": "", "ip_address": "", "social_id": "SOC001"}
    ])
    
    social_df = pd.DataFrame([
        {"social_event_id": "SOC_EVT0001", "person_id": "P001", "platform": "Twitter", "timestamp": "2026-09-01 12:00:00", "activity_type": "POST", "scenario_tag": "NORMAL"}
    ])
    
    add_person_nodes(G, persons_df)
    add_social_edges(G, social_df)
    
    # 1. Social activity is represented in the graph
    assert "social_event:SOC_EVT0001" in G
    
    # 2. Correct person/entity is connected to each social event
    edges = G.get_edge_data("person:P001", "social_event:SOC_EVT0001")
    assert edges is not None
    
    found = False
    for edge in edges.values():
        if edge["relationship"] == "PERFORMED_SOCIAL_ACTIVITY":
            found = True
            # 3. timestamp is preserved
            assert edge["timestamp"] == "2026-09-01 12:00:00"
            # 4. platform is preserved
            assert edge["platform"] == "Twitter"
            # 5. activity_type is preserved
            assert edge["activity_type"] == "POST"
            # 6. source/social_event_id is preserved
            assert edge["source"] == "SOC_EVT0001"
            
    assert found
    
    # 8. Empty social dataframe does not break graph creation
    G2 = create_graph()
    add_social_edges(G2, pd.DataFrame())
    assert len(G2.nodes) == 0
    
    # 9. Invalid social records are handled safely
    invalid_social_df = pd.DataFrame([
        {"social_event_id": "", "person_id": "P001", "platform": "Twitter", "timestamp": "2026-09-01", "activity_type": "POST", "scenario_tag": "NORMAL"},
        {"social_event_id": None, "person_id": "P001", "platform": "Twitter", "timestamp": "2026-09-01", "activity_type": "POST", "scenario_tag": "NORMAL"}
    ])
    G3 = create_graph()
    add_person_nodes(G3, persons_df)
    add_social_edges(G3, invalid_social_df)
    # Shouldn't add any social event nodes for invalid event ids
    assert len([n for n, attr in G3.nodes(data=True) if attr.get("node_type") == "SOCIAL_EVENT"]) == 0