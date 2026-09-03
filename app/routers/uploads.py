from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import ParsedFile, Transaction, UploadParseResponse
from app.services.transactions import ParseError, parse_transactions

router = APIRouter(prefix="/uploads", tags=["uploads"])

KIND_BY_SUFFIX = {
    ".csv": "transactions",
    ".xlsx": "transactions",
    ".xls": "transactions",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".pdf": "document",
}

MAX_FILES = 20
TOTAL_MAX_FACTOR = 3
CHUNK_BYTES = 256 * 1024


async def _read_capped(item: UploadFile, limit: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await item.read(CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=413, detail=f"{item.filename or 'unnamed'} 파일이 너무 큽니다."
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/parse", response_model=UploadParseResponse)
async def parse(files: list[UploadFile] = File(...)) -> UploadParseResponse:
    settings = get_settings()
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=413, detail=f"한 번에 {MAX_FILES}개까지만 올릴 수 있습니다.")

    parsed: list[ParsedFile] = []
    transactions: list[Transaction] = []
    total_limit = settings.upload_max_bytes * TOTAL_MAX_FACTOR
    budget = total_limit

    for item in files:
        name = item.filename or "unnamed"
        if budget <= 0:
            raise HTTPException(
                status_code=413,
                detail=f"전체 업로드 용량이 {total_limit // (1024 * 1024)}MB를 넘습니다.",
            )
        body = await _read_capped(item, min(settings.upload_max_bytes, budget))
        budget -= len(body)
        kind = KIND_BY_SUFFIX.get(Path(name).suffix.lower(), "unknown")
        entry = ParsedFile(name=name, size=len(body), kind=kind)
        if kind == "transactions":
            try:
                result = parse_transactions(name, body)
                entry.transaction_count = len(result.transactions)
                entry.skipped_rows = result.skipped_rows
                transactions.extend(result.transactions)
            except ParseError as exc:
                entry.error = str(exc)
            except Exception:
                entry.error = "파일을 읽지 못했습니다. 은행 앱에서 내려받은 원본 CSV/XLSX인지 확인해 주세요."
        parsed.append(entry)

    transactions.sort(key=lambda t: t.occurred_at)
    return UploadParseResponse(files=parsed, transactions=transactions)
