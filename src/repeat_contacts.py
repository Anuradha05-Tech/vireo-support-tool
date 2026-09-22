"""
src/repeat_contacts.py - Repeat contact detection pipeline based on support-policy.pdf §10.
"""

import sys
from pathlib import Path
import pandas as pd
import duckdb

from src.config import (
    PROJECT_ROOT,
    TICKETS_CSV_PATH,
    DATA_DIR,
    CHANNEL_COST_INR,
    QUALIFIED_RESOLVED_STATUSES,
    REPEAT_CONTACT_WINDOW_DAYS,
)


def run_repeat_contacts_detection():
    print("=" * 80)
    print("STAGE 4 — REPEAT CONTACT DETECTION PIPELINE")
    print("=" * 80)

    # 1. Load tickets dataset
    print(f"Loading dataset from: {TICKETS_CSV_PATH}")
    tickets_df = pd.read_csv(TICKETS_CSV_PATH, low_memory=False)
    print(f"Loaded {len(tickets_df):,} raw ticket rows.")

    # 2. Deduplicate tickets on ticket_id (favoring helpdesk over legacy_fd)
    # Stage 1 identified 653 duplicate ticket_ids re-imported from legacy_fd
    tickets_df["source_priority"] = tickets_df["source_system"].map({"helpdesk": 1, "legacy_fd": 2})
    tickets_df = (
        tickets_df.sort_values("source_priority")
        .drop_duplicates(subset=["ticket_id"], keep="first")
        .drop(columns=["source_priority"])
    )
    print(f"Unique tickets after deduplication: {len(tickets_df):,}")

    # Ensure datetime parsing for timestamp operations
    tickets_df["created_at_dt"] = pd.to_datetime(tickets_df["created_at"], errors="coerce")
    tickets_df["resolved_at_dt"] = pd.to_datetime(tickets_df["resolved_at"], errors="coerce")

    # Connect DuckDB for fast SQL window joins
    con = duckdb.connect()
    con.register("tickets", tickets_df)

    # Define channel cost mapping SQL CASE expression
    channel_cost_case = f"""
    CASE LOWER(repeat_channel)
        WHEN 'chat' THEN {CHANNEL_COST_INR['chat']}
        WHEN 'email' THEN {CHANNEL_COST_INR['email']}
        WHEN 'voice' THEN {CHANNEL_COST_INR['voice']}
        WHEN 'social' THEN {CHANNEL_COST_INR['social']}
        ELSE 290.0
    END
    """

    # ---------------------------------------------------------
    # Base SQL Query for 30-day window self-join
    # ---------------------------------------------------------
    base_join_sql = f"""
    SELECT 
        t1.ticket_id AS original_ticket_id,
        t2.ticket_id AS repeat_ticket_id,
        t1.customer_id,
        t1.resolved_at_dt AS original_resolved_at,
        t2.created_at_dt AS repeat_created_at,
        ROUND(CAST(EPOCH(t2.created_at_dt - t1.resolved_at_dt) AS DOUBLE) / 86400.0, 2) AS days_between,
        t1.category AS original_category,
        t2.category AS repeat_category,
        t1.product_sku AS original_sku,
        t2.product_sku AS repeat_sku,
        t2.channel AS repeat_channel,
        (t1.category = t2.category) AS same_category,
        (t1.product_sku = t2.product_sku) AS same_sku,
        {channel_cost_case} AS cost
    FROM tickets t1
    JOIN tickets t2
      ON t1.customer_id = t2.customer_id
     AND t1.ticket_id != t2.ticket_id
     AND t2.created_at_dt > t1.resolved_at_dt
     AND t2.created_at_dt <= t1.resolved_at_dt + INTERVAL {REPEAT_CONTACT_WINDOW_DAYS} DAYS
    WHERE LOWER(t1.status) IN ('resolved', 'closed')
      AND t1.resolved_at_dt IS NOT NULL
    """

    all_repeats_df = con.execute(base_join_sql).df()

    # Define matching strategies
    strat_both = all_repeats_df[all_repeats_df["same_category"] & all_repeats_df["same_sku"]].copy()
    strat_both["matched_on"] = "both"

    strat_cat_only = all_repeats_df[all_repeats_df["same_category"]].copy()
    strat_cat_only["matched_on"] = "category"

    strat_sku_only = all_repeats_df[all_repeats_df["same_sku"]].copy()
    strat_sku_only["matched_on"] = "sku"

    strat_either = all_repeats_df[all_repeats_df["same_category"] | all_repeats_df["same_sku"]].copy()
    
    # Assign matched_on label for either
    def get_matched_label(row):
        if row["same_category"] and row["same_sku"]:
            return "both"
        elif row["same_category"]:
            return "category"
        else:
            return "sku"

    strat_either["matched_on"] = strat_either.apply(get_matched_label, axis=1)

    # ---------------------------------------------------------
    # Analyze Q2 2026 (Last Quarter: 2026-04-01 to 2026-06-30)
    # ---------------------------------------------------------
    q2_start = pd.Timestamp("2026-04-01 00:00:00")
    q2_end = pd.Timestamp("2026-06-30 23:59:59")

    # Count resolved tickets in Q2 2026
    q2_resolved_df = tickets_df[
        (tickets_df["status"].str.lower().isin(["resolved", "closed"])) &
        (tickets_df["resolved_at_dt"] >= q2_start) &
        (tickets_df["resolved_at_dt"] <= q2_end)
    ]
    q2_resolved_count = len(q2_resolved_df)
    total_resolved_count = len(tickets_df[tickets_df["status"].str.lower().isin(["resolved", "closed"])])

    print(f"\nTotal Resolved Tickets (All Time): {total_resolved_count:,}")
    print(f"Total Resolved Tickets (Q2 2026 - Last Quarter): {q2_resolved_count:,}")

    # Function to print strategy stats
    def print_strategy_stats(name: str, df_strat: pd.DataFrame):
        q2_repeats = df_strat[
            (df_strat["original_resolved_at"] >= q2_start) & 
            (df_strat["original_resolved_at"] <= q2_end)
        ]
        
        all_cost = df_strat["cost"].sum()
        q2_cost = q2_repeats["cost"].sum()
        
        rate_all = (len(df_strat) / total_resolved_count * 100) if total_resolved_count > 0 else 0
        rate_q2 = (len(q2_repeats) / q2_resolved_count * 100) if q2_resolved_count > 0 else 0

        print("-" * 60)
        print(f"STRATEGY: {name}")
        print(f"  All-Time Repeats Found : {len(df_strat):,} ({rate_all:.2f}% of resolved)")
        print(f"  All-Time Total Cost    : ₹{all_cost:,.2f}")
        print(f"  Q2 2026 Repeats Found  : {len(q2_repeats):,} ({rate_q2:.2f}% of Q2 resolved)")
        print(f"  Q2 2026 Total Cost     : ₹{q2_cost:,.2f}")
        return {
            "strategy": name,
            "all_time_count": len(df_strat),
            "all_time_rate": rate_all,
            "all_time_cost": all_cost,
            "q2_count": len(q2_repeats),
            "q2_rate": rate_q2,
            "q2_cost": q2_cost,
        }

    stats_cat = print_strategy_stats("1. Category-Only Match (t1.category == t2.category)", strat_cat_only)
    stats_both = print_strategy_stats("2. Category + SKU Match (Both t1.category == t2.category AND t1.sku == t2.sku)", strat_both)
    stats_sku = print_strategy_stats("3. Product SKU-Only Match (t1.sku == t2.sku)", strat_sku_only)
    stats_either = print_strategy_stats("4. Category OR SKU Match (Either t1.category == t2.category OR t1.sku == t2.sku)", strat_either)

    print("-" * 60)

    # ---------------------------------------------------------
    # Save Selected Strategy to data/repeat_contacts.parquet
    # ---------------------------------------------------------
    # We output Category + SKU (Both) or Category-Only as primary defensible candidates.
    # We save Strategy 2 (Category + SKU) as the default parquet file, containing matched_on column.
    
    output_cols = [
        "original_ticket_id",
        "repeat_ticket_id",
        "customer_id",
        "days_between",
        "matched_on",
        "repeat_channel",
        "cost",
    ]
    
    # Format columns for parquet output
    parquet_df = strat_either[output_cols].copy()
    parquet_df.rename(columns={"repeat_channel": "channel"}, inplace=True)

    parquet_path = DATA_DIR / "repeat_contacts.parquet"
    parquet_df.to_parquet(parquet_path, index=False)
    print(f"\nSUCCESS: Exported {len(parquet_df):,} detected repeat contact records to: {parquet_path}")

    return {
        "cat_only": stats_cat,
        "both": stats_both,
        "sku_only": stats_sku,
        "either": stats_either,
        "parquet_path": parquet_path,
    }


if __name__ == "__main__":
    run_repeat_contacts_detection()
