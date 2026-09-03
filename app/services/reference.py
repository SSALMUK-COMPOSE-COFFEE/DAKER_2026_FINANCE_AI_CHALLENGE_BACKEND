from app.schemas import BankInfo, Citation, LetterTemplate, SubmissionItem

BANKS: list[BankInfo] = [
    BankInfo(
        name="카카오뱅크",
        dept="고객센터",
        tel="1599-3333",
        days="평일 09:00–18:00",
        requirements=[
            "신분증 사본",
            "거래 상대방과의 대화 내역",
            "거래 관련 증빙자료(계약서·영수증 등)",
            "이의제기신청서",
        ],
    ),
    BankInfo(
        name="국민은행",
        dept="여신거래지원팀",
        tel="1588-9999",
        days="평일 09:00–18:00",
        requirements=None,
    ),
    BankInfo(
        name="신한은행",
        dept="고객서비스팀",
        tel="1544-8000",
        days="평일 09:00–18:00",
        requirements=["신분증 사본", "거래사실 확인서류"],
    ),
    BankInfo(
        name="우리은행",
        dept="고객행복센터",
        tel="1588-5000",
        days="평일 09:00–18:00",
        requirements=None,
    ),
    BankInfo(
        name="하나은행",
        dept="고객상담팀",
        tel="1599-1111",
        days="평일 09:00–18:00",
        requirements=None,
    ),
]

BANK_DISCLOSURE_NOTE = (
    "금융회사 20곳을 조사한 결과, 이의제기 요구서류를 한 항목이라도 공개한 곳은 "
    "4곳(20%)뿐이었고, 유형별로 안내하는 곳은 한 곳도 없었습니다."
)

LETTERS: dict[str, LetterTemplate] = {
    "게임재화": LetterTemplate(
        purpose="게임재화",
        recipient="게임사 고객센터",
        subject="거래 관련 게임 내 재화·아이템 이동 기록 확인 요청",
        body="""안녕하세요, 계정 [내 계정/캐릭터명]을 이용 중인 이용자입니다.

[거래 일시]경 계정 간 재화·아이템 거래와 관련하여, 아래 내용에 대한 확인을
요청드립니다.

- 대상 계정/캐릭터: [내 계정/캐릭터명]
- 거래 상대 계정/캐릭터: [상대방 계정/캐릭터명] (아는 범위에서 기재)
- 거래 일시: [연/월/일 시:분]
- 거래 내용: [넘긴 재화·아이템 종류 및 수량]

본 계좌가 보이스피싱 관련 지급정지를 받아 은행에 이의제기를 준비 중이며,
위 거래가 실제로 있었음을 증명할 자료가 필요합니다. 확인 가능한 로그나
거래 내역 회신 부탁드립니다.""",
    ),
    "상품권": LetterTemplate(
        purpose="상품권",
        recipient="상품권 발행사 고객센터",
        subject="상품권 사용이력 조회 요청",
        body="""안녕하세요. 아래 상품권의 사용이력 조회를 요청드립니다.

- 상품권 종류: [상품권명]
- 핀번호/일련번호: [핀번호 뒷자리 또는 일련번호]
- 판매(전송) 일시: [연/월/일 시:분]

본 상품권을 판매하고 대금을 받은 계좌가 보이스피싱 관련 지급정지를
받아 은행에 이의제기를 준비 중입니다. 해당 상품권이 언제, 어디서
사용되었는지 확인해 주시면 소명 자료로 제출하겠습니다.""",
    ),
    "금귀금속외화": LetterTemplate(
        purpose="금귀금속외화",
        recipient="거래 장소 관할 구청 (CCTV 관리부서)",
        subject="대로변 방범 CCTV 영상 열람 신청",
        body="""안녕하세요. 아래 일시·장소에서 발생한 거래와 관련하여 관할 구역
방범 CCTV 영상 열람을 신청합니다.

- 거래 일시: [연/월/일 시:분]
- 거래 장소: [도로명 주소 또는 인근 지번]
- 신청 사유: 보이스피싱 관련 계좌 지급정지 이의제기 소명 자료 확보

CCTV 보관 기간이 통상 30일 이내로 알고 있어 빠른 확인을 부탁드립니다.
신청서 양식이 있다면 안내 부탁드립니다.""",
    ),
    "팬덤굿즈": LetterTemplate(
        purpose="팬덤굿즈",
        recipient="이용한 배송대행지(배대지) 운영사",
        subject="배송대행 이용 내역 확인 요청",
        body="""안녕하세요. 아래 배송건에 대한 이용 내역 확인을 요청드립니다.

- 발송 일시: [연/월/일]
- 받는 사람(수취인) 정보: [배대지 회원번호 또는 이름]
- 물품: [굿즈 종류]

본 거래 대금을 받은 계좌가 보이스피싱 관련 지급정지를 받아 이의제기를
준비 중이며, 실제 배송이 이루어졌음을 증명할 이용 내역이 필요합니다.""",
    ),
    "용역": LetterTemplate(
        purpose="용역",
        recipient="발주처 또는 거래 플랫폼",
        subject="용역 계약 및 정산 내역 확인 요청",
        body="""안녕하세요. 아래 용역 건에 대한 계약·정산 내역 확인을 요청드립니다.

- 용역 내용: [작업 내용]
- 진행 기간: [시작일 ~ 종료일]
- 정산 금액 및 일시: [금액 / 연·월·일]

본 정산 대금을 받은 계좌가 보이스피싱 관련 지급정지를 받아 이의제기를
준비 중이며, 정상적인 용역 거래였음을 증명할 자료가 필요합니다.""",
    ),
}

