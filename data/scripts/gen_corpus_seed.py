# -*- coding: utf-8 -*-
"""050_seed_corpus.sql 생성기.

T1(실물중고) · T4(게임재화) · T12(도박환전) 세 유형의 원문만 먼저 넣는다.
pack 형식을 검증하기 전에 전체를 적재하면, 형식이 틀렸을 때 전부 다시 써야 한다.

실행 : python scripts/gen_corpus_seed.py
"""
import csv, io, os, re, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 원시 조사 자료(기획자료/)는 레포 밖에 있다. 레포에 넣을 수 없는 수집 원본이라
# 그렇다. 위치가 다르면 PULLIM_RESEARCH_DIR 로 덮는다.
RESEARCH = os.environ.get("PULLIM_RESEARCH_DIR", "../../기획자료/5. 3자 사기 자료")
BASE = RESEARCH
OUT  = os.path.join("sql", "050_seed_corpus.sql")

def dq(s):
    """달러 인용. 긴 한글 본문에 작은따옴표가 섞여도 안전하다."""
    tag = "$doc$"
    while tag in (s or ""):
        tag = "$" + tag[1:-1] + "x$"
    return tag + (s or "") + tag

rows = []

# ── 1. 당사자 게시글 전문 2건 ────────────────────────────────
FULL = [
    ("data/cases/ruliweb-51046511.md",
     "루리웹 — 중고 노트북 판매 후 계좌 지급정지",
     "https://bbs.ruliweb.com/community/board/300143/read/51046511", "T1"),
    ("data/cases/dcinside-talesweaver-180340.md",
     "디시인사이드 테일즈위버 갤러리 — 게임 재화 판매 후 경찰 조사",
     "https://gall.dcinside.com/mgallery/board/view/?id=talesweaver&no=180340", "T4"),
]
for path, title, url, tcode in FULL:
    p = os.path.join(BASE, path)
    body = io.open(p, encoding="utf-8").read()
    rows.append(dict(source_type="당사자게시글", title=title, body=body,
                     url=url, reliability="B", tcode=tcode))

# ── 2. 도박·토토 환전형 상담사례 (summary.csv에서 추림) ──────
GAMBLE = ("도박", "토토", "바카라", "슬롯", "환전")
csv_path = os.path.join(BASE, "data", "summary.csv")
with io.open(csv_path, encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

cand = []
for r in all_rows:
    blob = (r.get("title") or "") + (r.get("snippet") or "")
    if not any(k in blob for k in GAMBLE):
        continue
    if "lawtalknews" not in (r.get("url") or ""):
        continue
    try:
        n = int(r.get("chars") or 0)
    except ValueError:
        n = 0
    cand.append((n, r))

cand.sort(key=lambda x: -x[0])
for n, r in cand[:5]:
    snippet = (r.get("snippet") or "").strip()
    rows.append(dict(source_type="상담사례",
                     title=re.sub(r"\s*-\s*로톡뉴스\s*$", "", (r.get("title") or "").strip()),
                     body=snippet, url=(r.get("url") or "").strip(),
                     reliability="B", tcode="T12",
                     published=(r.get("published_at") or "").strip() or None))

# ── 3. SQL 출력 ──────────────────────────────────────────────
out = io.open(OUT, "w", encoding="utf-8", newline="\n")
w = out.write
w("""-- 050_seed_corpus.sql · 원문 (T1·T4·T12만)
-- scripts/gen_corpus_seed.py 로 생성됨. 직접 고치지 말고 스크립트를 고칠 것.
--
-- 세 유형만 넣는 이유 : pack 형식을 먼저 검증한다.
-- 형식이 틀린 채로 16개 유형을 다 채우면 전부 다시 써야 한다.

""")
for r in rows:
    pub = "'%s'" % r["published"] if r.get("published") else "NULL"
    w("INSERT INTO corpus_documents (source_type, title, body, source_url, published_on, reliability, verified)\n")
    w("VALUES ('%s', %s, %s, %s, %s, '%s', false);\n\n"
      % (r["source_type"], dq(r["title"]), dq(r["body"]),
         dq(r["url"]), pub, r["reliability"]))

# damage_cases 로 유형을 이어 붙인다
w("-- 원문 ↔ 유형 연결\n")
for r in rows:
    w("INSERT INTO damage_cases (document_id, case_type_id, channel, summary)\n"
      "SELECT d.id, (SELECT id FROM case_types WHERE code='%s'), '', ''\n"
      "  FROM corpus_documents d WHERE d.source_url = %s;\n"
      % (r["tcode"], dq(r["url"])))
out.close()

print("done: %s" % OUT)
for r in rows:
    line = "  [%s] %-6s %6d chars  %s" % (r["tcode"], r["source_type"], len(r["body"]), r["title"][:38])
    print(line.encode("utf-8", "replace").decode("utf-8", "replace")
          if hasattr(sys.stdout, "reconfigure") else line)
