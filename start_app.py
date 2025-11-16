"""
Cross-platform launcher for the WaiterAI Streamlit app.

Usage:
  python start_app.py            # runs on http://127.0.0.1:8501
  python start_app.py --port 8502

Notes:
- Loads environment variables from .env if present.
- Validates presence of critical env vars (DATABASE_URL, optional ANTHROPIC_API_KEY).
- Runs Streamlit bound to localhost only.
"""
from __future__ import annotations

import argparse
import os
import sys
import shutil
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser(description="Start the WaiterAI app on localhost")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the app on (default: 8501)")
    args = parser.parse_args()

    # Load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        # dotenv is optional; Streamlit app also tries to load it
        pass

    # Validate required env vars early to fail fast with a helpful message
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[ERROR] DATABASE_URL is not set. Create a .env file with DATABASE_URL before starting.")
        print("        Example: DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/waiterai?charset=utf8mb4")
        return 1

    # Anthropic key is optional for starting, the UI will warn if missing
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[WARN] ANTHROPIC_API_KEY is not set. The chat will show a warning until you add it to .env.")

    # Ensure streamlit is available
    # Use module invocation via current Python to be cross-platform
    cmd = [sys.executable, "-m", "streamlit", "run", os.path.join(os.path.dirname(__file__), "app.py"),
           "--server.address", "127.0.0.1", "--server.port", str(args.port)]

    # Helpful hint if streamlit is missing
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except FileNotFoundError:
        print("[ERROR] Could not find Streamlit. Install dependencies first:")
        print("        pip install -r requirements.txt")
        return 1
    except subprocess.CalledProcessError as e:
        # Streamlit printed its own error; just propagate non-zero code
        return e.returncode


if __name__ == "__main__":
    raise SystemExit(main())
