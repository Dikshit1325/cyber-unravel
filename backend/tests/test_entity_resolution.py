from services.data_loader import load_all_data
from services.entity_resolution import EntityResolver


def test_entity_resolution():

    # ============================================================
    # LOAD DATA
    # ============================================================

    data = load_all_data()

    persons = data["persons"]

    resolver = EntityResolver(persons)

    # ============================================================
    # P001 DIRECT MATCH
    # ============================================================

    entity = resolver.resolve("P001")

    assert entity is not None
    assert entity["person_id"] == "P001"
    assert entity["name"] == "Aarav Mehta"

    # ============================================================
    # PHONE -> PERSON
    # ============================================================

    entity = resolver.resolve("PH001")

    assert entity is not None
    assert entity["person_id"] == "P001"

    # ============================================================
    # BANK ACCOUNT -> PERSON
    # ============================================================

    entity = resolver.resolve("A001")

    assert entity is not None
    assert entity["person_id"] == "P001"

    # ============================================================
    # SOCIAL ID -> PERSON
    # ============================================================

    entity = resolver.resolve("SOC001")

    assert entity is not None
    assert entity["person_id"] == "P001"

    # ============================================================
    # DEVICE -> PERSON
    # ============================================================

    entity = resolver.resolve("DEV001")

    assert entity is not None
    assert entity["person_id"] == "P001"

    # ============================================================
    # PERSON IP -> PERSON
    # ============================================================

    entity = resolver.resolve("10.10.1.11")

    assert entity is not None
    assert entity["person_id"] == "P001"

    # ============================================================
    # UNKNOWN IDENTIFIER
    # ============================================================

    entity = resolver.resolve(
        "UNKNOWN_IDENTIFIER"
    )

    assert entity is None

    # ============================================================
    # IDENTIFIER TYPE
    # ============================================================

    entity = resolver.resolve_by_type(
        "bank_account",
        "A001",
    )

    assert entity is not None
    assert entity["person_id"] == "P001"

    # ============================================================
    # GET ALL IDENTIFIERS
    # ============================================================

    identifiers = resolver.get_identifiers(
        "P001"
    )

    assert identifiers is not None

    assert identifiers["person_id"] == "P001"
    assert identifiers["phone"] == "PH001"
    assert identifiers["bank_account"] == "A001"
    assert identifiers["social_id"] == "SOC001"
    assert identifiers["ip_address"] == "10.10.1.11"
    assert identifiers["device_id"] == "DEV001"

    # ============================================================
    # NAME SEARCH
    # ============================================================

    results = resolver.find_by_name(
        "Aarav"
    )

    assert len(results) >= 1
    assert results[0]["person_id"] == "P001"

    # ============================================================
    # MULTIPLE IDENTIFIERS
    # ============================================================

    results = resolver.resolve_many(
        [
            "P001",
            "PH001",
            "A001",
            "SOC001",
            "DEV001",
        ]
    )

    # All identifiers belong to the same person.
    assert len(results) == 1
    assert results[0]["person_id"] == "P001"

    print(
        "\n✓ ENTITY RESOLUTION TEST PASSED"
    )