# Orchestration 실험 2: Planner + Executor

## Planner 계획 요약

- Planner는 도구를 직접 호출하지 않고 실행 순서와 판정 기준을 먼저 고정한다.
- Executor는 이 계획에 따라 위시리스트, 예산, 보유품, 판정 단계를 빠뜨리지 않고 수행한다.

## Executor 실행 결과

## 예산 정보

- 월 자유 예산: 300,000 KRW
- 이번 달 이미 쓴 금액: 180,000 KRW
- 남은 예산: 120,000 KRW

## 항목별 판결

| 물건 | 가격 | 카테고리 | 보유품 확인 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| HHKB 키보드 | 420,000 KRW | keyboard | 키크론 키보드(good, weekly), 로지텍 MX Keys(good, daily) | reject | high | high | high | HHKB 키보드은 남은 예산을 초과하고 같은 카테고리의 양호한 보유품이 많아 기각합니다. |
| 에어팟 맥스 | 790,000 KRW | audio | 에어팟 프로(good, daily) | cooldown | medium | high | low | 에어팟 맥스은 예산 초과 위험이 커서 이번 달 구매는 보류합니다. |
| 아이패드 미니 | 850,000 KRW | tablet | 아이패드 프로(good, weekly) | cooldown | medium | high | medium | 아이패드 미니은 예산 초과 위험이 커서 이번 달 구매는 보류합니다. |
| USB-C 허브 | 39,000 KRW | accessory | USB-C 허브 구형(bad, daily) | approve | low | low | low | USB-C 허브은 기존 accessory 품목 상태가 나쁘고 긴급도가 높아 구매를 승인합니다. |
| 기계식 계산기 | 120,000 KRW | toy | 없음 | cooldown | none | medium | high | 기계식 계산기은 충동구매 신호가 강하므로 냉각기간 후 다시 판단합니다. |

## Single Agent 대비 차이

- 최종 판결은 정상 core 판정과 동일하지만, 실행 전에 체크리스트가 고정되어 누락 위험이 낮다.
- Planner 문서가 추가되므로 토큰과 시간이 Single Agent보다 증가한다.

## 장점

- 예산, 중복, 충동구매 기준을 명시적으로 분리한다.
- Executor가 계획을 따라가므로 실험 재현성이 좋다.
- 이번 과제처럼 평가 기준을 설명해야 하는 작업에서 가장 안정적이다.

## 한계

- Planner 단계 자체가 추가 비용이다.
- 작업이 매우 작을 때는 Single Agent보다 과할 수 있다.

## Simulation Metrics

- tool call count: 12
- simulated latency: 27.5 seconds
- simulated token count: 6100
- failure layer: none
- quality score: 5 / 5

주의: 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다.
