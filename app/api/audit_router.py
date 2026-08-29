from fastapi import APIRouter, HTTPException

from app.orchestrator.audit_orchestrator import AuditOrchestrator
from app.schema.audit import AuditRequest


router = APIRouter()

@router.post("/audit")
async def audit_article(request: AuditRequest):
    try:
        orchestrator = AuditOrchestrator()

        report = await orchestrator.audit(
            str(request.url)
        )

        return report

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )