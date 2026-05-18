from __future__ import annotations
import json

class _Resp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
    def json(self):
        def conv(v):
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
        fn = self.app.routes.get(('GET', path))
        return _Resp(fn() if fn else {'detail':'not found'}, 200 if fn else 404)
    def post(self, path, json=None):
        fn = self.app.routes.get(('POST', path))
        if not fn: return _Resp({'detail':'not found'}, 404)
        arg = _make_arg(fn, json or {})
        return _Resp(fn(arg) if arg is not None else fn())
    def put(self, path, json=None):
        fn = self.app.routes.get(('PUT', path))
        if not fn: return _Resp({'detail':'not found'}, 404)
        arg = _make_arg(fn, json or {})
        return _Resp(fn(arg) if arg is not None else fn())

def _make_arg(fn, data):
    anns = getattr(fn, '__annotations__', {})
    params = [k for k in anns if k != 'return']
    if not params:
        return None
    cls = anns[params[0]]
    try:
        return cls(**data)
    except Exception:
        return data
