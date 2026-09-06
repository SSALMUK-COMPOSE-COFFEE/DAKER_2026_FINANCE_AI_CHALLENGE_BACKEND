-- 040_seed_banks.sql · 금융회사 20곳 이의제기 요구서류
-- 출처 : 기획자료/5. 3자 사기 자료/.../cases/11-bank-requirements.md
--        2026-08-29 Playwright 크롤링 · 공개 안내 페이지만 · 로그인 영역 미접근
--
-- discloses_documents 판정 기준 :
--   사용자에게 실제로 보여줄 서류 항목이 하나라도 있으면 true.
--   안내문으로 열거한 곳(카카오·씨티·전북)과 법정서식 PDF만 배포한 곳(하나·케이뱅크)을
--   모두 true로 두되, guidance_note에서 구분한다.
--
--
-- 제출된 기획서(첨부1)는 '4곳(20%)'으로 적혀 있다. 9/1 시점 중간 집계이며 어느 2곳을
-- 뺀 것인지 근거가 남아 있지 않다. 2026-09-06 팀 결정으로 정본은 이 파일의 5곳(25%)이다.
-- 되돌리지 말 것. 경위는 로그/2026-09-06.md 참고.
--
-- 원칙 : 페이지에 실제로 쓰여 있는 문구만 넣는다. 추측으로 채우지 않는다.

INSERT INTO banks
  (name, discloses_documents, has_type_guidance, review_days_min, review_days_max, guidance_note, source_url, checked_on)
