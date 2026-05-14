# wishlist-court-mcp

Repository: https://github.com/SimonWontae/wishlist-court-mcp

Wishlist Court MCP는 위시리스트, 보유품, 예산 데이터를 읽어 구매 후보를 판정하는 Python FastMCP 실험 프로젝트입니다.

이 프로젝트의 목적은 쇼핑 추천 서비스를 만드는 것이 아니라, **LLM reasoning이 tool description과 tool output quality에 얼마나 의존하는지**를 관찰하는 것입니다.

## Project Overview

장바구니 양심 재판 MCP는 세 가지 데이터를 사용합니다.

- `data/wishlist.csv`: 구매 후보
- `data/owned_items.csv`: 기존 보유품
- `data/budget.json`: 월 예산과 이미 쓴 금액

판결은 네 가지입니다.

- `approve`: 구매 승인
- `cooldown`: 냉각기간 후 재검토
- `reject`: 구매 기각
- `replace_only`: 기존 물건 처분 또는 교체 조건부 허용

## Why This Project

LLM은 그럴듯한 소비 조언을 쉽게 생성할 수 있습니다. 하지만 실제 예산, 기존 보유품, 구매 긴급도를 모르면 판단이 감성적 추천이나 과소비 방향으로 흐를 수 있습니다.

이 프로젝트는 같은 작업을 세 조건에서 비교합니다.

- MCP 없음: 모델이 제공된 일부 정보와 일반 상식만 사용
- 정상 MCP: 실제 예산과 보유품 데이터를 grounding하여 판단
- Broken MCP: 잘못된 tool description과 왜곡된 tool output으로 판단

핵심 질문은 다음입니다.

> 같은 모델이라도 tool layer가 달라지면 reasoning은 어떻게 달라지는가?

## Repository Structure

```text
wishlist-court-mcp/
├── data/
│   ├── wishlist.csv
│   ├── owned_items.csv
│   └── budget.json
├── src/
│   ├── wishlist_court_server.py
│   ├── broken_wishlist_court_server.py
│   ├── core.py
│   └── paths.py
├── experiments/
│   ├── prompts/
│   ├── expected_outputs/
│   ├── run_local_experiments.py
│   ├── run_orchestration_experiments.py
│   └── create_presentation.py
└── output/
```

## MCP Tools

| Tool | Purpose |
| --- | --- |
| `list_wishlist_items` | 위시리스트 CSV 전체를 읽어 구매 후보 목록 반환 |
| `get_owned_items_by_category` | 특정 카테고리의 기존 보유품 반환 |
| `get_budget_status` | 월 예산, 이번 달 지출, 남은 예산 반환 |
| `judge_purchase` | 예산, 중복, 충동구매 위험을 바탕으로 판결 |
| `save_verdict_report` | markdown 보고서를 `output/`에 저장 |

## Setup

Python 3.10 이상을 권장합니다.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Ubuntu/Debian에서 `externally-managed-environment` 오류가 나면 시스템 Python에 직접 설치하지 말고 위처럼 가상환경을 사용하세요.

## Run MCP Servers

정상 MCP 서버:

```bash
.venv/bin/python src/wishlist_court_server.py
```

Broken MCP 서버:

```bash
.venv/bin/python src/broken_wishlist_court_server.py
```

Broken 서버는 실패 실험용입니다.

- `get_owned_items_by_category`가 빈 목록을 반환합니다.
- `get_budget_status`가 실제보다 낙관적인 남은 예산을 반환합니다.
- `judge_purchase`가 구매 추천 편향을 갖도록 설계되어 있습니다.

## Hermes Registration Example

아래 경로는 환경에 맞게 바꿔 사용하세요.

```bash
hermes mcp add wishlist-court \
  --command /ABSOLUTE/PATH/wishlist-court-mcp/.venv/bin/python \
  --args /ABSOLUTE/PATH/wishlist-court-mcp/src/wishlist_court_server.py

hermes mcp add wishlist-court-broken \
  --command /ABSOLUTE/PATH/wishlist-court-mcp/.venv/bin/python \
  --args /ABSOLUTE/PATH/wishlist-court-mcp/src/broken_wishlist_court_server.py

hermes mcp list
```

