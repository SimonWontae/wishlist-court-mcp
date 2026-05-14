# Orchestration 실험 3: Parallel sub-agent

## 세 sub-agent 역할

- Agent A 예산 검사관: 가격과 남은 예산만 보고 budget_risk 판단
- Agent B 중복 구매 검사관: 카테고리별 보유품만 보고 duplicate_risk 판단
- Agent C 충동구매 검사관: 구매 사유와 긴급도만 보고 impulse_risk 판단
- Synthesizer: 세 관점을 종합해 최종 판결 작성

## sub-agent별 주요 관찰

- 예산 검사관: HHKB 키보드, 에어팟 맥스, 아이패드 미니는 남은 예산 120,000원을 초과한다.
- 중복 구매 검사관: keyboard 카테고리는 양호한 보유품이 2개라 중복 위험이 높다.
- 충동구매 검사관: 기계식 계산기는 '그냥 예뻐서 사고 싶음'과 낮은 긴급도로 충동구매 위험이 높다.

## 최종 항목별 판결

| 물건 | 예산 위험 | 중복 위험 | 충동 위험 | 최종 판결 | Synthesizer 근거 |
| --- | --- | --- | --- | --- | --- |
| HHKB 키보드 | high | high | high | reject | HHKB 키보드은 남은 예산을 초과하고 같은 카테고리의 양호한 보유품이 많아 기각합니다. |
| 에어팟 맥스 | high | medium | low | cooldown | 에어팟 맥스은 예산 초과 위험이 커서 이번 달 구매는 보류합니다. |
| 아이패드 미니 | high | medium | medium | cooldown | 아이패드 미니은 예산 초과 위험이 커서 이번 달 구매는 보류합니다. |
| USB-C 허브 | low | low | low | approve | USB-C 허브은 기존 accessory 품목 상태가 나쁘고 긴급도가 높아 구매를 승인합니다. |
| 기계식 계산기 | medium | none | high | cooldown | 기계식 계산기은 충동구매 신호가 강하므로 냉각기간 후 다시 판단합니다. |

## 장점

- 예산, 중복, 충동구매 관점이 분리되어 설명력이 좋다.
- 각 sub-agent 산출물을 발표 자료로 보여주기 쉽다.
- Synthesizer가 충돌하는 근거를 비교할 수 있다.

## 한계

- 같은 데이터를 여러 관점에서 반복 처리하므로 토큰 비용이 가장 크다.
- sub-agent 산출물을 합치는 병합 비용과 충돌 처리 비용이 생긴다.
- 이 프로젝트처럼 데이터가 작은 작업에는 실용 효율이 낮다.

## 회고

관점이 분리되었기 때문에 reasoning은 풍부하지만, 문서와 token cost가 증가했다. 최종 판결은 core.py 판정과 크게 어긋나지 않게 유지했다.

## Simulation Metrics

- tool call count: 16
- simulated latency: 23.4 seconds
- simulated token count: 8900
- failure layer: synthesis_overhead
- quality score: 4 / 5

주의: 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다.
