# -*- coding: utf-8 -*-
"""070_seed_corpus_oos.sql 생성 — 범위 밖 유형(T13·T14·T16)의 원문.

050 과 같은 방식이다. 원시 코퍼스(legalqa.jsonl)에서 해당 기사를 꺼내
corpus_documents INSERT 문으로 만든다. SQL 을 직접 고치지 말고 이 파일을 고칠 것.

실행 — 데이터작업 폴더에서
    python scripts/gen_corpus_oos.py
"""
import io
import os, json, os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 원시 조사 자료(기획자료/)는 레포 밖에 있다. 레포에 넣을 수 없는 수집 원본이라
# 그렇다. 위치가 다르면 PULLIM_RESEARCH_DIR 로 덮는다.
RESEARCH = os.environ.get("PULLIM_RESEARCH_DIR", "../../기획자료/5. 3자 사기 자료")
RAW = os.path.join(RESEARCH, "data", "raw", "legalqa.jsonl")
OUT = "sql/070_seed_corpus_oos.sql"

# 유형분류 문서 3장(T13·T14·T16) 의 '관측 근거' 에 적힌 기사들.
WANTED = [
    ("E4ROMI59NY5Q", "T13", "환치기·사설환전소형 — 중국 근무 남편 월급을 사설환전소로 수령"),
    ("PWDNO68JWIO2", "T14", "대리송금형 — 친구 부탁으로 100만원 이체 후 지급정지"),
    ("CNNQA1PH6XY3", "T14", "대리송금형 — 텔레그램 '양방작업 이체 알바' 후 전 계좌 정지"),
    ("V7STYMBG63W1", "T14", "대리송금형 — '일당 20만원' 송금 알바, 3일간 6,700만원"),
    ("257JK09933ZO", "T16", "접근매체 제공형 — 대출 미끼로 OTP·신분증 제공"),
    ("H40XMHGUXH8V", "T16", "접근매체 제공형 — 고액 알바 미끼로 카드·휴대폰 제공"),
    ("F5RL6SYENP1S", "T16", "접근매체 제공형(인접) — 명의도용 개통 주장"),
]


def load():
    by_key = {}
    for line in io.open(RAW, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        url = d.get("url") or ""
        for key, _, _ in WANTED:
            if key in url:
                by_key[key] = d
    return by_key


def dollar(text):
    """달러 인용. 본문에 $doc$ 가 없음을 확인하고 감싼다."""
    if "$doc$" in text:
        raise SystemExit("본문에 $doc$ 가 들어 있다: %r" % text[:60])
    return "$doc$" + text + "$doc$"


def main():
    if not os.path.exists(RAW):
        print("원시 코퍼스를 못 찾음: %s" % RAW)
        return 1
    found = load()
    missing = [k for k, _, _ in WANTED if k not in found]
    if missing:
        print("코퍼스에 없는 기사: %s" % ", ".join(missing))
        return 1

    out = [
        "-- 070_seed_corpus_oos.sql · 원문 (범위 밖 유형 T13·T14·T16)",
        "-- scripts/gen_corpus_oos.py 로 생성됨. 직접 고치지 말고 스크립트를 고칠 것.",
        "--",
        "-- 이 세 유형은 out_of_scope=true 다. 팩이 소명서 문안이 아니라 차단 안내문이라",
        "-- 원문 두께가 필요하지 않다. 다만 안내문도 근거가 있어야 하므로 출처는 남긴다.",
        "-- 전부 로톡뉴스 상담사례다. 당사자 1인칭 서사가 아니라 변호사 의견 기사이므로",
        "-- reliability 는 B, verified 는 false 로 둔다.",
        "",
    ]
    for key, code, title in WANTED:
        d = found[key]
        body = (
            "# [%s] %s\n\n"
            "- **원문 URL**: %s\n"
            "- **매체**: %s\n"
            "- **발행일**: %s\n"
            "- **수집일**: %s\n"
            "- **유형**: %s (범위 밖)\n\n"
            "---\n\n%s\n"
        ) % (code, d.get("title", "").strip(),
             d.get("url", ""), d.get("author", "") or "로톡뉴스",
             d.get("published_at", ""), (d.get("collected_at", "") or "")[:10],
             code, d.get("content", "").strip())
        out.append("-- ── %s · %s" % (code, title))
        out.append("INSERT INTO corpus_documents")
        out.append("  (source_type, title, body, source_url, published_on, reliability, verified)")
        out.append("VALUES ('상담사례', %s, %s," % (dollar(title), dollar(body)))
        out.append("        '%s', '%s', 'B', false);" % (d.get("url", ""), d.get("published_at", "")))
        out.append("")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("%s 생성 — 원문 %d건" % (OUT, len(WANTED)))
    for key, code, title in WANTED:
        print("   %-4s %s (%d자)" % (code, key, len(found[key].get("content", ""))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
