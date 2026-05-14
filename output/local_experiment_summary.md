# 로컬 실험 실행 요약

Hermes CLI가 설치되어 있지 않은 환경에서 MCP 도구 호출과 같은 로직을 로컬로 실행한 결과다.
토큰 사용량과 실제 LLM 레이턴시는 Hermes/Codex 실행 후 별도로 측정해야 한다.

## 실험 1

| 조건 | 완료 | 로컬 실행 시간(ms) | MCP 호출 수(계획 기준) | 보고서 |
| --- | --- | ---: | ---: | --- |
| MCP 없음 | True | 0.49 | 0 | output/no_mcp_verdict.md |
| 정상 MCP | True | 0.4 | 13 | output/good_mcp_verdict.md |
| 망가진 MCP | True | 0.33 | 13 | output/broken_mcp_verdict.md |

## 실험 2

| 패턴 | 완료 | 로컬 실행 시간(ms) | MCP 호출 수(계획 기준) | 보고서 |
| --- | --- | ---: | ---: | --- |
| Single Agent | True | 0.53 | 13 | output/single_agent_verdict.md |
| Planner+Executor | True | 0.37 | 13 | output/planner_executor_verdict.md |
| Parallel sub-agent | True | 0.36 | 14 | output/parallel_subagents_verdict.md |
