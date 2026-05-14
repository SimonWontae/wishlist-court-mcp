# wishlist-court-mcp 인수인계 문서

이 문서는 다른 ChatGPT/Codex 세션에서 현재 프로젝트 상태를 빠르게 이해하고, 남은 작업을 재논의하기 위한 프롬프트 겸 상태 보고서다.

## 1. 프로젝트 개요

프로젝트 이름:

- `wishlist-court-mcp`

주제:

- 장바구니 양심 재판 MCP
- 사용자의 위시리스트 CSV를 읽고 구매 후보를 "재판"한다.
- 이미 비슷한 물건을 보유했는지, 예산을 초과하는지, 충동구매 위험이 있는지 판단한다.
- 판결은 `approve`, `cooldown`, `reject`, `replace_only` 중 하나다.

과제 목적:

- 완성형 쇼핑 앱이 아니라 MCP tool-use 실험용 미니 프로젝트다.
- 정상 MCP / 망가진 MCP / MCP 없음 조건을 비교한다.
- Single Agent / Planner+Executor / Parallel sub-agent orchestration을 비교한다.
- tool description과 tool quality가 LLM 판단을 어떻게 바꾸는지 보여준다.

## 2. 현재 파일 구조

현재 주요 파일은 다음과 같다.

```text
wishlist-court-mcp/
├── README.md
├── HANDOFF_STATUS.md
├── requirements.txt
├── data/
│   ├── wishlist.csv
│   ├── owned_items.csv
│   └── budget.json
├── src/
│   ├── __init__.py
│   ├── wishlist_court_server.py
│   ├── broken_wishlist_court_server.py
│   ├── core.py
│   └── paths.py
├── experiments/
│   ├── prompts/
│   │   ├── 01_no_mcp_prompt.md
│   │   ├── 02_good_mcp_prompt.md
│   │   ├── 03_broken_mcp_prompt.md
│   │   ├── 04_single_agent_prompt.md
│   │   ├── 05_planner_prompt.md
│   │   ├── 06_executor_prompt.md
│   │   └── 07_parallel_subagents_prompt.md
│   ├── expected_outputs/
│   │   ├── comparison_table.md
│   │   ├── failure_log_analysis.md
│   │   └── orchestration_benchmark.md
│   ├── hermes_sandbox_registration.md
│   ├── presentation_slide_outline.md
│   ├── remaining_work_plan.md
│   ├── run_local_experiments.py
│   └── sample_run_log.md
├── output/
│   ├── no_mcp_verdict.md
│   ├── good_mcp_verdict.md
│   ├── broken_mcp_verdict.md
│   ├── single_agent_verdict.md
│   ├── planner_executor_verdict.md
│   ├── parallel_subagents_verdict.md
│   ├── local_experiment_summary.md
│   └── local_experiment_metrics.json
└── .hermes/
    └── config.yaml
```

## 3. 구현 완료 상태

완료된 것:

- 정상 MCP 서버 구현 완료: `src/wishlist_court_server.py`
- 망가진 MCP 서버 구현 완료: `src/broken_wishlist_court_server.py`
- 핵심 판정 로직 구현 완료: `src/core.py`
- 경로 상수 구현 완료: `src/paths.py`
- 샘플 데이터 작성 완료: `data/`
- 실험 프롬프트 7종 작성 완료: `experiments/prompts/`
- expected outputs 문서 작성 및 로컬 실행 결과 반영 완료
- 로컬 실험 러너 작성 완료: `experiments/run_local_experiments.py`
- output 보고서 생성 완료
- 발표 슬라이드 초안 작성 완료: `experiments/presentation_slide_outline.md`
- 남은 작업 기획서 작성 완료: `experiments/remaining_work_plan.md`
- Hermes sandbox 등록 기록 작성 완료: `experiments/hermes_sandbox_registration.md`

## 4. 데이터 상태

`data/wishlist.csv`에는 5개 구매 후보가 있다.

- HHKB 키보드: 420,000원, keyboard, urgency low
- 에어팟 맥스: 790,000원, audio, urgency medium
- 아이패드 미니: 850,000원, tablet, urgency medium
- USB-C 허브: 39,000원, accessory, urgency high
- 기계식 계산기: 120,000원, toy, urgency low

`data/owned_items.csv`에는 5개 보유품이 있다.

- 키크론 키보드: keyboard, good, weekly
- 로지텍 MX Keys: keyboard, good, daily
- 에어팟 프로: audio, good, daily
- 아이패드 프로: tablet, good, weekly
- USB-C 허브 구형: accessory, bad, daily

`data/budget.json`:

```json
{
  "monthly_discretionary_budget": 300000,
  "already_spent_this_month": 180000,
  "currency": "KRW"
}
```

남은 예산은 120,000원이다.

## 5. 정상 MCP 도구

`src/wishlist_court_server.py`의 도구:

