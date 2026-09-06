import re
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# Mapping from request path prefix to (action, resource_type)
_ROUTE_ACTION_MAP = [
    (re.compile(r"^/api/search"), "search", "search"),
    (re.compile(r"^/api/case"), "search", "case"),
    (re.compile(r"^/api/lead"), "search", "lead"),
    (re.compile(r"^/api/entity/(?P<entity_id>[^/]+)/summary"), "entity_lookup", "entity_summary"),
    (re.compile(r"^/api/entity/(?P<entity_id>[^/]+)/timeline"), "timeline_view", "timeline"),
    (re.compile(r"^/api/entity/(?P<entity_id>[^/]+)/connections"), "entity_lookup", "entity"),
    (re.compile(r"^/api/entity/(?P<entity_id>[^/]+)"), "entity_lookup", "entity"),
    (re.compile(r"^/api/graph"), "graph_view", "graph"),
    (re.compile(r"^/api/transactions/(?P<transaction_id>[^/]+)"), "transaction_view", "transaction"),
    (re.compile(r"^/api/transactions"), "transaction_view", "transaction"),
    (re.compile(r"^/api/communications/(?P<communication_id>[^/]+)"), "communication_view", "communication"),
    (re.compile(r"^/api/communications"), "communication_view", "communication"),
    (re.compile(r"^/api/network/(?P<ipdr_id>[^/]+)"), "network_view", "network"),
    (re.compile(r"^/api/network"), "network_view", "network"),
    (re.compile(r"^/api/anomalies"), "anomaly_view", "anomaly"),
    (re.compile(r"^/api/timeline"), "timeline_view", "timeline"),
    (re.compile(r"^/api/audit"), "audit_view", "audit"),
    (re.compile(r"^/api/relationships"), "relationship_view", "relationship"),
    (re.compile(r"^/api/incident_snapshot"), "incident_snapshot_view", "incident_snapshot"),
]

def _match_route(path: str):
    for pattern, action, rtype in _ROUTE_ACTION_MAP:
        m = pattern.match(path)
        if m:
            return action, rtype, m.groupdict()
    return None, None, {}

class AuthAuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_service, audit_service):
        super().__init__(app)
        self.auth_service = auth_service
        self.audit_service = audit_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Match route early to identify target action and resource
        action, resource_type, groups = _match_route(request.url.path)
        resource_id = next(iter(groups.values())) if groups else None

        if not action:
            # Not a protected route – pass through without auth or audit
            return await call_next(request)

        # Resolve user identity strictly from X-User-Id header (never trust X-User-Role from client)
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            response = JSONResponse({"detail": "Missing authentication"}, status_code=401)
            self.audit_service.log(
                user_id="anonymous",
                role="NONE",
                action=action,
                endpoint=request.url.path,
                resource_type=resource_type,
                resource_id=resource_id,
                status="DENIED",
                metadata={"reason": "Missing X-User-Id header"},
            )
            return response

        try:
            role = self.auth_service.resolve_role(user_id)
        except Exception:
            response = JSONResponse({"detail": "Invalid user"}, status_code=401)
            self.audit_service.log(
                user_id=user_id,
                role="NONE",
                action=action,
                endpoint=request.url.path,
                resource_type=resource_type,
                resource_id=resource_id,
                status="DENIED",
                metadata={"reason": "User not found"},
            )
            return response

        # RBAC Authorization check based strictly on resolved role
        if not self.auth_service.has_permission(role, action):
            response = JSONResponse({"detail": "Forbidden"}, status_code=403)
            self.audit_service.log(
                user_id=user_id,
                role=role,
                action=action,
                endpoint=request.url.path,
                resource_type=resource_type,
                resource_id=resource_id,
                status="DENIED",
                metadata={"reason": "Insufficient permission"},
            )
            return response

        # Proceed to actual endpoint
        response = await call_next(request)

        # Record audit entry – SUCCESS if 2xx, otherwise record actual status
        status_label = "SUCCESS" if 200 <= response.status_code < 300 else "FAILURE"
        self.audit_service.log(
            user_id=user_id,
            role=role,
            action=action,
            endpoint=request.url.path,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status_label,
        )
        return response
