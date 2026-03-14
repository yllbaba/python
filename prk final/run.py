from __future__ import annotations

import argparse
import subprocess
import sys
from typing import List, Optional


def run_api() -> int:
    return subprocess.call(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]
    )


def run_dashboard() -> int:
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", "dashboard/streamlit_app.py"]
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Basketball Game Tracker")
    parser.add_argument("target", choices=["api", "dashboard"])
    args = parser.parse_args(argv)

    if args.target == "api":
        return run_api()
    return run_dashboard()


if __name__ == "__main__":
    raise SystemExit(main())
