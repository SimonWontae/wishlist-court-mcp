# Orchestration 실험 1: Single Agent

## 실행 구조

Single Agent는 한 흐름에서 위시리스트 조회, 예산 확인, 카테고리별 보유품 확인, 판정, 보고서 저장을 모두 수행한다.
작업이 단순할 때 가장 빠르고 비용이 낮은 baseline이다.

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

## 장점

- 흐름이 단순하고 구현 비용이 낮다.
- 문맥 전환과 병합 비용이 거의 없다.
- 이 프로젝트처럼 데이터가 작은 경우 토큰 효율이 좋다.

## 한계

- 명시적 체크리스트가 없으면 예산, 중복, 충동구매 기준 중 하나를 빠뜨릴 수 있다.
- 판단 근거를 분리해 설명하는 힘은 Planner나 Parallel 구조보다 약하다.

## Simulation Metrics

- tool call count: 12
- simulated latency: 18.2 seconds
- simulated token count: 4200
- failure layer: none
- quality score: 4 / 5

주의: 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다.
