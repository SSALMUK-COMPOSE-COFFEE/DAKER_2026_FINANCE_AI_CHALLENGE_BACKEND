-- 003_content.sql · 「풀림」 콘텐츠/판정 계층
-- 작성 2026-09-02 · C(데이터/콘텐츠)
-- 전제 : 002_schema.sql 적용 후 실행. 기존 9개 테이블은 건드리지 않는다.

-- ============================================================
-- 0. 기존 case_types 확장
--    002는 code/name/track/description/out_of_scope만 있어서
--    유형지도의 판정 축(구조·목적물·조항)을 담지 못한다.
-- ============================================================

ALTER TABLE case_types
    ADD COLUMN IF NOT EXISTS structure      text,
    ADD COLUMN IF NOT EXISTS subject        text,
    ADD COLUMN IF NOT EXISTS clause         text,
    ADD COLUMN IF NOT EXISTS risk_level     text NOT NULL DEFAULT '없음',
    ADD COLUMN IF NOT EXISTS difficulty     text,
    ADD COLUMN IF NOT EXISTS observed_count smallint NOT NULL DEFAULT 0;

ALTER TABLE case_types
    ADD CONSTRAINT case_types_structure_chk CHECK (
        structure IS NULL OR structure IN ('물건넘김','계좌경유','통장묶기','환전대리')),
    ADD CONSTRAINT case_types_subject_chk CHECK (
        subject IS NULL OR subject IN (
            '실물중고','상품권','게임재화','팬덤굿즈','금외화','암호화폐','용역','없음')),
    ADD CONSTRAINT case_types_risk_chk CHECK (
        risk_level IN ('없음','경고','차단'));

COMMENT ON COLUMN case_types.risk_level IS
    '차단이면 LLM을 호출하지 않고 안내만 출력한다. 자기부죄 문서 방지.';

-- ============================================================
-- 1. 문진 — 질문과 선택지를 DB에 둔다
--    선택지 문구를 코드에 박으면 마감 직전 수정에 프론트 배포가 필요하다.
--    또한 option_key가 곧 판정 룰의 입력값이라 한 곳에서 관리해야 한다.
-- ============================================================

CREATE TABLE questions (
    code        text PRIMARY KEY,            -- 'q1'..'q8', 'q6f'(후속)
    ordinal     smallint NOT NULL,
    title       text NOT NULL,               -- 화면에 뜨는 질문 문장
    hint        text NOT NULL DEFAULT '',    -- 보조 설명
    input_kind  text NOT NULL CHECK (input_kind IN ('단일선택','복수선택','입력폼')),
    parent_code text REFERENCES questions(code) ON DELETE CASCADE,
    active      boolean NOT NULL DEFAULT true
);

CREATE TABLE question_options (
    id            serial PRIMARY KEY,
    question_code text NOT NULL REFERENCES questions(code) ON DELETE CASCADE,
    ordinal       smallint NOT NULL DEFAULT 0,
    option_key    text NOT NULL,             -- 'bank','police','exchange' … 판정 입력값
    label         text NOT NULL,             -- 사용자에게 보이는 문구
    axis          text CHECK (axis IN ('트랙','구조','목적물','조항','위험','없음')),
    axis_value    text,
    risk_flag     text CHECK (risk_flag IS NULL OR risk_flag IN
                    ('도박','환치기','대리송금','접근매체')),
    stop_here     boolean NOT NULL DEFAULT false,  -- 고르면 즉시 중단
    warning       text NOT NULL DEFAULT '',        -- 그 자리에서 띄울 경고문
    UNIQUE (question_code, option_key)
);

CREATE INDEX question_options_q_idx ON question_options (question_code, ordinal);

COMMENT ON COLUMN question_options.option_key IS
    '프론트가 서버로 돌려보내는 값. type_rules.condition의 입력이므로 한번 정하면 바꾸지 않는다.';

-- ============================================================
-- 2. 판정 룰 — 선택지 조합에서 유형을 확정한다 (LLM 아님)
-- ============================================================

CREATE TABLE type_rules (
    id           serial PRIMARY KEY,
    case_type_id smallint NOT NULL REFERENCES case_types(id) ON DELETE CASCADE,
    priority     smallint NOT NULL DEFAULT 100,   -- 낮을수록 먼저 평가
    condition    jsonb NOT NULL,                  -- {"q1":["bank"],"q3":["exchange"]}
    note         text NOT NULL DEFAULT ''
);

CREATE INDEX type_rules_priority_idx ON type_rules (priority);

COMMENT ON TABLE type_rules IS
    '문진 답 → 유형. 같은 입력에 같은 결과가 나와야 하므로 LLM에 위임하지 않는다.';

-- ============================================================
-- 3. 유형별 요약 뭉치 — LLM에 넣는 최소 단위
-- ============================================================

CREATE TABLE case_digests (
    id           bigserial PRIMARY KEY,
    document_id  bigint REFERENCES corpus_documents(id) ON DELETE SET NULL,
    case_type_id smallint NOT NULL REFERENCES case_types(id) ON DELETE CASCADE,
    section      text NOT NULL CHECK (section IN
                    ('상황','쟁점','인정된것','기각된것','표현')),
    body         text NOT NULL,              -- 3~8문장. 사실만. 추측 금지
    verified     boolean NOT NULL DEFAULT false,
    verified_on  date
);

CREATE INDEX case_digests_type_idx ON case_digests (case_type_id, section);

COMMENT ON COLUMN case_digests.document_id IS
    '원문 참조. 소명서 전 문장에 출처를 붙이려면 요약만으로는 근거를 못 댄다.';

CREATE TABLE refusal_reasons (
    id           serial PRIMARY KEY,
    case_type_id smallint REFERENCES case_types(id) ON DELETE CASCADE,
    document_id  bigint REFERENCES corpus_documents(id) ON DELETE SET NULL,
    reason       text NOT NULL,              -- '해외 포커사이트 게임머니'
    avoid_how    text NOT NULL DEFAULT ''    -- 소명서에서 피해야 할 서술
);

-- ============================================================
-- 4. 조립물 — 유형마다 하나씩 미리 합쳐 둔 프롬프트 팩
--    유형이 16개뿐이라 런타임 검색이 필요 없다. 키 조회 한 번이면 된다.
-- ============================================================

CREATE TABLE snippet_packs (
    case_type_id smallint PRIMARY KEY REFERENCES case_types(id) ON DELETE CASCADE,
    pack_text    text NOT NULL,              -- 법령 + digest + 반려사유 합본
    token_count  integer NOT NULL DEFAULT 0,
    built_at     timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE snippet_packs IS
    '프롬프트 앞쪽 고정 구간에 그대로 들어간다. 같은 유형 반복 호출 시 캐시가 재사용된다.';

-- ============================================================
-- 5. 편의 뷰
-- ============================================================

CREATE VIEW v_pack_ready AS
SELECT t.code, t.name, t.risk_level,
       count(d.id) FILTER (WHERE d.verified)     AS 검수완료,
       count(d.id) FILTER (WHERE NOT d.verified) AS 미검수,
       (p.case_type_id IS NOT NULL)              AS 팩있음
FROM case_types t
LEFT JOIN case_digests  d ON d.case_type_id = t.id
LEFT JOIN snippet_packs p ON p.case_type_id = t.id
GROUP BY t.code, t.name, t.risk_level, p.case_type_id
ORDER BY t.code;

COMMENT ON VIEW v_pack_ready IS
    '유형별 준비 상태 한눈에. 검수완료가 0인 유형은 LLM에 줄 근거가 없다는 뜻.';
