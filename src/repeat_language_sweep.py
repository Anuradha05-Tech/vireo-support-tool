"""
src/repeat_language_sweep.py - Stage 5 'already told you' language sweep for tickets missed by structural join.
"""

import sys
import re
import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from src.config import (
    PROJECT_ROOT,
    TICKETS_CSV_PATH,
    DATA_DIR,
    VALIDATION_DIR,
    LLM_API_KEY,
    LLM_MODEL_NAME,
)

# Robust Regex Pattern for "already told you" / repeat contact language
REPEAT_PHRASES_REGEX = re.compile(
    r"\b("
    r"already told|already reported|already spoke|already called|already emailed|"
    r"spoke to someone|spoke to your|told your colleague|as i mentioned|as mentioned earlier|"
    r"calling again|contacting again|writing again|emailed before|called before|"
    r"still waiting|no response since|no reply since|follow up on ticket|following up on|"
    r"second time|third time|multiple times|posted on twitter|escalate"
    r")\b",
    re.IGNORECASE,
)


def run_repeat_language_sweep():
    print("=" * 80)
    print("STAGE 5 — 'ALREADY TOLD YOU' LANGUAGE SWEEP")
    print("=" * 80)

    # 1. Load tickets
    print(f"Loading tickets dataset from: {TICKETS_CSV_PATH}")
    tickets_df = pd.read_csv(TICKETS_CSV_PATH, low_memory=False)
    
    # Deduplicate tickets on ticket_id
    tickets_df["source_priority"] = tickets_df["source_system"].map({"helpdesk": 1, "legacy_fd": 2})
    tickets_df = (
        tickets_df.sort_values("source_priority")
        .drop_duplicates(subset=["ticket_id"], keep="first")
        .drop(columns=["source_priority"])
    )

    tickets_df["created_at_dt"] = pd.to_datetime(tickets_df["created_at"], errors="coerce")
    tickets_df["resolved_at_dt"] = pd.to_datetime(tickets_df["resolved_at"], errors="coerce")

    # Resolved/Closed subset
    resolved_tickets_df = tickets_df[tickets_df["status"].str.lower().isin(["resolved", "closed"])]
    total_resolved_count = len(resolved_tickets_df)

    # 2. Load Stage 4 structural repeat contacts (Strategy 2: Category + SKU match)
    parquet_path = DATA_DIR / "repeat_contacts.parquet"
    if parquet_path.exists():
        struct_repeats_df = pd.read_parquet(parquet_path)
        # Filter for Strategy 2 (matched_on == 'both')
        strat2_df = struct_repeats_df[struct_repeats_df["matched_on"] == "both"] if "matched_on" in struct_repeats_df.columns else struct_repeats_df
        struct_repeat_ids = set(strat2_df["repeat_ticket_id"])
    else:
        struct_repeats_df = pd.DataFrame()
        struct_repeat_ids = set()

    print(f"Total Unique Dataset Tickets      : {len(tickets_df):,}")
    print(f"Total Resolved/Closed Tickets     : {total_resolved_count:,}")
    print(f"Structural Repeat Tickets (Stage 4 Strategy 2): {len(struct_repeat_ids):,}")

    # 3. Filter for tickets NOT already flagged as a repeat by Stage 4 Strategy 2
    unflagged_tickets = tickets_df[~tickets_df["ticket_id"].isin(struct_repeat_ids)].copy()
    print(f"Unflagged Tickets Swept in Stage 5: {len(unflagged_tickets):,}")

    # 4. Keyword / Regex Pre-Filter
    matches = []
    print("\nRunning keyword/regex pre-filter across unflagged messages...")
    for idx, row in unflagged_tickets.iterrows():
        msg = str(row["customer_message"])
        found = REPEAT_PHRASES_REGEX.findall(msg)
        if found:
            matched_unique = list(set(p.lower() for p in found))
            matches.append({
                "ticket_id": row["ticket_id"],
                "created_at": row["created_at"],
                "status": row["status"],
                "category": row["category"],
                "channel": row["channel"],
                "matched_phrase": matched_unique[0],
                "all_matched_phrases": ", ".join(matched_unique),
                "is_repeat_language": True,
                "customer_message": msg,
            })

    matches_df = pd.DataFrame(matches)
    match_count = len(matches_df)
    
    # 5. Compute Implied Repeat Contact Rates
    # Stage 4 Structural YTD rate (Jan-May 2026, n=3,926)
    censor_safe_start = pd.Timestamp("2026-01-01 00:00:00")
    censor_safe_end = pd.Timestamp("2026-05-31 23:59:59")

    stage4_ytd_resolved = tickets_df[
        (tickets_df["status"].str.lower().isin(["resolved", "closed"])) &
        (tickets_df["resolved_at_dt"] >= censor_safe_start) &
        (tickets_df["resolved_at_dt"] <= censor_safe_end)
    ]
    
    # Matches within Jan-May 2026 YTD window
    ytd_matches = matches_df[
        pd.to_datetime(matches_df["created_at"], errors="coerce") >= censor_safe_start
    ] if not matches_df.empty else pd.DataFrame()

    stage4_ytd_count = 541  # From Stage 4 Strategy 2 review (n=3,926, 13.78%)
    stage4_ytd_rate = 13.78

    stage5_ytd_match_count = len(ytd_matches)
    stage5_additional_rate = (stage5_ytd_match_count / len(stage4_ytd_resolved) * 100) if len(stage4_ytd_resolved) > 0 else 0
    combined_true_repeat_rate = stage4_ytd_rate + stage5_additional_rate

    # 6. Save results
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    results_path = VALIDATION_DIR / "repeat_language_sweep_results.csv"
    matches_df.to_csv(results_path, index=False)

    print("\n" + "=" * 80)
    print("STAGE 5 LANGUAGE SWEEP RESULTS SUMMARY")
    print("=" * 80)
    print(f"Unflagged Tickets Swept           : {len(unflagged_tickets):,}")
    print(f"Repeat-Language Matches Found     : {match_count:,} ({match_count/len(unflagged_tickets)*100:.2f}% of unflagged)")
    print(f"LLM Calls Made                    : 0 (Efficient regex/keyword pre-filter)")
    print(f"Stage 5 Estimated Cost            : ₹0.00 INR ($0.00 USD)")
    print("-" * 60)
    print(f"Stage 4 Structural YTD Repeat Rate : {stage4_ytd_rate:.2f}% ({stage4_ytd_count:,} tickets)")
    print(f"Stage 5 Additional Language Rate  : +{stage5_additional_rate:.2f}% (+{stage5_ytd_match_count:,} tickets missed by 30d join)")
    print(f"Combined Implied True Repeat Rate : {combined_true_repeat_rate:.2f}%")
    print("=" * 80 + "\n")

    print(f"Exported detailed results to: {results_path}")

    # Print top sample matches
    print("\nSample 'Already Told You' Customer Messages Missed by Structural Join:")
    for _, m_row in matches_df.head(6).iterrows():
        msg_snippet = str(m_row["customer_message"]).replace("\n", " ")
        if len(msg_snippet) > 85:
            msg_snippet = msg_snippet[:82] + "..."
        print(f"  • [`{m_row['ticket_id']}`] Category: {m_row['category']} | Matched: '{m_row['matched_phrase']}'")
        print(f"    Message: \"{msg_snippet}\"")
        print()

    return {
        "unflagged_swept": len(unflagged_tickets),
        "language_matches": match_count,
        "stage4_ytd_rate": stage4_ytd_rate,
        "stage5_additional_rate": stage5_additional_rate,
        "combined_true_rate": combined_true_repeat_rate,
        "results_path": results_path,
    }


if __name__ == "__main__":
    run_repeat_language_sweep()
