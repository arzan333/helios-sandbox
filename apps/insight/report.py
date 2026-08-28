"""Insight - reporting over Helios delivery data.

Two reports, both used by the training scenarios:

  stages   median and 90th percentile duration for every stage transition
  orders   order and invoice totals pulled live from OrderCore

Run:
    python apps/insight/report.py stages
    python apps/insight/report.py orders
"""

import argparse
import csv
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

TICKETS = Path(__file__).resolve().parents[2] / "data" / "helios-tickets.csv"
ORDERCORE_URL = "http://localhost:8080"

STAGES = [
    "created",
    "triaged",
    "analysis_start",
    "analysis_done",
    "design_start",
    "design_done",
    "build_start",
    "build_done",
    "test_start",
    "test_done",
    "deployed",
    "closed",
]


def parse(moment: str) -> datetime:
    return datetime.strptime(moment, "%Y-%m-%d %H:%M")


def load_tickets(workflow: str | None = None) -> list:
    with TICKETS.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if workflow:
        rows = [r for r in rows if r["workflow"] == workflow]
    return rows


def stage_report(workflow: str | None = None) -> None:
    rows = load_tickets(workflow)
    if not rows:
        print(f"No tickets found for workflow '{workflow}'.")
        return

    label = workflow or "all workflows"
    print(f"Stage durations in working hours - {label} ({len(rows)} tickets)\n")
    print(f"{'transition':<34}{'median':>9}{'p90':>9}")
    print("-" * 52)

    results = []
    for start, end in zip(STAGES, STAGES[1:], strict=False):
        gaps = sorted(
            (parse(r[end]) - parse(r[start])).total_seconds() / 3600 for r in rows
        )
        median = statistics.median(gaps)
        p90 = gaps[min(int(len(gaps) * 0.9), len(gaps) - 1)]
        results.append((f"{start} -> {end}", median, p90))
        print(f"{start + ' -> ' + end:<34}{median:>9.1f}{p90:>9.1f}")

    worst = sorted(results, key=lambda item: -item[1])[:3]
    print("\nLongest three by median:")
    for name, median, _p90 in worst:
        print(f"  {name:<32}{median:>7.1f} h")

    end_to_end = sorted(
        (parse(r["closed"]) - parse(r["created"])).total_seconds() / 3600 for r in rows
    )
    print(f"\nMedian created -> closed: {statistics.median(end_to_end):.1f} h")

    reworked = sum(1 for r in rows if int(r["rework_count"]) > 0)
    print(f"Rework rate: {reworked}/{len(rows)} = {100 * reworked / len(rows):.1f}%")

    reasons = Counter(r["rework_reason"] for r in rows if r["rework_reason"])
    if reasons:
        print("\nMost common rework reasons:")
        for reason, count in reasons.most_common(3):
            print(f"  {reason:<40}{count:>4}")


def order_report() -> None:
    # Imported here, not at module scope, so the stage report stays pure standard
    # library. Week 1 runs "report.py stages" on a machine that has never installed
    # the OrderCore requirements.
    try:
        import httpx
    except ImportError:
        print(
            "The orders report needs httpx. Install it with:\n"
            "  pip install -r apps/ordercore/requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    try:
        with httpx.Client(timeout=5.0) as client:
            orders = client.get(f"{ORDERCORE_URL}/orders").json()
            print(f"{'order':<12}{'customer':<22}{'status':<12}{'total':>12}")
            print("-" * 58)
            grand = 0
            for order in orders:
                invoice = client.get(
                    f"{ORDERCORE_URL}/orders/{order['order_id']}/invoice"
                ).json()
                grand += invoice["total_pence"]
                total = f"GBP {invoice['total_pence'] / 100:,.2f}"
                print(
                    f"{order['order_id']:<12}{order['customer']:<22}"
                    f"{order['status']:<12}{total:>12}"
                )
            print("-" * 58)
            print(f"{'':<46}{'GBP ' + format(grand / 100, ',.2f'):>12}")
    except httpx.HTTPError as exc:
        print(f"Could not reach OrderCore at {ORDERCORE_URL}: {exc}", file=sys.stderr)
        print("Start it with: uvicorn app.main:app --port 8080", file=sys.stderr)
        raise SystemExit(1) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Helios Insight reports")
    parser.add_argument("report", choices=["stages", "orders"])
    parser.add_argument(
        "--workflow",
        help="filter the stage report, e.g. request_to_release or defect_triage",
    )
    args = parser.parse_args()

    if args.report == "stages":
        stage_report(args.workflow)
    else:
        order_report()


if __name__ == "__main__":
    main()
