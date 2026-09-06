-- 100_build_packs.sql · 유형별 프롬프트 팩 조립
-- 여러 번 돌려도 안전하다 (ON CONFLICT DO UPDATE).
--
-- 넣는 규칙 :
--   범위 안 유형(out_of_scope=false) → verified=true 인 digest만 넣는다.
--   범위 밖 유형(out_of_scope=true)  → 미검수도 넣되 '차단 안내'로 성격을 명시한다.
--     이 유형의 팩은 소명서를 쓰기 위한 근거가 아니라 왜 못 쓰는지를 설명하는 글이라
--     원문 두께가 필요하지 않다.
--
-- 법조문 :
--   범위 안 유형 → 법 제7조(이의제기) 전문을 넣는다. 소명의 근거 조항이라
--     이것이 없으면 LLM 이 조항을 인용할 수 없고, 인용하면 지어낸 것이 된다.
--   범위 밖 유형 → 법 제16조(벌칙) 전문을 넣는다. 안내문이 이 조항을 근거로
--     "사실과 다르게 쓰면 처벌된다" 고 말하기 때문이다.
--   조문은 statutes 에서 그대로 가져온다. 팩에 문구를 복사해 두지 않는다.
--
-- token_count 는 글자 수다. 한글은 대략 글자당 1~2 토큰이므로 어림값으로만 쓴다.

INSERT INTO snippet_packs (case_type_id, pack_text, token_count, built_at)
SELECT
  t.id,
     '# 유형 ' || t.code || ' · ' || t.name || E'\n\n'
  || CASE WHEN t.out_of_scope
          THEN E'> **이 유형은 소명서를 생성하지 않는다.** 아래는 왜 생성하면 안 되는지에 대한 설명이며,\n'
            || E'> 사용자에게는 안내와 전문가 연결만 제공한다.\n\n'
          ELSE '' END
  || '**어떤 유형인가** ' || t.description || E'\n\n'
  || '**축** 구조=' || coalesce(t.structure,'-')
     || ' / 목적물=' || coalesce(t.subject,'-')
     || ' / 주로 가는 길=' || t.track
     || ' / 위험도=' || t.risk_level
     || ' / 코퍼스 관측 ' || t.observed_count || E'건\n\n'
  || CASE WHEN t.clause IS NOT NULL AND t.clause <> ''
          THEN '**다툴 조항** ' || t.clause || E'\n\n' ELSE '' END
  || '---' || E'\n\n'
  || coalesce(d.sections, E'(요약 자료 없음)\n')
  || coalesce(r.reasons, '')
  || coalesce(law.text, '')
  || E'\n---\n\n'
  || E'**작성 규칙**\n'
  || E'- 위 자료에 없는 날짜·금액·이름을 절대 만들어 내지 않는다.\n'
  || E'- 문장마다 어느 자료에 근거했는지 밝힌다.\n'
  || E'- "기각된 것"에 적힌 서술은 반복하지 않는다.\n'
  || E'- 법 조항은 위 "관련 법조문"에 실린 것만 인용한다. 없는 조항은 쓰지 않는다.\n'
  || CASE WHEN t.out_of_scope
          THEN E'- 이 유형에는 소명서 본문을 쓰지 않는다. 안내문만 출력한다.\n'
          ELSE '' END,
  length(
     '# 유형 ' || t.code || ' · ' || t.name
  || coalesce(d.sections,'') || coalesce(r.reasons,'') || coalesce(law.text,'')),
  now()
FROM case_types t
LEFT JOIN LATERAL (
  SELECT string_agg(
           '## ' || CASE cd.section
                      WHEN '인정된것' THEN '인정된 것'
                      WHEN '기각된것' THEN '기각된 것 — 반드시 피할 것'
                      WHEN '표현'     THEN '실제로 통한 표현'
                      ELSE cd.section END
           || E'\n' || cd.body || E'\n',
           E'\n' ORDER BY array_position(
             ARRAY['상황','쟁점','인정된것','기각된것','표현'], cd.section))
         AS sections
  FROM case_digests cd
  WHERE cd.case_type_id = t.id
    AND (cd.verified OR t.out_of_scope)
) d ON true
LEFT JOIN LATERAL (
  SELECT E'\n## 반려된 사유 (이렇게 쓰면 거절된다)\n'
         || string_agg('- ' || rr.reason
              || CASE WHEN rr.avoid_how <> '' THEN ' → ' || rr.avoid_how ELSE '' END,
              E'\n' ORDER BY rr.id) || E'\n'
         AS reasons
  FROM refusal_reasons rr WHERE rr.case_type_id = t.id
) r ON true
LEFT JOIN LATERAL (
  -- 범위 안이면 이의제기 근거 조항(제7조), 범위 밖이면 벌칙 조항(제16조).
  SELECT E'\n## 관련 법조문 (이 안에 있는 것만 인용할 것)\n\n'
         || string_agg(st.body, E'\n\n' ORDER BY st.article)
         || E'\n\n> ' || st.law_name || ' · 시행 '
         || to_char(max(st.effective_on), 'YYYY-MM-DD') || E'\n'
         AS text
  FROM statutes st
  WHERE st.law_name = '전기통신금융사기 피해 방지 및 피해금 환급에 관한 특별법'
    AND st.article = CASE WHEN t.out_of_scope THEN '제16조' ELSE '제7조' END
  GROUP BY st.law_name
) law ON true
WHERE d.sections IS NOT NULL
ON CONFLICT (case_type_id) DO UPDATE
  SET pack_text = EXCLUDED.pack_text,
      token_count = EXCLUDED.token_count,
      built_at = now();
