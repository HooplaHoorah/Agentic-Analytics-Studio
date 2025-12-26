#!/usr/bin/env python3
"""Seed synthetic 'live' data into Postgres for the AAS Tableau dashboards.

Usage:
  python3 scripts/seed_demo_data.py --database-url "$DATABASE_URL" --rows 800

Notes:
- This script is intentionally dependency-light. It only needs psycopg2-binary.
- It generates realistic-ish pipeline data (stages, owners, regions, aging) plus an initial
  queue of pending actions.
"""

import argparse
import datetime as dt
import json
import os
import random
import string
import uuid

import psycopg2

STAGES = [
    "Prospecting",
    "Qualification",
    "Discovery",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]

REGIONS = ["East", "Central", "West", "South"]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
OWNERS = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi"]


def rand_amount(stage: str) -> float:
    base = {
        "Prospecting": 15000,
        "Qualification": 25000,
        "Discovery": 35000,
        "Proposal": 50000,
        "Negotiation": 70000,
        "Closed Won": 60000,
        "Closed Lost": 45000,
    }[stage]
    return float(max(1000, random.gauss(base, base * 0.55)))


def maybe_date(days_back: int, days_forward: int) -> dt.date:
    start = dt.date.today() - dt.timedelta(days=days_back)
    span = days_back + days_forward
    return start + dt.timedelta(days=random.randint(0, span))


def opp_id(i: int) -> str:
    return f"OPP{str(i).zfill(5)}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--database-url", default=os.getenv("DATABASE_URL"), required=False)
    p.add_argument("--rows", type=int, default=800)
    p.add_argument("--truncate", action="store_true", help="Delete existing demo rows first")
    args = p.parse_args()

    if not args.database_url:
        raise SystemExit("Missing --database-url (or DATABASE_URL)")

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = True

    with conn.cursor() as cur:
        if args.truncate:
            cur.execute("TRUNCATE aas_executions, aas_actions, aas_findings, aas_pipeline_runs, aas_opportunities RESTART IDENTITY CASCADE;")

        # opportunities
        for i in range(1, args.rows + 1):
            stage = random.choices(STAGES, weights=[18, 18, 16, 14, 10, 12, 12])[0]
            owner = random.choice(OWNERS)
            region = random.choice(REGIONS)
            segment = random.choice(SEGMENTS)

            created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=random.randint(5, 120))
            close_date = maybe_date(10, 120)
            last_touch = maybe_date(1, 60)

            # stage age tends to be higher in later stages
            stage_bias = {
                "Prospecting": 7,
                "Qualification": 14,
                "Discovery": 18,
                "Proposal": 25,
                "Negotiation": 35,
                "Closed Won": 2,
                "Closed Lost": 2,
            }[stage]
            stage_age = max(1, int(random.gauss(stage_bias, stage_bias * 0.55)))

            amt = rand_amount(stage)

            cur.execute(
                """
                INSERT INTO aas_opportunities (
                  opportunity_id, owner, region, segment, stage, amount,
                  created_at, close_date, last_touch_date, stage_age_days
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (opportunity_id) DO NOTHING;
                """,
                (
                    opp_id(i),
                    owner,
                    region,
                    segment,
                    stage,
                    amt,
                    created_at,
                    close_date,
                    last_touch,
                    stage_age,
                ),
            )

        # initial run + a few actions so Tableau has something before the first audit
        run_id = str(uuid.uuid4())
        now = dt.datetime.now(dt.timezone.utc)
        cur.execute(
            "INSERT INTO aas_pipeline_runs (run_id, run_ts, play, notes) VALUES (%s,%s,%s,%s)",
            (run_id, now, "seed", "initial seed"),
        )

        # pick a few risky opps: high stage age + high amount
        cur.execute(
            """
            SELECT opportunity_id, owner, region, stage, amount, stage_age_days
            FROM aas_opportunities
            WHERE stage NOT IN ('Closed Won','Closed Lost')
            ORDER BY (stage_age_days * amount) DESC
            LIMIT 25;
            """
        )
        rows = cur.fetchall()
        for (opportunity_id, owner, region, stage, amount, stage_age_days) in rows:
            action_id = str(uuid.uuid4())
            title = f"Nudge stalled deal {opportunity_id}"
            desc = f"Deal is stuck in {stage} for {stage_age_days} days; amount ${amount:,.0f}. Send follow-up + update CRM next step."
            payload = {
                "type": "salesforce_task",
                "opportunity_id": opportunity_id,
                "suggested_next_step": "Schedule follow-up call",
                "severity": "high" if stage_age_days > 25 else "medium",
            }
            cur.execute(
                """
                INSERT INTO aas_actions (
                  action_id, run_id, created_at, status, action_type, title, description,
                  priority, owner, region, stage, opportunity_id, payload
                ) VALUES (%s,%s,%s,'pending',%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    action_id,
                    run_id,
                    now,
                    payload["type"],
                    title,
                    desc,
                    1,
                    owner,
                    region,
                    stage,
                    opportunity_id,
                    json.dumps(payload),
                ),
            )

    conn.close()
    print(f"Seed complete. opportunities={args.rows}, initial_run={run_id}")


if __name__ == "__main__":
    main()
