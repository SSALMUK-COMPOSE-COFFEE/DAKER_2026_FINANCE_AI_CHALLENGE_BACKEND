from fastapi import APIRouter, HTTPException

from app.schemas import AnalysisRequest, AnalysisResponse, Persona
from app.services.analysis import analyze
from app.services.personas import PERSONAS

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("", response_model=list[Persona])
def list_personas() -> list[Persona]:
    return list(PERSONAS.values())


@router.get("/{persona_id}", response_model=Persona)
def get_persona(persona_id: str) -> Persona:
    persona = PERSONAS.get(persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="페르소나를 찾을 수 없습니다.")
    return persona


@router.get("/{persona_id}/analysis", response_model=AnalysisResponse)
def persona_analysis(persona_id: str) -> AnalysisResponse:
    persona = PERSONAS.get(persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="페르소나를 찾을 수 없습니다.")
    return analyze(AnalysisRequest(answers=persona.answers, transactions=persona.transactions))