- `list_wishlist_items`
- `get_owned_items_by_category`
- `get_budget_status`
- `judge_purchase`
- `save_verdict_report`

정상 서버의 핵심 특징:

- 실제 CSV/JSON 데이터를 읽는다.
- 같은 카테고리 보유품을 확인한다.
- 남은 예산을 계산한다.
- 중복 위험, 예산 위험, 충동구매 위험을 반영한다.
- markdown 보고서를 `output/`에 저장한다.

## 6. 망가진 MCP 도구

`src/broken_wishlist_court_server.py`는 정상 서버와 같은 tool 이름을 갖지만, 실패 실험을 위해 일부러 잘못 동작한다.

망가진 동작:

- `judge_purchase` docstring이 소비 추천 편향을 유도한다.
- `get_owned_items_by_category`가 항상 빈 리스트를 반환한다.
- `get_budget_status`가 실제보다 낙관적인 남은 예산을 반환한다.
- `duplicate_risk`를 항상 low로 반환한다.
- `budget_risk`도 high가 거의 나오지 않는다.
- reject가 거의 나오지 않고 대부분 approve 또는 cooldown으로 처리된다.

## 7. 로컬 실험 결과

Hermes 실제 tool call 대신, `experiments/run_local_experiments.py`로 deterministic 로컬 실행을 했다.

실행 명령:

```bash
.venv/bin/python experiments/run_local_experiments.py
```

생성된 파일:

- `output/no_mcp_verdict.md`
- `output/good_mcp_verdict.md`
- `output/broken_mcp_verdict.md`
- `output/single_agent_verdict.md`
- `output/planner_executor_verdict.md`
- `output/parallel_subagents_verdict.md`
- `output/local_experiment_summary.md`
- `output/local_experiment_metrics.json`

실험 1 판결 분포:

| 조건 | approve | cooldown | reject | replace_only |
| --- | ---: | ---: | ---: | ---: |
| MCP 없음 | 1 | 4 | 0 | 0 |
| 정상 MCP | 1 | 3 | 1 | 0 |
| 망가진 MCP | 5 | 0 | 0 | 0 |

핵심 관찰:

- MCP 없음: 보유품과 실제 예산을 몰라 근거가 약하다.
- 정상 MCP: HHKB 키보드는 reject, USB-C 허브는 approve로 데이터 기반 판결이 나온다.
- 망가진 MCP: 5개 항목 모두 approve가 되어 구매 추천 편향이 선명하다.

## 7-1. Orchestration local experiment 결과

Orchestration 비교 실험도 deterministic local runner로 완료했다.

실행 명령:

```bash
.venv/bin/python experiments/run_orchestration_experiments.py
```

생성된 파일:

- `output/orchestration_single_agent_verdict.md`
- `output/orchestration_planner_executor_plan.md`
- `output/orchestration_planner_executor_verdict.md`
- `output/orchestration_parallel_budget_agent.md`
- `output/orchestration_parallel_duplicate_agent.md`
- `output/orchestration_parallel_impulse_agent.md`
- `output/orchestration_parallel_synthesized_verdict.md`
- `output/orchestration_experiment_summary.md`
- `output/orchestration_experiment_metrics.json`

Metrics 요약:

| 패턴 | simulated tokens | simulated latency | tool calls | failure layer | quality |
| --- | ---: | ---: | ---: | --- | ---: |
| Single Agent | 4,200 | 18.2s | 12 | none | 4/5 |
| Planner+Executor | 6,100 | 27.5s | 12 | none | 5/5 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | synthesis_overhead | 4/5 |

핵심 결론:

- Single Agent는 가장 빠르고 단순하지만 체크리스트 누락 위험이 있다.
- Planner+Executor는 토큰과 시간이 늘어도 판정 기준을 먼저 고정해 가장 안정적이다.
- Parallel sub-agent는 예산/중복/충동구매 관점 분리가 잘 보이지만 작은 작업에는 비용 대비 과하다.

## 8. Hermes 상태

Hermes 실행 파일 위치:

```bash
/home/ubtwt/.local/bin/hermes
```

프로젝트 내부 Hermes home:

```bash
/home/ubtwt/Projects/wishilist-court-mcp/.hermes
```

등록된 MCP 서버:

```text
wishlist-court          enabled
wishlist-court-broken   enabled
```

확인 명령:

```bash
HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp list
```

주의:

- sandbox 안에서는 `hermes mcp test`가 stdio 응답을 받지 못해 타임아웃됐다.
- 등록은 완료되어 `.hermes/config.yaml`에 enabled 상태로 저장되어 있다.
- 실제 일반 터미널에서 다시 테스트해야 한다.

일반 터미널 테스트 명령:

```bash
HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp test wishlist-court

HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp test wishlist-court-broken
```

Hermes 채팅 실행 예:

```bash
HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes chat
```

## 9. 검증 완료 항목

가상환경:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

검증 명령:

