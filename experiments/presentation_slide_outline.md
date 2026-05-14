# 발표 슬라이드 초안

## 1. 제목

장바구니 양심 재판 MCP

부제:

- Tool description, broken tool, orchestration이 LLM 판단을 어떻게 바꾸는가

발표 포인트:

- 쇼핑 추천 앱이 아니라 MCP tool-use 실험 프로젝트임을 먼저 밝힌다.

## 2. 과제 목표와 실험 질문

핵심 질문:

- LLM은 tool description만 보고 적절한 도구를 호출하는가?
- 정상 MCP가 있으면 결과 정확도가 좋아지는가?
- 망가진 MCP가 있으면 잘못된 판단으로 유도되는가?
- Single / Planner+Executor / Parallel sub-agent 중 어떤 구조가 적합한가?

넣을 이미지:

- 프로젝트 파일 트리 캡처

## 3. 프로젝트 구조

구성:

- `data/wishlist.csv`: 구매 후보
- `data/owned_items.csv`: 기존 보유품
- `data/budget.json`: 월 예산
- `src/wishlist_court_server.py`: 정상 MCP
- `src/broken_wishlist_court_server.py`: 망가진 MCP
- `experiments/prompts/`: 실험 프롬프트
- `output/`: 실행 결과 보고서

발표 포인트:

- 복잡한 UI나 DB 없이 MCP tool-use만 관찰하도록 작게 만들었다.

## 4. MCP 도구 설계

도구 목록:

- `list_wishlist_items`
- `get_owned_items_by_category`
- `get_budget_status`
- `judge_purchase`
- `save_verdict_report`

강조할 점:

- docstring에 "언제 호출해야 하는지"를 명시했다.
- `judge_purchase`는 예산, 중복, 충동구매 위험을 합쳐 판결한다.

넣을 코드 캡처:

- 정상 서버 `judge_purchase` docstring
- broken 서버 `judge_purchase` docstring

## 5. 실험 1 결과

비교:

| 조건 | 핵심 결과 |
| --- | --- |
| MCP 없음 | 보유품과 예산을 몰라 보수적이지만 근거가 약함 |
| 정상 MCP | HHKB reject, USB-C 허브 approve 등 데이터 기반 판결 |
| 망가진 MCP | 5개 항목 모두 approve로 소비 추천 편향 |

넣을 자료:

- `experiments/expected_outputs/comparison_table.md`
- `output/good_mcp_verdict.md`
- `output/broken_mcp_verdict.md`

발표 포인트:

- 같은 작업이라도 도구 품질이 결과를 크게 바꾼다.

## 6. 실험 2 결과: Orchestration 3패턴 비교

비교표:

| 패턴 | 장점 | 단점 | 결론 |
|---|---|---|---|
| Single Agent | 빠르고 단순 | 기준 누락 가능 | baseline |
| Planner+Executor | 기준 고정, 누락 감소 | 토큰/시간 증가 | 가장 안정적 |
| Parallel sub-agent | 관점 분리, 설명력 좋음 | 머지 비용, 토큰 증가 | 작은 작업엔 과함 |

Metrics:

| 패턴 | simulated tokens | simulated latency | tool calls | quality |
| --- | ---: | ---: | ---: | ---: |
| Single Agent | 4,200 | 18.2s | 12 | 4/5 |
| Planner+Executor | 6,100 | 27.5s | 12 | 5/5 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | 4/5 |

넣을 자료:

- `experiments/expected_outputs/orchestration_benchmark.md`
- `output/orchestration_experiment_summary.md`
- `output/orchestration_experiment_metrics.json`

발표 포인트:

- Single Agent는 빠르고 단순하지만 체크리스트 누락 위험이 있다.
- Planner+Executor는 기준을 먼저 고정하므로 이번 과제에서 가장 안정적이다.
- Parallel은 설명력은 좋지만 작은 작업에는 토큰과 병합 비용이 과하다.

## 7. 결론과 한계

결론:

- tool description은 LLM 행동을 바꾼다.
- 정상 도구는 결과 품질을 올린다.
- 망가진 도구는 구매 추천 편향을 만든다.
- orchestration 방식은 비용, 안정성, 병합 부담을 바꾼다.

한계:

- 실제 Hermes 실행 토큰 수는 현재 환경에서 미측정이다.
- 데이터가 작고 규칙 기반이다.
- 실제 소비 추천 앱이 아니라 MCP 실험용 미니 프로젝트다.

마무리 문장:

- 작은 프로젝트지만 MCP 도구의 품질과 설명이 LLM 판단에 주는 영향을 선명하게 보여준다.
