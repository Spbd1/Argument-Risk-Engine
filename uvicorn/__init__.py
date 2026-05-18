from __future__ import annotations

import http.server
import importlib
import inspect
import json
import socketserver
from email.parser import BytesParser
from email.policy import default as email_policy
from io import BytesIO
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

from fastapi import Response, UploadFile


def run(app_path: str, host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run a tiny local HTTP server for the repository's FastAPI-compatible app.

    This project ships lightweight FastAPI/Uvicorn shims so the demo can run in
    restricted/offline environments.  The server intentionally supports only the
    routing and request features used by the app: JSON bodies, query strings,
    dynamic path parameters, and single-file multipart uploads.
    """
    app = _load_app(app_path)

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def do_PUT(self):
            self._dispatch("PUT")

        def do_PATCH(self):
            self._dispatch("PATCH")

        def _dispatch(self, method: str) -> None:
            fn, kwargs, query = _resolve(app, method, self.path)
            if not fn:
                self._send_json({"detail": "not found"}, status=404)
                return
            kwargs.update(query)
            try:
                body_kwargs = _body_args(fn, self)
                kwargs.update(body_kwargs)
                payload = _call(fn, kwargs)
                self._send_payload(payload)
            except Exception as error:  # pragma: no cover - defensive server boundary
                self._send_json({"detail": str(error)}, status=500)

        def _send_payload(self, payload) -> None:
            if isinstance(payload, Response):
                content = payload.content
                if isinstance(content, str):
                    content = content.encode("utf-8")
                self.send_response(payload.status_code)
                self.send_header("Content-Type", payload.media_type)
                for key, value in payload.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(content or b"")
                return
            self._send_json(_to_jsonable(payload))

        def _send_json(self, payload, status: int = 200) -> None:
            body = json.dumps(_to_jsonable(payload), ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
        allow_reuse_port = True

    with ReusableTCPServer((host, port), Handler) as httpd:
        print(f"Backend: http://{host}:{port}", flush=True)
        httpd.serve_forever()


def _load_app(app_path: str):
    module_name, _, attr = app_path.partition(":")
    module = importlib.import_module(module_name)
    return getattr(module, attr or "app")


def _resolve(app, method: str, raw_path: str):
    parsed = urlparse(raw_path)
    path = parsed.path.rstrip("/") or "/"
    query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
    exact = app.routes.get((method, path)) or app.routes.get((method, parsed.path))
    if exact:
        return exact, {}, query
    path_parts = [part for part in path.split("/") if part]
    for (route_method, route_path), fn in app.routes.items():
        if route_method != method:
            continue
        route_parts = [part for part in route_path.split("/") if part]
        if len(route_parts) != len(path_parts):
            continue
        kwargs = {}
        matched = True
        for route_part, path_part in zip(route_parts, path_parts, strict=True):
            if route_part.startswith("{") and route_part.endswith("}"):
                kwargs[route_part[1:-1]] = path_part
            elif route_part != path_part:
                matched = False
                break
        if matched:
            return fn, kwargs, query
    return None, {}, query


def _body_args(fn, handler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    if length <= 0:
        return {}
    content_type = handler.headers.get("Content-Type", "")
    body = handler.rfile.read(length)
    if content_type.startswith("application/json"):
        data = json.loads(body.decode("utf-8") or "{}")
        return _json_args(fn, data)
    if content_type.startswith("multipart/form-data"):
        return _multipart_args(content_type, body)
    return {}


def _json_args(fn, data: dict) -> dict:
    if not data:
        return {}
    sig = inspect.signature(fn)
    required_model_params = []
    for name, param in sig.parameters.items():
        if name == "file":
            continue
        ann = _resolve_annotation(fn, param.annotation)
        if ann is inspect._empty or ann in {str, int, bool, float}:
            continue
        if param.default is inspect._empty:
            required_model_params.append((name, ann))
    if len(required_model_params) == 1:
        name, cls = required_model_params[0]
        try:
            return {name: cls(**data)}
        except Exception:
            return {name: data}
    return data


def _multipart_args(content_type: str, body: bytes) -> dict:
    message = BytesParser(policy=email_policy).parsebytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body
    )
    result = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename:
            result[name or "file"] = UploadFile(filename=filename, file=BytesIO(payload))
        elif name:
            result[name] = payload.decode(part.get_content_charset() or "utf-8")
    return result


def _call(fn, kwargs):
    sig = inspect.signature(fn)
    accepted = {}
    for name, param in sig.parameters.items():
        if name in kwargs:
            accepted[name] = kwargs[name]
        elif param.default is inspect._empty:
            ann = _resolve_annotation(fn, param.annotation)
            if ann is not inspect._empty:
                try:
                    accepted[name] = ann(**kwargs)
                except Exception:
                    pass
    return fn(**accepted)


def _resolve_annotation(fn, ann):
    if isinstance(ann, str):
        builtin = {"str": str, "int": int, "bool": bool, "float": float}.get(ann)
        if builtin is not None:
            return builtin
        return getattr(inspect.getmodule(fn), ann, fn.__globals__.get(ann, ann))
    return ann


def _to_jsonable(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, SimpleNamespace):
        return vars(value)
    return value
