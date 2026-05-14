# MCP 조건 비교표

이 표는 `experiments/run_local_experiments.py`로 실행한 로컬 deterministic 결과를 기준으로 작성했다. Hermes CLI가 현재 환경에 설치되어 있지 않아 실제 LLM 토큰 사용량은 미측정이다.

| 조건 | 작업 완료 | 소요 시간 | 토큰 사용량 | 결과 정확도 | 에이전트 행동 | 관찰 |
| --- | --- | ---: | ---: | ---: | --- | --- |
| MCP 없음 | 완료 | 0.67ms | 미측정 | 낮음 | 도구 호출 없이 위시리스트 정보만 보고 보수적으로 판단 | 보유품과 실제 예산을 몰라 duplicate_risk, budget_risk가 unknown으로 남음 |
| 정상 MCP | 완료 | 0.73ms | 미측정 | 높음 | 위시리스트, 보유품, 예산, 판결 도구를 순서대로 사용한 것으로 재현 | HHKB는 reject, USB-C 허브는 approve로 데이터 기반 차이가 드러남 |
| 망가진 MCP | 완료 | 0.30ms | 미측정 | 낮음 | broken tool의 낙관적 결과를 따른 것으로 재현 | 5개 항목 모두 approve가 되어 구매 추천 편향이 발생 |

## 판결 분포

| 조건 | approve | cooldown | reject | replace_only |
| --- | ---: | ---: | ---: | ---: |
| MCP 없음 | 1 | 4 | 0 | 0 |
| 정상 MCP | 1 | 3 | 1 | 0 |
| 망가진 MCP | 5 | 0 | 0 | 0 |

## 정상 MCP와 망가진 MCP의 예상 차이

정상 MCP는 위시리스트, 보유품, 예산 데이터를 직접 조회하므로 HHKB 키보드처럼 이미 keyboard 카테고리 보유품이 2개 있는 항목을 중복 위험 high로 판단한다. 또한 남은 예산이 120,000원뿐이므로 에어팟 맥스와 아이패드 미니 같은 고가 항목은 예산 위험 high로 판단한다.

망가진 MCP는 `get_owned_items_by_category`가 빈 목록을 반환하고 `judge_purchase`가 중복 위험을 항상 low로 낮춰 말한다. 로컬 실행 결과에서도 모든 항목이 approve가 되어 정상 MCP와 뚜렷하게 다른 결론이 나왔다.

MCP 없음 조건은 모델이 일반 상식으로는 합리적인 답을 줄 수 있지만, 실제 보유품과 예산을 모르면 정확한 기각 근거를 만들기 어렵다.

## 생성된 보고서

- `output/no_mcp_verdict.md`
- `output/good_mcp_verdict.md`
- `output/broken_mcp_verdict.md`
- `output/local_experiment_summary.md`
