"""
Streamlit Frontend Runner
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).resolve().parent / "frontend" / "app.py"
    print("Launching Follow-up Reply Assistant Streamlit UI...")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    subprocess.run(cmd)
