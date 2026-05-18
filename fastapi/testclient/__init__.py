from __future__ import annotations

import inspect
from io import BytesIO
from urllib.parse import parse_qs, urlparse

from fastapi import Response, UploadFile


class _Resp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = getattr(payload, 'status_code', status_code)
        self.content = getattr(payload, 'content', b'')
        self.headers = getattr(payload, 'headers', {})

    def json(self):
        def conv(v):
            if isinstance(v, Response):
                return v.content
            if hasattr(v, 'model_dump'):
                return v.model_dump()
            if isinstance(v, dict):
                return {k: conv(i) for k, i in v.items()}
            if isinstance(v, list):
                return [conv(i) for i in v]
            if hasattr(v, 'value'):
                return v.value
            return v
        return conv(self._payload)


class TestClient:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        fn, kwargs, query = _resolve(self.app, 'GET', path)
        if not fn:
            return _Resp({'detail': 'not found'}, 404)
        kwargs.update(query)
        return _Resp(_call(fn, kwargs))

    def post(self, path, json=None, files=None):
        fn, kwargs, query = _resolve(self.app, 'POST', path)
        if not fn:
            return _Resp({'detail': 'not found'}, 404)
        kwargs.update(query)
        kwargs.update(_json_args(fn, json or {}))
        kwargs.update(_file_args(files))
        return _Resp(_call(fn, kwargs))

    def put(self, path, json=None):
        fn, kwargs, query = _resolve(self.app, 'PUT', path)
        if not fn:
            return _Resp({'detail': 'not found'}, 404)
        kwargs.update(query)
        kwargs.update(_json_args(fn, json or {}))
        return _Resp(_call(fn, kwargs))

    def patch(self, path, json=None):
        fn, kwargs, query = _resolve(self.app, 'PATCH', path)
        if not fn:
            return _Resp({'detail': 'not found'}, 404)
        kwargs.update(query)
        kwargs.update(_json_args(fn, json or {}))
        return _Resp(_call(fn, kwargs))


def _resolve(app, method, raw_path):
    parsed = urlparse(raw_path)
    path = parsed.path
    query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
    exact = app.routes.get((method, path))
    if exact:
        return exact, {}, query
    path_parts = [part for part in path.split('/') if part]
    for (route_method, route_path), fn in app.routes.items():
        if route_method != method:
            continue
        route_parts = [part for part in route_path.split('/') if part]
        if len(route_parts) != len(path_parts):
            continue
        kwargs = {}
        matched = True
        for route_part, path_part in zip(route_parts, path_parts, strict=True):
            if route_part.startswith('{') and route_part.endswith('}'):
                kwargs[route_part[1:-1]] = path_part
            elif route_part != path_part:
                matched = False
                break
        if matched:
            return fn, kwargs, query
    return None, {}, query


def _call(fn, kwargs):
    sig = inspect.signature(fn)
    accepted = {}
    for name, param in sig.parameters.items():
        if name in kwargs:
            accepted[name] = kwargs[name]
        elif param.default is inspect._empty:
            ann = _resolve_annotation(fn, param.annotation)
            if isinstance(kwargs, dict) and ann is not inspect._empty:
                try:
                    accepted[name] = ann(**kwargs)
                except Exception:
                    pass
    return fn(**accepted)


def _json_args(fn, data):
    if not data:
        return {}
    sig = inspect.signature(fn)
    required_model_params = []
    for name, param in sig.parameters.items():
        if name in {'file'}:
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


def _resolve_annotation(fn, ann):
    if isinstance(ann, str):
        builtin = {'str': str, 'int': int, 'bool': bool, 'float': float}.get(ann)
        if builtin is not None:
            return builtin
        return getattr(inspect.getmodule(fn), ann, fn.__globals__.get(ann, ann))
    return ann


def _file_args(files):
    if not files:
        return {}
    file_info = files.get('file') if isinstance(files, dict) else None
    if file_info is None:
        return {}
    filename, content, *_ = file_info
    if hasattr(content, 'read'):
        file_obj = content
    else:
        file_obj = BytesIO(content if isinstance(content, bytes) else str(content).encode())
    return {'file': UploadFile(filename=filename, file=file_obj)}
