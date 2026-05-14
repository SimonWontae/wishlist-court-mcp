import sys


sys.path.insert(0, "src")

from wishlist_court_server import (  # noqa: E402
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
        "# Hermes 정상 MCP 장바구니 양심 재판 결과",
        "",
        "## 예산 확인",
        "",
        f"- 월 자유 예산: {budget['monthly_discretionary_budget']:,} {budget['currency']}",
        f"- 이번 달 이미 쓴 금액: {budget['already_spent_this_month']:,} {budget['currency']}",
        f"- 남은 예산: {budget['remaining_budget']:,} {budget['currency']}",
        "",
        "## 항목별 판결",
        "",
        "| 물건 | 가격 | 카테고리 | 보유품 확인 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |",
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
            "- `get_budget_status`: 남은 예산 120,000 KRW 확인",
            "- `get_owned_items_by_category`: 각 항목 카테고리별 보유품 확인",
            "- `judge_purchase`: 각 항목별 최종 판결 생성",
            "- `save_verdict_report`: 이 보고서를 output 폴더에 저장",
            "",
            "## 판결 요약",
            "",
            f"- `approve`: {summary.get('approve', 0)}개",
            f"- `cooldown`: {summary.get('cooldown', 0)}개",
            f"- `reject`: {summary.get('reject', 0)}개",
            f"- `replace_only`: {summary.get('replace_only', 0)}개",
        ]
    )

    content = "\n".join(lines) + "\n"
    saved_path = save_verdict_report("hermes_good_mcp_verdict.md", content)
    print(saved_path)


if __name__ == "__main__":
    main()
