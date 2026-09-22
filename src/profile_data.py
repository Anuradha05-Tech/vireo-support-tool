"""
src/profile_data.py - Data profiling and data-quality analysis script for vireo-support-tool.
"""

import sys
from pathlib import Path
import pandas as pd
import duckdb

# Import project configuration
from src.config import (
    PROJECT_ROOT,
    TICKETS_CSV_PATH,
    AGENTS_CSV_PATH,
    CUSTOMERS_CSV_PATH,
    ORDERS_CSV_PATH,
    PRODUCTS_CSV_PATH,
    README_TXT_PATH,
    EMAIL_THREAD_TXT_PATH,
)

EXPECTED_TICKET_COLUMNS = [
    "ticket_id",
    "created_at",
    "first_response_at",
    "resolved_at",
    "status",
    "channel",
    "customer_id",
    "order_id",
    "product_sku",
    "category",
    "priority",
    "assigned_team",
    "agent_id",
    "transfers",
    "csat_score",
    "refund_amount_inr",
    "refund_reason_code",
    "replacement_issued",
    "customer_message",
    "agent_notes",
    "source_system",
]


def run_profiling():
    output_lines = []

    def log(msg: str = ""):
        print(msg)
        output_lines.append(msg)

    log("=" * 80)
    log("VIREO SUPPORT TOOL - STAGE 1 DATA PROFILE REPORT")
    log("=" * 80)
    log()

    # ---------------------------------------------------------
    # 1. Load tickets.csv & Verify Schema
    # ---------------------------------------------------------
    log("### 1. Tickets Schema & Column Verification")
    log(f"Loading tickets from: {TICKETS_CSV_PATH}")
    if not TICKETS_CSV_PATH.exists():
        log(f"ERROR: Tickets CSV not found at {TICKETS_CSV_PATH}")
        sys.exit(1)

    tickets_df = pd.read_csv(TICKETS_CSV_PATH, low_memory=False)
    actual_cols = list(tickets_df.columns)

    log(f"Total Rows in tickets.csv: {len(tickets_df):,}")
    log(f"Actual Column Count: {len(actual_cols)}")

    missing_cols = set(EXPECTED_TICKET_COLUMNS) - set(actual_cols)
    extra_cols = set(actual_cols) - set(EXPECTED_TICKET_COLUMNS)

    if missing_cols or extra_cols:
        log("!!! COLUMN MISMATCH DETECTED !!!")
        if missing_cols:
            log(f"  Missing expected columns: {sorted(list(missing_cols))}")
        if extra_cols:
            log(f"  Extra unexpected columns: {sorted(list(extra_cols))}")
    else:
        log("SUCCESS: tickets.csv columns match expected architecture specification exactly!")
    log()

    # ---------------------------------------------------------
    # 2. General Data Summary (Null rates, Date ranges, Value Counts)
    # ---------------------------------------------------------
    log("### 2. General Data Summary & Column Metrics")
    
    # Date Range
    tickets_df['created_at_dt'] = pd.to_datetime(tickets_df['created_at'], errors='coerce')
    min_date = tickets_df['created_at_dt'].min()
    max_date = tickets_df['created_at_dt'].max()
    log(f"Date Range (created_at): {min_date} to {max_date}")
    log()

    # Null Rates Table
    log("#### Null Rates per Column:")
    null_info = []
    for col in actual_cols:
        null_count = tickets_df[col].isnull().sum()
        null_pct = (null_count / len(tickets_df)) * 100
        null_info.append({"Column": col, "Null Count": null_count, "Null Pct (%)": f"{null_pct:.2f}%"})
    
    null_df = pd.DataFrame(null_info)
    log(null_df.to_string(index=False))
    log()

    # Categorical Value Counts
    categorical_cols = [
        "status",
        "channel",
        "category",
        "priority",
        "assigned_team",
        "refund_reason_code",
        "source_system",
    ]

    for col in categorical_cols:
        log(f"#### Value Counts for `{col}`:")
        if col in tickets_df.columns:
            vc = tickets_df[col].value_counts(dropna=False).to_frame(name="Count")
            vc["Percentage (%)"] = (vc["Count"] / len(tickets_df) * 100).round(2)
            log(vc.to_string())
        else:
            log(f"Column `{col}` not found in tickets dataframe.")
        log()

    # ---------------------------------------------------------
    # 3. Check agents.csv & Tier Identification
    # ---------------------------------------------------------
    log("### 3. Agents Table Verification & Tier Mapping")
    log(f"Loading agents from: {AGENTS_CSV_PATH}")
    if AGENTS_CSV_PATH.exists():
        agents_df = pd.read_csv(AGENTS_CSV_PATH)
        log(f"Total Rows in agents.csv: {len(agents_df):,}")
        log(f"Columns in agents.csv: {list(agents_df.columns)}")
        
        if "tier" in agents_df.columns:
            tier_counts = agents_df["tier"].value_counts(dropna=False).to_frame(name="Agent Count")
            log("Unique `tier` values and agent counts:")
            log(tier_counts.to_string())
        else:
            log("!!! WARNING: `tier` column missing in agents.csv !!!")
    else:
        log(f"ERROR: Agents CSV not found at {AGENTS_CSV_PATH}")
    log()

    # ---------------------------------------------------------
    # 4. Specific Data-Quality Checks
    # ---------------------------------------------------------
    log("### 4. Data-Quality Deep Dives")

    # a. CSAT Score 0-values broken down by source_system
    log("#### 4a. CSAT Score Zero-Value Breakdown by source_system")
    if "csat_score" in tickets_df.columns and "source_system" in tickets_df.columns:
        # Check csat_score values
        csat_zero_mask = tickets_df["csat_score"] == 0
        csat_null_mask = tickets_df["csat_score"].isna()
        
        log(f"Total tickets with CSAT == 0: {csat_zero_mask.sum():,} ({csat_zero_mask.mean()*100:.2f}%)")
        log(f"Total tickets with CSAT is Null: {csat_null_mask.sum():,} ({csat_null_mask.mean()*100:.2f}%)")
        
        csat_by_source = (
            tickets_df.groupby("source_system")["csat_score"]
            .agg(
                total_tickets="count",
                zero_csat_count=lambda s: (s == 0).sum(),
                null_csat_count=lambda s: s.isna().sum(),
                valid_csat_count=lambda s: (s > 0).sum(),
                mean_including_zeros="mean",
                mean_excluding_zeros=lambda s: s[s > 0].mean(),
            )
            .reset_index()
        )
        log(csat_by_source.to_string(index=False))
    log()

    # b. refund_amount_inr summary stats by source_system
    log("#### 4b. Refund Amount (INR) Breakdown by source_system")
    if "refund_amount_inr" in tickets_df.columns and "source_system" in tickets_df.columns:
        refund_stats = (
            tickets_df.groupby("source_system")["refund_amount_inr"]
            .agg(
                total_rows="count",
                non_zero_rows=lambda s: (s > 0).sum(),
                sum_refund="sum",
                mean_refund="mean",
                median_refund="median",
                max_refund="max",
                min_refund="min",
            )
            .reset_index()
        )
        log(refund_stats.to_string(index=False))
    log()

    # c. ticket_id duplicate checks & legacy collision check
    log("#### 4c. Ticket ID Duplicates & Source Collision Check")
    if "ticket_id" in tickets_df.columns:
        total_tickets = len(tickets_df)
        unique_ticket_ids = tickets_df["ticket_id"].nunique()
        dupe_count = total_tickets - unique_ticket_ids
        log(f"Total ticket_id rows: {total_tickets:,}")
        log(f"Unique ticket_id count: {unique_ticket_ids:,}")
        log(f"Duplicate ticket_id count: {dupe_count:,}")

        if dupe_count > 0:
            log("Duplicate ticket_id sample:")
            dupes = tickets_df[tickets_df.duplicated(subset=["ticket_id"], keep=False)].sort_values("ticket_id")
            log(dupes[["ticket_id", "source_system", "created_at", "status"]].head(10).to_string(index=False))
        
        # Check ID prefixes / format per source system
        log("\nSample ticket_id values per source system:")
        sample_ids = tickets_df.groupby("source_system")["ticket_id"].apply(lambda s: list(s.head(5)))
        for src, ids in sample_ids.items():
            log(f"  {src}: {ids}")
    log()

    # d. order_id null rate & fallback join resolution against orders.csv
    log("#### 4d. Order ID Null Rate & Fallback Join Resolution Check")
    null_order_count = tickets_df["order_id"].isna().sum()
    null_order_pct = (null_order_count / len(tickets_df)) * 100
    log(f"Tickets missing order_id: {null_order_count:,} out of {len(tickets_df):,} ({null_order_pct:.2f}%)")

    if ORDERS_CSV_PATH.exists():
        log(f"Loading orders from: {ORDERS_CSV_PATH}")
        orders_df = pd.read_csv(ORDERS_CSV_PATH)
        log(f"Total rows in orders.csv: {len(orders_df):,}")
        log(f"Columns in orders.csv: {list(orders_df.columns)}")

        # Rename product SKU column if necessary
        order_sku_col = "product_sku" if "product_sku" in orders_df.columns else ("sku" if "sku" in orders_df.columns else None)
        
        if order_sku_col and "customer_id" in orders_df.columns:
            # Get tickets with missing order_id but having customer_id and product_sku
            missing_order_tickets = tickets_df[
                tickets_df["order_id"].isna() & 
                tickets_df["customer_id"].notna() & 
                tickets_df["product_sku"].notna()
            ].copy()
            
            log(f"Tickets missing order_id with valid customer_id & product_sku: {len(missing_order_tickets):,}")

            # Prepare orders lookup table (customer_id, sku -> order_id)
            orders_lookup = orders_df[["customer_id", order_sku_col, "order_id"]].dropna().drop_duplicates(subset=["customer_id", order_sku_col])
            
            # Merge to test resolution rate
            resolved = missing_order_tickets.merge(
                orders_lookup,
                left_on=["customer_id", "product_sku"],
                right_on=["customer_id", order_sku_col],
                how="inner",
                suffixes=("", "_resolved")
            )

            resolved_count = len(resolved)
            resolved_pct = (resolved_count / len(missing_order_tickets) * 100) if len(missing_order_tickets) > 0 else 0
            log(f"Successfully resolvable null order_ids via (customer_id + product_sku): {resolved_count:,} ({resolved_pct:.2f}%)")
        else:
            log(f"Cannot perform fallback join check: orders.csv missing customer_id or sku column.")
    else:
        log(f"ERROR: Orders CSV not found at {ORDERS_CSV_PATH}")
    log()

    # ---------------------------------------------------------
    # 5. Attach Reference Files (README.txt & email-thread.txt)
    # ---------------------------------------------------------
    log("=" * 80)
    log("REFERENCE DOCUMENTS")
    log("=" * 80)
    log()

    log("### Full Content of README.txt:")
    if README_TXT_PATH.exists():
        with open(README_TXT_PATH, "r", encoding="utf-8") as f:
            log(f.read())
    else:
        log(f"README.txt not found at {README_TXT_PATH}")
    log()

    log("### Full Content of email-thread.txt:")
    if EMAIL_THREAD_TXT_PATH.exists():
        with open(EMAIL_THREAD_TXT_PATH, "r", encoding="utf-8") as f:
            log(f.read())
    else:
        log(f"email-thread.txt not found at {EMAIL_THREAD_TXT_PATH}")
    log()

    # Write output to data_profile.md
    profile_md_path = PROJECT_ROOT / "data_profile.md"
    with open(profile_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log("=" * 80)
    log(f"SUCCESS: Data profiling complete! Full report saved to {profile_md_path}")
    log("=" * 80)


if __name__ == "__main__":
    run_profiling()
