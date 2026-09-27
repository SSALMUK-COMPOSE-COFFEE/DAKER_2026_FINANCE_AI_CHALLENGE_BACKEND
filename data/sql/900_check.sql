\echo '=== 적재 건수 ==='
SELECT 'case_types' t, count(*) FROM case_types
UNION ALL SELECT 'questions', count(*) FROM questions
UNION ALL SELECT 'question_options', count(*) FROM question_options
UNION ALL SELECT 'type_rules', count(*) FROM type_rules
ORDER BY 1;

\echo '=== 차단 유형 (LLM 호출 금지) ==='
SELECT code, name, risk_level, out_of_scope FROM case_types
WHERE risk_level <> '없음' ORDER BY code;

\echo '=== 즉시 중단 선택지 ==='
SELECT question_code, option_key, left(label,30) AS label FROM question_options
WHERE stop_here ORDER BY question_code, ordinal;

\echo '=== 룰이 하나도 없는 유형 (판정 불가) ==='
SELECT c.code, c.name FROM case_types c
LEFT JOIN type_rules r ON r.case_type_id = c.id
WHERE r.id IS NULL ORDER BY c.code;

\echo '=== 유형별 준비 상태 ==='
SELECT * FROM v_pack_ready;

\echo ''
\echo '=== 법조문 적재 상태 (2026-09-06 추가) ==='
SELECT law_name, count(*) AS 조문수, sum(length(body)) AS 총글자, min(effective_on) AS 시행일
FROM statutes GROUP BY law_name ORDER BY 1;

\echo '=== 유형별 다툴 조항 ==='
SELECT code, left(name,26) AS name, out_of_scope AS 범위밖,
       coalesce(clause,'(비움)') AS 다툴조항
FROM case_types ORDER BY id;

\echo '=== 팩 상태 — 조문이 실제로 들어갔나 ==='
SELECT t.code, t.out_of_scope AS 범위밖, p.token_count AS 글자수,
       (p.pack_text LIKE '%관련 법조문%') AS 조문포함,
       (p.pack_text LIKE '%다툴 조항%')   AS 조항표시,
       p.built_at::date AS 조립일
FROM snippet_packs p JOIN case_types t ON t.id = p.case_type_id
ORDER BY t.id;

\echo '=== 팩이 없는 유형 (근거 없이 소명서가 나가는 유형) ==='
SELECT c.code, left(c.name,30) AS name,
       count(d.id) FILTER (WHERE d.verified)     AS 검수완료,
       count(d.id) FILTER (WHERE NOT d.verified) AS 미검수
FROM case_types c
LEFT JOIN snippet_packs p ON p.case_type_id = c.id
LEFT JOIN case_digests  d ON d.case_type_id = c.id
WHERE p.case_type_id IS NULL
GROUP BY c.id, c.code, c.name ORDER BY c.id;

\echo '=== 아직 비어 있는 테이블 ==='
SELECT 'refusal_reasons' AS t, count(*) FROM refusal_reasons
UNION ALL SELECT 'evidence_items', count(*) FROM evidence_items
UNION ALL SELECT 'precedents',     count(*) FROM precedents
UNION ALL SELECT 'document_chunks',count(*) FROM document_chunks
ORDER BY 1;
