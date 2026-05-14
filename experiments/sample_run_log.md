# 샘플 실행 로그

이 파일은 실제 실험 전에 발표 자료 초안을 만들기 위한 예시 로그다.
실제 Hermes 또는 Codex 실행 후 수치와 캡처를 교체한다.

## 환경

- 프로젝트: wishlist-court-mcp
- 정상 서버: `python src/wishlist_court_server.py`
- 망가진 서버: `python src/broken_wishlist_court_server.py`
- 데이터 기준일: 2026-05

## 정상 MCP 예상 흐름

1. `list_wishlist_items` 호출
2. `get_budget_status` 호출
3. 항목별 `get_owned_items_by_category` 호출
4. 항목별 `judge_purchase` 호출
5. `save_verdict_report("good_mcp_verdict.md", content)` 호출

## 정상 MCP 예상 판결 요약

| 물건 | 예상 판결 | 핵심 근거 |
| --- | --- | --- |
| HHKB 키보드 | reject | 예산 초과, keyboard 보유품 2개 |
| 에어팟 맥스 | cooldown 또는 reject | 예산 초과, audio 보유품 있음 |
| 아이패드 미니 | cooldown 또는 reject | 예산 초과, tablet 보유품 있음 |
| USB-C 허브 | approve | 기존 허브 상태 bad, 긴급도 high, 가격이 남은 예산 이내 |
| 기계식 계산기 | cooldown | 충동구매 신호, 긴급도 low |

## 망가진 MCP 예상 흐름

- 보유품 조회 결과가 빈 목록으로 나와 중복 위험이 낮아진다.
- 예산이 낙관적으로 반환되어 고가 항목이 덜 위험해 보인다.
- `judge_purchase` 설명이 소비 추천 편향을 유도한다.

## 발표 메모

- 같은 프롬프트라도 도구 설명과 반환값이 바뀌면 최종 판단이 달라진다는 점을 강조한다.
- 이 프로젝트의 목적은 쇼핑 추천 정확도가 아니라 MCP tool-use의 민감도를 보여주는 것이다.

## Orchestration local experiment

Command:

```bash
.venv/bin/python experiments/run_orchestration_experiments.py
```

Generated files:

* output/orchestration_single_agent_verdict.md
* output/orchestration_planner_executor_plan.md
* output/orchestration_planner_executor_verdict.md
* output/orchestration_parallel_budget_agent.md
* output/orchestration_parallel_duplicate_agent.md
* output/orchestration_parallel_impulse_agent.md
* output/orchestration_parallel_synthesized_verdict.md
* output/orchestration_experiment_summary.md
* output/orchestration_experiment_metrics.json

Success message:

```text
Orchestration local experiment completed.
Generated 9 output files under output/.
```

Metrics summary:

| 패턴 | simulated tokens | simulated latency | tool calls | quality |
| --- | ---: | ---: | ---: | ---: |
| Single Agent | 4,200 | 18.2s | 12 | 4/5 |
| Planner+Executor | 6,100 | 27.5s | 12 | 5/5 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | 4/5 |
