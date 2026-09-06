from datetime import datetime
from pathlib import Path

from fpdf import FPDF

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
FOOTER = "본 문서는 풀림(PULL-LIM)이 제안한 초안입니다. 법률 대리인의 검토를 대신하지 않으며, 최종 판단은 금융회사가 합니다."

# 1면은 법정서식이라 별도로 그린다. 나머지는 일반 문서 면.
SECTIONS = (
    ("incident", "경위서"),
    ("evidence_index", "증거 인덱스"),
)

GLYPH_FALLBACK = str.maketrans({chr(0x2460 + i): f"{i + 1}." for i in range(20)})

# 시행령 별지 제4호서식 문구 그대로.
FORM_HEAD = "■ 전기통신금융사기 피해 방지 및 피해금 환급에 관한 특별법 시행령 [별지 제4호서식] <개정 2016. 7. 26.>"
FORM_NOTE = "※ 색상이 어두운 란은 신청인이 적지 않습니다."
FORM_CLAUSE = (
    "「전기통신금융사기 피해 방지 및 피해금 환급에 관한 특별법」 제7조 제1항 및 같은 법 시행령 "
    "제7조에 따라 본인의 계좌에 대한 지급정지, 전자금융거래 제한 또는 채권소멸절차에 대하여 "
    "위와 같이 이의제기를 신청합니다."
)
ATTACHMENTS = (
    "1. 사기이용계좌가 아니라는 사실을 증명하는 자료 1부",
    "2. 사기이용계좌 명의인의 신분증 사본 1부",
    "3. 명의인 본인서명사실확인서 1부 (주민센터 발급)",
)

LEFT = 15.0
FORM_W = 180.0
SHADE = (226, 228, 232)
LINE = (90, 90, 90)
ROW_H = 7.0
MIN_REASON_MM = 62.0   # 사유란 최소 높이. 짧아도 서식 모양이 무너지지 않게.


class _Doc(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_font("nanum", "", str(FONT_DIR / "NanumGothic-Regular.ttf"))
        self.add_font("nanum", "B", str(FONT_DIR / "NanumGothic-Bold.ttf"))
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(20, 18, 20)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("nanum", "", 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, FOOTER, align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 4, f"- {self.page_no()} -", align="C")


def _box(pdf: FPDF, x: float, y: float, w: float, h: float, text: str = "",
         bold: bool = False, shade: bool = False, size: float = 8.5,
         align: str = "L") -> None:
    """칸 하나. 값칸은 text를 비워 두면 그대로 빈칸이 된다."""
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.2)
    if shade:
        pdf.set_fill_color(*SHADE)
        pdf.rect(x, y, w, h, style="FD")
    else:
        pdf.rect(x, y, w, h)
    if not text:
        return
    pdf.set_font("nanum", "B" if bold else "", size)
    pdf.set_text_color(20, 20, 20)
    lines = text.splitlines() or [""]
    lh = size * 0.42
    top = y + (h - lh * len(lines)) / 2
    for i, line in enumerate(lines):
        pdf.set_xy(x, top + i * lh)
        pdf.cell(w, lh, line if align != "L" else f"  {line}", align=align)


def _group(pdf: FPDF, y: float, label: str, rows: list[list[tuple[float, str]]]) -> float:
    """왼쪽에 세로로 걸치는 묶음 라벨(신청인·지급정지계좌) + 오른쪽 행들."""
    label_w = 18.0
    h = ROW_H * len(rows)
    _box(pdf, LEFT, y, label_w, h, label, bold=True, align="C")
    yy = y
    for row in rows:
        x = LEFT + label_w
        for w, text in row:
            # 라벨칸은 text가 있고, 값칸은 빈 문자열이라 그대로 빈칸이 된다.
            _box(pdf, x, yy, w, ROW_H, text, bold=bool(text))
            x += w
        yy += ROW_H
    return y + h


