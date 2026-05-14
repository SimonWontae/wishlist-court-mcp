# Orchestration 비교 실험 요약

## 1. 실험 목적

동일한 장바구니 양심 재판 작업을 Single Agent, Planner+Executor, Parallel sub-agent 구조로 나누어 비교한다. 목표는 실제 multi-agent framework 구현이 아니라, reasoning 구조와 비용 추정치가 어떻게 달라지는지 보여주는 것이다.

## 2. 세 orchestration 패턴

- Single Agent: 하나의 흐름에서 데이터 조회, 예산 확인, 보유품 확인, 판정, 보고서 저장을 모두 수행한다.
- Planner+Executor: Planner가 도구 호출 계획과 판정 체크리스트를 먼저 만들고, Executor가 그 계획을 따라 실행한다.
- Parallel sub-agent: 예산 검사관, 중복 구매 검사관, 충동구매 검사관이 관점을 나누고 Synthesizer가 최종 판결을 만든다.

## 3. 결과 비교표

| 패턴 | simulated token count | simulated latency | tool call count | failure layer | quality score | 요약 |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Single Agent | 4,200 | 18.2s | 12 | none | 4/5 | 가장 빠르고 단순한 baseline |
| Planner+Executor | 6,100 | 27.5s | 12 | none | 5/5 | 기준을 먼저 고정해 가장 안정적 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | synthesis_overhead | 4/5 | 설명력은 좋지만 병합 비용이 큼 |

## 4. 핵심 관찰

- Single Agent는 토큰과 절차가 가장 적지만 체크리스트 누락 위험이 있다.
- Planner+Executor는 토큰과 시간이 늘지만 판정 기준을 먼저 고정해 누락 가능성을 줄인다.
- Parallel sub-agent는 세 관점의 설명이 가장 풍부하지만, 작은 작업에서는 토큰과 병합 비용이 과하다.
- 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다.

## 5. 최종 회고

이 장바구니 양심 재판 작업은 예산, 중복, 충동구매라는 세 기준으로 자연스럽게 분해된다. 따라서 Parallel sub-agent 구조는 설명력은 좋았지만, 실제 작업 규모가 작아서 비용 대비 효율은 낮았다. Single Agent는 빠르고 단순했지만 체크리스트 누락 위험이 있다. Planner+Executor는 토큰과 시간이 약간 늘어도 판정 기준을 먼저 고정하기 때문에 이번 과제에는 가장 안정적인 구조였다.
