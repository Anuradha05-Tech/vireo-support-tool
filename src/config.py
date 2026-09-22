"""
src/config.py - Configuration paths and constants for vireo-support-tool.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Project directory paths
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
VALIDATION_DIR = PROJECT_ROOT / "validation"
DOCS_DIR = PROJECT_ROOT / "docs"

def resolve_data_file(pattern: str, default_name: str) -> Path:
    """Find a file in DATA_DIR matching a glob pattern or exact name."""
    exact = DATA_DIR / default_name
    if exact.exists():
        return exact
    matches = list(DATA_DIR.glob(pattern))
    if matches:
        return matches[0]
    return exact

# Expected Data File Paths (resolved dynamically to handle UUID-prefixed filenames)
TICKETS_CSV_PATH = resolve_data_file("*tickets*.csv", "tickets.csv")
AGENTS_CSV_PATH = resolve_data_file("*agents*.csv", "agents.csv")
CUSTOMERS_CSV_PATH = resolve_data_file("*customers*.csv", "customers.csv")
ORDERS_CSV_PATH = resolve_data_file("*orders*.csv", "orders.csv")
PRODUCTS_CSV_PATH = resolve_data_file("*products*.csv", "products.csv")
SUPPORT_POLICY_PDF_PATH = resolve_data_file("*support*.pdf", "support-policy.pdf")
README_TXT_PATH = resolve_data_file("*README*.txt", "README.txt")
EMAIL_THREAD_TXT_PATH = resolve_data_file("*email*.txt", "email-thread.txt")

# Financial & Policy Constants (Values confirmed from support-policy.pdf & architecture doc)
BLEND_COST_PER_CONTACT_INR = 290.0
CHANNEL_COST_INR = {
    "chat": 210.0,
    "email": 260.0,
    "voice": 520.0,
    "social": 240.0,
}
INTERNAL_TRANSFER_COST_INR = 305.0
AGENT_HOURLY_COST_INR = 165.0
SLA_BREACH_CREDIT_INR = 350.0
REVERSE_FORWARD_SHIPPING_COST_INR = 340.0
GOODWILL_CREDIT_CAP_INR = 500.0

# Repeat Contact Window (in days)
REPEAT_CONTACT_WINDOW_DAYS = 30

# Ticket Status & Filtering Constants
QUALIFIED_RESOLVED_STATUSES = {"resolved", "closed"}
CSAT_LEGACY_NULL_VALUE = 0  # 0 CSAT in legacy rows represents missing score, not literal 0

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", "")))
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")

# Ensure required output directories exist
for path in [REPORTS_DIR, VALIDATION_DIR, DATA_DIR]:
    path.mkdir(parents=True, exist_ok=True)
