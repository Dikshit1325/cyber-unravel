import threading
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class AuditRecord:
    def __init__(
        self,
        audit_id: str,
        timestamp: str,
        user_id: str,
        role: str,
        action: str,
        endpoint: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        query: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.audit_id = audit_id
        self.timestamp = timestamp
        self.user_id = user_id
        self.role = role
        self.action = action
        self.endpoint = endpoint
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.status = status
        self.query = query
        self.metadata = metadata

    def as_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the audit record.
        All primary fields are always present; optional fields are added when not None.
        """
        data = {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "role": self.role,
            "action": self.action,
            "endpoint": self.endpoint,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "status": self.status,
        }
        if self.query is not None:
            data["query"] = self.query
        if self.metadata is not None:
            data["metadata"] = self.metadata
        return data

class AuditService:
    """Thread‑safe in‑memory audit log.

    * `log` records a new audit entry. All fields are required except optional ones.
    * `query` returns a list of dicts matching the supplied filters and ordered newest‑first.
    """

    def __init__(self):
        self._records: List[AuditRecord] = []
        self._lock = threading.Lock()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def log(
        self,
        *,
        user_id: str,
        role: str,
        action: str,
        endpoint: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        query: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        audit_id = str(uuid.uuid4())
        timestamp = self._now_iso()
        record = AuditRecord(
            audit_id=audit_id,
            timestamp=timestamp,
            user_id=user_id,
            role=role,
            action=action,
            endpoint=endpoint,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            query=query,
            metadata=metadata,
        )
        with self._lock:
            self._records.append(record)

    def query(
        self,
        *,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return matching audit records newest‑first.

        Filters accept ISO timestamps for `start_time` / `end_time`.
        """
        with self._lock:
            filtered = []
            for rec in reversed(self._records):  # newest first
                if user_id and rec.user_id != user_id:
                    continue
                if action and rec.action != action:
                    continue
                if resource_type and rec.resource_type != resource_type:
                    continue
                if status and rec.status != status:
                    continue
                if start_time and rec.timestamp < start_time:
                    continue
                if end_time and rec.timestamp > end_time:
                    continue
                filtered.append(rec.as_dict())
            return filtered

# Export a singleton for easy import
audit_service = AuditService()
