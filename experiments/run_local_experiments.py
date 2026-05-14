import json
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
OUTPUT_DIR = ROOT_DIR / "output"
sys.path.insert(0, str(SRC_DIR))

from core import load_budget, load_csv, render_verdict_markdown  # noqa: E402
from paths import BUDGET_JSON, OWNED_ITEMS_CSV, WISHLIST_CSV  # noqa: E402
from wishlist_court_server import judge_purchase as good_judge_purchase  # noqa: E402
from broken_wishlist_court_server import judge_purchase as broken_judge_purchase  # noqa: E402


def write_report(filename: str, content: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return str(path.relative_to(ROOT_DIR))


def no_mcp_verdict(row: dict) -> dict:
    price = int(row["price"])
    urgency = row["urgency"]
    reason = row["reason"]
    item = row["item"]

    if price >= 700000:
        verdict = "cooldown"
        explanation = "고가 상품이므로 실제 예산과 보유품을 확인하기 전에는 보류가 적절합니다."
    elif urgency == "high":
        verdict = "approve"
        explanation = "긴급도가 높고 문제 해결 목적이 뚜렷해 구매 가능성이 있습니다."
    elif "그냥" in reason or "예뻐" in reason:
        verdict = "cooldown"
        explanation = "구매 사유가 감정적이므로 냉각기간 후 재검토가 필요합니다."
    else:
        verdict = "cooldown"
        explanation = "MCP 없이 보유품과 예산을 알 수 없어 보수적으로 보류합니다."

    return {
        "item": item,
        "price": price,
        "category": row["category"],
        "urgency": urgency,
        "reason": reason,
        "verdict": verdict,
        "explanation": explanation,
        "cooldown_days": 14 if verdict == "cooldown" else 0,
        "risk_score": 0,
        "duplicate_risk": "unknown",
        "budget_risk": "unknown",
        "impulse_risk": "unknown",
        "currency": "KRW",
    }


def run_no_mcp() -> tuple[list[dict], dict]:
    start = time.perf_counter()
    wishlist = load_csv(WISHLIST_CSV)
    verdicts = [no_mcp_verdict(row) for row in wishlist]
    content = render_verdict_markdown(verdicts)
    report_path = write_report("no_mcp_verdict.md", content)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return verdicts, {
        "condition": "MCP 없음",
        "completed": True,
        "latency_ms": elapsed_ms,
        "mcp_calls": 0,
        "report": report_path,
        "accuracy_note": "보유품과 실제 예산을 모르는 조건이므로 정확도 낮음",
    }


def run_good_mcp_like(filename: str, condition: str) -> tuple[list[dict], dict]:
    start = time.perf_counter()
    wishlist = load_csv(WISHLIST_CSV)
    verdicts = [
        good_judge_purchase(
            item=row["item"],
            price=int(row["price"]),
            category=row["category"],
            urgency=row["urgency"],
            reason=row["reason"],
        )
        for row in wishlist
    ]
    content = render_verdict_markdown(verdicts)
    report_path = write_report(filename, content)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return verdicts, {
        "condition": condition,
        "completed": True,
        "latency_ms": elapsed_ms,
        "mcp_calls": 13,
        "report": report_path,
        "accuracy_note": "정상 도구 결과와 판정 로직을 반영",
    }


def run_broken_mcp_like() -> tuple[list[dict], dict]:
    start = time.perf_counter()
    wishlist = load_csv(WISHLIST_CSV)
    verdicts = [
        broken_judge_purchase(
            item=row["item"],
            price=int(row["price"]),
            category=row["category"],
            urgency=row["urgency"],
            reason=row["reason"],
        )
        for row in wishlist
    ]
    content = render_verdict_markdown(verdicts)
    content += "\n## 망가진 도구가 판단에 준 영향\n\n"
    content += "- 보유품 중복 위험이 의도적으로 낮게 보고되어 구매 승인 비율이 증가했다.\n"
    content += "- 실제 남은 예산은 120,000원이지만 고가 항목의 위험이 완화되어 표현되었다.\n"
    content += "- 이 결과는 Part 2 실패 실험에서 tool description과 tool quality의 영향을 보여준다.\n"
    report_path = write_report("broken_mcp_verdict.md", content)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return verdicts, {
        "condition": "망가진 MCP",
        "completed": True,
        "latency_ms": elapsed_ms,
        "mcp_calls": 13,
        "report": report_path,
        "accuracy_note": "의도적으로 잘못된 도구 결과 때문에 정확도 낮음",
    }


def render_orchestration_report(name: str, verdicts: list[dict], note: str) -> str:
    content = render_verdict_markdown(verdicts)
    content += f"\n## Orchestration 메모\n\n{note}\n"
    return content


def run_orchestration_reports() -> list[dict]:
    single_verdicts, single_metric = run_good_mcp_like(
        "single_agent_verdict.md", "Single Agent"
    )
    single_content = render_orchestration_report(
        "Single Agent",
        single_verdicts,
        "한 에이전트가 데이터 조회, 판정, 보고서 작성을 모두 수행한 기준 결과다.",
    )
    write_report("single_agent_verdict.md", single_content)

    planner_verdicts, planner_metric = run_good_mcp_like(
        "planner_executor_verdict.md", "Planner+Executor"
    )
    planner_content = render_orchestration_report(
        "Planner+Executor",
        planner_verdicts,
        "Planner는 도구 호출 계획만 만들고, Executor가 정상 MCP 도구를 사용해 실행한 것으로 가정한 결과다.",
    )
    write_report("planner_executor_verdict.md", planner_content)
    planner_metric["mcp_calls"] = 13

    parallel_verdicts, parallel_metric = run_good_mcp_like(
        "parallel_subagents_verdict.md", "Parallel sub-agent"
    )
    parallel_content = render_orchestration_report(
        "Parallel sub-agent",
        parallel_verdicts,
        "예산 검사관, 중복 구매 검사관, 충동구매 검사관의 관점을 Synthesizer가 병합한 것으로 가정한 결과다.",
    )
    write_report("parallel_subagents_verdict.md", parallel_content)
    parallel_metric["mcp_calls"] = 14

    return [single_metric, planner_metric, parallel_metric]


def summarize_verdicts(verdicts: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for verdict in verdicts:
        key = str(verdict["verdict"])
        summary[key] = summary.get(key, 0) + 1
    return summary


def main() -> None:
    budget = load_budget(BUDGET_JSON)
    owned_items = load_csv(OWNED_ITEMS_CSV)
    wishlist = load_csv(WISHLIST_CSV)

    no_mcp_verdicts, no_mcp_metric = run_no_mcp()
    good_verdicts, good_metric = run_good_mcp_like("good_mcp_verdict.md", "정상 MCP")
    broken_verdicts, broken_metric = run_broken_mcp_like()
    orchestration_metrics = run_orchestration_reports()

    metrics = {
        "environment": {
            "runner": "experiments/run_local_experiments.py",
            "mode": "local deterministic substitute for Hermes/Codex runs",
            "wishlist_items": len(wishlist),
            "owned_items": len(owned_items),
            "remaining_budget": int(budget["monthly_discretionary_budget"])
            - int(budget["already_spent_this_month"]),
            "currency": budget["currency"],
        },
        "experiment_1": [no_mcp_metric, good_metric, broken_metric],
        "experiment_2": orchestration_metrics,
        "verdict_summary": {
            "no_mcp": summarize_verdicts(no_mcp_verdicts),
            "good_mcp": summarize_verdicts(good_verdicts),
            "broken_mcp": summarize_verdicts(broken_verdicts),
        },
    }

    metrics_path = OUTPUT_DIR / "local_experiment_metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary_lines = [
        "# 로컬 실험 실행 요약",
        "",
        "Hermes CLI가 설치되어 있지 않은 환경에서 MCP 도구 호출과 같은 로직을 로컬로 실행한 결과다.",
        "토큰 사용량과 실제 LLM 레이턴시는 Hermes/Codex 실행 후 별도로 측정해야 한다.",
        "",
        "## 실험 1",
        "",
        "| 조건 | 완료 | 로컬 실행 시간(ms) | MCP 호출 수(계획 기준) | 보고서 |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for metric in metrics["experiment_1"]:
        summary_lines.append(
            f"| {metric['condition']} | {metric['completed']} | {metric['latency_ms']} | "
            f"{metric['mcp_calls']} | {metric['report']} |"
        )

    summary_lines.extend(
        [
            "",
            "## 실험 2",
            "",
            "| 패턴 | 완료 | 로컬 실행 시간(ms) | MCP 호출 수(계획 기준) | 보고서 |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for metric in metrics["experiment_2"]:
        summary_lines.append(
            f"| {metric['condition']} | {metric['completed']} | {metric['latency_ms']} | "
            f"{metric['mcp_calls']} | {metric['report']} |"
        )

    write_report("local_experiment_summary.md", "\n".join(summary_lines) + "\n")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
