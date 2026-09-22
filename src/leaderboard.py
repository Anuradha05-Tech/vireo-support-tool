"""
src/leaderboard.py - Stage 7 Tier 1 Agent Leaderboard Generator.
Generates agent volume rankings for Tier 1 and resolution time metrics for Tier 2,
rendering reports/leaderboard_latest.html per docs/06_REPORT_DESIGN.md.
"""

import sys
from pathlib import Path
import pandas as pd
import duckdb

from src.config import (
    PROJECT_ROOT,
    TICKETS_CSV_PATH,
    AGENTS_CSV_PATH,
    REPORTS_DIR,
    QUALIFIED_RESOLVED_STATUSES,
)


def run_agent_leaderboard():
    print("=" * 80)
    print("STAGE 7 — AGENT LEADERBOARD GENERATOR")
    print("=" * 80)

    # 1. Load Data
    print(f"Loading tickets from: {TICKETS_CSV_PATH}")
    tickets_df = pd.read_csv(TICKETS_CSV_PATH, low_memory=False)
    
    # Deduplicate tickets on ticket_id
    tickets_df["source_priority"] = tickets_df["source_system"].map({"helpdesk": 1, "legacy_fd": 2})
    tickets_df = (
        tickets_df.sort_values("source_priority")
        .drop_duplicates(subset=["ticket_id"], keep="first")
        .drop(columns=["source_priority"])
    )

    print(f"Loading agents from: {AGENTS_CSV_PATH}")
    agents_df = pd.read_csv(AGENTS_CSV_PATH)
    
    # Standardize tier column as string or integer
    agents_df["tier_str"] = agents_df["tier"].astype(str).str.strip()

    # Deduplicate agents roster by agent_id (if multi-row roster, take latest)
    agents_roster = agents_df.drop_duplicates(subset=["agent_id"], keep="first").copy()

    # 2. Week Grouping
    tickets_df["created_at_dt"] = pd.to_datetime(tickets_df["created_at"], errors="coerce")
    tickets_df["resolved_at_dt"] = pd.to_datetime(tickets_df["resolved_at"], errors="coerce")
    
    # Use resolved_at for leaderboard closed counts, fallback to created_at
    tickets_df["event_dt"] = tickets_df["resolved_at_dt"].fillna(tickets_df["created_at_dt"])
    tickets_df["week_start"] = tickets_df["event_dt"].dt.to_period("W-SUN").dt.start_time

    # Filter for complete weeks
    unique_weeks = sorted(tickets_df["week_start"].dropna().unique())
    complete_weeks = [w for w in unique_weeks if w >= pd.Timestamp("2025-01-06") and w <= pd.Timestamp("2026-06-22")]

    latest_complete_week_start = complete_weeks[-1]
    prior_complete_week_start = complete_weeks[-2]

    latest_week_end = latest_complete_week_start + pd.Timedelta(days=6)
    prior_week_end = prior_complete_week_start + pd.Timedelta(days=6)

    latest_week_str = f"{latest_complete_week_start.strftime('%b %d, %Y')} – {latest_week_end.strftime('%b %d, %Y')}"
    prior_week_str = f"{prior_complete_week_start.strftime('%b %d, %Y')} – {prior_week_end.strftime('%b %d, %Y')}"

    print(f"Latest Complete Week : {latest_week_str}")
    print(f"Prior Complete Week  : {prior_week_str}")

    # 3. Filter Tickets by Status in {resolved, closed}
    qualified_tickets = tickets_df[
        tickets_df["status"].str.lower().isin(["resolved", "closed"])
    ].copy()

    # 4. Join Tickets with Agents Roster
    merged_df = qualified_tickets.merge(
        agents_roster[["agent_id", "name", "team", "site", "tier_str"]],
        on="agent_id",
        how="inner"
    )

    # ---------------------------------------------------------
    # 5. TIER 1 FRONT-LINE LEADERBOARD (tier == '1')
    # ---------------------------------------------------------
    tier1_agents = agents_roster[agents_roster["tier_str"] == "1"].copy()
    tier1_agent_ids = set(tier1_agents["agent_id"])

    # Count tickets for latest week
    latest_t1_df = merged_df[
        (merged_df["tier_str"] == "1") & 
        (merged_df["week_start"] == latest_complete_week_start)
    ]
    latest_counts = latest_t1_df.groupby("agent_id").size().to_dict()

    # Count tickets for prior week
    prior_t1_df = merged_df[
        (merged_df["tier_str"] == "1") & 
        (merged_df["week_start"] == prior_complete_week_start)
    ]
    prior_counts = prior_t1_df.groupby("agent_id").size().to_dict()

    # Build Tier 1 Leaderboard Table
    t1_leaderboard = []
    for _, agent_row in tier1_agents.iterrows():
        a_id = agent_row["agent_id"]
        name = agent_row["name"]
        team = agent_row["team"]
        site = agent_row["site"]

        count_latest = latest_counts.get(a_id, 0)
        count_prior = prior_counts.get(a_id, 0)
        delta = count_latest - count_prior

        t1_leaderboard.append({
            "agent_id": a_id,
            "name": name,
            "team": team,
            "site": site,
            "count_latest": count_latest,
            "count_prior": count_prior,
            "delta": delta,
        })

    t1_df = pd.DataFrame(t1_leaderboard).sort_values(
        by=["count_latest", "count_prior", "name"], ascending=[False, False, True]
    ).reset_index(drop=True)

    t1_df["rank"] = t1_df.index + 1

    print("\nTier 1 Agent Leaderboard Top 10:")
    print(t1_df[["rank", "name", "team", "count_latest", "count_prior", "delta"]].head(10).to_string(index=False))

    # ---------------------------------------------------------
    # 6. TIER 2 WARRANTY & ESCALATIONS METRICS (tier == '2')
    # ---------------------------------------------------------
    tier2_agents = agents_roster[agents_roster["tier_str"] == "2"].copy()
    tier2_agent_ids = set(tier2_agents["agent_id"])

    latest_t2_df = merged_df[
        (merged_df["tier_str"] == "2") & 
        (merged_df["week_start"] == latest_complete_week_start)
    ].copy()

    # Compute resolution time in days for Tier 2 tickets
    latest_t2_df["resolution_days"] = (
        (latest_t2_df["resolved_at_dt"] - latest_t2_df["created_at_dt"]).dt.total_seconds() / 86400.0
    )

    t2_summary = []
    for _, agent_row in tier2_agents.iterrows():
        a_id = agent_row["agent_id"]
        name = agent_row["name"]
        team = agent_row["team"]
        site = agent_row["site"]

        agent_t2_tickets = latest_t2_df[latest_t2_df["agent_id"] == a_id]
        closed_count = len(agent_t2_tickets)
        median_res_days = agent_t2_tickets["resolution_days"].median() if closed_count > 0 else None

        t2_summary.append({
            "agent_id": a_id,
            "name": name,
            "team": team,
            "site": site,
            "closed_count": closed_count,
            "median_res_days": f"{median_res_days:.1f} days" if pd.notna(median_res_days) else "N/A",
        })

    t2_df = pd.DataFrame(t2_summary)
    print("\nTier 2 Escalations & Warranty Resolution Metrics (Not Ranked by Volume):")
    print(t2_df.to_string(index=False))

    # ---------------------------------------------------------
    # 7. Render HTML Report per docs/06_REPORT_DESIGN.md
    # ---------------------------------------------------------
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Leaderboard - Vireo Audio Support</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --paper: #F6F5F1;
            --ink: #1B1D1F;
            --rule: #C9C6BE;
            --signal: #2F6F62;
            --spike: #B5482F;
            --muted: #6B6862;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--paper);
            color: var(--ink);
            font-family: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        header {{
            border-bottom: 1px solid var(--rule);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}

        h1 {{
            font-size: 28px;
            line-height: 1.15;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-bottom: 4px;
        }}

        .meta-date {{
            font-size: 13px;
            color: var(--muted);
        }}

        .section-title {{
            font-size: 16px;
            font-weight: 600;
            margin: 28px 0 12px 0;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            font-variant-numeric: tabular-nums;
            margin-bottom: 24px;
        }}

        th {{
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: var(--muted);
            border-bottom: 1px solid var(--rule);
            padding: 8px 4px;
            text-transform: uppercase;
        }}

        th.num, td.num {{
            text-align: right;
        }}

        td {{
            padding: 10px 4px;
            border-bottom: 1px solid var(--rule);
            font-size: 14px;
        }}

        .rank-col {{
            width: 48px;
            font-weight: 600;
            color: var(--muted);
        }}

        .agent-name {{
            font-weight: 600;
        }}

        .sub-text {{
            font-size: 12px;
            color: var(--muted);
        }}

        .delta-pos {{
            color: var(--signal);
            font-weight: 600;
        }}

        .delta-neg {{
            color: var(--spike);
        }}

        /* Tier 2 Card Container */
        .tier2-block {{
            background: #FFFFFF;
            border: 1px solid var(--rule);
            padding: 16px;
            margin-top: 32px;
        }}

        .tier2-header {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .tier2-sub {{
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 12px;
        }}

        footer {{
            margin-top: 36px;
            padding-top: 16px;
            border-top: 1px solid var(--rule);
            font-size: 12px;
            color: var(--muted);
        }}

        .caveat-box {{
            background: #FFFFFF;
            border-left: 3px solid var(--rule);
            padding: 10px 14px;
            font-size: 12px;
            color: var(--muted);
            margin-top: 24px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tier 1 Agent Leaderboard</h1>
            <div class="meta-date">Week of {latest_week_str} &bull; Qualified Tickets Closed (Resolved & Closed)</div>
        </header>

        <div class="section-title">
            <span>Frontline Tier 1 Performance Ranking</span>
            <span style="font-size: 12px; color: var(--muted); font-weight: normal;">{len(t1_df)} Tier 1 Agents</span>
        </div>

        <table>
            <thead>
                <tr>
                    <th class="rank-col">Rank</th>
                    <th>Agent Name</th>
                    <th>Team / Site</th>
                    <th class="num">Closed This Week</th>
                    <th class="num">Prior Week</th>
                    <th class="num">Δ vs Prior</th>
                </tr>
            </thead>
            <tbody>
"""

    for _, r in t1_df.iterrows():
        delta_str = f"+{r['delta']}" if r['delta'] > 0 else (f"{r['delta']}" if r['delta'] < 0 else "0")
        delta_class = "delta-pos" if r['delta'] > 0 else ("delta-neg" if r['delta'] < 0 else "")

        html_content += f"""                <tr>
                    <td class="rank-col">#{r['rank']}</td>
                    <td class="agent-name">{r['name']}</td>
                    <td>{r['team']} <span class="sub-text">({r['site']})</span></td>
                    <td class="num"><strong>{r['count_latest']}</strong></td>
                    <td class="num">{r['count_prior']}</td>
                    <td class="num {delta_class}">{delta_str}</td>
                </tr>
"""

    html_content += f"""            </tbody>
        </table>

        <!-- Tier 2 Separate Section -->
        <div class="tier2-block">
            <div class="tier2-header">Tier 2 Escalations & Warranty Team — Resolution Efficiency</div>
            <div class="tier2-sub">Measured on median days-to-resolution per policy §6 (Not ranked by ticket volume).</div>
            
            <table>
                <thead>
                    <tr>
                        <th>Agent Name</th>
                        <th>Team / Site</th>
                        <th class="num">Cases Closed This Week</th>
                        <th class="num">Median Days-to-Resolution</th>
                    </tr>
                </thead>
                <tbody>
"""

    for _, r in t2_df.iterrows():
        html_content += f"""                    <tr>
                        <td class="agent-name">{r['name']}</td>
                        <td>{r['team']} <span class="sub-text">({r['site']})</span></td>
                        <td class="num">{r['closed_count']}</td>
                        <td class="num"><strong>{r['median_res_days']}</strong></td>
                    </tr>
"""

    html_content += f"""                </tbody>
            </table>
        </div>

        <div class="caveat-box">
            <strong>Policy Caveat (§6 & §10):</strong> Tier 1 agents are ranked strictly by tickets closed (resolved + closed). This volume metric does not account for ticket complexity, category difficulty, or handle time. Tier 2 agents are evaluated separately on resolution time.
        </div>

        <footer>
            <span>Vireo Audio Support Intelligence System &bull; Confidential Internal Leaderboard</span>
        </footer>
    </div>
</body>
</html>
"""

    # 8. Save HTML File
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_html_path = REPORTS_DIR / "leaderboard_latest.html"
    with open(report_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nSUCCESS: Generated agent leaderboard HTML report at: {report_html_path}")
    return report_html_path


if __name__ == "__main__":
    run_agent_leaderboard()
