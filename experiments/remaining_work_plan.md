# 남은 작업 완료 기획서

이 문서는 `wishlist-court-mcp` 프로젝트 구현 이후, 과제 제출을 완성하기 위해 남은 실험 실행·기록·발표 준비 작업을 정리한 실행 계획서다.

## 1. 현재 완료 상태

- 정상 MCP 서버 구현 완료: `src/wishlist_court_server.py`
- 망가진 MCP 서버 구현 완료: `src/broken_wishlist_court_server.py`
- 순수 판정 로직 구현 완료: `src/core.py`
- 샘플 데이터 작성 완료: `data/`
- 실험 프롬프트 7종 작성 완료: `experiments/prompts/`
- 예상 결과 템플릿 작성 완료: `experiments/expected_outputs/`
- README 작성 완료
- `.venv` 가상환경 생성 및 의존성 설치 완료
- Python 컴파일 검증 완료
- 정상 서버와 broken 서버 import 검증 완료

## 2. 최종 제출까지 남은 산출물

최종적으로 아래 자료를 채우면 과제 제출 상태가 된다.

1. Hermes에 정상 MCP와 broken MCP 등록
2. 실험 1 실행 결과 기록
   - MCP 없음
   - 정상 MCP
   - 망가진 MCP
3. 실험 2 실행 결과 기록
   - Single Agent
   - Planner+Executor
   - Parallel sub-agent
4. `experiments/expected_outputs/` 문서에 실제 수치와 관찰 내용 기입
5. `output/` 폴더에 실행 결과 markdown 보고서 저장
6. 발표용 캡처 이미지 확보
7. 30초 데모 영상 촬영
8. 발표 슬라이드 초안 작성

## 3. 실행 전 준비

프로젝트 루트에서 가상환경을 활성화한다.

```bash
source .venv/bin/activate
```

정상 서버가 실행되는지 확인한다.

```bash
python src/wishlist_court_server.py
```

broken 서버가 실행되는지 확인한다.

```bash
python src/broken_wishlist_court_server.py
```

서버 실행 확인 후에는 Hermes 또는 Codex MCP 클라이언트에서 등록해 사용한다.

## 4. Hermes 등록 계획

아래 명령에서 경로가 현재 프로젝트 경로와 맞는지 확인한다.

```bash
hermes mcp add wishlist-court "python /home/ubtwt/Projects/wishilist-court-mcp/src/wishlist_court_server.py"
hermes mcp add wishlist-court-broken "python /home/ubtwt/Projects/wishilist-court-mcp/src/broken_wishlist_court_server.py"
hermes mcp list
```

등록 후 확인할 것:

- `wishlist-court`가 정상 서버로 등록되었는가
- `wishlist-court-broken`이 broken 서버로 등록되었는가
- 두 서버의 tool 이름이 동일하게 보이는가
- broken 서버 설명에 소비 추천 편향이 드러나는가

## 5. 실험 1 실행 계획: MCP 없음 vs 정상 MCP vs 망가진 MCP

### 5.1 MCP 없음

사용 프롬프트:

- `experiments/prompts/01_no_mcp_prompt.md`

기록할 항목:

- 보유품 정보를 언급했는가
- 예산 정보를 추측했는가
- 어떤 항목을 구매 승인했는가
- 중복 구매 위험을 놓쳤는가
- 일반 소비 조언으로 흐르는가

예상 관찰:

- 기존 키보드 2개, 에어팟 프로, 아이패드 프로 보유 사실을 반영하지 못한다.
- 남은 예산 120,000원을 알 수 없으므로 고가 항목의 예산 위험 판단이 약해진다.

### 5.2 정상 MCP

사용 프롬프트:

- `experiments/prompts/02_good_mcp_prompt.md`

기록할 항목:

- `list_wishlist_items` 호출 여부
- `get_owned_items_by_category` 호출 횟수
- `get_budget_status` 호출 여부
- `judge_purchase` 호출 횟수
- `save_verdict_report` 호출 여부
- `output/good_mcp_verdict.md` 생성 여부

예상 판결:

| 항목 | 예상 판결 | 근거 |
| --- | --- | --- |
| HHKB 키보드 | reject | 예산 초과, keyboard 보유품 2개 |
| 에어팟 맥스 | cooldown 또는 reject | 예산 초과, audio 보유품 존재 |
| 아이패드 미니 | cooldown 또는 reject | 예산 초과, tablet 보유품 존재 |
| USB-C 허브 | approve | 기존 허브 상태 bad, 긴급도 high |
| 기계식 계산기 | cooldown | 충동구매 신호, 긴급도 low |

### 5.3 망가진 MCP

사용 프롬프트:

- `experiments/prompts/03_broken_mcp_prompt.md`

기록할 항목:

- 보유품 조회가 빈 목록으로 나왔는가
- 남은 예산이 실제보다 낙관적으로 나왔는가
- `judge_purchase` 설명이 구매 추천 방향으로 작동했는가
- 정상 MCP 대비 approve 비율이 늘었는가
- 잘못된 도구 결과를 모델이 그대로 믿었는가

