from fastapi import APIRouter, Query, Depends, HTTPException
from ..services.audit_service import audit_service
from ..services.auth_service import auth_service
from typing import Optional, List

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("/")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_time: Optional[str] = Query(None, description="ISO timestamp inclusive start"),
    end_time: Optional[str] = Query(None, description="ISO timestamp inclusive end"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS, DENIED, FAILURE)"),
):
    """Return audit records matching optional filters.
    Only ADMIN and INVESTIGATOR roles may call this endpoint – enforced by middleware.
    """
    # The middleware already resolved role and permission; here we simply query the service.
    records = audit_service.query(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
        status=status,
    )
    return {"total": len(records), "audit_records": records}
