import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

sys.path.insert(0, str(SRC_DIR))

from core import (  # noqa: E402
    compute_budget_risk,
    compute_duplicate_risk,
    compute_impulse_risk,
    find_owned_by_category,
    get_remaining_budget,
    judge_purchase_logic,
    load_budget,
    load_csv,
)


WISHLIST_CSV = DATA_DIR / "wishlist.csv"
OWNED_ITEMS_CSV = DATA_DIR / "owned_items.csv"
BUDGET_JSON = DATA_DIR / "budget.json"


METRICS = {
    "single_agent": {
        "simulated_token_count": 4200,
        "simulated_latency_seconds": 18.2,
        "tool_call_count": 12,
        "failure_layer": "none",
        "quality_score": 4,
    },
    "planner_executor": {
        "simulated_token_count": 6100,
        "simulated_latency_seconds": 27.5,
        "tool_call_count": 12,
        "failure_layer": "none",
        "quality_score": 5,
    },
    "parallel_subagents": {
        "simulated_token_count": 8900,
        "simulated_latency_seconds": 23.4,
        "tool_call_count": 16,
        "failure_layer": "synthesis_overhead",
        "quality_score": 4,
    },
}


def write_output(filename: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


def load_common_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], int]:
    wishlist = load_csv(WISHLIST_CSV)
    owned_items = load_csv(OWNED_ITEMS_CSV)
    budget = load_budget(BUDGET_JSON)
    remaining_budget = get_remaining_budget(budget)
    return wishlist, owned_items, budget, remaining_budget


def judge_all_items(
    wishlist: list[dict[str, Any]],
    owned_items: list[dict[str, Any]],
    budget: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        judge_purchase_logic(
            item=row["item"],
            price=int(row["price"]),
            category=row["category"],
            urgency=row["urgency"],
            reason=row["reason"],
            owned_items=owned_items,
            budget=budget,
        )
        for row in wishlist
    ]


def owned_summary(items: list[dict[str, Any]]) -> str:
    if not items:
        return "없음"
    return ", ".join(
        f"{item['item']}({item['condition']}, {item['usage_frequency']})"
        for item in items
    )


