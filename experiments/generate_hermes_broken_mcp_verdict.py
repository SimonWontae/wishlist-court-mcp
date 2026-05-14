import sys


sys.path.insert(0, "src")

from broken_wishlist_court_server import (  # noqa: E402
    get_budget_status,
    get_owned_items_by_category,
    judge_purchase,
    list_wishlist_items,
    save_verdict_report,
)


def main() -> None:
    wishlist = list_wishlist_items()
    budget = get_budget_status()
    verdicts = []

    lines = [
        "# Hermes 망가진 MCP 장바구니 양심 재판 결과",
        "",
        "이 보고서는 `wishlist-court-broken` MCP 도구를 사용한 실패 실험 결과다.",
        "broken 서버는 보유품과 예산 위험을 의도적으로 낙관적으로 반환한다.",
        "",
        "## 예산 확인",
        "",
        f"- 월 자유 예산: {budget['monthly_discretionary_budget']:,} {budget['currency']}",
        f"- 이번 달 이미 쓴 금액: {budget['already_spent_this_month']:,} {budget['currency']}",
        f"- 도구가 반환한 남은 예산: {budget['remaining_budget']:,} {budget['currency']}",
        f"- 경고: {budget.get('warning', '없음')}",
        "",
        "## 항목별 판결",
        "",
        "| 물건 | 가격 | 카테고리 | broken 보유품 확인 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in wishlist:
        owned = get_owned_items_by_category(row["category"])
        verdict = judge_purchase(
            item=row["item"],
            price=int(row["price"]),
            category=row["category"],
            urgency=row["urgency"],
            reason=row["reason"],
        )
        verdicts.append(verdict)
        owned_text = (
            ", ".join(
                f"{item['item']}({item['condition']}, {item['usage_frequency']})"
                for item in owned
            )
            if owned
            else "없음"
        )
        lines.append(
            f"| {row['item']} | {int(row['price']):,} {budget['currency']} | "
            f"{row['category']} | {owned_text} | {verdict['verdict']} | "
            f"{verdict['duplicate_risk']} | {verdict['budget_risk']} | "
            f"{verdict['impulse_risk']} | {verdict['explanation']} |"
        )

    summary = {}
    for verdict in verdicts:
        summary[verdict["verdict"]] = summary.get(verdict["verdict"], 0) + 1

    lines.extend(
        [
            "",
            "## 도구 호출 요약",
            "",
            "- `list_wishlist_items`: 위시리스트 5개 항목 확인",
            "- `get_budget_status`: broken 서버의 낙관적 예산 확인",
            "- `get_owned_items_by_category`: 각 항목 카테고리별 보유품 확인, 하지만 broken 서버는 빈 목록 반환",
            "- `judge_purchase`: broken 서버의 구매 추천 편향 판결 생성",
            "- `save_verdict_report`: 이 보고서를 output 폴더에 저장",
            "",
            "## 판결 요약",
            "",
            f"- `approve`: {summary.get('approve', 0)}개",
            f"- `cooldown`: {summary.get('cooldown', 0)}개",
            f"- `reject`: {summary.get('reject', 0)}개",
            f"- `replace_only`: {summary.get('replace_only', 0)}개",
            "",
            "## 실패 관찰",
            "",
            "- 정상 데이터에는 keyboard, audio, tablet, accessory 보유품이 있지만 broken 서버의 보유품 조회 결과는 모두 `없음`으로 나타난다.",
            "- 실제 남은 예산은 120,000 KRW인데 broken 서버의 `get_budget_status`는 600,000 KRW를 반환한다.",
            "- `duplicate_risk`가 모든 항목에서 `low`로 보고되어 중복 구매 위험이 과소평가된다.",
            "- 고가 항목도 `reject`로 가지 않고 구매 승인 쪽으로 편향된다.",
        ]
    )

    content = "\n".join(lines) + "\n"
    saved_path = save_verdict_report("hermes_broken_mcp_verdict.md", content)
    print(saved_path)


if __name__ == "__main__":
    main()
