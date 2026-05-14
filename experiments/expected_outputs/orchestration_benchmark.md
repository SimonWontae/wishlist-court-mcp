# Orchestration 비교표

이 표는 `experiments/run_orchestration_experiments.py`의 deterministic local runner 결과를 기준으로 작성했다. 실제 LLM 토큰 합계와 총 레이턴시는 Hermes/Codex 실행 후 교체할 수 있다.

| 패턴 | 토큰 합계 | 총 레이턴시 | MCP 호출 수 | 실패 발생 레이어 | 결과 퀄리티 | 회고 |
| -- | ----: | -----: | -------: | --------- | -----: | -- |
| Single Agent | 4,200 | 18.2s | 12 | none | 4 | 가장 단순하고 빠른 baseline이지만 체크리스트 누락 위험이 있음 |
| Planner+Executor | 6,100 | 27.5s | 12 | none | 5 | 판정 기준을 먼저 고정해 이번 과제에서 가장 안정적 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | synthesis_overhead | 4 | 예산/중복/충동 관점 분리는 좋지만 병합 비용과 토큰 비용이 큼 |

실제 Hermes/OpenRouter 토큰 로그를 직접 측정하지 못한 경우, 이 수치는 deterministic local runner 기준의 simulation estimate다. 발표에서는 이 한계를 명확히 밝히고, 비교의 핵심은 절대값이 아니라 패턴별 상대적 차이라고 설명한다.

## 생성된 보고서

- `output/orchestration_single_agent_verdict.md`
- `output/orchestration_planner_executor_plan.md`
- `output/orchestration_planner_executor_verdict.md`
- `output/orchestration_parallel_budget_agent.md`
- `output/orchestration_parallel_duplicate_agent.md`
- `output/orchestration_parallel_impulse_agent.md`
- `output/orchestration_parallel_synthesized_verdict.md`
- `output/orchestration_experiment_summary.md`
- `output/orchestration_experiment_metrics.json`

## 최종 회고

이 작업은 데이터 조회와 판단 기준이 비교적 단순하므로 Single Agent가 토큰 효율은 가장 좋다. 다만 예산, 중복, 충동구매라는 세 기준 중 하나를 누락할 위험이 있다.

Planner+Executor는 토큰 비용과 레이턴시가 늘지만, 판정 기준을 먼저 고정하기 때문에 누락 가능성을 줄인다. 과제 발표에서는 이 구조가 가장 안정적인 orchestration이라는 결론을 내리기 좋다.

Parallel sub-agent는 예산, 중복, 충동구매를 분리해 설명하므로 발표용으로 가장 풍부하다. 그러나 같은 데이터를 여러 관점에서 반복 처리하고 Synthesizer 병합 단계가 필요하므로, 이 작은 작업에는 비용 대비 효율이 낮다.

## 실제 Hermes 실행 시 보완할 항목

- 각 패턴별 실제 토큰 사용량
- 각 패턴별 wall-clock 레이턴시
- 실제 tool call sequence 캡처
- Planner 결과와 Executor 결과의 불일치 여부
- Parallel sub-agent 병합 과정에서 발생한 판단 충돌
