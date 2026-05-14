# 장바구니 양심 재판 결과

| 물건 | 가격 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |
| --- | ---: | --- | --- | --- | --- | --- |
| HHKB 키보드 | 420,000 KRW | reject | high | high | high | HHKB 키보드은 남은 예산을 초과하고 같은 카테고리의 양호한 보유품이 많아 기각합니다. |
| 에어팟 맥스 | 790,000 KRW | cooldown | medium | high | low | 에어팟 맥스은 예산 초과 위험이 커서 이번 달 구매는 보류합니다. |
| 아이패드 미니 | 850,000 KRW | cooldown | medium | high | medium | 아이패드 미니은 예산 초과 위험이 커서 이번 달 구매는 보류합니다. |
| USB-C 허브 | 39,000 KRW | approve | low | low | low | USB-C 허브은 기존 accessory 품목 상태가 나쁘고 긴급도가 높아 구매를 승인합니다. |
| 기계식 계산기 | 120,000 KRW | cooldown | none | medium | high | 기계식 계산기은 충동구매 신호가 강하므로 냉각기간 후 다시 판단합니다. |

## 판결 기준

- `approve`: 예산과 필요성이 충분히 맞아 구매 승인
- `cooldown`: 충동 또는 예산 위험이 있어 냉각기간 후 재검토
- `reject`: 예산 초과와 중복 위험이 커서 기각
- `replace_only`: 기존 물건 처분 또는 교체 조건에서만 허용

## Orchestration 메모

Planner는 도구 호출 계획만 만들고, Executor가 정상 MCP 도구를 사용해 실행한 것으로 가정한 결과다.
