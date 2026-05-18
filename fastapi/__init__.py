from __future__ import annotations

class Response:
    def __init__(self, content='', media_type='text/plain', status_code=200):
        self.content = content
        self.media_type = media_type
        self.status_code = status_code

class APIRouter:
    def __init__(self, prefix='', tags=None):
        self.prefix = prefix
        self.routes = {}
    def get(self, path='', **kwargs):
        def deco(fn):
            self.routes[('GET', self.prefix + path)] = fn
            return fn
        return deco
    def post(self, path='', **kwargs):
        def deco(fn):
            self.routes[('POST', self.prefix + path)] = fn
            return fn
        return deco
    def put(self, path='', **kwargs):
        def deco(fn):
            self.routes[('PUT', self.prefix + path)] = fn
            return fn
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
