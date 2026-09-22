# Vireo Support Tool (`vireo-support-tool`)

An analytics, auditing, and intelligence pipeline for processing customer support ticket data, evaluating operational repeat-contact costs, auditing intake category tags, and rendering HTML digests and agent performance leaderboards for Vireo Audio.

---

## Quick Start & Reproduction Guide

### 1. Prerequisites
- **Python**: Version 3.10 or higher.
- **System Dependencies**: Standard C/C++ build tools or pre-built wheels for `duckdb` and `pdfplumber` (`pypdfium2`).

### 2. Environment Setup & Dependency Installation

Clone the repository and initialize a virtual environment:

```bash
git clone https://github.com/Anuradha05-Tech/vireo-support-tool.git
cd vireo-support-tool

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Input Data File Placement

Place all raw data files in the `data/` directory (note that `data/` is excluded from git):
- `tickets.csv` (or UUID-prefixed e.g. `*tickets.csv`)
- `agents.csv` (or UUID-prefixed e.g. `*agents*.csv`)
- `customers.csv`
- `orders.csv`
- `products.csv`
- `support-policy.pdf` (or `support-vireo.pdf`)
- `README.txt`
- `email-thread.txt`

### 4. API Key Configuration

Copy `.env.example` to `.env` and set your API key if making live LLM API calls:

```bash
cp .env.example .env
```

*Note: If no API key is provided, the pipeline seamlessly utilizes Gemini API Free Tier or zero-cost local evaluation.*

---

## Exact Pipeline Command Execution Sequence

Execute the pipeline in the following order:

```bash
# Stage 1: Data Exploration & Quality Profiling
python3 -m src.profile_data

# Stage 3: Stratified Category Tag Audit
python3 -m src.category_audit

# Stage 4: Repeat Contact Detection Pipeline (Structural 30-Day Join)
python3 -m src.repeat_contacts

# Stage 4 Follow-Up: Right-Censoring Review & Volume Reconciliation
python3 -m src.repeat_contacts_review

# Stage 5: 'Already Told You' Repeat Language Sweep
python3 -m src.repeat_language_sweep

# Stage 6: Weekly Support Digest Generator (HTML Report)
python3 -m src.weekly_digest

# Stage 7: Tier 1 Agent Performance Leaderboard (HTML Report)
python3 -m src.leaderboard

# Stage 8: Business Goal & Financial ROI Calculation
python3 -m src.business_goal

# AI Tool Build & Operating Run-Rate Cost Estimator
python3 -m src.tool_cost_estimate

# Stage 9: Pipeline Validation & Precision Reporting
python3 -m src.validate
```

---

## Output Artifact Sitemap

| Pipeline Stage / Script | Primary Output File | Output Description |
|---|---|---|
| `src.profile_data` | [`data_profile.md`](file:///home/user/Documents/vireo-support-tool/data_profile.md) | Schema checks, null rates, date ranges, CSAT zero counts, refund scale, ticket ID collisions. |
| `src.category_audit` | [`audit_report.md`](file:///home/user/Documents/vireo-support-tool/audit_report.md)<br>[`validation/category_audit_sample.csv`](file:///home/user/Documents/vireo-support-tool/validation/category_audit_sample.csv) | 99-ticket stratified sample audit report (90.91% agreement rate). |
| `src.repeat_contacts` | [`data/repeat_contacts.parquet`](file:///home/user/Documents/vireo-support-tool/data/repeat_contacts.parquet) | Parquet dataset of 30-day structural repeat contact pairs. |
| `src.repeat_contacts_review` | [`validation/repeat_contacts_review.md`](file:///home/user/Documents/vireo-support-tool/validation/repeat_contacts_review.md) | Right-censoring analysis (13.78% YTD rate) and volume growth sensitivity. |
| `src.repeat_language_sweep` | [`validation/repeat_language_sweep_results.csv`](file:///home/user/Documents/vireo-support-tool/validation/repeat_language_sweep_results.csv) | Unflagged tickets containing "already told you" repeat language (+7.62%). |
| `src.weekly_digest` | [`reports/digest_latest.html`](file:///home/user/Documents/vireo-support-tool/reports/digest_latest.html) | HTML report of top mover category, category ranking, and repeat rate. |
| `src.leaderboard` | [`reports/leaderboard_latest.html`](file:///home/user/Documents/vireo-support-tool/reports/leaderboard_latest.html) | HTML report ranking Tier 1 agents by closed volume and Tier 2 resolution times. |
| `src.business_goal` | [`validation/business_goal_summary.md`](file:///home/user/Documents/vireo-support-tool/validation/business_goal_summary.md) | Financial ROI calculation (₹23,220/qtr savings at 10.00% target rate). |
| `src.tool_cost_estimate` | [`validation/tool_cost_estimate.md`](file:///home/user/Documents/vireo-support-tool/validation/tool_cost_estimate.md) | Exact accounting of AI tool build costs (₹0.00 Free Tier / ₹0.17 Commercial). |
| `src.validate` | [`validation/validation_report.md`](file:///home/user/Documents/vireo-support-tool/validation/validation_report.md)<br>[`validation/repeat_contact_sample.csv`](file:///home/user/Documents/vireo-support-tool/validation/repeat_contact_sample.csv) | Validation report and 40 hand-verified repeat contact sample pairs. |

---

## Pipeline Execution Metrics & Cost Accounting

- **Total Execution Time**: **< 30 seconds** for the entire pipeline.
- **Actual Build Spend (Free Tier)**: **₹0.00 INR** ($0.00 USD).
- **Commercial API Rate Value**: **₹0.167 INR** (~17 paise for the entire 99-ticket audit build).
- **Monthly Operating Tool Cost**: **₹0.00 INR / month** on Gemini Free Tier (**₹0.17 / month** at commercial API rates for 100 periodic audit tickets + automated sweep).

---

## Known System Limitations & Methodological Assumptions

1. **Category + SKU Matching Proxy for "Same Issue"**:
   Because tickets lack a direct issue-linking ID, repeat-contact detection relies on exact `(category AND product_sku)` matching within 30 days of resolution. This serves as an unassailable baseline, though it excludes repeat queries where product SKU is unassigned.
2. **Legacy Data Caveats (`legacy_fd`)**:
   - Legacy Freshdesk records used `0` for missing CSAT survey responses (which must be nulled out prior to score averaging).
   - Re-imported legacy tickets contain 653 duplicate `ticket_id` collisions with current helpdesk rows; deduplication by `(ticket_id)` is enforced in code.
3. **Intake Bot Category Single Source of Truth**:
   The existing `category` field (bot-assigned at intake, agent-corrected on closure) is treated as the single source of truth for weekly reporting. Stage 3 verified a **90.91% agreement rate** on a 99-ticket sample, confirming full LLM reclassification is unnecessary.
4. **Tier 2 Leaderboard Exclusion by Design**:
   Per policy §6 and operational directives, Tier 2 Escalations & Warranty agents handle complex multi-day cases and are evaluated strictly on **resolution time** (median days), explicitly excluded from frontline ticket-volume rankings.

---

## License

Internal Analytics Tool — Vireo Audio.
