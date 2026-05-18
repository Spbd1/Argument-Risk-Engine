from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

NAME = "argument_risk_engine"
VERSION = "0.1.0"
DIST = f"{NAME}-{VERSION}.dist-info"
ROOT = Path(__file__).parent.resolve()


def _metadata() -> str:
    return "\n".join([
        "Metadata-Version: 2.1",
        "Name: argument-risk-engine",
        f"Version: {VERSION}",
        "Summary: Local taxonomy-grounded argument risk analysis dashboard.",
        "Requires-Python: >=3.10",
        "Provides-Extra: dev",
        "",
    ])


def _wheel() -> str:
    return "\n".join([
        "Wheel-Version: 1.0",
        "Generator: argument-risk-engine-local-backend",
        "Root-Is-Purelib: true",
        "Tag: py3-none-any",
        "",
    ])


def _record_line(path: str, data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    import base64
    encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return f"{path},sha256={encoded},{len(data)}"


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _write_wheel(Path(wheel_directory), editable=False)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _write_wheel(Path(wheel_directory), editable=True)


def get_requires_for_build_wheel(config_settings=None):
    return []


def get_requires_for_build_editable(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    dist = Path(metadata_directory) / DIST
    dist.mkdir(parents=True, exist_ok=True)
    (dist / "METADATA").write_text(_metadata())
    (dist / "WHEEL").write_text(_wheel())
    return DIST


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def _write_wheel(out_dir: Path, editable: bool) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{NAME}-{VERSION}-py3-none-any.whl"
    wheel_path = out_dir / filename
    records: list[str] = []
    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as zf:
        files: dict[str, bytes] = {
            f"{DIST}/METADATA": _metadata().encode(),
            f"{DIST}/WHEEL": _wheel().encode(),
        }
        if editable:
            files["argument_risk_engine_editable.pth"] = f"{ROOT}\n{ROOT / 'engine'}\n".encode()
        else:
            for base in [ROOT / "engine" / "argument_risk_engine", ROOT / "backend"]:
                for path in base.rglob("*.py"):
                    files[str(path.relative_to(base.parent))] = path.read_bytes()
        for path, data in files.items():
            zf.writestr(path, data)
            records.append(_record_line(path, data))
        record_path = f"{DIST}/RECORD"
        zf.writestr(record_path, "\n".join(records + [f"{record_path},,"]) + "\n")
    return filename
