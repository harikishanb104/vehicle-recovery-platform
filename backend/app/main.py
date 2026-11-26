from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.eligibility import router as eligibility_router
from app.api.scans import router as scans_router
from app.config import DATABASE_URL
from app.database import check_connection, get_engine

app = FastAPI(title="Plate Scan & Case Matching Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173","http://127.0.0.1:8000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(scans_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(eligibility_router)


@app.get("/")
def root() -> dict[str, str]:
    """Identify the service without touching the database."""
    return {"service": "plate-scan-case-matching", "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    """Report whether this process can run a query against Postgres."""
    if not DATABASE_URL:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL is not set. Copy backend/.env.example to backend/.env.",
        )
    try:
        check_connection(get_engine())
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"database unavailable: {exc.__class__.__name__}",
        ) from exc
    return {"status": "ok", "database": "connected"}
