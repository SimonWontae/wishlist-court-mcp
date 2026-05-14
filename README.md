# wishlist-court-mcp

Repository: https://github.com/SimonWontae/wishlist-court-mcp

장바구니 양심 재판 MCP는 사용자의 위시리스트 CSV를 읽고 구매 후보를 "재판"하는 Python MCP 미니 프로젝트입니다. 목적은 실용 쇼핑 앱을 만드는 것이 아니라, LLM이 도구 설명을 보고 어떤 도구를 호출하는지, 좋은 도구와 망가진 도구가 결과를 어떻게 바꾸는지, orchestration 패턴에 따라 비용과 안정성이 어떻게 달라지는지 보여주는 것입니다.

## 1. 프로젝트 소개

이 서버는 `data/wishlist.csv`, `data/owned_items.csv`, `data/budget.json`을 읽어 구매 후보를 판정합니다.

판결은 네 가지입니다.

- `approve`: 구매 승인
- `cooldown`: 냉각기간 후 재검토
- `reject`: 구매 기각
- `replace_only`: 기존 물건 처분 또는 교체 조건부 허용

## 2. 과제 요구사항과의 대응

| 요구사항 | 구현 위치 |
| --- | --- |
| 직접 만든 MCP 서버 | `src/wishlist_court_server.py` |
| 정상 MCP / 망가진 MCP 비교 | `src/wishlist_court_server.py`, `src/broken_wishlist_court_server.py` |
| MCP 없음 / 정상 MCP / 망가진 MCP 프롬프트 | `experiments/prompts/01_no_mcp_prompt.md` ~ `03_broken_mcp_prompt.md` |
| Single / Planner+Executor / Parallel 비교 | `experiments/prompts/04_single_agent_prompt.md` ~ `07_parallel_subagents_prompt.md` |
| 예상 결과 템플릿 | `experiments/expected_outputs/` |
| 발표용 샘플 로그 | `experiments/sample_run_log.md` |

## 3. 왜 이 병목을 골랐는가

장바구니 판단은 LLM이 그럴듯한 조언을 하기 쉬운 작업입니다. 하지만 실제로는 보유품, 남은 예산, 구매 사유, 긴급도 같은 작은 데이터가 판결을 크게 바꿉니다.

따라서 이 프로젝트는 MCP의 효과를 관찰하기 좋습니다.

- 도구가 없으면 모델은 일반 상식으로 답한다.
- 정상 도구가 있으면 실제 데이터 기반 판단이 가능하다.
- 망가진 도구가 있으면 모델이 잘못된 설명과 결과를 따라갈 수 있다.
- orchestration을 바꾸면 누락, 비용, 병합 부담이 달라진다.

## 4. MCP 도구 목록

| 도구 | 역할 |
| --- | --- |
| `list_wishlist_items` | 위시리스트 CSV 전체를 읽어 구매 후보 목록을 반환 |
| `get_owned_items_by_category` | 특정 카테고리의 기존 보유품을 반환 |
| `get_budget_status` | 월 예산, 이번 달 지출, 남은 예산을 반환 |
| `judge_purchase` | 예산, 중복, 충동구매 위험을 바탕으로 판결 |
| `save_verdict_report` | output 폴더에 markdown 보고서 저장 |

## 5. 정상 서버 실행법