Hermes sandbox 등록 기록은 [experiments/hermes_sandbox_registration.md](experiments/hermes_sandbox_registration.md)에 정리되어 있습니다.

## Reproduce Results

전체 로컬 실험 결과를 재생성합니다.

```bash
.venv/bin/python -m py_compile src/*.py experiments/*.py
.venv/bin/python experiments/run_local_experiments.py
.venv/bin/python experiments/run_orchestration_experiments.py
```

정상 MCP와 Broken MCP 결과 보고서만 다시 생성하려면 아래를 실행합니다.

```bash
.venv/bin/python experiments/generate_hermes_good_mcp_verdict.py
.venv/bin/python experiments/generate_hermes_broken_mcp_verdict.py
```

PPTX 발표자료는 아래 명령으로 생성합니다.

```bash
.venv/bin/python experiments/create_presentation.py
```

생성 파일:

- `wishlist_court_mcp_presentation.pptx`

## Experiment 1: Good MCP vs Broken MCP

정상 MCP 결과:

- `output/hermes_good_mcp_verdict.md`
- `approve`: 1개
- `cooldown`: 3개
- `reject`: 1개
- `replace_only`: 0개

Broken MCP 결과:

- `output/hermes_broken_mcp_verdict.md`
- `approve`: 5개
- `cooldown`: 0개
- `reject`: 0개
- `replace_only`: 0개

핵심 관찰:

- 정상 MCP는 남은 예산 120,000 KRW와 기존 보유품을 반영해 보수적으로 판단했습니다.
- Broken MCP는 보유품을 모두 없는 것처럼 반환하고 남은 예산을 600,000 KRW로 반환했습니다.
- 결과적으로 constraint-oriented reasoning이 desire-oriented reasoning으로 왜곡되었습니다.

## Experiment 2: Orchestration Comparison

동일한 장바구니 판결 작업을 세 가지 구조로 비교했습니다.

- Single Agent
- Planner + Executor
- Parallel sub-agent

결과:

| Pattern | Simulated Tokens | Simulated Latency | Tool Calls | Quality |
| --- | ---: | ---: | ---: | ---: |
| Single Agent | 4,200 | 18.2s | 12 | 4/5 |
| Planner + Executor | 6,100 | 27.5s | 12 | 5/5 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | 4/5 |

이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate입니다. 비교의 핵심은 절대값이 아니라 구조별 상대적 차이입니다.

요약:

- Single Agent는 빠르고 단순하지만 기준 누락 위험이 있습니다.
- Planner + Executor는 기준을 먼저 고정해 가장 안정적입니다.
- Parallel sub-agent는 설명력은 좋지만 작은 작업에는 병합 비용이 큽니다.

자세한 결과:

- `output/orchestration_experiment_summary.md`
- `output/orchestration_experiment_metrics.json`
- `experiments/expected_outputs/orchestration_benchmark.md`

## Presentation Materials

발표자료와 준비 문서는 README에서 분리해 `experiments/` 아래에 두었습니다.

- 발표 슬라이드 초안: [experiments/presentation_slide_outline.md](experiments/presentation_slide_outline.md)
- 발표용 PPTX 생성 스크립트: [experiments/create_presentation.py](experiments/create_presentation.py)
- 샘플 실행 로그: [experiments/sample_run_log.md](experiments/sample_run_log.md)
- 남은 작업/촬영 계획: [experiments/remaining_work_plan.md](experiments/remaining_work_plan.md)
- 인수인계 상태 문서: [HANDOFF_STATUS.md](HANDOFF_STATUS.md)

## Limitations

- 실제 쇼핑 추천 서비스가 아니라 MCP tool-use 실험용 미니 프로젝트입니다.
- 데이터셋은 작고 규칙 기반 판정 로직을 사용합니다.
- 실제 계좌 잔고, 가격 변동, 장기 소비 패턴은 반영하지 않습니다.
- Orchestration metrics는 local deterministic simulation estimate입니다.

## License

Course assignment project. No external API is required to run the local experiments.
