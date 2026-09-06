"""유형 판정과 프롬프트 팩 조회 — 코퍼스 DB에서 꺼내 온다.

소명서를 쓰기 전에 "이 사람은 어떤 유형이고, 그 유형에서 실제로 무엇이 인정되고
무엇이 기각됐는지"를 LLM 에 쥐여 주기 위한 모듈이다. 이것이 없으면 모델은
그럴듯하지만 근거 없는 문장을 쓴다.

설계 원칙 두 가지.

1. 유형 목록을 코드에 박지 않는다.
   문진 답에서 두 축(구조·목적물)만 뽑아 case_types 에서 찾는다. 유형이 늘거나
   이름이 바뀌어도 이 파일은 그대로다. 서버는 꺼내서 넘기기만 한다.

2. 못 찾으면 그냥 넘어간다.
   팩이 없어도 기존 템플릿 경로로 소명서는 나온다. 근거가 얇아질 뿐이다.
   차단은 이 모듈이 아니라 riskgate 가 한다 — 그쪽은 fail closed 다.

지금 화면이 보내는 값과 코퍼스의 option_key 는 어휘가 다르다. 아래 AXIS_* 표가
그 사이를 잇는다. 화면이 question_options 를 그대로 렌더링하게 되면 이 표는 지운다.
"""

import logging
import time

import psycopg

from app.config import get_settings
from app.schemas import Answers

log = logging.getLogger(__name__)

# 목적물 축 — 화면의 q3 값 → case_types.subject
AXIS_SUBJECT: dict[str, str] = {
    "실물중고": "실물중고",
    "상품권": "상품권",
    "게임재화": "게임재화",
    "팬덤굿즈": "팬덤굿즈",
    "금귀금속외화": "금외화",
    "암호화폐": "암호화폐",
    "용역": "용역",
    "없음": "없음",
}

# 구조 축 — 무엇을 넘겼는가가 아니라 돈이 어떻게 흘렀는가다.
# 목적물보다 우선한다. 초과입금이면 물건을 팔았어도 구조가 다르다.
STRUCTURE_EXCHANGE = "환전대리"   # 환전·대리송금
STRUCTURE_PASS = "계좌경유"       # 거래 없이 계좌만 거쳐 감
STRUCTURE_GOODS = "물건넘김"      # 팔고 대가를 받음

_SQL = """
SELECT c.code, c.name, c.clause, c.out_of_scope, p.pack_text
FROM case_types c
JOIN snippet_packs p ON p.case_type_id = c.id
WHERE c.structure = %s AND c.subject = %s
ORDER BY c.id
LIMIT 1
"""

_CACHE_TTL_SECONDS = 300.0
_cache: dict[tuple[str, str], dict | None] = {}
_cache_at = 0.0


def axes(answers: Answers) -> tuple[str, str]:
    """문진 답에서 (구조, 목적물) 두 축을 뽑는다."""
    q2 = answers.get("q2") if isinstance(answers.get("q2"), str) else ""
    q3 = answers.get("q3") if isinstance(answers.get("q3"), str) else ""
    q5 = answers.get("q5") if isinstance(answers.get("q5"), str) else ""

    subject = AXIS_SUBJECT.get(q3, "없음")

    if q2 == "환전대리송금":
        # 환전·대리송금은 목적물과 무관하게 구조가 결정된다
        return STRUCTURE_EXCHANGE, subject
    if q5 == "더받음":
        # 초과입금형. 거래분과 초과분이 갈리므로 물건을 팔았어도 계좌경유다
        return STRUCTURE_PASS, subject
    if subject == "없음":
        # 넘긴 것이 없으면 거래가 아니라 계좌가 경유지로 쓰인 것이다
        return STRUCTURE_PASS, subject
    return STRUCTURE_GOODS, subject


async def load(answers: Answers) -> dict | None:
    """유형을 판정해 그 유형의 팩을 돌려준다. 못 찾으면 None."""
    global _cache, _cache_at

    key = axes(answers)
    now = time.monotonic()
    if now - _cache_at >= _CACHE_TTL_SECONDS:
        _cache, _cache_at = {}, now
    if key in _cache:
        return _cache[key]

    url = get_settings().database_url
    if not url:
        log.warning("casepack: DATABASE_URL 이 비어 있다. 팩 없이 진행한다")
        return None

    try:
        async with await psycopg.AsyncConnection.connect(url, connect_timeout=3) as conn:
            async with conn.cursor() as cur:
                await cur.execute(_SQL, key)
                row = await cur.fetchone()
    except Exception as exc:  # noqa: BLE001 - 팩이 없어도 소명서는 나와야 한다
        log.warning("casepack: DB 를 못 읽었다(%s). 팩 없이 진행한다", exc)
        return None

    if row is None:
        log.info("casepack: %s 에 맞는 팩이 없다", key)
        _cache[key] = None
        return None

    found = {
        "code": row[0],
        "name": row[1],
        "clause": row[2] or "",
        "out_of_scope": row[3],
        "pack_text": row[4],
    }
    _cache[key] = found
    return found