예상 관찰:

- 중복 위험이 낮게 보고된다.
- 고가 항목도 reject 대신 approve 또는 cooldown으로 완화될 가능성이 높다.
- 도구 description이 모델의 판단 문체와 결론을 바꾼다.

## 6. 실험 2 실행 계획: Orchestration 3패턴 비교

### 6.1 Single Agent

사용 프롬프트:

- `experiments/prompts/04_single_agent_prompt.md`

기록할 항목:

- 총 소요 시간
- 총 토큰 사용량
- MCP 호출 수
- 판단 누락 여부
- 최종 보고서 저장 여부

예상 결론:

- 가장 단순하고 빠르다.
- 이 프로젝트처럼 데이터가 작고 판단 기준이 단순한 경우 토큰 효율이 좋다.

### 6.2 Planner+Executor

사용 프롬프트:

- Planner: `experiments/prompts/05_planner_prompt.md`
- Executor: `experiments/prompts/06_executor_prompt.md`

진행 방식:

1. Planner 프롬프트를 실행한다.
2. Planner 결과를 복사한다.
3. Executor 프롬프트의 `Planner 계획 붙여넣기` 위치에 붙여넣는다.
4. Executor가 정상 MCP를 사용해 실제 판결을 수행한다.

기록할 항목:

- Planner가 도구 호출 계획을 잘 세웠는가
- Executor가 계획을 따랐는가
- Single Agent 대비 누락이 줄었는가
- 토큰 사용량이 얼마나 증가했는가

예상 결론:

- 비용은 늘지만 안정성이 높다.
- 발표에서는 "계획과 실행을 분리하면 도구 호출 누락이 줄어든다"는 점을 보여주기 좋다.

### 6.3 Parallel sub-agent

사용 프롬프트:

- `experiments/prompts/07_parallel_subagents_prompt.md`

진행 방식:

1. Agent A 예산 검사관을 실행한다.
2. Agent B 중복 구매 검사관을 실행한다.
3. Agent C 충동구매 검사관을 실행한다.
4. 세 결과를 Synthesizer 프롬프트에 붙여넣는다.
5. Synthesizer가 최종 판결을 작성하고 저장한다.

기록할 항목:

- Agent별 토큰 사용량
- 가장 오래 걸린 Agent
- 중복된 MCP 호출 수
- Synthesizer 병합 시간
- Single Agent 대비 추가 발견점
- 병합 과정에서 충돌한 판단

예상 결론:

- 관점 분리는 명확하지만 비용이 크다.
- 이 과제에서는 실용 효율보다 orchestration 차이를 보여주는 발표 가치가 크다.

## 7. 결과 문서 작성 계획

실험 후 아래 파일을 채운다.

### `experiments/expected_outputs/comparison_table.md`

채울 내용:

- MCP 없음 / 정상 MCP / 망가진 MCP의 작업 완료 여부
- 소요 시간
- 토큰 사용량
- 결과 정확도
- 에이전트 행동
- 주요 관찰

### `experiments/expected_outputs/failure_log_analysis.md`

채울 내용:

- broken MCP의 실패 주입이 실제로 어떤 결과를 만들었는가
- 잘못된 description이 문장과 결론에 어떤 영향을 줬는가
- 중복 구매 확인 실패가 어느 항목에서 나타났는가
- 예산 초과 판단 실패가 어느 항목에서 나타났는가
- 발표에서 보여줄 캡처 위치

### `experiments/expected_outputs/orchestration_benchmark.md`

채울 내용:

- Single / Planner+Executor / Parallel sub-agent 토큰 합계
- 총 레이턴시
- MCP 호출 수
- 실패 발생 레이어
- 결과 퀄리티
- 최종 회고

## 8. 발표 캡처 계획

최소 캡처 목록:

1. 프로젝트 파일 트리
2. `data/wishlist.csv`
3. `data/owned_items.csv`
4. 정상 MCP tool list
5. 정상 MCP 실행 중 tool call 장면
6. 정상 MCP 결과 보고서
7. broken MCP의 빈 보유품 반환 또는 낙관적 예산 반환
8. 정상 MCP와 broken MCP의 같은 항목 판결 차이
9. orchestration 비교표

## 9. 30초 데모 영상 구성

권장 흐름:

| 시간 | 화면 | 설명 |
| ---: | --- | --- |
| 0~5초 | 프로젝트 트리 | 직접 만든 MCP 서버와 실험 자료가 있음을 보여준다. |
| 5~10초 | 데이터 파일 | 위시리스트, 보유품, 예산 데이터 구조를 보여준다. |
| 10~18초 | 정상 MCP 실행 | 도구 호출 후 보수적 판결이 나오는 장면을 보여준다. |
| 18~25초 | broken MCP 실행 | 같은 작업에서 더 낙관적인 판결이 나오는 장면을 보여준다. |
| 25~30초 | 비교표 | tool description과 도구 품질이 결과를 바꾼다는 결론을 보여준다. |

