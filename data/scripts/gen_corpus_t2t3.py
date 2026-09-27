# -*- coding: utf-8 -*-
"""092_seed_corpus_t2t3.sql 생성 — T2(고액 환금성 실물자산)·T3(암호화폐) 원문.

원시 코퍼스에서 판례·보도자료·상담사례를 꺼내 corpus_documents INSERT 로 만든다.
SQL 을 직접 고치지 말고 이 파일을 고칠 것.
"""
import io
import os, json, os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 원시 조사 자료(기획자료/)는 레포 밖에 있다. 레포에 넣을 수 없는 수집 원본이라
# 그렇다. 위치가 다르면 PULLIM_RESEARCH_DIR 로 덮는다.
RESEARCH = os.environ.get("PULLIM_RESEARCH_DIR", "../../기획자료/5. 3자 사기 자료")
RAWDIR = os.path.join(RESEARCH, "data", "raw")
OUT = "sql/092_seed_corpus_t2t3.sql"

# (검색키, source_type, 유형, 제목, 쓸 source_url)
WANTED = [
    ("240967", "판례", "T2",
     "대법원 2024. 6. 27. 선고 2024다216187 — 중고 순금 목걸이 판매대금이 보이스피싱 편취금이었던 사건",
     "https://www.law.go.kr/precInfoP.do?precSeq=240967"),
    ("nttId=210654", "보도자료", "T2",
     "금융감독원 소비자경보 2026-05호 — 금 팔고 받은 돈이 보이스피싱 피해금",
     "https://www.fss.or.kr/fss/bbs/B0000188/view.do?nttId=210654&menuNo=200218"),
    ("KMMQY905ENT6", "상담사례", "T2",
     "당근서 물건 팔았다가 사기꾼으로 몰려 — 대법 몰랐다면 책임 없다 (홍콩달러 477만원)",
     "https://lawtalknews.co.kr/article/KMMQY905ENT6"),
    ("TRWRP6F11Y0F", "상담사례", "T3",
     "코인 팔았는데 보이스피싱 자금이? 쓴 돈까지 다 갚아야 할까 (코인 2,000만원)",
     "https://lawtalknews.co.kr/article/TRWRP6F11Y0F"),
    ("BX1ZQTBBU9UZ", "상담사례", "T3",
     "9건 무혐의 받았는데 피해자 이의제기 후 검찰 소환 (테더 거래)",
     "https://lawtalknews.co.kr/article/BX1ZQTBBU9UZ"),
]


def load():
    found = {}
    for fn in ("legalqa.jsonl", "news.jsonl", "law.jsonl", "reference.jsonl"):
        p = os.path.join(RAWDIR, fn)
        if not os.path.exists(p):
            continue
        for line in io.open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            hay = (d.get("url") or "") + " " + (d.get("title") or "") + " " + (d.get("content") or "")[:400]
            for key, _, _, _, _ in WANTED:
                if key in hay and key not in found:
                    found[key] = d
    return found


def dollar(t):
    if "$doc$" in t:
        raise SystemExit("본문에 $doc$ 가 있다")
    return "$doc$" + t + "$doc$"


def main():
    found = load()
    missing = [k for k, _, _, _, _ in WANTED if k not in found]
    if missing:
        print("코퍼스에 없음: %s" % ", ".join(missing))
        return 1

    out = [
        "-- 092_seed_corpus_t2t3.sql · 원문 (T2 고액 환금성 실물자산 · T3 암호화폐)",
        "-- scripts/gen_corpus_t2t3.py 로 생성됨. 직접 고치지 말고 스크립트를 고칠 것.",
        "--",
        "-- T2 는 코퍼스에서 근거의 질이 가장 높은 유형이다. 대법원 2024다216187 은",
        "-- 판매자가 실제로 이긴 사건이고(원심 파기환송), 금감원 소비자경보가 수법을 단계별로 적어 뒀다.",
        "-- 판례와 보도자료는 reliability A, 상담사례는 B 로 둔다.",
        "--",
        "-- 판례 URL 은 국가법령정보센터 판례 링크로 정규화했다. 수집 당시 URL 에는",
        "-- 수집자의 Open API 발급 ID(OC 파라미터)가 들어 있어 그대로 두지 않는다.",
        "",
    ]
    for key, stype, code, title, url in WANTED:
        d = found[key]
        rel = "A" if stype in ("판례", "보도자료") else "B"
        pub = (d.get("published_at") or "").strip()
        body = (
            "# [%s] %s\n\n"
            "- **원문 URL**: %s\n"
            "- **출처 구분**: %s\n"
            "- **발행일**: %s\n"
            "- **수집일**: %s\n"
            "- **유형**: %s\n\n"
            "---\n\n%s\n"
        ) % (code, d.get("title", "").strip(), url, stype, pub or "(미상)",
             (d.get("collected_at") or "")[:10], code, d.get("content", "").strip())
        out.append("-- ── %s · %s" % (code, title[:60]))
        out.append("INSERT INTO corpus_documents")
        out.append("  (source_type, title, body, source_url, published_on, reliability, verified)")
        out.append("VALUES ('%s', %s, %s," % (stype, dollar(title), dollar(body)))
        out.append("        '%s', %s, '%s', true);" % (
            url, ("'%s'" % pub) if pub else "NULL", rel))
        out.append("")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("%s 생성 — 원문 %d건" % (OUT, len(WANTED)))
    for key, stype, code, title, _ in WANTED:
        print("   %-4s %-6s %5d자  %s" % (code, stype, len(found[key].get("content", "")), title[:44]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
