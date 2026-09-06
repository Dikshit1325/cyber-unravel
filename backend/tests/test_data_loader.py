from services.data_loader import load_all_data


def test_data_loader():
    """
    Test the complete investigation data loader.
    """

    # ============================================================
    # 1. LOAD DATA
    # ============================================================

    data = load_all_data()

    # ============================================================
    # 2. DATASET EXISTENCE
    # ============================================================

    assert "persons" in data
    assert "cdr" in data
    assert "transactions" in data
    assert "ipdr" in data
    assert "social" in data
    assert "entity_mapping" in data

    # ============================================================
    # 3. DATASETS ARE NOT EMPTY
    # ============================================================

    assert not data["persons"].empty
    assert not data["cdr"].empty
    assert not data["transactions"].empty
    assert not data["ipdr"].empty
    assert not data["social"].empty
    assert not data["entity_mapping"].empty

    # ============================================================
    # 4. PERSONS CHECKS
    # ============================================================

    assert data["persons"]["person_id"].dtype.name == "string"
    assert data["persons"]["name"].dtype.name == "string"
    assert data["persons"]["phone"].dtype.name == "string"
    assert data["persons"]["bank_account"].dtype.name == "string"
    assert data["persons"]["social_id"].dtype.name == "string"
    assert data["persons"]["ip_address"].dtype.name == "string"
    assert data["persons"]["device_id"].dtype.name == "string"

    assert data["persons"]["age"].dtype.kind in "fi"

    # ============================================================
    # 5. CDR CHECKS
    # ============================================================

    assert data["cdr"]["cdr_id"].dtype.name == "string"
    assert data["cdr"]["caller"].dtype.name == "string"
    assert data["cdr"]["receiver"].dtype.name == "string"
    assert data["cdr"]["scenario_tag"].dtype.name == "string"

    assert data["cdr"]["timestamp"].dtype.kind == "M"
    assert data["cdr"]["duration_seconds"].dtype.kind in "fi"

    # ============================================================
    # 6. TRANSACTION CHECKS
    # ============================================================

    assert data["transactions"]["transaction_id"].dtype.name == "string"

    assert (
        data["transactions"]["sender_account"].dtype.name
        == "string"
    )

    assert (
        data["transactions"]["receiver_account"].dtype.name
        == "string"
    )

    assert (
        data["transactions"]["channel"].dtype.name
        == "string"
    )

    assert (
        data["transactions"]["scenario_tag"].dtype.name
        == "string"
    )

    assert (
        data["transactions"]["timestamp"].dtype.kind
        == "M"
    )

    assert (
        data["transactions"]["amount"].dtype.kind
        in "fi"
    )

    # ============================================================
    # 7. IPDR CHECKS
    # ============================================================

    assert data["ipdr"]["ipdr_id"].dtype.name == "string"
    assert data["ipdr"]["person_id"].dtype.name == "string"
    assert data["ipdr"]["ip_address"].dtype.name == "string"
    assert data["ipdr"]["device_id"].dtype.name == "string"
    assert data["ipdr"]["scenario_tag"].dtype.name == "string"

    assert data["ipdr"]["timestamp"].dtype.kind == "M"

    assert (
        data["ipdr"]["session_duration_seconds"]
        .dtype.kind
        in "fi"
    )

    # ============================================================
    # 8. SOCIAL CHECKS
    # ============================================================

    assert (
        data["social"]["social_event_id"].dtype.name
        == "string"
    )

    assert (
        data["social"]["person_id"].dtype.name
        == "string"
    )

    assert (
        data["social"]["platform"].dtype.name
        == "string"
    )

    assert (
        data["social"]["activity_type"].dtype.name
        == "string"
    )

    assert (
        data["social"]["scenario_tag"].dtype.name
        == "string"
    )

    assert data["social"]["timestamp"].dtype.kind == "M"

    # ============================================================
    # 9. ENTITY MAPPING CHECKS
    # ============================================================

    assert (
        data["entity_mapping"]["person_id"].dtype.name
        == "string"
    )

    assert (
        data["entity_mapping"]["phone"].dtype.name
        == "string"
    )

    assert (
        data["entity_mapping"]["bank_account"].dtype.name
        == "string"
    )

    assert (
        data["entity_mapping"]["social_id"].dtype.name
        == "string"
    )

    assert (
        data["entity_mapping"]["ip_address"].dtype.name
        == "string"
    )

    assert (
        data["entity_mapping"]["device_id"].dtype.name
        == "string"
    )

    # ============================================================
    # 10. RELATIONSHIP CHECKS
    # ============================================================

    person_ids = set(
        data["persons"]["person_id"].dropna()
    )

    bank_accounts = set(
        data["persons"]["bank_account"].dropna()
    )

    # CDR -> Persons
    assert set(
        data["cdr"]["caller"].dropna()
    ).issubset(person_ids)

    assert set(
        data["cdr"]["receiver"].dropna()
    ).issubset(person_ids)

    # Transactions -> Bank Accounts
    assert set(
        data["transactions"]["sender_account"].dropna()
    ).issubset(bank_accounts)

    assert set(
        data["transactions"]["receiver_account"].dropna()
    ).issubset(bank_accounts)

    # IPDR -> Persons
    assert set(
        data["ipdr"]["person_id"].dropna()
    ).issubset(person_ids)

    # Social -> Persons
    assert set(
        data["social"]["person_id"].dropna()
    ).issubset(person_ids)

    # Entity Mapping -> Persons
    assert set(
        data["entity_mapping"]["person_id"].dropna()
    ).issubset(person_ids)

    # ============================================================
    # 11. FINAL SUCCESS MESSAGE
    # ============================================================

    print("\n✓ DATA LOADER TEST PASSED")