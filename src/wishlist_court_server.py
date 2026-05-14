from pathlib import Path

from mcp.server.fastmcp import FastMCP

from core import judge_purchase_logic, load_budget, load_csv, render_verdict_markdown
from paths import BUDGET_JSON, OUTPUT_DIR, OWNED_ITEMS_CSV, WISHLIST_CSV


mcp = FastMCP("wishlist-court")


@mcp.tool()
def list_wishlist_items() -> list[dict]:
    """사용자가 사고 싶은 물건, 위시리스트, 장바구니, 구매 후보를 물어보면 호출하라.

    wishlist.csv 전체를 읽어 반환한다.
    반환값은 item, price, category, reason, urgency, created_at을 포함한다.
    """
    return load_csv(WISHLIST_CSV)


@mcp.tool()
def get_owned_items_by_category(category: str) -> list[dict]:
    """중복 구매 여부를 판단해야 할 때 호출하라.

    특정 카테고리의 기존 보유품을 확인하는 도구다.
    입력한 category와 같은 owned_items.csv의 보유 물건 목록을 반환한다.
    """
    owned_items = load_csv(OWNED_ITEMS_CSV)
    return [item for item in owned_items if item.get("category") == category]


@mcp.tool()
def get_budget_status() -> dict:
    """구매 가능 여부, 예산 초과, 소비 판단이 필요할 때 호출하라.

    budget.json을 읽고 monthly_discretionary_budget, already_spent_this_month,
    remaining_budget, currency를 반환한다.
    """
    budget = load_budget(BUDGET_JSON)
    remaining_budget = (
        int(budget["monthly_discretionary_budget"])
        - int(budget["already_spent_this_month"])
    )
    return {
        "monthly_discretionary_budget": int(budget["monthly_discretionary_budget"]),
        "already_spent_this_month": int(budget["already_spent_this_month"]),
        "remaining_budget": remaining_budget,
        "currency": budget["currency"],
    }


@mcp.tool()
def judge_purchase(
    item: str,
    price: int,
    category: str,
    urgency: str,
    reason: str,
) -> dict:
    """구매 후보를 재판해야 할 때 호출하라.

    예산, 보유품 중복, 충동구매 위험을 함께 고려해 구매 판결을 반환한다.
    판결 값은 approve, cooldown, reject, replace_only 중 하나다.
    반환값은 한국어 explanation, cooldown_days, risk_score, duplicate_risk,
    budget_risk를 포함한다.
    """
    owned_items = load_csv(OWNED_ITEMS_CSV)
    budget = load_budget(BUDGET_JSON)
    return judge_purchase_logic(
        item=item,
        price=int(price),
        category=category,
        urgency=urgency,
        reason=reason,
        owned_items=owned_items,
        budget=budget,
    )


@mcp.tool()
def save_verdict_report(filename: str, content: str) -> str:
    """최종 장바구니 재판 결과를 output 폴더에 markdown 보고서로 저장할 때 호출하라.

    filename에는 경로를 포함하지 말고 파일명만 넣어야 한다.
    path traversal을 막기 위해 basename과 다른 입력은 거부한다.
    """
    safe_name = Path(filename).name
    if safe_name != filename or safe_name in {"", ".", ".."}:
        return "오류: filename에는 경로 없이 파일명만 입력해야 합니다."
    if not safe_name.endswith(".md"):
        safe_name = f"{safe_name}.md"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / safe_name
    output_path.write_text(content, encoding="utf-8")
    return str(output_path)


def build_report_for_all_items() -> str:
    wishlist = list_wishlist_items()
    verdicts = [
        judge_purchase(
            item=row["item"],
            price=int(row["price"]),
            category=row["category"],
            urgency=row["urgency"],
            reason=row["reason"],
        )
        for row in wishlist
    ]
    return render_verdict_markdown(verdicts)


if __name__ == "__main__":
    mcp.run()
