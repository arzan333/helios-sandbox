"""Generate data/helios-tickets.csv.

Deterministic: the same seed always produces the same file, so every participant
sees identical numbers and facilitators can check answers.

Bottlenecks are planted on purpose. Two stages wait far longer than the rest:
  - design_start  waits on a single architect
  - test_start    waits on a shared QA environment
Week 1 participants are expected to find them from the data, not be told.

Run:  python scripts/generate_tickets.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20260101
START = datetime(2025, 9, 1, 9, 0)
DAYS = 182  # six months
COUNT = 210

OUT = Path(__file__).resolve().parents[1] / "data" / "helios-tickets.csv"

WORKFLOWS = {
    # name              share  systems
    "intake":           (0.34, ["OrderCore", "Shop", "Insight", "Billing"]),
    "defect_triage":    (0.30, ["OrderCore", "Shop", "Billing"]),
    "release_notes":    (0.14, ["OrderCore", "Shop"]),
    "developer_onboarding": (0.10, ["OrderCore"]),
    "change_approval":  (0.12, ["OrderCore", "Billing", "Insight"]),
}

# Two tickets are pinned because the labs refer to them by number.
# The twelve tickets that also exist as full text in helios-backlog/ are pinned so
# the CSV title and the ticket summary can never drift apart.
PINNED = {
    "HEL-018": ("defect_triage", "Invoice total ignores line level discount", "Billing"),
    "HEL-035": ("defect_triage", "Cart badge count wrong after removing an item", "Shop"),
    "HEL-061": ("intake", "Support split shipment on order confirmation", "OrderCore"),
    "HEL-077": ("defect_triage", "Order search times out beyond 500 results", "OrderCore"),
    "HEL-089": ("release_notes", "Compile release notes for the monthly drop", "OrderCore"),
    "HEL-104": ("change_approval", "Approve schema change on the orders table", "OrderCore"),
    "HEL-118": ("defect_triage", "Currency rounding differs between Shop and Billing", "Billing"),
    "HEL-133": ("defect_triage", "Duplicate confirmation email on retry", "OrderCore"),
    "HEL-142": ("intake", "Show estimated delivery window in the cart", "Shop"),
    "HEL-166": ("developer_onboarding", "Onboard a new developer to OrderCore", "OrderCore"),
    "HEL-181": ("intake", "Allow partial refund against a paid invoice", "Billing"),
    "HEL-207": ("intake", "Add discount code field to the order API", "OrderCore"),
}

OWNERS = ["Business Analyst", "Developer", "Architect", "Quality Engineer", "Release Manager"]
PRIORITIES = ["low", "medium", "high"]

REWORK_REASONS = [
    "acceptance criteria missing",
    "design not reviewed",
    "wrong system identified",
    "no test evidence",
    "scope changed after analysis",
]

# Stage gaps in working hours: (min, max). The two planted bottlenecks are wide.
GAPS = {
    "triaged":        (1, 6),
    "analysis_start": (2, 10),
    "analysis_done":  (3, 14),
    "design_start":   (16, 72),   # BOTTLENECK - waiting on the architect
    "design_done":    (4, 16),
    "build_start":    (2, 12),
    "build_done":     (6, 30),
    "test_start":     (12, 60),   # BOTTLENECK - waiting on the QA environment
    "test_done":      (4, 18),
    "deployed":       (2, 10),
    "closed":         (1, 5),
}

STAGES = list(GAPS.keys())

TITLES = {
    "intake": [
        "Support split shipment on order confirmation",
        "Add customer purchase order reference to checkout",
        "Show estimated delivery window in the cart",
        "Allow partial refund against a paid invoice",
        "Capture marketing consent at account creation",
        "Add discount code field to the order API",
    ],
    "defect_triage": [
        "Invoice total ignores line level discount",
        "Cart badge count wrong after removing an item",
        "Order search times out beyond 500 results",
        "Duplicate confirmation email on retry",
        "Currency rounding differs between Shop and Billing",
    ],
    "release_notes": [
        "Compile release notes for the monthly drop",
        "Summarise defects fixed since last release",
        "Publish upgrade steps for the Shop bundle",
    ],
    "developer_onboarding": [
        "Onboard a new developer to OrderCore",
        "Refresh the local environment setup guide",
    ],
    "change_approval": [
        "Approve schema change on the orders table",
        "Approve new outbound call from OrderCore to Billing",
        "Approve retention change on Insight extracts",
    ],
}


def working_hours_later(moment: datetime, hours: float) -> datetime:
    """Advance a timestamp by working hours, skipping nights and weekends."""
    remaining = hours
    current = moment
    while remaining > 0:
        if current.weekday() >= 5:                       # weekend
            current = (current + timedelta(days=1)).replace(hour=9, minute=0)
            continue
        end_of_day = current.replace(hour=18, minute=0)
        if current >= end_of_day:
            current = (current + timedelta(days=1)).replace(hour=9, minute=0)
            continue
        available = (end_of_day - current).total_seconds() / 3600
        step = min(available, remaining)
        current = current + timedelta(hours=step)
        remaining -= step
    return current


def pick_workflow(rng: random.Random) -> str:
    roll = rng.random()
    running = 0.0
    for name, (share, _systems) in WORKFLOWS.items():
        running += share
        if roll <= running:
            return name
    return "intake"


def main() -> None:
    rng = random.Random(SEED)
    rows = []

    for index in range(1, COUNT + 1):
        ticket_id = f"HEL-{index:03d}"
        workflow, title, system = PINNED.get(ticket_id, (None, None, None))
        if workflow is None:
            workflow = pick_workflow(rng)
        systems = WORKFLOWS[workflow][1]
        created = START + timedelta(
            days=rng.randint(0, DAYS - 10),
            hours=rng.randint(0, 7),
            minutes=rng.choice([0, 15, 30, 45]),
        )
        if created.weekday() >= 5:
            created += timedelta(days=2)

        row = {
            "ticket_id": ticket_id,
            "workflow": workflow,
            "title": title or rng.choice(TITLES[workflow]),
            "system": system or rng.choice(systems),
            "priority": rng.choices(PRIORITIES, weights=[3, 5, 2])[0],
            "owner_role": rng.choice(OWNERS),
            "created": created,
        }

        moment = created
        for stage in STAGES:
            low, high = GAPS[stage]
            # release notes and onboarding skip design and build effort
            if workflow in ("release_notes", "developer_onboarding") and stage in (
                "design_start",
                "design_done",
            ):
                low, high = 1, 4
            gap = rng.uniform(low, high)
            moment = working_hours_later(moment, gap)
            row[stage] = moment

        rework = rng.choices([0, 1, 2], weights=[70, 24, 6])[0]
        row["rework_count"] = rework
        row["rework_reason"] = rng.choice(REWORK_REASONS) if rework else ""
        rows.append(row)

    fields = (
        ["ticket_id", "workflow", "title", "system", "priority", "owner_role", "created"]
        + STAGES
        + ["rework_count", "rework_reason"]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in ["created"] + STAGES:
                out[key] = row[key].strftime("%Y-%m-%d %H:%M")
            writer.writerow(out)

    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
