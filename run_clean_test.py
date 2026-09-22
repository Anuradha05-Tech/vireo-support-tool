"""
run_clean_test.py - Clean room runner to test README command sequence.
"""

import subprocess
import time
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python3"

COMMANDS = [
    ("Stage 1: Data Profiling", "src.profile_data", ["data_profile.md"]),
    ("Stage 3: Category Audit", "src.category_audit", ["audit_report.md", "validation/category_audit_sample.csv"]),
    ("Stage 4: Repeat Contacts Structural Join", "src.repeat_contacts", ["data/repeat_contacts.parquet"]),
    ("Stage 4 Review: Censoring & Volume Review", "src.repeat_contacts_review", ["validation/repeat_contacts_review.md"]),
    ("Stage 5: Language Sweep", "src.repeat_language_sweep", ["validation/repeat_language_sweep_results.csv"]),
    ("Stage 6: Weekly Digest", "src.weekly_digest", ["reports/digest_latest.html"]),
    ("Stage 7: Agent Leaderboard", "src.leaderboard", ["reports/leaderboard_latest.html"]),
    ("Stage 8: Business Goal ROI", "src.business_goal", ["validation/business_goal_summary.md"]),
    ("AI Tool Cost Estimator", "src.tool_cost_estimate", ["validation/tool_cost_estimate.md"]),
    ("Stage 9: Validation & Precision", "src.validate", ["validation/validation_report.md", "validation/repeat_contact_sample.csv"]),
    ("Stage 10: Summary Dashboard", "src.summary_dashboard", ["reports/summary_dashboard.html"]),
]


def run_clean_test():
    print("=" * 80)
    print("CLEAN-ROOM REPRODUCIBILITY TEST RUNNER")
    print("=" * 80)
    print(f"Python Executable: {VENV_PYTHON}\n")

    results = []

    for name, module, expected_files in COMMANDS:
        cmd_str = f"python3 -m {module}"
        print(f"--> Running: {cmd_str} ({name})")
        start_time = time.perf_counter()
        
        proc = subprocess.run(
            [str(VENV_PYTHON), "-m", module],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        elapsed = time.perf_counter() - start_time

        succeeded = (proc.returncode == 0)
        
        produced_details = []
        for rel_path in expected_files:
            abs_p = PROJECT_ROOT / rel_path
            if abs_p.exists():
                stat = abs_p.stat()
                size_bytes = stat.st_size
                mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                produced_details.append(f"{rel_path} ({size_bytes:,} bytes, {mtime_str})")
            else:
                produced_details.append(f"{rel_path} (MISSING!)")

        results.append({
            "name": name,
            "cmd": cmd_str,
            "succeeded": succeeded,
            "returncode": proc.returncode,
            "elapsed_sec": elapsed,
            "expected_files": expected_files,
            "produced_details": produced_details,
            "stderr": proc.stderr.strip(),
        })

        status_str = "SUCCESS" if succeeded else f"FAILED (code {proc.returncode})"
        print(f"    Status: {status_str} | Duration: {elapsed:.2f}s")
        for pd_info in produced_details:
            print(f"    File: {pd_info}")
        if not succeeded:
            print(f"    Error output:\n{proc.stderr[:300]}")
        print("-" * 60)

    # Summary of outputs under reports/ and validation/
    print("\n" + "=" * 80)
    print("FINAL OUTPUT FILE LISTING UNDER reports/ AND validation/")
    print("=" * 80)

    for target_dir_name in ["reports", "validation"]:
        target_dir = PROJECT_ROOT / target_dir_name
        print(f"\nDirectory: {target_dir_name}/")
        if target_dir.exists():
            files = sorted(list(target_dir.glob("*")))
            for f in files:
                if f.is_file():
                    stat = f.stat()
                    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                    print(f"  • {f.name:<38} | Size: {stat.st_size:>9,} bytes | Last Modified: {mtime}")
        else:
            print("  Directory does not exist!")

    print("\n" + "=" * 80)
    print("CLEAN-ROOM TEST REPORT SUMMARY")
    print("=" * 80)
    failures = [r for r in results if not r["succeeded"]]
    missing_files = [
        pd_info for r in results for pd_info in r["produced_details"] if "MISSING" in pd_info or "0 bytes" in pd_info
    ]

    print(f"Total Commands Executed: {len(COMMANDS)}")
    print(f"Commands Succeeded     : {len(COMMANDS) - len(failures)}")
    print(f"Commands Failed        : {len(failures)}")
    print(f"Suspicious/Missing Files: {len(missing_files)}")

    if failures:
        print("\nFailed Commands:")
        for f in failures:
            print(f"  - {f['cmd']}: {f['stderr']}")
    else:
        print("\nALL COMMANDS SUCCEEDED CLEANLY WITH EXIT CODE 0.")

    if missing_files:
        print("\nSuspicious Output Files:")
        for mf in missing_files:
            print(f"  - {mf}")
    else:
        print("NO MISSING OR EMPTY OUTPUT FILES DETECTED.")


if __name__ == "__main__":
    run_clean_test()
