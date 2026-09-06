from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


# ============================================================
# EXPECTED COLUMN SCHEMAS
# ============================================================

PERSON_COLUMNS = [
    "person_id",
    "name",
    "age",
    "phone",
    "bank_account",
    "social_id",
    "ip_address",
    "device_id",
]

CDR_COLUMNS = [
    "cdr_id",
    "caller",
    "receiver",
    "timestamp",
    "duration_seconds",
    "scenario_tag",
]

TRANSACTION_COLUMNS = [
    "transaction_id",
    "sender_account",
    "receiver_account",
    "amount",
    "timestamp",
    "channel",
    "scenario_tag",
]

IPDR_COLUMNS = [
    "ipdr_id",
    "person_id",
    "ip_address",
    "timestamp",
    "session_duration_seconds",
    "device_id",
    "scenario_tag",
]

SOCIAL_COLUMNS = [
    "social_event_id",
    "person_id",
    "platform",
    "timestamp",
    "activity_type",
    "scenario_tag",
]

ENTITY_MAPPING_COLUMNS = [
    "person_id",
    "phone",
    "bank_account",
    "social_id",
    "ip_address",
    "device_id",
]


# ============================================================
# GENERIC CSV LOADER
# ============================================================

def _load_csv(filename: str) -> pd.DataFrame:
    """
    Load a CSV file from backend/data.
    """

    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            f"Dataset is empty: {file_path}"
        )

    return df


# ============================================================
# COLUMN VALIDATION
# ============================================================

def _validate_columns(
    df: pd.DataFrame,
    expected_columns: list[str],
    dataset_name: str,
) -> None:
    """
    Make sure the dataset contains all required columns.
    """

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing columns: "
            f"{missing_columns}"
        )


# ============================================================
# STRING NORMALIZATION
# ============================================================

def _normalize_strings(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """
    Convert selected columns to pandas StringDtype.
    """

    for column in columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    return df


# ============================================================
# NUMERIC NORMALIZATION
# ============================================================

def _normalize_numeric(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """
    Convert selected columns to numeric values.
    """

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="raise",
            )

    return df


# ============================================================
# TIMESTAMP NORMALIZATION
# ============================================================

def _normalize_timestamp(
    df: pd.DataFrame,
    column: str = "timestamp",
) -> pd.DataFrame:
    """
    Convert timestamp column to pandas datetime.
    """

    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="raise",
        )

    return df


# ============================================================
# DUPLICATE ID CHECK
# ============================================================

def _check_duplicate_ids(
    df: pd.DataFrame,
    id_column: str,
    dataset_name: str,
) -> None:
    """
    Check that a dataset's primary ID is unique.
    """

    if id_column not in df.columns:
        return

    duplicate_count = df[id_column].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"{dataset_name} contains "
            f"{duplicate_count} duplicate {id_column} values."
        )


# ============================================================
# PERSONS
# ============================================================

def load_persons() -> pd.DataFrame:
    """
    Load and normalize persons.csv.
    """

    df = _load_csv("persons.csv")

    _validate_columns(
        df,
        PERSON_COLUMNS,
        "persons.csv",
    )

    string_columns = [
        "person_id",
        "name",
        "phone",
        "bank_account",
        "social_id",
        "ip_address",
        "device_id",
    ]

    _normalize_strings(df, string_columns)

    _normalize_numeric(
        df,
        ["age"],
    )

    _check_duplicate_ids(
        df,
        "person_id",
        "persons.csv",
    )

    return df


# ============================================================
# CDR
# ============================================================

def load_cdr() -> pd.DataFrame:
    """
    Load and normalize cdr.csv.
    """

    df = _load_csv("cdr.csv")

    _validate_columns(
        df,
        CDR_COLUMNS,
        "cdr.csv",
    )

    string_columns = [
        "cdr_id",
        "caller",
        "receiver",
        "scenario_tag",
    ]

    _normalize_strings(df, string_columns)

    _normalize_numeric(
        df,
        ["duration_seconds"],
    )

    _normalize_timestamp(df)

    _check_duplicate_ids(
        df,
        "cdr_id",
        "cdr.csv",
    )

    return df


# ============================================================
# TRANSACTIONS
# ============================================================

def load_transactions() -> pd.DataFrame:
    """
    Load and normalize transactions.csv.

    Actual schema:
        transaction_id
        sender_account
        receiver_account
        amount
        timestamp
        channel
        scenario_tag
    """

    df = _load_csv("transactions.csv")

    _validate_columns(
        df,
        TRANSACTION_COLUMNS,
        "transactions.csv",
    )

    string_columns = [
        "transaction_id",
        "sender_account",
        "receiver_account",
        "channel",
        "scenario_tag",
    ]

    _normalize_strings(df, string_columns)

    _normalize_numeric(
        df,
        ["amount"],
    )

    _normalize_timestamp(df)

    _check_duplicate_ids(
        df,
        "transaction_id",
        "transactions.csv",
    )

    return df


# ============================================================
# IPDR
# ============================================================

def load_ipdr() -> pd.DataFrame:
    """
    Load and normalize ipdr.csv.
    """

    df = _load_csv("ipdr.csv")

    _validate_columns(
        df,
        IPDR_COLUMNS,
        "ipdr.csv",
    )

    string_columns = [
        "ipdr_id",
        "person_id",
        "ip_address",
        "device_id",
        "scenario_tag",
    ]

    _normalize_strings(df, string_columns)

    _normalize_numeric(
        df,
        ["session_duration_seconds"],
    )

    _normalize_timestamp(df)

    _check_duplicate_ids(
        df,
        "ipdr_id",
        "ipdr.csv",
    )

    return df


# ============================================================
# SOCIAL
# ============================================================

