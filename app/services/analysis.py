from calendar import monthrange
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median

from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    Answers,
    EvidenceFinding,
    Fact,
    GraphEdge,
    GraphNode,
    Metrics,
    Signal,
    Transaction,
    TransactionGraph,
)
from app.services.evidence import DELIVERY_LABELS, PURPOSE_LABELS
from app.services.transactions import classify_kind

PASS_THROUGH_TERMINAL = 0.5
WINDOW_DAYS = 3.0
SPEND_WINDOW_DAYS = 30.0
MIN_TRANSACTIONS = 3


def _days(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 86400


def _kind(t: Transaction) -> str:
    if t.kind != "unknown":
        return t.kind
    return classify_kind(f"{t.counterparty} {t.memo}")


def _target_deposit(answers: Answers, deposits: list[Transaction]) -> Transaction | None:
    if not deposits:
        return None
    amount = _int(answers.get("q7_amount"))
    date = str(answers.get("q7_date", "") or "")
    candidates = deposits
    if amount:
        exact = [t for t in deposits if t.amount == amount]
        if exact:
            candidates = exact
    if date:
        same_day = [t for t in candidates if t.occurred_at.strftime("%Y-%m-%d") == date]
        if same_day:
            candidates = same_day
    if candidates is deposits and amount:
        return min(deposits, key=lambda t: abs(t.amount - amount))
    return max(candidates, key=lambda t: t.amount)


def _int(value) -> int | None:
    try:
        n = int(str(value).replace(",", "").strip())
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


def _recurring_months(txs: list[Transaction]) -> int:
    seen: dict[str, set[str]] = defaultdict(set)
    for t in txs:
        key = (t.counterparty or t.memo).strip()
        if not key:
            continue
        seen[key].add(t.occurred_at.strftime("%Y-%m"))
    return max((len(m) for m in seen.values()), default=0)


def compute_metrics(answers: Answers, txs: list[Transaction]) -> tuple[Metrics, Transaction | None]:
    deposits = [t for t in txs if t.direction == "in"]
    withdrawals = [t for t in txs if t.direction == "out"]
    metrics = Metrics(deposit_count=len(deposits), withdrawal_count=len(withdrawals))
    if txs:
        metrics.account_span_days = int(_days(txs[0].occurred_at, txs[-1].occurred_at))
        metrics.night_ratio = round(sum(1 for t in txs if t.occurred_at.hour < 6) / len(txs), 2)
        metrics.recurring_months = _recurring_months(txs)
    target = _target_deposit(answers, deposits)
    if target is None:
        return metrics, None

    after = [t for t in withdrawals if t.occurred_at >= target.occurred_at]
    window = [t for t in after if _days(target.occurred_at, t.occurred_at) <= WINDOW_DAYS]
    transfers = [t for t in window if _kind(t) == "transfer"]
    spends = [
        t
        for t in after
        if _kind(t) == "spend" and _days(target.occurred_at, t.occurred_at) <= SPEND_WINDOW_DAYS
    ]
    moved = sum(t.amount for t in transfers)
    metrics.pass_through_ratio = round(min(moved / target.amount, 1.0), 2) if target.amount else None
    metrics.fan_out = len(transfers)
    metrics.spend_ratio = round(min(sum(t.amount for t in spends) / target.amount, 1.0), 2) if target.amount else None
    metrics.dwell_days = round(_days(target.occurred_at, after[0].occurred_at), 2) if after else None
    return metrics, target


def _notes(metrics: Metrics, tx_count: int) -> list[str]:
    notes = [
        "본 화면은 계좌의 정상성 여부를 판정하지 않습니다. 소명서에 쓸 수 있는 지표를 정리해 보여 줄 뿐이며, 최종 판단은 금융회사와 수사기관이 합니다.",
    ]
    if metrics.pass_through_ratio is None:
        notes.append("입금 내역이 없어 자금 흐름 지표를 계산하지 못했습니다.")
    if tx_count < MIN_TRANSACTIONS:
        notes.append("거래 건수가 적어 지표의 대표성이 낮습니다. 수개월치 거래내역을 올리면 근거가 두터워집니다.")
    if metrics.recurring_months >= 3:
        notes.append(f"{metrics.recurring_months}개월간 반복된 거래가 확인됩니다. 소액 간소화 트랙의 생계 연관성 근거로 쓸 수 있습니다.")
    return notes


def _facts(answers: Answers, target: Transaction | None) -> list[Fact]:
    when = " ".join(str(answers.get(k, "") or "") for k in ("q7_date", "q7_time")).strip()
    if not when and target:
        when = target.occurred_at.strftime("%Y-%m-%d %H:%M")
    amount = _int(answers.get("q7_amount")) or (target.amount if target else None)
    depositor = str(answers.get("q7_depositor", "") or "") or (target.counterparty if target else "")
    q6 = str(answers.get("q6", ""))
    match = {"다름": "불일치", "같음": "일치"}.get(q6, "미확인")
    return [
        Fact(label="입금 일시", value=when or "미입력"),
        Fact(label="입금액", value=f"{amount:,}원" if amount else "미입력"),
        Fact(label="입금자명", value=depositor or "미입력"),
        Fact(label="입금자명 일치 여부", value=match),
    ]


def _signals(answers: Answers) -> list[Signal]:
    out: list[Signal] = []
    if answers.get("q6") == "다름":
        out.append(
            Signal(
                key="name_mismatch",
                title="입금자명 불일치 신호 감지",
                body="입금자 이름이 대화 상대방과 달랐다는 답변을 소명서 전면에 배치해 선제적으로 해명하도록 반영했습니다. "
                "대화 기록에 입금자 이름이 등장하지 않는 것은 오히려 3자사기 구조의 증거입니다.",
                level="info",
            )
        )
    deal = _int(answers.get("q7_dealAmount"))
    notice = _int(answers.get("q7_noticeAmount"))
    if deal and notice and deal != notice:
        out.append(
            Signal(
                key="amount_mismatch",
                title="금액 정합성 확인 필요",
                body=f"거래금액 {deal:,}원과 공고금액 {notice:,}원이 다릅니다. 환급 청구 상한은 공고되어 소멸된 채권액이므로 "
                f"청구액을 {min(deal, notice):,}원 이하로 맞춰야 초과분 기각을 피할 수 있습니다.",
                level="warn",
            )
        )
    if answers.get("q5") == "더받음":
        out.append(
            Signal(
                key="overpaid",
                title="초과 입금 — 직접 반환 금지",
                body="약속보다 더 들어온 돈은 계좌만 거쳐가는 구조일 수 있습니다. 차액은 반드시 은행을 통해서만 반환하세요.",
                level="warn",
            )
        )
    return out


def _findings(answers: Answers, metrics: Metrics, target: Transaction | None) -> list[EvidenceFinding]:
    findings: list[EvidenceFinding] = []
    ratio = metrics.pass_through_ratio
    dwell = metrics.dwell_days
    if ratio is not None:
        if dwell is None:
            detail = "입금 후 출금 이력이 없어 자금이 계좌에 그대로 머물러 있습니다."
        else:
            detail = f"입금 후 첫 출금까지 {dwell:.1f}일 체류, 3일 내 재이체 통과율 {ratio:.0%}"
        findings.append(
            EvidenceFinding(
                category="C",
                label="자금 체류 패턴",
                detail=detail,
                verdict="정상" if ratio < PASS_THROUGH_TERMINAL else "주의",
            )
        )
        findings.append(
            EvidenceFinding(
                category="C",
                label="재이체 여부",
                detail=f"입금 직후 타 계좌 이체 {metrics.fan_out}건"
                + (f", 소비성 지출 비율 {metrics.spend_ratio:.0%}" if metrics.spend_ratio is not None else ""),
                verdict="정상" if metrics.fan_out == 0 else "주의",
            )
        )
    if metrics.recurring_months >= 3:
        findings.append(
            EvidenceFinding(
                category="C",
                label="반복 거래 패턴",
                detail=f"같은 상대와 {metrics.recurring_months}개월에 걸쳐 반복 거래 — 대포통장에 없는 장기 패턴",
                verdict="정상",
            )
        )
    elif metrics.deposit_count + metrics.withdrawal_count > 0:
        findings.append(
            EvidenceFinding(
                category="C",
                label="반복 거래 패턴",
                detail="올린 거래내역 안에서 3개월 이상 반복되는 상대를 찾지 못했습니다. 더 긴 기간을 올리면 보강됩니다.",
                verdict="확인필요",
            )
        )
    q6 = str(answers.get("q6", ""))
    if q6 == "다름":
        findings.append(
            EvidenceFinding(
                category="A",
                label="입금자명 불일치",
                detail="대화 상대와 입금자명이 달라 제3자 송금 구조에 해당합니다. 대화 캡처와 입금내역을 병치해 해명합니다.",
                verdict="확인필요",
            )
        )
    elif q6 == "같음":
        findings.append(
            EvidenceFinding(
                category="A",
                label="입금자명 일치",
                detail="대화 상대와 입금자명이 일치해 거래 실재를 직접 뒷받침합니다.",
                verdict="정상",
            )
        )
    q5 = str(answers.get("q5", ""))
    if q5 == "같음":
        findings.append(
            EvidenceFinding(category="A", label="약정 금액 일치", detail="약속한 금액과 입금액이 같습니다.", verdict="정상")
        )
    elif q5 in ("더받음", "덜받음"):
        findings.append(
            EvidenceFinding(
                category="A",
                label="약정 금액 불일치",
                detail="약속 금액과 입금액이 달라 경위 설명이 필요합니다.",
                verdict="확인필요",
            )
        )
    q3 = str(answers.get("q3", ""))
    q4 = str(answers.get("q4", ""))
    if q3 and q3 != "없음":
        findings.append(
            EvidenceFinding(
                category="B",
                label="물품·용역 인도",
                detail=f"{PURPOSE_LABELS.get(q3, q3)} — {DELIVERY_LABELS.get(q4, q4 or '전달 방식 미입력')}",
                verdict="확인필요" if q4 == "미전달" else "정상",
            )
        )
    return findings


def _account_normality(metrics: Metrics, target: Transaction | None, txs: list[Transaction]) -> list[Fact]:
    span = metrics.account_span_days
    span_text = "거래내역 없음"
    if span is not None:
        span_text = f"{span}일치 거래 확인" if span < 365 else f"{span // 365}년 이상 거래 확인"
    deviation = "확인 불가"
    deposits = [t.amount for t in txs if t.direction == "in"]
    if target and len(deposits) >= 3:
        med = median(deposits)
        ratio = target.amount / med if med else 0
        deviation = "낮음" if ratio <= 3 else "보통" if ratio <= 10 else "높음"
    return [
        Fact(label="거래내역 기간", value=span_text),
        Fact(label="반복 거래 개월수", value=f"{metrics.recurring_months}개월"),
        Fact(label="평소 패턴과의 이탈도", value=deviation),
    ]


def _graph(metrics: Metrics, target: Transaction | None, txs: list[Transaction]) -> TransactionGraph:
    self_hint = ""
    if metrics.dwell_days is not None and metrics.pass_through_ratio is not None:
        self_hint = f"체류 {metrics.dwell_days:.1f}일 · 통과율 {metrics.pass_through_ratio:.0%}"
    elif metrics.pass_through_ratio is not None:
        self_hint = "출금 없음 · 통과율 0%"
    nodes = [GraphNode(id="self", label="내 계좌", type="self", hint=self_hint)]
    edges: list[GraphEdge] = []
    if target is None:
        return TransactionGraph(nodes=nodes, edges=edges)

    nodes.append(GraphNode(id="origin", label="피해자 계좌", type="origin", hint="피해 신고 출처"))
    nodes.append(
        GraphNode(id="suspect", label=target.counterparty or "입금자", type="suspect", hint="지목된 입금 건")
    )
    edges.append(GraphEdge(source="origin", target="suspect", suspicious=True))
    edges.append(
        GraphEdge(source="suspect", target="self", amount=target.amount, suspicious=True, highlighted=True)
    )

    after = [t for t in txs if t.direction == "out" and t.occurred_at >= target.occurred_at]
    for i, t in enumerate(after[:4]):
        kind = _kind(t)
        node_id = f"out{i}"
        nodes.append(
            GraphNode(
                id=node_id,
                label=t.counterparty or ("소비" if kind == "spend" else "이체"),
                type="normal" if kind == "spend" else "other",
                hint="소비성 지출" if kind == "spend" else "타 계좌 이체",
            )
        )
        edges.append(
            GraphEdge(
                source="self",
                target=node_id,
                amount=t.amount,
                suspicious=False,
                highlighted=kind == "spend",
            )
        )
    return TransactionGraph(nodes=nodes, edges=edges)


def analyze(req: AnalysisRequest) -> AnalysisResponse:
    txs = sorted(req.transactions, key=lambda t: t.occurred_at)
    metrics, target = compute_metrics(req.answers, txs)
    return AnalysisResponse(
        account_normality=_account_normality(metrics, target, txs),
        facts=_facts(req.answers, target),
        findings=_findings(req.answers, metrics, target),
        signals=_signals(req.answers),
        metrics=metrics,
        graph=_graph(metrics, target, txs),
        notes=_notes(metrics, len(txs)),
    )


def deadline_days(answers: Answers, today: datetime | None = None) -> int | None:
    if answers.get("q10") != "받음":
        return None
    raw = str(answers.get("q10_date", "") or "")
    try:
        notice = datetime.strptime(raw, "%Y-%m-%d")
    except ValueError:
        return None
    month = notice.month + 2
    year = notice.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(notice.day, monthrange(year, month)[1])
    deadline = notice.replace(year=year, month=month, day=day)
    now = today or datetime.now()
    return (deadline - now + timedelta(days=1)).days
