try:
    import bcrypt
except ImportError:
    class _FallbackBcrypt:
        @staticmethod
        def hashpw(pw: bytes, _):
            return pw
        @staticmethod
        def checkpw(pw: bytes, hashed: bytes) -> bool:
            return pw == hashed
        @staticmethod
        def gensalt():
            return b""
    bcrypt = _FallbackBcrypt()
import uuid
from dataclasses import dataclass
from typing import Dict, List

# Demo user definitions (passwords are bcrypt hashed)
_demo_users = {
    "admin_01": {
        "hashed_pw": bcrypt.hashpw(b"adminpass", bcrypt.gensalt()),
        "role": "ADMIN",
    },
    "investigator_01": {
        "hashed_pw": bcrypt.hashpw(b"investigatorpass", bcrypt.gensalt()),
        "role": "INVESTIGATOR",
    },
    "analyst_01": {
        "hashed_pw": bcrypt.hashpw(b"analystpass", bcrypt.gensalt()),
        "role": "ANALYST",
    },
}

# Permission matrix
_permission_matrix: Dict[str, List[str]] = {
    "ADMIN": [
        "search",
        "entity_lookup",
        "graph_view",
        "transaction_view",
        "communication_view",
        "network_view",
        "anomaly_view",
        "timeline_view",
        "audit_view",
        "user_management",
        "relationship_view",
        "incident_snapshot_view",
    ],
    "INVESTIGATOR": [
        "search",
        "entity_lookup",
        "graph_view",
        "transaction_view",
        "communication_view",
        "network_view",
        "anomaly_view",
        "timeline_view",
        "audit_view",
        "relationship_view",
        "incident_snapshot_view",
    ],
    "ANALYST": [
        "search",
        "entity_lookup",
        "graph_view",
        "transaction_view",
        "communication_view",
        "network_view",
        "anomaly_view",
        "timeline_view",
        "relationship_view",
        "incident_snapshot_view",
    ],
}

@dataclass
class AuthResult:
    user_id: str
    role: str

class AuthService:
    """Simple authentication and RBAC service for the prototype.

    * `authenticate` validates a username/password pair.
    * `resolve_role` fetches a role for a known user ID.
    * `has_permission` checks the matrix.
    """

    def __init__(self):
        self._users = _demo_users

    def authenticate(self, username: str, password: str) -> AuthResult:
        user = self._users.get(username)
        if not user:
            raise ValueError("Invalid credentials")
        if not bcrypt.checkpw(password.encode("utf-8"), user["hashed_pw"]):
            raise ValueError("Invalid credentials")
        return AuthResult(user_id=username, role=user["role"])

    def resolve_role(self, user_id: str) -> str:
        user = self._users.get(user_id)
        if not user:
            raise ValueError("Unknown user")
        return user["role"]

    def has_permission(self, role: str, action: str) -> bool:
        return action in _permission_matrix.get(role, [])

# Export a singleton for easy import elsewhere
auth_service = AuthService()
