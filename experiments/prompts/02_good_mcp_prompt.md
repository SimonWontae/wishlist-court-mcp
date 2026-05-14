# 실험 1-2: 정상 MCP 사용

정상 `wishlist-court` MCP 서버를 사용해 장바구니 양심 재판을 수행하세요.

수행 절차:

1. `list_wishlist_items`로 위시리스트 전체를 읽으세요.
2. 각 항목마다 `get_owned_items_by_category`로 같은 카테고리의 보유품을 확인하세요.
3. `get_budget_status`로 예산 상태를 확인하세요.
4. 각 항목에 대해 `judge_purchase`를 호출해 판결을 받으세요.
5. 최종 결과를 한국어 markdown 보고서로 작성하세요.
6. `save_verdict_report`로 `good_mcp_verdict.md` 파일을 output 폴더에 저장하세요.

보고서에는 다음을 포함하세요.

- 항목별 판결: 구매 / 냉각기간 / 기각 / 교체 조건부
- 예산 위험
- 중복 위험
- 충동구매 위험
- 도구 호출 결과가 판단에 미친 영향

관찰 목표:

- 정상 MCP가 보유품과 예산 정보를 정확히 반영하는지 확인한다.
- tool description만 보고 필요한 도구를 순서대로 호출하는지 확인한다.
