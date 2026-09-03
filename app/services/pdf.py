from datetime import datetime
from pathlib import Path

from fpdf import FPDF

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
FOOTER = "본 문서는 풀림(PULL-LIM)이 제안한 초안입니다. 법률 대리인의 검토를 대신하지 않으며, 최종 판단은 금융회사가 합니다."

SECTIONS = (
    ("application", "이의제기신청서 사유란"),
    ("incident", "경위서"),
    ("evidence_index", "증거 인덱스"),
)

GLYPH_FALLBACK = str.maketrans({chr(0x2460 + i): f"{i + 1}." for i in range(20)})


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


def build_pdf(sections: dict[str, str], applicant_name: str = "") -> bytes:
    pdf = _Doc()
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
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
