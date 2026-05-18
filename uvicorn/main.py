from __future__ import annotations

import argparse

from uvicorn import run


def main() -> None:
    parser = argparse.ArgumentParser(prog="uvicorn")
    parser.add_argument("app_path")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    run(args.app_path, host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
