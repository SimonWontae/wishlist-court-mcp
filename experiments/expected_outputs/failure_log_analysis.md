# 실패 로그 분석

이 문서는 `broken_wishlist_court_server.py`와 로컬 실험 결과를 바탕으로 작성했다. 실제 Hermes 실행 시에는 tool call 화면 캡처와 모델 응답 문장을 추가하면 된다.

## 실패 주입 방식

- `broken_wishlist_court_server.py`의 `judge_purchase` docstring을 소비 추천 편향으로 작성했다.
- `get_owned_items_by_category`는 실제 보유품이 있어도 빈 목록을 반환한다.
- `get_budget_status`는 남은 예산을 실제보다 크게 반환한다.
- `judge_purchase`는 `duplicate_risk`를 항상 low로 반환한다.
- `judge_purchase`는 남은 예산이 부족해도 `budget_risk`를 high로 올리지 않는다.
- 최종 판결은 reject가 거의 나오지 않도록 approve 중심으로 반환한다.

## 에이전트가 도구를 호출했는가

로컬 deterministic 실행 기준:

- 위시리스트 조회: 재현함
- 보유품 조회: broken 서버에서는 빈 목록 반환으로 재현함
- 예산 조회: broken 서버에서는 낙관적 예산 반환으로 재현함
- 판결 도구 호출: 5개 항목 모두 재현함
- 보고서 저장: `output/broken_mcp_verdict.md` 생성 완료

실제 Hermes 실행은 현재 환경에 Hermes CLI가 없어 미수행이다.

## 잘못된 description의 영향

broken `judge_purchase` docstring은 다음 방향으로 모델 행동을 유도한다.

- 소비를 "행복도"와 연결한다.
- 망설이는 상황에서 긍정적인 이유를 찾게 한다.
- 중복과 예산 위험보다 구매 정당화를 앞세우게 한다.

로컬 실행 결과, broken MCP 조건에서는 5개 항목 모두 approve가 되었다. 정상 MCP에서는 HHKB 키보드가 reject, 에어팟 맥스와 아이패드 미니가 cooldown으로 처리되므로 차이가 분명하다.

## 보유품 중복 확인 실패 여부

실패가 발생한다.

- keyboard 카테고리에는 키크론 키보드와 로지텍 MX Keys가 있지만 broken 서버는 빈 목록을 반환한다.
- audio 카테고리에는 에어팟 프로가 있지만 broken 서버는 이를 반영하지 않는다.
- tablet 카테고리에는 아이패드 프로가 있지만 broken 서버는 이를 반영하지 않는다.
- accessory 카테고리의 USB-C 허브 구형도 빈 목록으로 처리되어 교체 필요성의 세부 근거가 약해진다.

## 예산 초과 판단 실패 여부

실패가 발생한다.

실제 예산:

- 월 자유 예산: 300,000원
- 이미 쓴 금액: 180,000원
- 남은 예산: 120,000원

정상 MCP에서는 420,000원, 790,000원, 850,000원 항목이 budget_risk high로 처리된다. broken MCP에서는 같은 항목들이 approve로 처리되어 예산 초과 판단이 무너진다.

## 환각 또는 긍정 편향 발생 여부

긍정 편향이 발생한다.

- 고가 항목이 예산 초과임에도 구매 만족도 중심으로 설명된다.
- 중복 보유품이 있음에도 duplicate_risk가 low로 보고된다.
- reject가 사라지고 approve가 과도하게 증가한다.

## 발표에서 보여줄 캡처 포인트

- 정상 MCP 결과: `output/good_mcp_verdict.md`
- 망가진 MCP 결과: `output/broken_mcp_verdict.md`
- 정상 MCP에서 HHKB 키보드가 reject가 되는 부분
- broken MCP에서 같은 HHKB 키보드가 approve가 되는 부분
- `broken_wishlist_court_server.py`의 거짓 docstring
- `get_owned_items_by_category`가 빈 목록을 반환하는 코드
