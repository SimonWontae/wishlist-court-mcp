# 실험 2-3: Parallel Sub-Agent 수동 실행 절차

정상 `wishlist-court` MCP 서버를 사용한다.
실제로 병렬 실행 코드를 작성하지 않고, 세 역할을 별도 세션 또는 별도 프롬프트로 실행한 뒤 Synthesizer가 합친다.

## 공통 데이터 수집

먼저 `list_wishlist_items`로 위시리스트를 읽는다.
필요하면 각 Agent가 직접 MCP 도구를 다시 호출해도 된다.

## Agent A: 예산 검사관

역할:

예산 초과 여부만 집중적으로 검사한다.

프롬프트:

```text
당신은 예산 검사관입니다.
정상 wishlist-court MCP 서버를 사용하세요.
get_budget_status를 호출하고, 각 위시리스트 항목의 가격이 남은 예산과 비교해 어떤 위험을 갖는지 판단하세요.
최종 판결은 내리지 말고 budget_risk와 근거만 표로 작성하세요.
```

## Agent B: 중복 구매 검사관

역할:

이미 보유한 물건과의 중복 여부만 검사한다.

프롬프트:

```text
당신은 중복 구매 검사관입니다.
정상 wishlist-court MCP 서버를 사용하세요.
각 위시리스트 항목마다 get_owned_items_by_category를 호출하세요.
같은 카테고리의 보유품 개수, 상태, 사용 빈도를 바탕으로 duplicate_risk와 근거만 표로 작성하세요.
최종 판결은 내리지 마세요.
```

## Agent C: 충동구매 검사관

역할:

구매 사유와 긴급도를 보고 충동구매 위험만 검사한다.

프롬프트:

```text
당신은 충동구매 검사관입니다.
정상 wishlist-court MCP 서버를 사용하세요.
위시리스트의 reason과 urgency를 중심으로 impulse_risk를 판단하세요.
"그냥", "예뻐서", "갖고 싶음", "좋아 보임" 같은 표현을 충동구매 신호로 보세요.
최종 판결은 내리지 말고 impulse_risk와 근거만 표로 작성하세요.
```

## Synthesizer

역할:

세 Agent 결과를 합쳐 최종 판결을 만든다.

프롬프트:

```text
당신은 Synthesizer입니다.
Agent A, B, C의 결과를 받아 항목별 최종 판결을 내리세요.
가능하면 정상 wishlist-court MCP의 judge_purchase를 호출해 최종 판결과 비교하세요.
결과를 parallel_subagents_verdict.md로 저장하세요.

합성 기준:
- 예산 위험 high + 중복 위험 high이면 reject 우선
- 충동구매 위험 high이면 cooldown 우선
- 긴급도 high이고 기존 물건 상태가 bad이면 approve 또는 replace_only 가능
- 판단 충돌이 있으면 도구가 반환한 근거를 보고 보수적으로 결정
```

측정할 항목:

- Agent별 토큰 사용량
- 가장 오래 걸린 Agent
- 결과 병합에 든 시간
- Single Agent 대비 추가로 발견한 관점
- 중복 호출로 인한 비용 증가
