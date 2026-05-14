import csv
import json
from pathlib import Path
from typing import Any


IMPULSE_KEYWORDS = ("그냥", "예뻐", "이뻐", "갖고 싶", "사고 싶", "좋아 보임")


def load_csv(path: str | Path) -> list[dict[str, Any]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        if "price" in row:
            try:
                row["price"] = int(row["price"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"가격 값이 숫자가 아닙니다: {row.get('item', '알 수 없음')}") from exc
    return rows


def load_budget(path: str | Path) -> dict[str, Any]:
    budget_path = Path(path)
    if not budget_path.exists():
        raise FileNotFoundError(f"예산 파일을 찾을 수 없습니다: {budget_path}")

    with budget_path.open("r", encoding="utf-8") as file:
        budget = json.load(file)

    required_keys = {"monthly_discretionary_budget", "already_spent_this_month", "currency"}
    missing = sorted(required_keys - set(budget))
    if missing:
        raise ValueError(f"예산 파일에 필요한 키가 없습니다: {', '.join(missing)}")
    return budget


def get_remaining_budget(budget: dict[str, Any]) -> int:
    return int(budget["monthly_discretionary_budget"]) - int(budget["already_spent_this_month"])


def find_owned_by_category(
    owned_items: list[dict[str, Any]], category: str
) -> list[dict[str, Any]]:
    return [item for item in owned_items if item.get("category") == category]


def compute_duplicate_risk(owned_items: list[dict[str, Any]]) -> str:
    good_items = [item for item in owned_items if item.get("condition") == "good"]
    if len(good_items) >= 2:
        return "high"
    if len(good_items) == 1:
        return "medium"
    if owned_items:
        return "low"
    return "none"


def compute_budget_risk(price: int, remaining_budget: int) -> str:
    if price > remaining_budget:
        return "high"
    if remaining_budget <= 0:
        return "high"
    if price >= remaining_budget * 0.8:
        return "medium"
    return "low"


def compute_impulse_risk(reason: str, urgency: str) -> str:
    normalized_reason = reason.strip().lower()
    has_impulse_keyword = any(keyword in normalized_reason for keyword in IMPULSE_KEYWORDS)
    if urgency == "low" and has_impulse_keyword:
        return "high"
    if urgency == "medium" and has_impulse_keyword:
        return "medium"
    if urgency == "low":
        return "medium"
    return "low"


def _risk_to_points(risk: str) -> int:
    return {
        "none": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
    }.get(risk, 0)


def judge_purchase_logic(
    item: str,
    price: int,
    category: str,
    urgency: str,
    reason: str,
    owned_items: list[dict[str, Any]],
    budget: dict[str, Any],
) -> dict[str, Any]:
    related_owned_items = find_owned_by_category(owned_items, category)
    remaining_budget = get_remaining_budget(budget)
    duplicate_risk = compute_duplicate_risk(related_owned_items)
    budget_risk = compute_budget_risk(price, remaining_budget)
    impulse_risk = compute_impulse_risk(reason, urgency)

    has_bad_existing_item = any(
        owned.get("condition") == "bad" for owned in related_owned_items
    )
    risk_score = (
        _risk_to_points(duplicate_risk)
        + _risk_to_points(budget_risk)
        + _risk_to_points(impulse_risk)
    )

    if urgency == "high" and has_bad_existing_item and price <= remaining_budget:
        verdict = "approve"
        explanation = (
            f"{item}은 기존 {category} 품목 상태가 나쁘고 긴급도가 높아 구매를 승인합니다."
        )
        cooldown_days = 0
    elif urgency == "high" and has_bad_existing_item:
        verdict = "replace_only"
        explanation = (
            f"{item}은 교체 필요성은 있지만 남은 예산을 초과하므로 기존 물건 교체 조건으로만 허용합니다."
        )
        cooldown_days = 7
    elif budget_risk == "high" and duplicate_risk == "high":
        verdict = "reject"
        explanation = (
            f"{item}은 남은 예산을 초과하고 같은 카테고리의 양호한 보유품이 많아 기각합니다."
        )
        cooldown_days = 30
    elif budget_risk == "high" and urgency == "low":
        verdict = "reject"
        explanation = f"{item}은 긴급도가 낮은데 남은 예산을 초과하므로 기각합니다."
        cooldown_days = 30
    elif impulse_risk == "high":
        verdict = "cooldown"
        explanation = f"{item}은 충동구매 신호가 강하므로 냉각기간 후 다시 판단합니다."
        cooldown_days = 14
    elif budget_risk == "high":
        verdict = "cooldown"
        explanation = f"{item}은 예산 초과 위험이 커서 이번 달 구매는 보류합니다."
        cooldown_days = 14
    elif duplicate_risk == "high":
        verdict = "replace_only"
        explanation = (
            f"{item}은 유사한 보유품이 충분하므로 기존 물건을 처분하거나 교체할 때만 허용합니다."
        )
        cooldown_days = 7
    else:
        verdict = "approve"
        explanation = f"{item}은 예산과 중복 위험이 관리 가능한 수준이라 구매를 승인합니다."
        cooldown_days = 0

    return {
        "item": item,
        "price": price,
        "category": category,
        "urgency": urgency,
        "reason": reason,
        "verdict": verdict,
        "explanation": explanation,
        "cooldown_days": cooldown_days,
        "risk_score": risk_score,
        "duplicate_risk": duplicate_risk,
        "budget_risk": budget_risk,
        "impulse_risk": impulse_risk,
        "remaining_budget": remaining_budget,
        "owned_items_checked": related_owned_items,
        "currency": budget.get("currency", "KRW"),
    }


def render_verdict_markdown(verdicts: list[dict[str, Any]]) -> str:
    lines = [
        "# 장바구니 양심 재판 결과",
        "",
        "| 물건 | 가격 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for verdict in verdicts:
        row = {"currency": "KRW", **verdict}
        lines.append(
            "| {item} | {price:,} {currency} | {verdict} | {duplicate_risk} | "
            "{budget_risk} | {impulse_risk} | {explanation} |".format(
                **row,
            )
        )

    lines.extend(
        [
            "",
            "## 판결 기준",
            "",
            "- `approve`: 예산과 필요성이 충분히 맞아 구매 승인",
            "- `cooldown`: 충동 또는 예산 위험이 있어 냉각기간 후 재검토",
            "- `reject`: 예산 초과와 중복 위험이 커서 기각",
            "- `replace_only`: 기존 물건 처분 또는 교체 조건에서만 허용",
        ]
    )
    return "\n".join(lines) + "\n"
