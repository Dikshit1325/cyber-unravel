from __future__ import annotations

from typing import Any

import pandas as pd


class EntityResolver:
    """
    Exact-match entity resolution engine.

    Converts different identifiers into a common person_id.

    Supported identifiers:
        person_id
        phone
        bank_account
        social_id
        ip_address
        device_id
    """

    IDENTIFIER_COLUMNS = [
        "person_id",
        "phone",
        "bank_account",
        "social_id",
        "ip_address",
        "device_id",
    ]

    def __init__(self, persons: pd.DataFrame):
        self.persons = persons.copy()

        self._indexes: dict[str, dict[str, str]] = {}

        self._build_indexes()

    # ============================================================
    # BUILD EXACT-MATCH INDEXES
    # ============================================================

    def _build_indexes(self) -> None:
        """
        Build exact identifier -> person_id indexes.
        """

        for column in self.IDENTIFIER_COLUMNS:

            self._indexes[column] = {}

            for _, row in self.persons.iterrows():

                value = row[column]

                if pd.isna(value):
                    continue

                value = str(value).strip()

                if not value:
                    continue

                person_id = str(
                    row["person_id"]
                ).strip()

                self._indexes[column][value] = person_id

    # ============================================================
    # RESOLVE ANY IDENTIFIER
    # ============================================================

    def resolve(
        self,
        identifier: str,
    ) -> dict[str, Any] | None:
        """
        Resolve an identifier using exact matching.

        Example:

            PH001 -> P001
            A001  -> P001
            SOC001 -> P001
            DEV001 -> P001
        """

        if identifier is None:
            return None

        identifier = str(identifier).strip()

        if not identifier:
            return None

        for column in self.IDENTIFIER_COLUMNS:

            person_id = self._indexes[column].get(
                identifier
            )

            if person_id is not None:
                return self.get_entity(person_id)

        return None

    # ============================================================
    # RESOLVE BY IDENTIFIER TYPE
    # ============================================================

    def resolve_by_type(
        self,
        identifier_type: str,
        identifier: str,
    ) -> dict[str, Any] | None:
        """
        Resolve an identifier when the identifier type is known.

        Example:

            resolve_by_type("phone", "PH001")
            resolve_by_type("bank_account", "A001")
        """

        if identifier_type not in self.IDENTIFIER_COLUMNS:
            raise ValueError(
                f"Unsupported identifier type: "
                f"{identifier_type}"
            )

        if identifier is None:
            return None

        identifier = str(identifier).strip()

        person_id = self._indexes[
            identifier_type
        ].get(identifier)

        if person_id is None:
            return None

        return self.get_entity(person_id)

    # ============================================================
    # GET COMPLETE PERSON ENTITY
    # ============================================================

    def get_entity(
        self,
        person_id: str,
    ) -> dict[str, Any] | None:
        """
        Return complete identity information.
        """

        person_id = str(person_id).strip()

        matches = self.persons[
            self.persons["person_id"] == person_id
        ]

        if matches.empty:
            return None

        row = matches.iloc[0]

        return {
            "person_id": str(row["person_id"]),
            "name": str(row["name"]),
            "age": int(row["age"]),
            "phone": str(row["phone"]),
            "bank_account": str(
                row["bank_account"]
            ),
            "social_id": str(
                row["social_id"]
            ),
            "ip_address": str(
                row["ip_address"]
            ),
            "device_id": str(
                row["device_id"]
            ),
        }

    # ============================================================
    # GET ALL IDENTIFIERS FOR A PERSON
    # ============================================================

    def get_identifiers(
        self,
        person_id: str,
    ) -> dict[str, str] | None:
        """
        Return the identity mapping for a person.
        """

        entity = self.get_entity(person_id)

        if entity is None:
            return None

        return {
            "person_id": entity["person_id"],
            "phone": entity["phone"],
            "bank_account": entity["bank_account"],
            "social_id": entity["social_id"],
            "ip_address": entity["ip_address"],
            "device_id": entity["device_id"],
        }

    # ============================================================
    # SEARCH PERSON BY NAME
    # ============================================================

    def find_by_name(
        self,
        name: str,
    ) -> list[dict[str, Any]]:
        """
        Find persons using case-insensitive partial name matching.
        """

        if not name:
            return []

        search_name = name.strip().lower()

        matches = self.persons[
            self.persons["name"]
            .str.lower()
            .str.contains(
                search_name,
                na=False,
                regex=False,
            )
        ]

        results = []

        for person_id in matches["person_id"]:
            entity = self.get_entity(person_id)

            if entity is not None:
                results.append(entity)

        return results

    # ============================================================
    # RESOLVE MULTIPLE IDENTIFIERS
    # ============================================================

    def resolve_many(
        self,
        identifiers: list[str],
    ) -> list[dict[str, Any]]:
        """
        Resolve multiple identifiers.

        Duplicate persons are removed.
        """

        results = []
        seen_person_ids = set()

        for identifier in identifiers:

            entity = self.resolve(identifier)

            if entity is None:
                continue

            person_id = entity["person_id"]

            if person_id in seen_person_ids:
                continue

            seen_person_ids.add(person_id)
            results.append(entity)

        return results


# ================================================================
# CONVENIENCE FUNCTION
# ================================================================

def create_entity_resolver(
    persons: pd.DataFrame,
) -> EntityResolver:
    """
    Create an EntityResolver from the persons dataset.
    """

    return EntityResolver(persons)