CITATIONS: list[Citation] = [
    Citation(
        key="법 제7조",
        kind="statute",
        title="통신사기피해환급법 제7조",
        summary="지급정지 및 채권소멸절차. 명의인은 공고일부터 2개월 이내에 이의를 제기할 수 있다.",
    ),
    Citation(
        key="법 제7조①3호",
        kind="statute",
        title="통신사기피해환급법 제7조 제1항 제3호",
        summary="통장협박 등 피해금과 무관한 계좌의 지급정지 해제 근거. 2024년 8월 개정으로 신속 해제 가능.",
    ),
    Citation(
        key="법 제8조②2호 단서",
        kind="statute",
        title="통신사기피해환급법 제8조 제2항 제2호 단서",
        summary="객관적 자료로 충분히 소명되면 2개월 기한을 다 기다리지 않고 조기 해제할 수 있다.",
    ),
    Citation(
        key="법 제16조",
        kind="statute",
        title="통신사기피해환급법 제16조",
        summary="허위 이의제기 시 3년 이하 징역 또는 3천만원 이하 벌금.",
    ),
    Citation(
        key="대법원 2024다216187",
        kind="precedent",
        title="대법원 2024다216187 판결",
        summary="중고거래 대금 수령자에게 악의·중과실이 없으면 법률상 원인이 있고, 증명책임은 상대방에게 있다.",
        caution="민사 부당이득 법리이므로 은행 심사에 구속력은 없는 설득 논거로만 활용한다.",
    ),
]

SUBMISSION_CHECKLIST: list[SubmissionItem] = [
    SubmissionItem(id="doc", label="소명서 (풀림 AI 작성본)"),
    SubmissionItem(id="tx", label="거래 내역서 (최소 3개월치)"),
    SubmissionItem(id="tax", label="세금계산서 또는 입금 근거 자료"),
    SubmissionItem(id="biz", label="사업자등록증 또는 신분증 사본"),
    SubmissionItem(id="etc", label="기타 거래 계약서 또는 용역 확인서"),
]

SUBMISSION_STAGES: list[SubmissionItem] = [
    SubmissionItem(id="filed", label="이의제기 접수됨", desc="냈다"),
    SubmissionItem(
        id="accepted",
        label="이의제기 수용됨",
        desc="은행이 받아들였다 — 아직 해제는 아니다",
    ),
    SubmissionItem(id="released", label="은행 지급정지 해제됨", desc="그 은행 계좌가 풀렸다"),
    SubmissionItem(
        id="fss",
        label="금감원 전자금융거래제한 해제됨",
        desc="전 금융권 제한이 풀렸다 — 은행 해제와 열흘 넘게 차이 날 수 있다",
    ),
]


def find_bank(name: str) -> BankInfo | None:
    return next((b for b in BANKS if b.name == name), None)


def citation_by_key(key: str) -> Citation | None:
    return next((c for c in CITATIONS if c.key == key), None)
