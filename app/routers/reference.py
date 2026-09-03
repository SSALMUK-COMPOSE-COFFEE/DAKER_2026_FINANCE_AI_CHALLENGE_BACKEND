from fastapi import APIRouter, HTTPException

from app.schemas import BanksResponse, Citation, LetterTemplate, SubmissionGuide
from app.services.reference import (
    BANK_DISCLOSURE_NOTE,
    BANKS,
    CITATIONS,
    LETTERS,
    SUBMISSION_CHECKLIST,
    SUBMISSION_STAGES,
)

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/banks", response_model=BanksResponse)
def banks() -> BanksResponse:
    return BanksResponse(banks=BANKS, disclosure_note=BANK_DISCLOSURE_NOTE)


@router.get("/letters", response_model=list[LetterTemplate])
def letters() -> list[LetterTemplate]:
    return list(LETTERS.values())


@router.get("/letters/{purpose}", response_model=LetterTemplate)
def letter(purpose: str) -> LetterTemplate:
    template = LETTERS.get(purpose)
    if template is None:
        raise HTTPException(status_code=404, detail="해당 목적물의 발급 요청문이 없습니다.")
    return template


@router.get("/citations", response_model=list[Citation])
def citations() -> list[Citation]:
    return CITATIONS


@router.get("/submission", response_model=SubmissionGuide)
def submission() -> SubmissionGuide:
    return SubmissionGuide(checklist=SUBMISSION_CHECKLIST, stages=SUBMISSION_STAGES, contacts=BANKS)