Python 3.10 이상을 권장합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/wishlist_court_server.py
```

환경에 `python` 별칭이 없으면 `python3`로 실행하면 됩니다.
Ubuntu/Debian에서 `externally-managed-environment` 오류가 나면 시스템 Python에 직접 설치하지 말고 위처럼 가상환경을 사용하세요.

정상 서버는 실제 CSV/JSON 데이터를 사용합니다. 보유품 중복과 남은 예산을 보수적으로 반영합니다.

## 6. 망가진 서버 실행법

```bash
source .venv/bin/activate
python src/broken_wishlist_court_server.py
```

broken server는 Part 2 실패 실험용입니다. 정상 서버와 같은 tool 이름을 갖지만 일부 도구가 의도적으로 잘못 동작합니다.

- `judge_purchase` 설명이 소비를 긍정적으로 추천하도록 작성되어 있다.
- `get_owned_items_by_category`가 항상 빈 목록을 반환한다.
- `get_budget_status`가 실제보다 낙관적인 남은 예산을 반환한다.
- `duplicate_risk`와 `budget_risk`가 낮게 보고된다.

## 7. Hermes 등록 예시

아래 `/ABSOLUTE/PATH/wishlist-court-mcp`는 실제 프로젝트 절대경로로 바꾸면 됩니다.

```bash
hermes mcp add wishlist-court "python /ABSOLUTE/PATH/wishlist-court-mcp/src/wishlist_court_server.py"
hermes mcp add wishlist-court-broken "python /ABSOLUTE/PATH/wishlist-court-mcp/src/broken_wishlist_court_server.py"
hermes mcp list
```

현재 워크스페이스 기준 예시는 다음과 같습니다.

```bash
hermes mcp add wishlist-court --command /home/ubtwt/Projects/wishilist-court-mcp/.venv/bin/python --args /home/ubtwt/Projects/wishilist-court-mcp/src/wishlist_court_server.py
hermes mcp add wishlist-court-broken --command /home/ubtwt/Projects/wishilist-court-mcp/.venv/bin/python --args /home/ubtwt/Projects/wishilist-court-mcp/src/broken_wishlist_court_server.py
```

sandbox 안에서는 기본 Hermes home 대신 프로젝트 내부 설정을 사용할 수 있습니다.

```bash
export HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes
hermes mcp list
```

이 프로젝트에는 sandbox에서 등록한 결과가 `.hermes/config.yaml`에 남아 있습니다. 다만 sandbox의 stdio 제한 때문에 `hermes mcp test`는 타임아웃될 수 있으므로, 일반 터미널에서 다시 테스트하는 것을 권장합니다.

## 8. 실험 1: MCP 없음 vs 정상 MCP vs 망가진 MCP

프롬프트:

- `experiments/prompts/01_no_mcp_prompt.md`
- `experiments/prompts/02_good_mcp_prompt.md`
- `experiments/prompts/03_broken_mcp_prompt.md`

측정 항목:

- 작업 완료 여부
- 소요 시간
- 토큰 사용량
- tool call sequence
- 항목별 판결 정확도
- 보유품 중복과 예산 초과 반영 여부

예상 관찰:

- MCP 없음: 위시리스트만 보고 일반적인 소비 조언을 한다.
- 정상 MCP: HHKB 키보드는 keyboard 보유품 2개와 예산 초과 때문에 기각 쪽으로 간다.
- 망가진 MCP: 보유품이 없다고 반환되므로 중복 위험이 낮게 나오고, 구매 승인 비율이 올라간다.

결과 기록 템플릿:

- `experiments/expected_outputs/comparison_table.md`
- `experiments/expected_outputs/failure_log_analysis.md`

## 9. 실험 2: Orchestration 3패턴 비교

프롬프트:

- Single Agent: `experiments/prompts/04_single_agent_prompt.md`
- Planner: `experiments/prompts/05_planner_prompt.md`
- Executor: `experiments/prompts/06_executor_prompt.md`
- Parallel sub-agent: `experiments/prompts/07_parallel_subagents_prompt.md`

비교 관점:

- Single Agent는 가장 단순하고 토큰 효율이 좋을 가능성이 높다.
- Planner+Executor는 호출 순서와 체크리스트가 명확해 누락이 줄 수 있다.
- Parallel sub-agent는 예산, 중복, 충동구매 관점을 분리해 발표용으로 좋지만 토큰과 병합 비용이 증가한다.

결과 기록 템플릿:

- `experiments/expected_outputs/orchestration_benchmark.md`

### Orchestration 비교 실험

이 프로젝트는 동일한 장바구니 판결 작업을 세 가지 구조로 비교했다.

1. Single Agent
2. Planner + Executor
3. Parallel sub-agent

실험은 `experiments/run_orchestration_experiments.py`로 재현할 수 있다.

```bash
.venv/bin/python experiments/run_orchestration_experiments.py
```

결과는 `output/orchestration_experiment_summary.md`와 `output/orchestration_experiment_metrics.json`에 저장된다.

현재 deterministic local runner 기준 simulation estimate:

| 패턴 | simulated tokens | simulated latency | MCP/tool 호출 수 | 결과 퀄리티 |
| --- | ---: | ---: | ---: | ---: |
| Single Agent | 4,200 | 18.2s | 12 | 4/5 |
| Planner+Executor | 6,100 | 27.5s | 12 | 5/5 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | 4/5 |

주의: 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 local deterministic runner 기준 simulation estimate다. 실제 발표에서는 이 한계를 밝힌다.

## 10. 30초 데모 영상 촬영 시나리오

1. 프로젝트 파일 트리를 보여준다.
2. `data/wishlist.csv`, `data/owned_items.csv`, `data/budget.json`을 빠르게 보여준다.
3. Hermes에서 정상 MCP 서버가 등록된 화면을 보여준다.
4. `02_good_mcp_prompt.md`를 실행해 tool call이 발생하는 장면을 보여준다.
5. 생성된 `output/good_mcp_verdict.md`를 보여준다.
6. 같은 작업을 broken MCP로 실행해 판결이 달라지는 장면을 보여준다.
7. 정상/망가진 결과의 approve/reject 차이를 강조한다.

## 11. 발표 슬라이드 구성안

1. 문제 정의: LLM의 소비 판단은 데이터가 없으면 그럴듯하지만 불안정하다.
2. 프로젝트 구조: CSV/JSON, 정상 MCP, broken MCP, 실험 프롬프트.
3. MCP 도구 설명: 어떤 도구를 언제 호출하게 설계했는가.
4. 실험 1 결과: MCP 없음 vs 정상 MCP vs 망가진 MCP.
5. 실패 주입 분석: 잘못된 description과 잘못된 반환값의 영향.
6. 실험 2 결과: Single / Planner+Executor / Parallel sub-agent.
7. 결론: tool description과 orchestration이 결과 품질과 비용을 바꾼다.

## 12. 한계와 회고

이 프로젝트는 완벽한 쇼핑 추천 앱이 아닙니다. 가격 변동, 실제 계좌 잔고, 장기 소비 패턴, 사용자 가치관은 반영하지 않습니다. 데이터도 작고 규칙 기반 판정입니다.

하지만 과제 목적에는 맞습니다. 작은 데이터와 단순한 도구만으로도 MCP 도구 설명, 도구 품질, orchestration 방식이 LLM 결과를 크게 바꾼다는 점을 보여줄 수 있습니다.

## 재현 방법

전체 로컬 결과는 아래 명령으로 재생성할 수 있습니다.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m py_compile src/*.py experiments/*.py
.venv/bin/python experiments/run_local_experiments.py
.venv/bin/python experiments/run_orchestration_experiments.py
```

정상 MCP와 broken MCP 보고서만 다시 만들려면 아래 명령을 실행합니다.

```bash
.venv/bin/python experiments/generate_hermes_good_mcp_verdict.py
.venv/bin/python experiments/generate_hermes_broken_mcp_verdict.py
```

## 다음에 해야 할 일

1. `pip install -r requirements.txt`로 의존성을 설치한다.
2. Hermes에 정상 서버와 broken 서버를 등록한다.
3. `experiments/prompts/`의 프롬프트를 순서대로 실행한다.
4. 결과 수치와 캡처를 `experiments/expected_outputs/` 문서에 채운다.
5. 발표자료에는 정상 MCP와 broken MCP의 같은 항목 판결 차이를 중심으로 넣는다.
