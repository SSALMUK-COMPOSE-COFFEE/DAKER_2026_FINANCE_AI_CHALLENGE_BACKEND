from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Answers = dict[str, str | list[str]]
FindingVerdict = Literal["정상", "주의", "확인필요"]
EvidenceCategory = Literal["A", "B", "C", "D"]
EvidencePriority = Literal["필수", "권장", "가점"]
TxKind = Literal["transfer", "spend", "unknown"]


class Transaction(BaseModel):
    occurred_at: datetime
    amount: int
    direction: Literal["in", "out"]
    counterparty: str = ""
    memo: str = ""
    kind: TxKind = "unknown"


class ParsedFile(BaseModel):
    name: str
    size: int
    kind: Literal["transactions", "image", "document", "unknown"]
    transaction_count: int = 0
    skipped_rows: int = 0
    error: str | None = None


class UploadParseResponse(BaseModel):
    files: list[ParsedFile]
    transactions: list[Transaction]


class IntakeRequest(BaseModel):
    text: str = Field(max_length=4000)


class IntakeResponse(BaseModel):
    answers: Answers
    summary: str
    generated_by: Literal["llm", "rules"]


class EvidenceItem(BaseModel):
    id: str
    category: EvidenceCategory
    priority: EvidencePriority
    label: str
    description: str


class EvidenceChecklistRequest(BaseModel):
    answers: Answers = Field(default_factory=dict)


class EvidenceChecklistResponse(BaseModel):
    items: list[EvidenceItem]
    must_count: int


class BankInfo(BaseModel):
    name: str
    dept: str
    tel: str
    days: str
    requirements: list[str] | None


class BanksResponse(BaseModel):
    banks: list[BankInfo]
    disclosure_note: str


class LetterTemplate(BaseModel):
    purpose: str
    recipient: str
    subject: str
    body: str


class Citation(BaseModel):
    key: str
    kind: Literal["statute", "precedent"]
    title: str
    summary: str
    caution: str = ""


class SubmissionItem(BaseModel):
    id: str
    label: str
    desc: str = ""


class SubmissionGuide(BaseModel):
    checklist: list[SubmissionItem]
    stages: list[SubmissionItem]
    contacts: list[BankInfo]


class Metrics(BaseModel):
    pass_through_ratio: float | None = None
    dwell_days: float | None = None
    fan_out: int = 0
    spend_ratio: float | None = None
    night_ratio: float | None = None
    account_span_days: int | None = None
    recurring_months: int = 0
    deposit_count: int = 0
    withdrawal_count: int = 0


class Fact(BaseModel):
    label: str
    value: str


class Signal(BaseModel):
    key: str
    title: str
    body: str
    level: Literal["info", "warn"]


class EvidenceFinding(BaseModel):
    category: EvidenceCategory
    label: str
    detail: str
    verdict: FindingVerdict


class GraphNode(BaseModel):
    id: str
    label: str
    type: Literal["origin", "suspect", "self", "normal", "other"]
    hint: str = ""


class GraphEdge(BaseModel):
    source: str
    target: str
    amount: int | None = None
    suspicious: bool = False
    highlighted: bool = False


class TransactionGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class AnalysisRequest(BaseModel):
    answers: Answers = Field(default_factory=dict)
    transactions: list[Transaction] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    account_normality: list[Fact]
    facts: list[Fact]
    findings: list[EvidenceFinding]
    signals: list[Signal]
    metrics: Metrics
    graph: TransactionGraph
    notes: list[str]


class Applicant(BaseModel):
    name: str = ""
    birth: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    bank: str = ""
    branch: str = ""
    account_type: str = "입출금통장"
    account_no: str = ""


class DocumentDraftRequest(BaseModel):
    answers: Answers = Field(default_factory=dict)
    analysis: AnalysisResponse | None = None
    checked_evidence: list[str] = Field(default_factory=list)
    memo: str = Field(default="", max_length=2000)
    applicant: Applicant = Field(default_factory=Applicant)


class DocumentDraftResponse(BaseModel):
    application: str
    incident: str
    evidence_index: str
    citations: list[Citation]
    generated_by: Literal["llm", "template"]
    # 위험 유형이라 소명서를 만들지 않은 경우 true. 이때 application 에는
    # 소명서가 아니라 안내문이 들어간다. 기존 클라이언트는 무시해도 된다.
    blocked: bool = False


class DocumentRewriteRequest(BaseModel):
    doc_key: Literal["application", "incident", "evidence"]
    content: str = Field(max_length=20000)
    instruction: str = Field(max_length=1000)
    answers: Answers = Field(default_factory=dict)


class DocumentRewriteResponse(BaseModel):
    content: str
    generated_by: Literal["llm"]


class DocumentExportRequest(BaseModel):
    application: str
    incident: str
    evidence_index: str
    applicant: Applicant = Field(default_factory=Applicant)
    applicant_name: str = ""


class Persona(BaseModel):
    id: str
    title: str
    summary: str
    expected_basis: list[Fact]
    answers: Answers
    transactions: list[Transaction]
