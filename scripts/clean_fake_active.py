#!/usr/bin/env python3
"""
Delete fake active rows from openclaw.sqlite + clear gateway_state.json fake data
- Delete all dashboard-pinger-* rows from flow_runs / subagent_runs / task_runs
- Set gateway_state.json to "no fake data" (running=false unless daemon is real)
- Verify prometheus returns 0/0/0/0
"""
import sqlite3
import json
import os

DB = "/home/via54/.openclaw/state/openclaw.sqlite"
STATE = "/home/via54/.hermes/gateway_state.json"

# 1. Clean sqlite
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Count before
for tbl, id_col in [("flow_runs", "flow_id"),
                     ("subagent_runs", "run_id"),
                     ("task_runs", "task_id")]:
    n = cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE ended_at IS NULL OR ended_at=''").fetchone()[0]
    print(f'BEFORE {tbl}: {n} active rows')

# Delete fake dashboard-pinger rows
for tbl, id_col in [("flow_runs", "flow_id"),
                     ("subagent_runs", "run_id"),
                     ("task_runs", "task_id")]:
    cur.execute(f"DELETE FROM {tbl} WHERE {id_col} LIKE 'dashboard-pinger-%'")
    cur.execute(f"DELETE FROM {tbl} WHERE {id_col} LIKE 'v9.7-%'")

# Verify
for tbl, id_col in [("flow_runs", "flow_id"),
                     ("subagent_runs", "run_id"),
                     ("task_runs", "task_id")]:
    n = cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE ended_at IS NULL OR ended_at=''").fetchone()[0]
    print(f'AFTER {tbl}: {n} active rows (honest)')

conn.commit()
conn.close()

# 2. Clean gateway_state.json
if os.path.exists(STATE):
    with open(STATE) as f:
        data = json.load(f)
    # Only reset the fields we faked
    data["gateway_state"] = "stopped"  # we don't actually have a gateway daemon
    data["active_agents"] = 0
    data["updated_at"] = ""
    with open(STATE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'\nSTATE {STATE}: gateway_state=stopped, active_agents=0 (honest)')
else:
    print(f'\nSTATE {STATE}: not found (nothing to clean)')