## 10. 발표 슬라이드 작성 계획

권장 7장 구성:

1. 제목: 장바구니 양심 재판 MCP
2. 과제 목표: tool-use, broken tool, orchestration 비교
3. 프로젝트 구조: 데이터, 정상 서버, broken 서버, 실험 프롬프트
4. MCP 도구 설계: 5개 도구와 tool description 의도
5. 실험 1 결과: MCP 없음 vs 정상 MCP vs 망가진 MCP
6. 실험 2 결과: Single vs Planner+Executor vs Parallel sub-agent
7. 결론과 한계: MCP는 결과 품질을 올리지만 망가진 도구는 편향을 만든다

## 11. 최종 체크리스트

- [x] Hermes에 정상 MCP 등록: 프로젝트 내부 `.hermes/config.yaml`에 등록 완료
- [x] Hermes에 broken MCP 등록: 프로젝트 내부 `.hermes/config.yaml`에 등록 완료
- [x] MCP 없음 프롬프트 실행: 로컬 deterministic 대체 실행 완료
- [x] 정상 MCP 프롬프트 실행: 로컬 deterministic 대체 실행 완료
- [x] broken MCP 프롬프트 실행: 로컬 deterministic 대체 실행 완료
- [x] Single Agent 프롬프트 실행: 로컬 deterministic 대체 실행 완료
- [x] Planner 프롬프트 실행: 로컬 deterministic 대체 실행 완료
- [x] Executor 프롬프트 실행: 로컬 deterministic 대체 실행 완료
- [x] Parallel sub-agent 절차 실행: 로컬 deterministic 대체 실행 완료
- [x] `comparison_table.md` 실제 수치 기입
- [x] `failure_log_analysis.md` 실제 관찰 기입
- [x] `orchestration_benchmark.md` 실제 수치 기입
- [x] `output/`에 결과 보고서 생성 확인
- [ ] 발표 캡처 수집: GUI/Hermes 실행 화면이 필요해 미수행
- [ ] 30초 데모 영상 촬영: GUI/Hermes 실행 화면이 필요해 미수행
- [x] 발표 슬라이드 초안 완성: `experiments/presentation_slide_outline.md`

## 12. 제출 전 최종 검증 명령

```bash
source .venv/bin/activate
python -m py_compile src/*.py
python -c "import sys; sys.path.insert(0, 'src'); import wishlist_court_server, broken_wishlist_court_server; print('server imports ok')"
find . -path './.venv' -prune -o -path './src/__pycache__' -prune -o -type f -print | sort
```

성공 기준:

- 컴파일 에러가 없다.
- 서버 import가 성공한다.
- README, data, src, experiments, output 구조가 모두 보인다.
- 실험 결과 문서에 빈 표가 남아 있지 않다.

## 13. 실행 결과 기록

2026-05-13 기준 실제 수행 결과:

- `command -v hermes`: `/home/ubtwt/.local/bin/hermes` 확인.
- `HERMES_HOME=.hermes hermes mcp add wishlist-court ...`: 등록 완료.
- `HERMES_HOME=.hermes hermes mcp add wishlist-court-broken ...`: 등록 완료.
- `HERMES_HOME=.hermes hermes mcp list`: 두 서버 모두 enabled 상태 확인.
- `HERMES_HOME=.hermes hermes mcp test wishlist-court`: sandbox stdio 제한으로 타임아웃.
- `.venv/bin/python experiments/run_local_experiments.py`: 성공.
- 실험 1 보고서 생성 완료:
  - `output/no_mcp_verdict.md`
  - `output/good_mcp_verdict.md`
  - `output/broken_mcp_verdict.md`
- 실험 2 보고서 생성 완료:
  - `output/single_agent_verdict.md`
  - `output/planner_executor_verdict.md`
  - `output/parallel_subagents_verdict.md`
- 실행 요약 생성 완료:
  - `output/local_experiment_summary.md`
  - `output/local_experiment_metrics.json`
- 발표 슬라이드 초안 생성 완료:
  - `experiments/presentation_slide_outline.md`
- Hermes sandbox 등록 기록 생성 완료:
  - `experiments/hermes_sandbox_registration.md`
- 결과 문서 갱신 완료:
  - `experiments/expected_outputs/comparison_table.md`
  - `experiments/expected_outputs/failure_log_analysis.md`
  - `experiments/expected_outputs/orchestration_benchmark.md`

주의:

- 현재 결과의 소요 시간은 LLM/Hermes 실행 시간이 아니라 로컬 Python 실행 시간이다.
- 토큰 사용량은 실제 Hermes 또는 Codex에서 프롬프트를 실행한 뒤 교체해야 한다.
- 발표 캡처와 데모 영상은 화면 녹화가 필요한 작업이라 이 환경에서는 생성하지 않았다.
- Hermes MCP 서버 두 개는 `.hermes/config.yaml`에 등록되어 enabled 상태로 보이지만, sandbox의 stdio 제한 때문에 `hermes mcp test`는 타임아웃됐다.
