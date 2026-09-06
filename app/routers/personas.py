from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas import AnalysisRequest, AnalysisResponse, Persona, SampleFile
from app.services.analysis import analyze
from app.services.personas import PERSONAS

router = APIRouter(prefix="/personas", tags=["personas"])

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "assets" / "samples"


def _persona(persona_id: str) -> Persona:
    persona = PERSONAS.get(persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="페르소나를 찾을 수 없습니다.")
    return persona


@router.get("", response_model=list[Persona])
def list_personas() -> list[Persona]:
    return list(PERSONAS.values())


@router.get("/{persona_id}", response_model=Persona)
def get_persona(persona_id: str) -> Persona:
    return _persona(persona_id)


@router.get("/{persona_id}/analysis", response_model=AnalysisResponse)
def persona_analysis(persona_id: str) -> AnalysisResponse:
    persona = _persona(persona_id)
    return analyze(AnalysisRequest(answers=persona.answers, transactions=persona.transactions))


@router.get("/{persona_id}/samples", response_model=list[SampleFile])
def persona_samples(persona_id: str) -> list[SampleFile]:
    _persona(persona_id)
    folder = SAMPLE_DIR / persona_id
    if not folder.is_dir():
        return []
    return [
        SampleFile(name=p.name, url=f"/api/personas/{persona_id}/samples/{quote(p.name)}")
        for p in sorted(folder.iterdir())
        if p.is_file()
    ]


@router.get("/{persona_id}/samples/{name}")
def persona_sample_file(persona_id: str, name: str) -> FileResponse:
    _persona(persona_id)
    path = (SAMPLE_DIR / persona_id / name).resolve()
    if not path.is_file() or path.parent != (SAMPLE_DIR / persona_id).resolve():
        raise HTTPException(status_code=404, detail="샘플 파일을 찾을 수 없습니다.")
    return FileResponse(path)
