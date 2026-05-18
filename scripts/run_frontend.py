import subprocess
from pathlib import Path

if __name__ == "__main__":
    subprocess.check_call(["npm", "run", "dev"], cwd=Path(__file__).resolve().parents[1] / "frontend")
