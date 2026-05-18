import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    host = os.environ.get("ARE_BACKEND_HOST", "127.0.0.1")
    port = int(os.environ.get("ARE_BACKEND_PORT", "8000"))
    reload = os.environ.get("ARE_BACKEND_RELOAD", "1") not in {"0", "false", "False"}
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=reload)
