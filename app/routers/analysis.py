from fastapi import APIRouter

from app.schemas import AnalysisRequest, AnalysisResponse
from app.services.analysis import analyze

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisResponse)
def run_analysis(req: AnalysisRequest) -> AnalysisResponse:
    return analyze(req)
