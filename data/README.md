# data — 코퍼스와 프롬프트 자료 (담당 김주현)

「풀림」이 소명서를 쓸 때 근거로 삼는 자료를 만드는 곳. **매일 로그를 남긴다.**

**인계받았다면 [인수인계.md](인수인계.md)부터 읽는다** (세팅 + 바로 실행).
**처음이면 [내작업_흐름도.md](내작업_흐름도.md)부터 읽는다** (비개발자용 · 용어 풀이 포함).

## 여기와 db/init 의 관계

`sql/` 이 **고치는 곳**이고 `../db/init/` 이 **배포되는 곳**이다. 스크립트가 `sql/` 에
생성하므로 그쪽을 고친 뒤 `db/init/` 으로 복사한다. `900_check.sql`(점검 쿼리)은
기동 때 돌 이유가 없어 `db/init/` 에 두지 않는다.

## 원시 조사 자료는 레포 밖에 있다

`gen_corpus_*.py` 와 `gen_statutes.py` 는 수집 원본(`기획자료/`)을 읽는다. 레포에
넣을 수 없는 자료라 기본값이 `../../기획자료/5. 3자 사기 자료` 다. 위치가 다르면
`PULLIM_RESEARCH_DIR` 로 덮는다.

---

## 접속

```bash
ssh -i ~/.ssh/pullim_kimjuhyeon pullim@hajin.xyz
psql -h 127.0.0.1 -p 15432 -U pullim -d pullim     # .pgpass 등록됨, 비밀번호 안 물음
```

포트는 **15432**다. 5432는 호스트의 다른 Postgres라 붙으면 안 된다.
`docker exec`은 `pullim` 계정이 docker 그룹에 없어 못 쓴다. psql 직결로 간다.

로컬에서 한 줄로 쿼리:

```bash
ssh -i ~/.ssh/pullim_kimjuhyeon pullim@hajin.xyz \
  "psql -h 127.0.0.1 -p 15432 -U pullim -d pullim -c '\dt'"
```

SQL 파일 적용:

```bash
ssh -i ~/.ssh/pullim_kimjuhyeon pullim@hajin.xyz \
  "psql -h 127.0.0.1 -p 15432 -U pullim -d pullim" < sql/003_content.sql
```

---

## 폴더

| 경로 | 무엇 |
|---|---|
| `로그/` | **매일 작업 로그.** `YYYY-MM-DD.md`. 템플릿은 `_템플릿.md` |
| `sql/` | 스키마와 시드. 번호 순서대로 적용 |
| `digest/` | `case_digests` 원고. 유형별 5섹션 |
| `pack/` | 조립된 프롬프트 팩 (`snippet_packs`에 들어갈 것) |
| `mock/프롬프트/` | GPT에 넣은 입력 그대로 |
| `mock/결과/` | 나온 답과 채점 |
| `scripts/` | 팩 조립·적재 스크립트 |

## sql 번호 규칙

| 번호대 | 무엇 |
|---|---|
| `001`~`002` | 서버 `db/init/`에서 내려받은 원본. **고치지 않는다** |
| `003` | 콘텐츠/판정 계층 추가 (C 작성) |
| `010`~ | 시드 데이터 INSERT |
| `070`~`080` | 범위 밖 유형(T13·T14·T16) 원문·요약 |
| `090`~`091` | T9 순수 계좌도용형 원문·요약 |
| `900`~ | 점검 쿼리 |

---

## 지금 상태

- [x] SSH·psql 접속 확보
- [x] `003_content.sql` 작성
- [x] `002` + `003` 서버 적용 — 테이블 15개
- [x] 시드 적재 — `case_types` 16 · `questions` 9 · `question_options` 44 · `type_rules` 20
- [x] `banks` 20곳 + `bank_requirements` 14행 — 기존 조사 자료에서 적재
- [ ] `statutes` 3~5건 · `case_types.clause` 매핑
- [x] `corpus_documents` 7건 (T1·T4·T12)
- [x] `case_digests` 15행
- [x] `snippet_packs` 3건 조립
- [x] 검증 재료 (시스템 프롬프트·사연 3건·채점표·실행 스크립트)
- [x] **검증 1회 완료** — 3유형 × 5항목 전부 통과 (2026-09-06 · $0.08)
- [ ] `statutes` 제2조·제7조
- [x] 범위 밖 3유형 digest — T13·T14·T16 (원문 7건 + 요약 15행) · **서버 적재 완료**
- [x] T9 순수 계좌도용형 — 더쿠 원문 + 요약 5행 · **서버 적재 완료** (팩 7건)
- [ ] **T2·T3 ← 다음** (대법원 판례 기반) → T6·T8·T15
- [ ] T5·T10·T11 재수집 · T7은 관측 0으로 불가
