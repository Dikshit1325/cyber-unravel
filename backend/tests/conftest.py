import pytest

# Demo user IDs defined in auth_service
ADMIN = "admin_01"
INVESTIGATOR = "investigator_01"
ANALYST = "analyst_01"

def auth_headers(user_id: str):
    return {"X-User-Id": user_id}
