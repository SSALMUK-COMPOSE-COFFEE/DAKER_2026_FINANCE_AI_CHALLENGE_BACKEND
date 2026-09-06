-- 030_seed_type_rules.sql · 문진 답 → 유형 판정 룰
-- 출처 : 3자사기_유형분류.md 「판정 결과 매핑 요약」 (서비스플로우 Q번호로 변환)
--
-- condition 읽는 법 : {"q3":["sale"],"q4":["gold"]}
--   모든 키를 만족해야 한다(AND). 각 키의 값 배열 중 하나라도 맞으면 그 키는 만족(OR).
--   복수선택 문항(q8)은 사용자가 고른 것 중 하나라도 배열에 있으면 만족.
-- priority : 낮을수록 먼저 평가한다. 먼저 맞은 룰에서 멈춘다.
--   위험 유형을 앞에 두는 이유 — 물건을 팔았더라도 도박 환전이면 T12가 이겨야 한다.

INSERT INTO type_rules (case_type_id, priority, condition, note) VALUES
-- ── 10번대 : 위험 게이트. 무조건 먼저 ──────────────────
 ((SELECT id FROM case_types WHERE code='T16'),10,'{"q8":["access_medium"]}',
  '접근매체 제공. 영구 제외'),
 ((SELECT id FROM case_types WHERE code='T12'),11,'{"q8":["gambling"]}',
  '도박 환전 — 자기부죄'),
 ((SELECT id FROM case_types WHERE code='T12'),12,'{"q3":["exchange"]}',
  'Q3에서 환전을 고른 경우도 같은 유형'),
 ((SELECT id FROM case_types WHERE code='T13'),13,'{"q8":["fx"]}',
  '환치기 — 외국환거래법'),
 ((SELECT id FROM case_types WHERE code='T14'),14,'{"q8":["proxy_withdraw"]}',
  '대리 인출·송금'),
 ((SELECT id FROM case_types WHERE code='T14'),15,'{"q3":["proxy"]}',
  'Q3에서 대리송금을 고른 경우'),
 ((SELECT id FROM case_types WHERE code='T14'),16,'{"q6f":["sent"]}',
  '반환 요구에 이미 송금 — 자금 전달책으로 지위 이동'),
-- ── 20번대 : 거래가 없거나 금액이 어긋난 경우 ──────────
 ((SELECT id FROM case_types WHERE code='T8'),20,'{"q6":["more"]}',
  '초과 입금. 가장 강력한 단일 신호'),
 ((SELECT id FROM case_types WHERE code='T15'),21,'{"q3":["family"]}',
  '가족·지인 경유'),
 ((SELECT id FROM case_types WHERE code='T10'),22,'{"q3":["unknown"],"q6f":["threat"]}',
  '모르는 돈 + 협박 = 통장협박'),
 ((SELECT id FROM case_types WHERE code='T11'),23,'{"q3":["unknown"],"q6f":["none"]}',
  '모르는 돈 + 요구 없음 = 통장묶기'),
 ((SELECT id FROM case_types WHERE code='T9'),24,'{"q3":["unknown"]}',
  '모르는 돈. 위 둘에 안 걸리면 계좌도용'),
 ((SELECT id FROM case_types WHERE code='T9'),25,'{"q4":["none"],"q1":["alert"]}',
  '넘긴 것이 없고 아직 정지 전'),
-- ── 30번대 : 물건을 팔았다. 목적물로 가른다 ────────────
 ((SELECT id FROM case_types WHERE code='T2'),30,'{"q3":["sale"],"q4":["gold"]}',
  '금·귀금속·외화'),
 ((SELECT id FROM case_types WHERE code='T3'),31,'{"q3":["sale"],"q4":["crypto"]}',
  '암호화폐'),
 ((SELECT id FROM case_types WHERE code='T4'),32,'{"q3":["sale"],"q4":["game"]}',
  '게임 재화·계정'),
 ((SELECT id FROM case_types WHERE code='T5'),33,'{"q3":["sale"],"q4":["giftcard"]}',
  '상품권'),
 ((SELECT id FROM case_types WHERE code='T6'),34,'{"q3":["sale"],"q4":["fandom"]}',
  '팬덤 굿즈·티켓'),
 ((SELECT id FROM case_types WHERE code='T7'),35,'{"q3":["wage","sale"],"q4":["service"]}',
  '용역·급여'),
 ((SELECT id FROM case_types WHERE code='T1'),40,'{"q3":["sale"],"q4":["used_goods"]}',
  '실물 중고물품. 가장 흔한 기본값');