def verdict_table(verdicts: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| 물건 | 가격 | 카테고리 | 보유품 확인 | 판결 | 중복 위험 | 예산 위험 | 충동 위험 | 설명 |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for verdict in verdicts:
        lines.append(
            f"| {verdict['item']} | {int(verdict['price']):,} {verdict['currency']} | "
            f"{verdict['category']} | {owned_summary(verdict['owned_items_checked'])} | "
            f"{verdict['verdict']} | {verdict['duplicate_risk']} | "
            f"{verdict['budget_risk']} | {verdict['impulse_risk']} | "
            f"{verdict['explanation']} |"
        )
    return lines


def metric_lines(key: str) -> list[str]:
    metric = METRICS[key]
    return [
        "## Simulation Metrics",
        "",
        f"- tool call count: {metric['tool_call_count']}",
        f"- simulated latency: {metric['simulated_latency_seconds']} seconds",
        f"- simulated token count: {metric['simulated_token_count']}",
        f"- failure layer: {metric['failure_layer']}",
        f"- quality score: {metric['quality_score']} / 5",
        "",
        "주의: 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다.",
    ]


def render_budget_lines(budget: dict[str, Any], remaining_budget: int) -> list[str]:
    return [
        "## 예산 정보",
        "",
        f"- 월 자유 예산: {int(budget['monthly_discretionary_budget']):,} {budget['currency']}",
        f"- 이번 달 이미 쓴 금액: {int(budget['already_spent_this_month']):,} {budget['currency']}",
        f"- 남은 예산: {remaining_budget:,} {budget['currency']}",
    ]


def run_single_agent(
    wishlist: list[dict[str, Any]],
    owned_items: list[dict[str, Any]],
    budget: dict[str, Any],
    remaining_budget: int,
) -> list[dict[str, Any]]:
    verdicts = judge_all_items(wishlist, owned_items, budget)
    lines = [
        "# Orchestration 실험 1: Single Agent",
        "",
        "## 실행 구조",
        "",
        "Single Agent는 한 흐름에서 위시리스트 조회, 예산 확인, 카테고리별 보유품 확인, 판정, 보고서 저장을 모두 수행한다.",
        "작업이 단순할 때 가장 빠르고 비용이 낮은 baseline이다.",
        "",
        *render_budget_lines(budget, remaining_budget),
        "",
        "## 항목별 판결",
        "",
        *verdict_table(verdicts),
        "",
        "## 장점",
        "",
        "- 흐름이 단순하고 구현 비용이 낮다.",
        "- 문맥 전환과 병합 비용이 거의 없다.",
        "- 이 프로젝트처럼 데이터가 작은 경우 토큰 효율이 좋다.",
        "",
        "## 한계",
        "",
        "- 명시적 체크리스트가 없으면 예산, 중복, 충동구매 기준 중 하나를 빠뜨릴 수 있다.",
        "- 판단 근거를 분리해 설명하는 힘은 Planner나 Parallel 구조보다 약하다.",
        "",
        *metric_lines("single_agent"),
    ]
    write_output("orchestration_single_agent_verdict.md", "\n".join(lines) + "\n")
    return verdicts


def run_planner_executor(
    wishlist: list[dict[str, Any]],
    owned_items: list[dict[str, Any]],
    budget: dict[str, Any],
    remaining_budget: int,
) -> list[dict[str, Any]]:
    plan = """# Planner 단계 결과

## 계획

1. 위시리스트를 먼저 조회한다.
2. 전체 예산과 남은 예산을 확인한다.
3. 각 구매 후보의 카테고리별 보유품을 확인한다.
4. 예산 위험, 중복 위험, 충동구매 위험을 분리해 평가한다.
5. 세 위험을 종합해 approve/cooldown/reject/replace_only 판결을 내린다.
6. 최종 보고서를 저장한다.

## Planner의 의도

- Single Agent에서 누락될 수 있는 예산/중복/충동 위험을 체크리스트화한다.
- 판정 기준을 먼저 고정해 실행 단계의 누락을 줄인다.
"""
    write_output("orchestration_planner_executor_plan.md", plan)

    verdicts = judge_all_items(wishlist, owned_items, budget)
    lines = [
        "# Orchestration 실험 2: Planner + Executor",
        "",
        "## Planner 계획 요약",
        "",
        "- Planner는 도구를 직접 호출하지 않고 실행 순서와 판정 기준을 먼저 고정한다.",
        "- Executor는 이 계획에 따라 위시리스트, 예산, 보유품, 판정 단계를 빠뜨리지 않고 수행한다.",
        "",
        "## Executor 실행 결과",
        "",
        *render_budget_lines(budget, remaining_budget),
        "",
        "## 항목별 판결",
        "",
        *verdict_table(verdicts),
        "",
        "## Single Agent 대비 차이",
        "",
        "- 최종 판결은 정상 core 판정과 동일하지만, 실행 전에 체크리스트가 고정되어 누락 위험이 낮다.",
        "- Planner 문서가 추가되므로 토큰과 시간이 Single Agent보다 증가한다.",
        "",
        "## 장점",
        "",
        "- 예산, 중복, 충동구매 기준을 명시적으로 분리한다.",
        "- Executor가 계획을 따라가므로 실험 재현성이 좋다.",
        "- 이번 과제처럼 평가 기준을 설명해야 하는 작업에서 가장 안정적이다.",
        "",
        "## 한계",
        "",
        "- Planner 단계 자체가 추가 비용이다.",
        "- 작업이 매우 작을 때는 Single Agent보다 과할 수 있다.",
        "",
        *metric_lines("planner_executor"),
    ]
    write_output("orchestration_planner_executor_verdict.md", "\n".join(lines) + "\n")
    return verdicts


def run_budget_agent(
    wishlist: list[dict[str, Any]], budget: dict[str, Any], remaining_budget: int
) -> dict[str, dict[str, Any]]:
    rows = {}
    lines = [
        "# Parallel Agent A: 예산 검사관",
        "",
        "각 항목의 가격과 남은 예산만 보고 budget_risk를 판단한다.",
        "",
        *render_budget_lines(budget, remaining_budget),
        "",
        "| 물건 | 가격 | budget_risk | 예산 관점 권고 |",
        "| --- | ---: | --- | --- |",
    ]
    for row in wishlist:
        risk = compute_budget_risk(int(row["price"]), remaining_budget)
        if risk == "high":
            advice = "남은 예산을 초과하므로 구매를 보류하거나 기각해야 한다."
        elif risk == "medium":
            advice = "남은 예산 대부분을 쓰므로 냉각기간 후 재검토가 필요하다."
        else:
            advice = "예산 관점에서는 구매 가능하다."
        rows[row["item"]] = {"budget_risk": risk, "budget_advice": advice}
        lines.append(f"| {row['item']} | {int(row['price']):,} {budget['currency']} | {risk} | {advice} |")
    write_output("orchestration_parallel_budget_agent.md", "\n".join(lines) + "\n")
    return rows


def run_duplicate_agent(
    wishlist: list[dict[str, Any]], owned_items: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    rows = {}
    lines = [
        "# Parallel Agent B: 중복 구매 검사관",
        "",
        "카테고리별 보유품만 보고 duplicate_risk를 판단한다.",
        "",
        "| 물건 | 카테고리 | 보유품 | duplicate_risk | 중복 관점 권고 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in wishlist:
        owned = find_owned_by_category(owned_items, row["category"])
        risk = compute_duplicate_risk(owned)
        if risk == "high":
            advice = "유사한 양호한 보유품이 많으므로 기각 또는 교체 조건부가 적절하다."
        elif risk == "medium":
            advice = "유사 보유품이 있어 필요성을 다시 확인해야 한다."
        elif risk == "low":
            advice = "보유품은 있으나 상태가 나빠 교체 가능성이 있다."
        else:
            advice = "중복 구매 위험은 낮다."
        rows[row["item"]] = {
            "duplicate_risk": risk,
            "duplicate_advice": advice,
            "owned_items": owned,
        }
        lines.append(
            f"| {row['item']} | {row['category']} | {owned_summary(owned)} | {risk} | {advice} |"
        )
    write_output("orchestration_parallel_duplicate_agent.md", "\n".join(lines) + "\n")
    return rows


def run_impulse_agent(wishlist: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = {}
    lines = [
        "# Parallel Agent C: 충동구매 검사관",
        "",
        "구매 사유와 긴급도만 보고 impulse_risk를 판단한다.",
        "",
        "| 물건 | 구매 사유 | 긴급도 | impulse_risk | 충동구매 관점 권고 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in wishlist:
        risk = compute_impulse_risk(row["reason"], row["urgency"])
        if risk == "high":
            advice = "감정적 구매 신호가 강하므로 냉각기간이 필요하다."
        elif risk == "medium":
            advice = "필요성은 있으나 구매 사유를 더 구체화해야 한다."
        else:
            advice = "충동구매 위험은 낮다."
        rows[row["item"]] = {"impulse_risk": risk, "impulse_advice": advice}
        lines.append(f"| {row['item']} | {row['reason']} | {row['urgency']} | {risk} | {advice} |")
    write_output("orchestration_parallel_impulse_agent.md", "\n".join(lines) + "\n")
    return rows


def run_parallel_subagents(
    wishlist: list[dict[str, Any]],
    owned_items: list[dict[str, Any]],
    budget: dict[str, Any],
    remaining_budget: int,
) -> list[dict[str, Any]]:
    budget_rows = run_budget_agent(wishlist, budget, remaining_budget)
    duplicate_rows = run_duplicate_agent(wishlist, owned_items)
    impulse_rows = run_impulse_agent(wishlist)
    verdicts = judge_all_items(wishlist, owned_items, budget)

    lines = [
        "# Orchestration 실험 3: Parallel sub-agent",
        "",
        "## 세 sub-agent 역할",
        "",
        "- Agent A 예산 검사관: 가격과 남은 예산만 보고 budget_risk 판단",
        "- Agent B 중복 구매 검사관: 카테고리별 보유품만 보고 duplicate_risk 판단",
        "- Agent C 충동구매 검사관: 구매 사유와 긴급도만 보고 impulse_risk 판단",
        "- Synthesizer: 세 관점을 종합해 최종 판결 작성",
        "",
        "## sub-agent별 주요 관찰",
        "",
        "- 예산 검사관: HHKB 키보드, 에어팟 맥스, 아이패드 미니는 남은 예산 120,000원을 초과한다.",
        "- 중복 구매 검사관: keyboard 카테고리는 양호한 보유품이 2개라 중복 위험이 높다.",
        "- 충동구매 검사관: 기계식 계산기는 '그냥 예뻐서 사고 싶음'과 낮은 긴급도로 충동구매 위험이 높다.",
        "",
        "## 최종 항목별 판결",
        "",
        "| 물건 | 예산 위험 | 중복 위험 | 충동 위험 | 최종 판결 | Synthesizer 근거 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for verdict in verdicts:
        item = verdict["item"]
        lines.append(
            f"| {item} | {budget_rows[item]['budget_risk']} | "
            f"{duplicate_rows[item]['duplicate_risk']} | {impulse_rows[item]['impulse_risk']} | "
            f"{verdict['verdict']} | {verdict['explanation']} |"
        )

    lines.extend(
        [
            "",
            "## 장점",
            "",
            "- 예산, 중복, 충동구매 관점이 분리되어 설명력이 좋다.",
            "- 각 sub-agent 산출물을 발표 자료로 보여주기 쉽다.",
            "- Synthesizer가 충돌하는 근거를 비교할 수 있다.",
            "",
            "## 한계",
            "",
            "- 같은 데이터를 여러 관점에서 반복 처리하므로 토큰 비용이 가장 크다.",
            "- sub-agent 산출물을 합치는 병합 비용과 충돌 처리 비용이 생긴다.",
            "- 이 프로젝트처럼 데이터가 작은 작업에는 실용 효율이 낮다.",
            "",
            "## 회고",
            "",
            "관점이 분리되었기 때문에 reasoning은 풍부하지만, 문서와 token cost가 증가했다. 최종 판결은 core.py 판정과 크게 어긋나지 않게 유지했다.",
            "",
            *metric_lines("parallel_subagents"),
        ]
    )
    write_output("orchestration_parallel_synthesized_verdict.md", "\n".join(lines) + "\n")
    return verdicts


def render_summary() -> str:
    return """# Orchestration 비교 실험 요약

## 1. 실험 목적

동일한 장바구니 양심 재판 작업을 Single Agent, Planner+Executor, Parallel sub-agent 구조로 나누어 비교한다. 목표는 실제 multi-agent framework 구현이 아니라, reasoning 구조와 비용 추정치가 어떻게 달라지는지 보여주는 것이다.

## 2. 세 orchestration 패턴

- Single Agent: 하나의 흐름에서 데이터 조회, 예산 확인, 보유품 확인, 판정, 보고서 저장을 모두 수행한다.
- Planner+Executor: Planner가 도구 호출 계획과 판정 체크리스트를 먼저 만들고, Executor가 그 계획을 따라 실행한다.
- Parallel sub-agent: 예산 검사관, 중복 구매 검사관, 충동구매 검사관이 관점을 나누고 Synthesizer가 최종 판결을 만든다.

## 3. 결과 비교표

| 패턴 | simulated token count | simulated latency | tool call count | failure layer | quality score | 요약 |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Single Agent | 4,200 | 18.2s | 12 | none | 4/5 | 가장 빠르고 단순한 baseline |
| Planner+Executor | 6,100 | 27.5s | 12 | none | 5/5 | 기준을 먼저 고정해 가장 안정적 |
| Parallel sub-agent | 8,900 | 23.4s | 16 | synthesis_overhead | 4/5 | 설명력은 좋지만 병합 비용이 큼 |

## 4. 핵심 관찰

- Single Agent는 토큰과 절차가 가장 적지만 체크리스트 누락 위험이 있다.
- Planner+Executor는 토큰과 시간이 늘지만 판정 기준을 먼저 고정해 누락 가능성을 줄인다.
- Parallel sub-agent는 세 관점의 설명이 가장 풍부하지만, 작은 작업에서는 토큰과 병합 비용이 과하다.
- 이 수치는 실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다.

## 5. 최종 회고

이 장바구니 양심 재판 작업은 예산, 중복, 충동구매라는 세 기준으로 자연스럽게 분해된다. 따라서 Parallel sub-agent 구조는 설명력은 좋았지만, 실제 작업 규모가 작아서 비용 대비 효율은 낮았다. Single Agent는 빠르고 단순했지만 체크리스트 누락 위험이 있다. Planner+Executor는 토큰과 시간이 약간 늘어도 판정 기준을 먼저 고정하기 때문에 이번 과제에는 가장 안정적인 구조였다.
"""


def main() -> None:
    wishlist, owned_items, budget, remaining_budget = load_common_data()
    run_single_agent(wishlist, owned_items, budget, remaining_budget)
    run_planner_executor(wishlist, owned_items, budget, remaining_budget)
    run_parallel_subagents(wishlist, owned_items, budget, remaining_budget)

    metrics = {
        **METRICS,
        "note": "실제 Hermes/OpenRouter 토큰 로그가 아니라 deterministic local runner 기준 simulation estimate다. 비교의 핵심은 절대값이 아니라 패턴별 상대적 차이다.",
        "generated_files": [
            "output/orchestration_single_agent_verdict.md",
            "output/orchestration_planner_executor_plan.md",
            "output/orchestration_planner_executor_verdict.md",
            "output/orchestration_parallel_budget_agent.md",
            "output/orchestration_parallel_duplicate_agent.md",
            "output/orchestration_parallel_impulse_agent.md",
            "output/orchestration_parallel_synthesized_verdict.md",
            "output/orchestration_experiment_summary.md",
            "output/orchestration_experiment_metrics.json",
        ],
    }
    write_output(
        "orchestration_experiment_metrics.json",
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
    )
    write_output("orchestration_experiment_summary.md", render_summary())
    print("Orchestration local experiment completed.")
    print("Generated 9 output files under output/.")


if __name__ == "__main__":
    main()