VALUES
 ('카카오뱅크', true, false, 14, 21,
  '안내문에 서류 3항 열거. 법정서식 2항에 더해 본인서명사실확인서를 은행이 추가로 요구한다. 접수는 모바일 앱 또는 이메일(cw@kakaobank.email), 절차 페이지에는 팩스(0504-305-9852) 병기. 팩스·이메일 제출 시 본인서명사실확인서 필수. 처리기한을 "통상 2~3주"로 안내 — 금감원 5영업일 기준은 반영돼 있지 않다.',
  'https://www.kakaobank.com/Help/FinanceFraud/CopingMethod/Protest', '2026-08-29'),

 ('한국씨티은행', true, false, NULL, NULL,
  '「[전기통신금융사기] 이의제기 비대면 서류 제출 안내」에 서류 4항 열거. 접수 채널 3개 병기 — 팩스 02-6306-0365 / 이메일 financialfraud@citi.com / 영업점 방문. "서류 접수 후 3영업일 이내 접수 문자 발송"은 접수확인 기한이며 심사 기한이 아니다.',
  'https://www.citibank.co.kr/CusFconCnts0500.act', '2026-08-29'),

 ('전북은행', true, false, NULL, NULL,
  '안내문에 서류 3항 열거. 접수 채널 명시 없음 — 공시 페이지에 "지참하여"라는 표현이 있어 방문 전제로 보인다. 신청 가능 기간만 안내: 지급정지일부터 공고일 기준 2개월 경과 전까지.',
  'https://www.jbbank.co.kr/TCFF_INFO.act', '2026-08-29'),

 ('하나은행', true, false, NULL, NULL,
  '서식자료실에 「이의제기 신청서」 PDF(양식번호 5-08-0246)만 배포. 안내문 형태의 서류 목록은 없다. 접수 채널 안내문도 미발견이나, 금감원 비대면 목록에는 하나원큐 딥링크가 등재돼 있다.',
  'https://www.kebhana.com/cont/customer/customer07/customer0701/customer070106/index,1,list,3.jsp', '2026-08-29'),

 ('케이뱅크', true, false, NULL, NULL,
  '서식자료실에 「이의제기신청서」(2021.09.09) 배포. 첨부서류는 법정서식 2항 그대로. 본문은 절차 설명만 있고 서류 목록은 없다.',
  'https://www.kbanknow.com/web/customer/data/list?tab=form&chip=10', '2026-08-29'),

 ('KB국민은행', false, false, NULL, NULL,
  '이의제기 요구서류 안내 없음. 각주 한 줄만 — "사기이용계좌 명의인은 채권소멸 공고 기간 중 사기계좌가 아니라는 사실을 소명하여 지급정지에 대해 이의제기 가능".',
  'https://obank.kbstar.com/quics?page=C102304', '2026-08-29'),

 ('우리은행', false, false, NULL, NULL,
  '이의제기 요구서류 안내 없음. 다만 비대면 접수 신설 사실은 별도 페이지에 기재 — "피해구제 및 이의제기 비대면 접수채널 신설(2026.06), 우리WON뱅킹 內 접수 프로세스 신설".',
  'https://spot.wooribank.com/pot/Dream?withyou=CQCCS0088', '2026-08-29'),

 ('NH농협은행', false, false, NULL, NULL,
  '이의제기 안내 없음. 피해구제신청안내 페이지만 있고 그마저 피해자용이다. 명의인 쪽 안내가 부재하다.',
  'https://banking.nonghyup.com/servlet/content/ip/ec/ipec0535r.thtml', '2026-08-29'),

 ('MG새마을금고', false, false, NULL, NULL,
  '이의제기 요구서류 안내 없음. "이의제기는 금융회사로 신청"이라는 한 줄만 있다.',
  'https://www.kfcc.co.kr/cc/financialFraudPrevention.do', '2026-08-29'),

 ('신협', false, false, NULL, NULL,
  '이의제기 안내 없음. 전기통신금융사기 3개 탭(정의·신고·대처방안) 어디에도 "이의제기" 문자열이 없다. 신고 안내만 있다.',
  'https://www.cu.co.kr/cu/cm/cntnts/cntntsView.do?mi=100463&cntntsId=1195', '2026-08-29'),

 ('우체국예금', false, false, NULL, NULL,
  '이의제기 안내 없음. 피해구제 신고서류만 안내한다 — 지급정지요청서, 사건사고사실 확인원, 신분증, 개인정보수집 이용동의서, 피해구제신청서 등.',
  'https://www.epostbank.go.kr/LNCTFF0100.do', '2026-08-29'),

 ('BNK경남은행', false, false, NULL, NULL,
  '이의제기 안내 없음. 2016년 새소식에 피해구제 제출서류만 기재. 피해구제 기한 안내는 "피해 신고일로부터 3영업일+14일".',
  'https://www.knbank.co.kr/ib20/mnu/BHPBKI020100000', '2026-08-29'),

 ('BNK부산은행', false, false, NULL, NULL,
  '이의제기 안내 없음. 「전기통신금융사기관련공시 > 지급정지관련공시내용」만 운영한다.',
  'https://www.busanbank.co.kr/ib20/mnu/BHPCSC361009001', '2026-08-29'),

 ('iM뱅크(대구)', false, false, NULL, NULL,
  '이의제기 안내 없음. 「보이스피싱 피해 신고 절차」 페이지는 콜센터 번호표와 금감원 링크뿐이다.',
  'https://www.imbank.co.kr/cms/fsv/sdb_2/sdb_26/sdb_267/1221201_5581.html', '2026-08-29'),

 ('신한은행', false, false, NULL, NULL,
  '안내 페이지 미발견. 별건으로 「금융거래목적 확인 증빙자료」 표는 있으나 이의제기와 무관하다. 금감원 비대면 서류제출 목록에는 앱 딥링크가 등재돼 있다.',
  'https://www.shinhan.com/hpe/index.jsp?cr=902301000000&NOTC_SEQ=9573', '2026-08-29'),

 ('IBK기업은행', false, false, NULL, NULL,
  '안내 페이지 미발견. 금감원 비대면 서류제출 목록에는 앱 딥링크가 등재돼 있다.',
  NULL, '2026-08-29'),

 ('토스뱅크', false, false, NULL, NULL,
  '안내 페이지 미발견. 공개 웹에 고객센터 도움말이 없고 앱 내에만 있는 것으로 보인다. 금감원 비대면 서류제출 목록에는 앱 딥링크가 등재돼 있다.',
  NULL, '2026-08-29'),

 ('SC제일은행', false, false, NULL, NULL,
  '이의제기 안내 미발견. 금융사기예방 섹션에는 「비대면 금융사고 책임분담 안내」만 있으며 별개 제도다.',
  'https://www.standardchartered.co.kr/np/kr/cm/cc/finan_risk_division.jsp', '2026-08-29'),

 ('광주은행', false, false, NULL, NULL,
  '안내 페이지 미발견. 금감원 비대면 서류제출 목록에는 앱 딥링크가 등재돼 있다.',
  NULL, '2026-08-29'),

 ('제주은행', false, false, NULL, NULL,
  '안내 페이지 미발견. 조사 시점에 사이트 접속 타임아웃.',
  NULL, '2026-08-29');