```bash
.venv/bin/python -m py_compile src/*.py experiments/run_local_experiments.py
.venv/bin/python -c "import sys; sys.path.insert(0, 'src'); import wishlist_court_server, broken_wishlist_court_server; print('server imports ok')"
```

결과:

- Python compile 통과
- 정상 서버 import 성공
- broken 서버 import 성공
- 로컬 실험 러너 실행 성공
- Orchestration local experiment 실행 성공
- Hermes MCP list에서 두 서버 enabled 확인

## 10. 중요한 제한 사항

현재 상태에서 아직 완전히 끝나지 않은 부분:

- 실제 Hermes tool call 기반 실험은 아직 완료되지 않았다.
- `hermes mcp test`는 sandbox 안에서 타임아웃됐다.
- 실제 LLM 토큰 사용량은 미측정이다.
- 실제 Hermes/Codex 레이턴시는 미측정이다.
- 발표용 화면 캡처는 아직 없다.
- 30초 데모 영상은 아직 없다.
- 실제 발표 슬라이드 파일은 없고, markdown 초안만 있다.
- GitHub 제출용 정리 여부는 아직 확인하지 않았다.

이미 보완된 부분:

- 로컬 deterministic 실행 결과는 `output/`에 있다.
- Orchestration local experiment 결과도 `output/orchestration_*` 파일들로 있다.
- expected output 문서는 로컬 실행 결과 기준으로 채워져 있다.
- 발표 슬라이드 초안은 markdown으로 있다.
- Hermes sandbox 등록 기록은 있다.

## 11. 다음 세션에서 논의할 일

다른 ChatGPT/Codex 세션에서는 아래를 중점적으로 논의하면 된다.

1. 일반 터미널에서 Hermes MCP test를 성공시키는 방법
2. Hermes 실제 tool call 로그를 얻는 방법
3. `experiments/prompts/`의 프롬프트를 실제 Hermes에서 실행하는 절차
4. 실제 토큰 사용량과 레이턴시 기록 방식
5. 발표 캡처 목록과 촬영 순서
6. 30초 데모 영상 스크립트 확정
7. 발표 슬라이드 파일을 만들지, markdown 초안만 제출할지 결정
8. `.hermes/config.yaml`을 제출물에 포함할지 여부
9. GitHub 제출용으로 `.venv`, cache, 개인 Hermes 로그가 제외됐는지 확인

## 12. 다음 세션에 줄 요청 프롬프트

아래 프롬프트를 다른 ChatGPT/Codex 세션에 그대로 붙여넣으면 된다.

```text
나는 생성모델응용 수업의 MCP 고도화 과제로 wishlist-court-mcp 프로젝트를 만들고 있다.

현재 프로젝트는 구현이 거의 완료되어 있고, 이 세션에는 HANDOFF_STATUS.md의 내용을 기준으로 상태를 이어받아 논의해주면 된다.

핵심 목표는 다음이다.

1. 직접 만든 Python FastMCP 서버를 과제 제출 가능 상태로 정리한다.
2. MCP 없음 / 정상 MCP / 망가진 MCP 비교를 발표할 수 있게 만든다.
3. Single Agent / Planner+Executor / Parallel sub-agent 비교를 발표할 수 있게 만든다.
4. Hermes에서 실제 MCP tool call이 가능한지 확인하고, 가능하면 실제 실험 로그를 얻는다.
5. 토큰 사용량, 레이턴시, 캡처, 30초 데모 영상 계획을 마무리한다.

현재 완료된 것:

- 정상 MCP 서버: src/wishlist_court_server.py
- 망가진 MCP 서버: src/broken_wishlist_court_server.py
- 핵심 로직: src/core.py
- 데이터: data/
- 실험 프롬프트: experiments/prompts/
- 로컬 실행 결과: output/
- 결과 템플릿: experiments/expected_outputs/
- Hermes sandbox 등록: .hermes/config.yaml

주의할 점:

- sandbox 안에서는 hermes mcp test가 stdio 타임아웃됐다.
- 일반 터미널에서 다시 테스트해야 한다.
- 실제 LLM 토큰 사용량과 Hermes tool call 캡처는 아직 없다.

이 상태를 기준으로, 남은 과제 제출 작업을 무엇부터 하면 좋을지 점검하고 실행 계획을 제안해줘.
```

## 13. 현재 판단

코드와 문서 산출물은 과제 제출용으로 상당히 완성되어 있다.

남은 핵심은 "실제 Hermes 실행 증거"다.

최소 제출 가능 상태:

- 코드
- README
- 실험 프롬프트
- 로컬 실행 결과
- expected output 문서
- 발표 슬라이드 초안

더 좋은 제출 상태:

- Hermes 실제 tool call 캡처
- 정상 MCP와 broken MCP의 실제 실행 비교 로그
- 실제 토큰/레이턴시 수치
- 30초 데모 영상
