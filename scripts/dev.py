import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
TAXONOMY_IMPORT_DIR = ROOT / "data/taxonomy/imports"


def run_checked(command: list[str], cwd: Path = ROOT) -> None:
    subprocess.check_call(command, cwd=cwd)


def ensure_install() -> Path:
    if not VENV_PYTHON.exists():
        run_checked([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    run_checked([str(VENV_PYTHON), "-m", "pip", "install", "-e", ".[dev]"])
    run_checked(["npm", "install"], cwd=ROOT / "frontend")
    return VENV_PYTHON


def seed(python: Path) -> None:
    run_checked([str(python), "scripts/seed_demo_data.py"])


def import_taxonomy_if_available(python: Path) -> None:
    workbooks = sorted(TAXONOMY_IMPORT_DIR.glob("*.xlsx")) if TAXONOMY_IMPORT_DIR.exists() else []
    if not workbooks:
        print("No taxonomy workbook found in data/taxonomy/imports; using local YAML packs.")
        return
    workbook = workbooks[0]
    print(f"Importing taxonomy workbook: {workbook}")
    try:
        run_checked([str(python), "scripts/import_taxonomy_excel.py", "--input", str(workbook)])
    except subprocess.CalledProcessError as error:
        print(f"Warning: taxonomy workbook import failed ({error}); continuing with local YAML packs.")


def run_servers(python: Path, should_open: bool) -> int:
    backend = subprocess.Popen([str(python), "scripts/run_backend.py"], cwd=ROOT)
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd=ROOT / "frontend")
    try:
        time.sleep(3)
        if should_open:
            webbrowser.open("http://localhost:5173")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:5173")
        return frontend.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        for process in (frontend, backend):
            if process.poll() is None:
                process.terminate()


def main() -> int:
    parser = argparse.ArgumentParser(description="Install, seed, and run the local Argument-Risk-Engine dashboard.")
    parser.add_argument("--install", action="store_true", help="Install backend and frontend dependencies first.")
    parser.add_argument("--run", action="store_true", help="Start backend and frontend development servers.")
    parser.add_argument("--open", action="store_true", help="Open the dashboard in the default browser after startup.")
    args = parser.parse_args()
    python = ensure_install() if args.install else (VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable))
    seed(python)
    import_taxonomy_if_available(python)
    if args.run:
        return run_servers(python, args.open)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