-- ── 요구서류 항목 ──────────────────────────────────────────

INSERT INTO bank_requirements (bank_id, ordinal, item, source_url) VALUES
 ((SELECT id FROM banks WHERE name='카카오뱅크'),1,'사기이용계좌가 아니라는 사실을 증명하는 자료 1부','https://www.kakaobank.com/Help/FinanceFraud/DamageReportDocuments'),
 ((SELECT id FROM banks WHERE name='카카오뱅크'),2,'사기이용계좌 명의인의 신분증 사본 1부','https://www.kakaobank.com/Help/FinanceFraud/DamageReportDocuments'),
 ((SELECT id FROM banks WHERE name='카카오뱅크'),3,'명의인 본인서명사실확인서 1부 (주민센터 발급) — 법정서식에 없는 은행 추가 항목','https://www.kakaobank.com/Help/FinanceFraud/DamageReportDocuments'),

 ((SELECT id FROM banks WHERE name='한국씨티은행'),1,'이의제기신청서 (서식 및 작성예시 제공)','https://www.citibank.co.kr/CusFconCnts0500.act'),
 ((SELECT id FROM banks WHERE name='한국씨티은행'),2,'명의인 신분증 사본 (앞면)','https://www.citibank.co.kr/CusFconCnts0500.act'),
 ((SELECT id FROM banks WHERE name='한국씨티은행'),3,'본인서명사실확인서 (최근 3개월 이내 발급분, 영업점 방문 제출 시 불필요)','https://www.citibank.co.kr/CusFconCnts0500.act'),
 ((SELECT id FROM banks WHERE name='한국씨티은행'),4,'객관적인 증빙 자료','https://www.citibank.co.kr/CusFconCnts0500.act'),

 ((SELECT id FROM banks WHERE name='전북은행'),1,'이의제기 신청서','https://www.jbbank.co.kr/TCFF_INFO.act'),
 ((SELECT id FROM banks WHERE name='전북은행'),2,'신분증','https://www.jbbank.co.kr/TCFF_INFO.act'),
 ((SELECT id FROM banks WHERE name='전북은행'),3,'사기이용계좌가 아니라는 사실을 증명하는 자료','https://www.jbbank.co.kr/TCFF_INFO.act'),

 ((SELECT id FROM banks WHERE name='하나은행'),1,'사기이용계좌가 아니라는 사실을 증빙하는 자료 1부','https://image.kebhana.com/cont/customer/customer07/customer0701/customer070106/__icsFiles/afieldfile/2024/08/21/5-08-0246.pdf'),
 ((SELECT id FROM banks WHERE name='하나은행'),2,'사기이용계좌 명의인의 신분증 사본 1부','https://image.kebhana.com/cont/customer/customer07/customer0701/customer070106/__icsFiles/afieldfile/2024/08/21/5-08-0246.pdf'),

 ((SELECT id FROM banks WHERE name='케이뱅크'),1,'사기이용계좌가 아니라는 사실을 증명하는 자료 1부','https://www.kbanknow.com/web/customer/data/list?tab=form&chip=10'),
 ((SELECT id FROM banks WHERE name='케이뱅크'),2,'사기이용계좌 명의인의 신분증 사본 1부','https://www.kbanknow.com/web/customer/data/list?tab=form&chip=10');
