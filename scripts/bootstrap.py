import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def ensure_venv() -> Path:
    if not PYTHON.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    return PYTHON


def install() -> None:
    python = ensure_venv()
    subprocess.check_call([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(python), "-m", "pip", "install", "-e", ".[dev]"], cwd=ROOT)
    subprocess.check_call(["npm", "install"], cwd=ROOT / "frontend")


if __name__ == "__main__":
    install()
