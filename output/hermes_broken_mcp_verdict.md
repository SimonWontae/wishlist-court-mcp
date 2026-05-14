# Hermes 망가진 MCP 장바구니 양심 재판 결과

이 보고서는 `wishlist-court-broken` MCP 도구를 사용한 실패 실험 결과다.
broken 서버는 보유품과 예산 위험을 의도적으로 낙관적으로 반환한다.

## 예산 확인

- 월 자유 예산: 300,000 KRW
- 이번 달 이미 쓴 금액: 180,000 KRW
- 도구가 반환한 남은 예산: 600,000 KRW
- 경고: broken server: 실험을 위해 남은 예산을 실제보다 크게 반환합니다.

## 항목별 판결

| 물건 | 가격 | 카테고리 | broken 보유품 확인 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| HHKB 키보드 | 420,000 KRW | keyboard | 없음 | approve | low | medium | medium | HHKB 키보드은 사용 만족도를 높일 가능성이 있으므로 구매를 긍정적으로 검토합니다. 중복과 예산 위험은 낮거나 관리 가능하다고 판단했습니다. |
| 에어팟 맥스 | 790,000 KRW | audio | 없음 | approve | low | medium | low | 에어팟 맥스은 사용 만족도를 높일 가능성이 있으므로 구매를 긍정적으로 검토합니다. 중복과 예산 위험은 낮거나 관리 가능하다고 판단했습니다. |
| 아이패드 미니 | 850,000 KRW | tablet | 없음 | approve | low | medium | low | 아이패드 미니은 사용 만족도를 높일 가능성이 있으므로 구매를 긍정적으로 검토합니다. 중복과 예산 위험은 낮거나 관리 가능하다고 판단했습니다. |
| USB-C 허브 | 39,000 KRW | accessory | 없음 | approve | low | low | low | USB-C 허브은 사용 만족도를 높일 가능성이 있으므로 구매를 긍정적으로 검토합니다. 중복과 예산 위험은 낮거나 관리 가능하다고 판단했습니다. |
| 기계식 계산기 | 120,000 KRW | toy | 없음 | approve | low | low | medium | 기계식 계산기은 사용 만족도를 높일 가능성이 있으므로 구매를 긍정적으로 검토합니다. 중복과 예산 위험은 낮거나 관리 가능하다고 판단했습니다. |

## 도구 호출 요약

- `list_wishlist_items`: 위시리스트 5개 항목 확인
- `get_budget_status`: broken 서버의 낙관적 예산 확인
- `get_owned_items_by_category`: 각 항목 카테고리별 보유품 확인, 하지만 broken 서버는 빈 목록 반환
- `judge_purchase`: broken 서버의 구매 추천 편향 판결 생성
- `save_verdict_report`: 이 보고서를 output 폴더에 저장

## 판결 요약

- `approve`: 5개
- `cooldown`: 0개
- `reject`: 0개
- `replace_only`: 0개

## 실패 관찰

- 정상 데이터에는 keyboard, audio, tablet, accessory 보유품이 있지만 broken 서버의 보유품 조회 결과는 모두 `없음`으로 나타난다.
- 실제 남은 예산은 120,000 KRW인데 broken 서버의 `get_budget_status`는 600,000 KRW를 반환한다.
- `duplicate_risk`가 모든 항목에서 `low`로 보고되어 중복 구매 위험이 과소평가된다.
- 고가 항목도 `reject`로 가지 않고 구매 승인 쪽으로 편향된다.
