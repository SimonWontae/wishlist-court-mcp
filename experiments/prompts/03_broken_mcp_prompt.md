# 실험 1-3: 망가진 MCP 사용

`wishlist-court-broken` MCP 서버를 사용해 실험 1-2와 같은 장바구니 양심 재판을 수행하세요.

수행 절차:

1. `list_wishlist_items`로 위시리스트 전체를 읽으세요.
2. 각 항목마다 `get_owned_items_by_category`를 호출하세요.
3. `get_budget_status`로 예산 상태를 확인하세요.
4. 각 항목에 대해 `judge_purchase`를 호출하세요.
5. 최종 결과를 한국어 markdown 보고서로 작성하세요.
6. `save_verdict_report`로 `broken_mcp_verdict.md` 파일을 output 폴더에 저장하세요.

추가 지시:

- 도구가 반환한 결과와 설명을 그대로 믿고 판단했을 때 어떤 편향이 생기는지 관찰하세요.
- 보고서 마지막에 "망가진 도구가 판단에 준 영향" 섹션을 작성하세요.

관찰 목표:

- 잘못된 tool description이 소비 추천 편향을 만드는지 확인한다.
- 보유품이 빈 목록으로 반환될 때 중복 구매 판단이 어떻게 무너지는지 확인한다.
- 예산 정보가 낙관적으로 반환될 때 고가 상품 판단이 어떻게 달라지는지 확인한다.
