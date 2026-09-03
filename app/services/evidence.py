from app.schemas import Answers, EvidenceItem

CATEGORY_LABELS = {
    "A": "거래 실재",
    "B": "물품 인도",
    "C": "계좌 정상성",
    "D": "절차 메타",
}

PURPOSE_LABELS = {
    "실물중고": "실물 중고물품",
    "상품권": "상품권·기프티콘",
    "게임재화": "게임 재화·계정",
    "팬덤굿즈": "팬덤 굿즈",
    "금귀금속외화": "금·귀금속·외화",
    "암호화폐": "암호화폐",
    "용역": "용역·서비스",
    "없음": "해당 없음",
}

DELIVERY_LABELS = {
    "택배": "택배 발송",
    "직접": "직접 만나서 전달",
    "온라인전송": "온라인 전송",
    "미전달": "아직 전달하지 않음",
}


def _item(id: str, category: str, priority: str, label: str, description: str) -> EvidenceItem:
    return EvidenceItem(
        id=id, category=category, priority=priority, label=label, description=description
    )


def build_checklist(answers: Answers) -> list[EvidenceItem]:
    items = [
        _item("notif", "D", "필수", "지급정지 통보 캡처", "문자·앱 알림 스크린샷"),
        _item("chat", "A", "필수", "거래 대화 전체 스크린샷", "협의~입금 요청까지 전 과정"),
        _item("txhistory", "C", "필수", "거래내역 CSV (수개월치 권장)", "은행 앱·영업점에서 발급"),
        _item("id", "D", "필수", "신분증 사본", "주민등록증 또는 운전면허증"),
    ]
    q3 = str(answers.get("q3", ""))
    q4 = str(answers.get("q4", ""))
    q6 = str(answers.get("q6", ""))
    q13 = answers.get("q13", [])
    q13 = q13 if isinstance(q13, list) else [q13]

    if q3 == "상품권":
        items.append(
            _item("voucher-usage", "A", "필수", "상품권 발행사 사용이력 조회 결과", "언제·어디서 사용됐는지 발행사에 요청")
        )
        items.append(_item("voucher-pin", "B", "권장", "핀번호·바코드 전송 화면", "상대에게 전달한 캡처"))
    elif q3 == "게임재화":
        items.append(_item("game-log", "A", "필수", "게임사 고객센터 거래 로그 회신", "아이템·재화 이동 기록 요청 결과"))
        items.append(_item("game-chat", "B", "권장", "게임 내 거래·우편 전송 캡처", "인수인계 시점 확인"))
    elif q3 == "팬덤굿즈":
        items.append(_item("goods-tracking", "B", "권장", "택배 송장·배송조회", "발송 및 배송완료 확인"))
        items.append(_item("goods-agent", "B", "권장", "배송대행지(배대지) 이용 내역", "대행지 회원번호·이용 기록"))
    elif q3 == "금귀금속외화":
        items.append(_item("bullion-receipt", "A", "필수", "매입 영수증 또는 시세 확인 자료", "물품 취득 경로 증빙"))
        items.append(_item("bullion-cctv", "B", "권장", "구청 CCTV 열람 신청 접수증", "거래 장소 관할 구청에 신청"))
    elif q3 == "암호화폐":
        items.append(
            _item("crypto-tx", "A", "필수", "블록체인 전송 기록 (트랜잭션 해시)", "지갑 주소·전송 시각이 담긴 기록 — 가장 강력한 증거")
        )
    elif q3 == "용역":
        items.append(_item("service-contract", "A", "필수", "계약서 또는 업무 의뢰 확인 자료", "용역 내용·기간 명시"))
        items.append(_item("service-output", "B", "권장", "작업물·정산 내역", "실제 수행 및 정산 증빙"))
    elif q3 == "실물중고":
        if q4 == "택배":
            items.append(_item("tracking", "B", "권장", "운송장·배송조회 완료 캡처", "배송완료 상태 확인 가능한 것"))
            items.append(_item("receipt", "B", "권장", "편의점 택배 영수증", "발송 사실 추가 증명"))
        elif q4 == "직접":
            items.append(_item("meetup", "B", "권장", "만남 약속 대화 캡처", "시각·장소 특정 가능한 것"))
            items.append(_item("movement", "B", "권장", "이동 기록 (지도 앱·교통카드)", "정황 증거로 인도 시점 특정"))

    if q4 == "온라인전송":
        items.append(_item("online-transfer", "B", "필수", "핀번호·계정·아이템 전송 화면", "상대에게 전달한 캡처"))

    if q6 == "다름":
        items.append(_item("mismatch", "A", "권장", "입금내역 + 대화 병치 캡처", "불일치를 전면에 해명하는 핵심 증거"))

    items.append(
        _item("livelihood-cert", "C", "권장", "건강보험자격득실확인서 (또는 재직증명서, 택1)", "온라인 즉시 발급 가능 — 회사에 알리지 않고도 뗄 수 있음")
    )
    items.append(
        _item("autopay", "C", "가점", "자동이체 등록내역 (통신비·공과금·카드대금 등)", "어카운트인포에서 즉시 발급 — 장기 반복 패턴은 대포통장에 없음")
    )
    items.append(
        _item("livelihood-etc", "C", "가점", "생활비·등록금 송금 또는 재학·연금 증명", "부모님 정기 송금, 재학증명서, 국민연금 가입증명 등 (해당 시)")
    )

    if "경찰신고" in q13:
        items.append(_item("police", "D", "가점", "경찰 신고 접수증·사건사고사실확인원", '"본인도 피해자" 절차 기록'))
    if "더치트" in q13:
        items.append(_item("thecheat", "D", "가점", "더치트 조회 결과 캡처", "사기범 정보 기록"))
    return items
