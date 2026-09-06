# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from backend.api package
from backend.api.graph_api import router as graph_router
from backend.api.anomalies import router as anomalies_router
from backend.api.audit import router as audit_router
from backend.api.transactions import router as transactions_router
from backend.api.communications import router as communications_router
from backend.api.network import router as network_router
from backend.api.search import router as search_router
from backend.api.lead import router as lead_router
from backend.api.relationships import router as relationships_router
from backend.api.incident_snapshot import router as incident_snapshot_router

# Import services and middleware from backend package
from backend.services.auth_service import auth_service
from backend.services.audit_service import audit_service
from backend.api.middleware import AuthAuditMiddleware

app = FastAPI(
    title="Digital Investigation Intelligence Platform",
    description=(
        "Backend API for telecom, financial, IPDR, "
        "and social-media investigation analytics."
    ),
    version="1.0.0",
)

# Enable CORS (allow all for hackathon prototype)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication and audit middleware
app.add_middleware(
    AuthAuditMiddleware,
    auth_service=auth_service,
    audit_service=audit_service,
)

# Include API routers
app.include_router(graph_router)
app.include_router(anomalies_router)
app.include_router(audit_router)
app.include_router(transactions_router)
app.include_router(communications_router)
app.include_router(network_router)
app.include_router(search_router)
app.include_router(lead_router)
app.include_router(relationships_router)
app.include_router(incident_snapshot_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Digital Investigation Intelligence Platform",
        "version": "1.0.0",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}