def _form_page(pdf: FPDF, reason: str, bank: str) -> None:
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)

    pdf.set_font("nanum", "", 7)
    pdf.set_xy(LEFT, 14)
    pdf.cell(FORM_W, 4, FORM_HEAD)

    pdf.set_font("nanum", "B", 17)
    pdf.set_xy(LEFT, 20)
    pdf.cell(FORM_W, 10, "이의제기신청서", align="C")

    pdf.set_font("nanum", "", 7.5)
    pdf.set_xy(LEFT, 31)
    pdf.cell(FORM_W, 4, FORM_NOTE)

    y = 36.0
    # 접수번호·접수일자 — 신청인이 적지 않는 칸이라 음영.
    _box(pdf, LEFT, y, 25, ROW_H, "접수번호", bold=True)
    _box(pdf, LEFT + 25, y, 65, ROW_H, shade=True)
    _box(pdf, LEFT + 90, y, 25, ROW_H, "접수일자", bold=True)
    _box(pdf, LEFT + 115, y, 65, ROW_H, shade=True)
    y += ROW_H

    # 신청인 — 전부 빈칸으로 둔다. 손으로 적거나 따로 채운다.
    y = _group(pdf, y, "신청인", [
        [(27, "성 명"), (55, ""), (27, "생년월일"), (53, "")],
        [(27, "주 소"), (135, "")],
        [(27, "전화번호"), (55, ""), (27, "휴대전화번호"), (53, "")],
        [(27, "전자우편주소"), (135, "")],
    ])

    y = _group(pdf, y, "지급정지\n계좌", [
        [(27, "금융회사"), (55, ""), (27, "개설점포"), (53, "")],
        [(27, "예금종별"), (135, "")],
        [(27, "계좌번호"), (135, "")],
        [(27, "명의인"), (135, "")],
    ])

    # 이의제기 사유 — 여기에만 생성된 내용이 들어간다.
    _box(pdf, LEFT, y, FORM_W, ROW_H, "이의제기 사유 (구체적으로 기재합니다)", bold=True)
    y += ROW_H

    pdf.set_font("nanum", "", 8.5)
    pdf.set_xy(LEFT + 3, y + 2)
    start = pdf.get_y()
    pdf.multi_cell(FORM_W - 6, 4.6, reason.strip())
    used = pdf.get_y() - start + 4
    h = max(used, MIN_REASON_MM)
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.2)
    pdf.rect(LEFT, y, FORM_W, h)
    y += h

    pdf.set_font("nanum", "", 8.5)
    pdf.set_xy(LEFT + 3, y + 2.5)
    pdf.multi_cell(FORM_W - 6, 4.6, FORM_CLAUSE)
    y = pdf.get_y() + 4

    pdf.set_font("nanum", "", 9.5)
    pdf.set_xy(LEFT, y)
    pdf.cell(FORM_W, 6, "년         월         일", align="C")
    y += 9

    pdf.set_xy(LEFT, y)
    pdf.cell(FORM_W - 6, 6, "신청인  성 명                              (서명 또는 인)", align="R")
    y += 10

    pdf.set_font("nanum", "B", 10.5)
    pdf.set_xy(LEFT, y)
    pdf.cell(FORM_W, 6, f"{bank or ''}  귀하".strip(), align="C")
    y += 10

    _box(pdf, LEFT, y, 25, ROW_H * 3, "첨부서류", bold=True, align="C")
    pdf.set_font("nanum", "", 8)
    pdf.set_draw_color(*LINE)
    pdf.rect(LEFT + 25, y, 130, ROW_H * 3)
    for i, line in enumerate(ATTACHMENTS):
        pdf.set_xy(LEFT + 28, y + 2 + i * ROW_H)
        pdf.cell(124, 4, line)
    _box(pdf, LEFT + 155, y, 25, ROW_H * 3, "수수료\n없음", bold=True, align="C")


def build_pdf(sections: dict[str, str], applicant_name: str = "", bank: str = "") -> bytes:
    pdf = _Doc()
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    reason = sections.get("application", "").strip().translate(GLYPH_FALLBACK)
    if reason:
        _form_page(pdf, reason, bank)

    for key, title in SECTIONS:
        body = sections.get(key, "").strip().translate(GLYPH_FALLBACK)
        if not body:
            continue
        pdf.add_page()
        pdf.set_text_color(16, 35, 63)
        pdf.set_font("nanum", "B", 15)
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("nanum", "", 8)
        pdf.set_text_color(110, 110, 110)
        meta = f"작성 {generated}" + (f" · 신청인 {applicant_name}" if applicant_name else "")
        pdf.cell(0, 5, meta, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("nanum", "", 10)
        pdf.multi_cell(0, 6, body)

    if pdf.page_no() == 0:
        pdf.add_page()
        pdf.set_font("nanum", "", 10)
        pdf.multi_cell(0, 6, "내보낼 문서 내용이 없습니다.")
    return bytes(pdf.output())
