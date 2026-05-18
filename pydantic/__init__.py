from __future__ import annotations
from typing import Any

class FieldInfo:
    def __init__(self, default: Any = None, default_factory=None, **kwargs):
        self.default = default
        self.default_factory = default_factory
        self.kwargs = kwargs

def Field(default: Any = None, default_factory=None, **kwargs):
    return FieldInfo(default, default_factory, **kwargs)

def field_validator(*fields, **kwargs):
    def deco(fn):
        return fn
    return deco

class BaseModel:
    def __init__(self, **data):
        annotations = {}
        for cls in reversed(self.__class__.mro()):
            annotations.update(getattr(cls, '__annotations__', {}))
        for name in annotations:
            if name in data:
                value = data[name]
            else:
                default = getattr(self.__class__, name, None)
                if isinstance(default, FieldInfo):
                    value = default.default_factory() if default.default_factory else default.default
                else:
                    value = default
            setattr(self, name, value)
        for name, value in data.items():
            if not hasattr(self, name):
                setattr(self, name, value)

    @classmethod
    def model_validate(cls, data):
        return cls(**data)

    def model_dump(self, mode: str | None = None):
        def conv(v):
            if isinstance(v, BaseModel):
                return v.model_dump(mode=mode)
            if isinstance(v, list):
                return [conv(i) for i in v]
            if isinstance(v, dict):
                return {k: conv(i) for k, i in v.items()}
            if hasattr(v, 'value'):
                return v.value
            return v
        return {k: conv(v) for k, v in self.__dict__.items()}
