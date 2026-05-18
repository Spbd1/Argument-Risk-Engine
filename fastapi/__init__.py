from __future__ import annotations


class Response:
    def __init__(self, content='', media_type='text/plain', status_code=200, headers=None):
        self.content = content
        self.media_type = media_type
        self.status_code = status_code
        self.headers = headers or {}


class APIRouter:
    def __init__(self, prefix='', tags=None):
        self.prefix = prefix
        self.routes = {}

    def _add(self, method, path, fn):
        self.routes[(method, self.prefix + path)] = fn
        return fn

    def get(self, path='', **kwargs):
        def deco(fn):
            return self._add('GET', path, fn)
        return deco

    def post(self, path='', **kwargs):
        def deco(fn):
            return self._add('POST', path, fn)
        return deco

    def put(self, path='', **kwargs):
        def deco(fn):
            return self._add('PUT', path, fn)
        return deco

    def patch(self, path='', **kwargs):
        def deco(fn):
            return self._add('PATCH', path, fn)
        return deco


class FastAPI:
    def __init__(self, **kwargs):
        self.routes = {}

    def add_middleware(self, *args, **kwargs):
        return None

    def include_router(self, router, prefix=''):
        for (method, path), fn in router.routes.items():
            self.routes[(method, prefix + path)] = fn

    def get(self, path='', **kwargs):
        def deco(fn):
            self.routes[('GET', path)] = fn
            return fn
        return deco

    def post(self, path='', **kwargs):
        def deco(fn):
            self.routes[('POST', path)] = fn
            return fn
        return deco

    def patch(self, path='', **kwargs):
        def deco(fn):
            self.routes[('PATCH', path)] = fn
            return fn
        return deco


class UploadFile:
    def __init__(self, filename='', file=None):
        self.filename = filename
        self.file = file


def File(default=None, **kwargs):
    return default
