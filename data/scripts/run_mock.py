# -*- coding: utf-8 -*-
"""팩 + 가짜 사연을 LLM에 넣고 결과를 저장한다.

배포 서버(deploy/docker-compose.yml)와 **같은 경로**를 쓴다 — OpenRouter.
검증과 실서비스가 다른 모델을 타면 검증이 의미가 없기 때문이다.

표준 라이브러리만 쓴다. pip install 이 필요 없다.

사전 준비 — 키 하나만 있으면 된다
    데이터작업/.env 파일에 아래 한 줄. (이 파일은 git에 안 올라간다)
        OPENROUTER_API_KEY=sk-or-v1-...
    또는 환경변수로:
        Windows PowerShell : $env:OPENROUTER_API_KEY="sk-or-v1-..."
        macOS / Linux      : export OPENROUTER_API_KEY=sk-or-v1-...

    키는 배포 서버 deploy/.env 의 LLM_API_KEY 와 같은 것을 쓰면 된다(권하진).

실행 — 데이터작업 폴더에서
    python scripts/run_mock.py            # 3건 전부
    python scripts/run_mock.py T12        # 하나만

결과는 mock/결과/<유형>_<시각>.md 로 남는다. 채점은 mock/채점표.md.
끝난 이유가 length 면 상한에 걸려 잘린 것이므로 LLM_MAX_TOKENS 를 올린다.
"""
import io, json, os, sys, time, urllib.request, urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_dotenv(path=".env"):
    """의존성 없이 .env 를 읽는다. 이미 있는 환경변수를 덮지 않는다."""
    if not os.path.exists(path):
        return
    for line in io.open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


load_dotenv()

# 배포 서버 기본값과 동일하게 맞춰 둔다 (app/config.py)
BASE  = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-5")
KEY   = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("LLM_API_KEY", "")
# 상한을 안 주면 모델 최대치(65,536)를 예약하고 시작해서, 잔액이 적으면 402 가 난다.
MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "6000"))

CASES = [
    ("T1",  "pack/T1.md",  "mock/사연/T1_실물중고.md"),
    ("T4",  "pack/T4.md",  "mock/사연/T4_게임재화.md"),
    ("T12", "pack/T12.md", "mock/사연/T12_도박환전.md"),
]


def read(p):
    return io.open(p, encoding="utf-8").read()


def ask(system, user):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user",   "content": user}],
        "temperature": 0,      # 채점을 두 번 해도 같은 글이 나오게
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        BASE.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + KEY,
                 "HTTP-Referer": "https://pullim.hajin.xyz",
                 "X-Title": "pullim-pack-verify"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    choice = data["choices"][0]
    usage = data.get("usage") or {}
    meta = {
        "id": data.get("id", ""),
        # stop = 모델이 스스로 끝냄 / length = 상한에 걸려 잘림
        "finish": choice.get("finish_reason", "?"),
        "pt": usage.get("prompt_tokens", 0),
        "ct": usage.get("completion_tokens", 0),
        "tt": usage.get("total_tokens", 0),
    }
    return choice["message"]["content"], meta


def generation_cost(gen_id):
    """OpenRouter 가 실제 청구한 금액. 집계가 늦어 몇 번 재시도한다."""
    if not gen_id:
        return None
    for _ in range(6):
        try:
            req = urllib.request.Request(
                BASE.rstrip("/") + "/generation?id=" + gen_id,
                headers={"Authorization": "Bearer " + KEY})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))["data"].get("total_cost")
        except Exception:
            time.sleep(2)
    return None


def main():
    if not KEY:
        print("키가 없습니다.")
        print("  데이터작업/.env 에 OPENROUTER_API_KEY=sk-or-v1-... 한 줄을 넣으세요.")
        print("  배포 서버 deploy/.env 의 LLM_API_KEY 와 같은 값입니다.")
        return 1

    only = sys.argv[1] if len(sys.argv) > 1 else None
    system = read("mock/프롬프트/시스템.md")
    os.makedirs("mock/결과", exist_ok=True)
    print("모델 %s  (%s, max_tokens=%d)" % (MODEL, BASE, MAX_TOKENS))

    failed = 0
    rows = []
    for code, packp, casep in CASES:
        if only and code != only:
            continue
        print("[%s] 요청 중..." % code)
        user = ("# 참고 자료\n\n" + read(packp)
                + "\n\n---\n\n# 이 사람의 사정\n\n" + read(casep))
        try:
            out, meta = ask(system, user)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            print("  실패: HTTP %s\n  %s" % (e.code, detail))
            if e.code == 401:
                print("  → 키가 틀렸습니다.")
            elif e.code == 402:
                print("  → 잔액 부족. 충전하거나 LLM_MAX_TOKENS 를 낮추세요.")
            elif e.code == 404:
                print("  → 모델 이름이 틀렸습니다. LLM_MODEL 을 확인하세요.")
            failed += 1
            continue
        except urllib.error.URLError as e:
            print("  실패: 접속 안 됨 — %s" % e)
            failed += 1
            continue

        cut = meta["finish"] == "length"
        cost = generation_cost(meta["id"])
        rows.append((code, meta, cost, cut))
        stamp = time.strftime("%Y%m%d-%H%M%S")
        path = "mock/결과/%s_%s.md" % (code, stamp)
        io.open(path, "w", encoding="utf-8", newline="\n").write(
            "# %s 결과 (%s / %s)\n\n"
            "채점은 mock/채점표.md 참고. 특히 T12 는 소명서가 나오면 실패.\n\n"
            "- 끝난 이유 : %s%s\n"
            "- 토큰 : 입력 %d + 출력 %d = %d\n"
            "- 비용 : %s\n\n"
            "---\n\n%s\n" % (
                code, MODEL, stamp,
                meta["finish"],
                "  ← 상한에 걸려 잘렸다. LLM_MAX_TOKENS 를 올릴 것" if cut else "",
                meta["pt"], meta["ct"], meta["tt"],
                ("$%.6f" % cost) if cost is not None else "조회 실패",
                out))
        print("  저장: %s  (%d자)" % (path, len(out)))
        print("        끝난이유 %s%s | 토큰 %d+%d=%d | %s" % (
            meta["finish"], " ★잘림" if cut else "",
            meta["pt"], meta["ct"], meta["tt"],
            ("$%.6f" % cost) if cost is not None else "비용 조회 실패"))

    if rows:
        line = "-" * 68
        print()
        print(line)
        print("%-5s %-8s %8s %8s %8s  %s" % ("유형", "끝난이유", "입력", "출력", "합계", "비용"))
        print(line)
        total = 0.0
        for code, meta, cost, cut in rows:
            total += cost or 0.0
            print("%-5s %-8s %8d %8d %8d  %s%s" % (
                code, meta["finish"], meta["pt"], meta["ct"], meta["tt"],
                ("$%.6f" % cost) if cost is not None else "?",
                "  ★잘림" if cut else ""))
        print(line)
        print("%-5s %-8s %8d %8d %8d  $%.6f" % (
            "합계", "",
            sum(m["pt"] for _, m, _, _ in rows),
            sum(m["ct"] for _, m, _, _ in rows),
            sum(m["tt"] for _, m, _, _ in rows), total))
        if total > 0 and len(rows) == len(CASES):
            print()
            print("전체 1회(3건) 소진 : $%.6f  →  $5 로 약 %d회 가능" % (total, int(5.0 / total)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
