# Vireo Support Tool (`vireo-support-tool`)

An analytics and intelligence tool for processing, auditing, and generating insights from customer support ticket data for Vireo Audio.

## Project Structure

```text
vireo-support-tool/
├── README.md              # Project documentation and setup guide
├── requirements.txt       # Python dependencies (pandas, duckdb, pdfplumber, LLM SDK, etc.)
├── .env.example           # Environment variables template
├── .gitignore             # Git exclusion rules (data/, .env, __pycache__, *.pyc)
├── docs/                  # Planning and architecture documentation
├── data/                  # Raw input datasets (tickets.csv, agents.csv, policy PDF, etc.) [gitignored]
├── src/                   # Python source code package
│   ├── __init__.py
│   └── config.py          # Centralized configuration, directory paths, and business policy constants
├── reports/               # Output directory for generated HTML and summary reports
└── validation/            # Output directory for audit, validation samples, and data profile reports
```

## Core Features & Tech Stack

- **Data Processing & Analytics:** Built on **Pandas** and **DuckDB** for efficient relational querying across support tickets, customer details, orders, and agent data.
- **PDF Policy Extraction:** Uses **pdfplumber** to inspect `support-policy.pdf` and extract cost structures, SLA terms, and policy parameters programmatically.
- **Environment Management:** Powered by **python-dotenv** for API key management and environment isolation.
- **LLM Integration:** Pluggable LLM SDK support for targeted category tag audits and repeat-contact message flag checks.
- **Centralized Configuration:** All paths and financial metrics (e.g. ₹290 blended contact cost) are configured in `src/config.py`.

## Getting Started

### 1. Prerequisites & Virtual Environment

Ensure you have Python 3.10+ installed. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Installation

Install required Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and set your API keys:

```bash
cp .env.example .env
```

Edit `.env` to supply your LLM API key and configuration settings.

### 4. Data Setup

Drop the input data files into the `data/` directory (note that `data/` is excluded from git):
- `tickets.csv`
- `agents.csv`
- `customers.csv`
- `orders.csv`
- `products.csv`
- `support-policy.pdf`

## Project Configuration & Constants

All business rules, path constants, and unit economics are defined in [`src/config.py`](file:///home/user/Documents/vireo-support-tool/src/config.py):
- **Blended Contact Cost:** ₹290.0
- **Repeat Contact Window:** 30 days
- **CSAT Null Value Normalization:** Legacy 0 normalized to null score
- **Qualified Resolution Statuses:** `resolved`, `closed`

## License

Internal Tool - Vireo Audio.