def load_social() -> pd.DataFrame:
    """
    Load and normalize social.csv.
    """

    df = _load_csv("social.csv")

    _validate_columns(
        df,
        SOCIAL_COLUMNS,
        "social.csv",
    )

    string_columns = [
        "social_event_id",
        "person_id",
        "platform",
        "activity_type",
        "scenario_tag",
    ]

    _normalize_strings(df, string_columns)

    _normalize_timestamp(df)

    _check_duplicate_ids(
        df,
        "social_event_id",
        "social.csv",
    )

    return df


# ============================================================
# ENTITY MAPPING
# ============================================================

def load_entity_mapping() -> pd.DataFrame:
    """
    Load and normalize entity_mapping.csv.

    This file connects:
        person
        phone
        bank account
        social account
        IP address
        device
    """

    df = _load_csv("entity_mapping.csv")

    _validate_columns(
        df,
        ENTITY_MAPPING_COLUMNS,
        "entity_mapping.csv",
    )

    _normalize_strings(
        df,
        ENTITY_MAPPING_COLUMNS,
    )

    _check_duplicate_ids(
        df,
        "person_id",
        "entity_mapping.csv",
    )

    return df


# ============================================================
# RELATIONSHIP VALIDATION
# ============================================================

def validate_relationships(
    persons: pd.DataFrame,
    cdr: pd.DataFrame,
    transactions: pd.DataFrame,
    ipdr: pd.DataFrame,
    social: pd.DataFrame,
) -> None:
    """
    Validate relationships between datasets.

    CDR:
        caller / receiver -> person_id

    Transactions:
        sender_account / receiver_account -> bank_account

    IPDR:
        person_id -> person_id

    Social:
        person_id -> person_id
    """

    # --------------------------------------------------------
    # PERSON IDs
    # --------------------------------------------------------

    person_ids = set(
        persons["person_id"].dropna()
    )

    # --------------------------------------------------------
    # BANK ACCOUNT IDs
    # --------------------------------------------------------

    bank_accounts = set(
        persons["bank_account"].dropna()
    )

    # --------------------------------------------------------
    # CDR
    # --------------------------------------------------------

    caller_ids = set(
        cdr["caller"].dropna()
    )

    receiver_ids = set(
        cdr["receiver"].dropna()
    )

    invalid_callers = caller_ids - person_ids
    invalid_receivers = receiver_ids - person_ids

    if invalid_callers:
        raise ValueError(
            f"CDR contains unknown caller person IDs: "
            f"{sorted(invalid_callers)}"
        )

    if invalid_receivers:
        raise ValueError(
            f"CDR contains unknown receiver person IDs: "
            f"{sorted(invalid_receivers)}"
        )

    # --------------------------------------------------------
    # TRANSACTIONS
    # --------------------------------------------------------

    sender_accounts = set(
        transactions["sender_account"].dropna()
    )

    receiver_accounts = set(
        transactions["receiver_account"].dropna()
    )

    invalid_senders = sender_accounts - bank_accounts
    invalid_receivers = receiver_accounts - bank_accounts

    if invalid_senders:
        raise ValueError(
            f"Transactions contain unknown sender "
            f"bank accounts: {sorted(invalid_senders)}"
        )

    if invalid_receivers:
        raise ValueError(
            f"Transactions contain unknown receiver "
            f"bank accounts: {sorted(invalid_receivers)}"
        )

    # --------------------------------------------------------
    # IPDR
    # --------------------------------------------------------

    ipdr_person_ids = set(
        ipdr["person_id"].dropna()
    )

    invalid_ipdr_persons = (
        ipdr_person_ids - person_ids
    )

    if invalid_ipdr_persons:
        raise ValueError(
            f"IPDR contains unknown person IDs: "
            f"{sorted(invalid_ipdr_persons)}"
        )

    # --------------------------------------------------------
    # SOCIAL
    # --------------------------------------------------------

    social_person_ids = set(
        social["person_id"].dropna()
    )

    invalid_social_persons = (
        social_person_ids - person_ids
    )

    if invalid_social_persons:
        raise ValueError(
            f"Social data contains unknown person IDs: "
            f"{sorted(invalid_social_persons)}"
        )


# ============================================================
# LOAD EVERYTHING
# ============================================================

def load_all_data() -> dict[str, pd.DataFrame]:
    """
    Load all investigation datasets.

    Returns:
        Dictionary containing normalized DataFrames.
    """

    persons = load_persons()
    cdr = load_cdr()
    transactions = load_transactions()
    ipdr = load_ipdr()
    social = load_social()
    entity_mapping = load_entity_mapping()

    # Validate cross-dataset relationships
    validate_relationships(
        persons,
        cdr,
        transactions,
        ipdr,
        social,
    )

    return {
        "persons": persons,
        "cdr": cdr,
        "transactions": transactions,
        "ipdr": ipdr,
        "social": social,
        "entity_mapping": entity_mapping,
    }


# ============================================================
# DATASET SUMMARY
# ============================================================

def get_dataset_summary(
    data: dict[str, pd.DataFrame],
) -> dict[str, int]:
    """
    Return the number of records in each dataset.
    """

    return {
        name: len(df)
        for name, df in data.items()
    }


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DIGITAL INVESTIGATION DATA LOADER")
    print("=" * 60)

    data = load_all_data()

    summary = get_dataset_summary(data)

    print("\nDataset Summary:")
    print("-" * 60)

    for name, count in summary.items():
        print(f"{name:20} : {count:>5} records")

    print("-" * 60)

    print("\nData Types:")
    print("-" * 60)

    for name, df in data.items():
        print(f"\n{name}:")
        print(df.dtypes)

    print("\n" + "=" * 60)
    print("✓ ALL DATASETS LOADED AND VALIDATED SUCCESSFULLY")
    print("=" * 60)