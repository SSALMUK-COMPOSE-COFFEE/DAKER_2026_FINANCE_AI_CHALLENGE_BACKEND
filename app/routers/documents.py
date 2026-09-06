from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.schemas import (
    DocumentDraftRequest,
    DocumentDraftResponse,
    DocumentExportRequest,
    DocumentRewriteRequest,
    DocumentRewriteResponse,
)
from app.services.documents import generate_draft, rewrite
from app.services.riskgate import blocked_reason
from app.services.llm import LLMUnavailable
from app.services.pdf import build_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/draft", response_model=DocumentDraftResponse)
async def draft(req: DocumentDraftRequest) -> DocumentDraftResponse:
    return await generate_draft(req)


@router.post("/rewrite", response_model=DocumentRewriteResponse)
async def rewrite_document(req: DocumentRewriteRequest) -> DocumentRewriteResponse:
    # 초안이 막힌 유형은 재작성도 막는다. 안 그러면 게이트를 우회하는 경로가 된다.
    if await blocked_reason(req.answers) is not None:
        raise HTTPException(
            status_code=422,
            detail="이 유형은 소명서를 생성하지 않습니다. 전문가 상담 안내를 확인하세요.",
        )
    try:
        return await rewrite(req)
    except LLMUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"AI 재작성을 사용할 수 없습니다: {exc}") from exc


@router.post("/export")
def export(req: DocumentExportRequest) -> Response:
    applicant = req.applicant.model_copy(update={"name": req.applicant.name or req.applicant_name})
    pdf = build_pdf(
        {
            "application": req.application,
            "incident": req.incident,
            "evidence_index": req.evidence_index,
        },
        applicant,
    )
    stamp = datetime.now().strftime("%Y%m%d")
    name = f"소명서_{applicant.name or '신청인'}_{stamp}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=\"pullim_{stamp}.pdf\"; filename*=UTF-8''{quote(name)}"
        },
    )
