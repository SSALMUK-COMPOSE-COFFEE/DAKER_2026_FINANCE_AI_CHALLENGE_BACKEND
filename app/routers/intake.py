from fastapi import APIRouter

from app.schemas import IntakeRequest, IntakeResponse
from app.services.intake import parse_intake

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/parse", response_model=IntakeResponse)
async def parse(req: IntakeRequest) -> IntakeResponse:
    return await parse_intake(req)
