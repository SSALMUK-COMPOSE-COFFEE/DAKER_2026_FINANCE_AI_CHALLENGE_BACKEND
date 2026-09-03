from fastapi import APIRouter

from app.schemas import EvidenceChecklistRequest, EvidenceChecklistResponse
from app.services.evidence import build_checklist

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/checklist", response_model=EvidenceChecklistResponse)
def checklist(req: EvidenceChecklistRequest) -> EvidenceChecklistResponse:
    items = build_checklist(req.answers)
    return EvidenceChecklistResponse(
        items=items, must_count=sum(1 for i in items if i.priority == "필수")
    )
