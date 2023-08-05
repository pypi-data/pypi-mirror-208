import asyncio
from contextlib import contextmanager
from inspect import iscoroutinefunction
import sys
import types
from functools import partial


nothing = object()


class Module(types.ModuleType):
    _cache = {}
    _lazy_loaders = {}

    def register_loader(self, key, lazy_loader, rewrite=False):
        current_loader = self._lazy_loaders.get(key, None)
        assert callable(lazy_loader)
        assert rewrite is True or current_loader is None
        self._lazy_loaders[key] = lazy_loader
        return current_loader

    def get(self, key):
        try:
            value = self._cache[key]
        except KeyError:
            if key in self._lazy_loaders:
                loader = self._lazy_loaders[key]
                if iscoroutinefunction(loader):
                    fut = asyncio.ensure_future(loader())
                    setter = partial(self.set_from_future, key,)
                    fut.add_done_callback(setter)
                    value = fut
                else:
                    value = loader()
                self.set(key, value)
            else:
                raise
        return value

    def set_from_future(self, key, fut: asyncio.Future):
        self.set(key, fut.result())

    def set(self, key, value):
        self._cache[key] = value
        return value

    def alias(self, src, dst):
        loader = self._lazy_loaders.get(src, nothing)
        if loader is not nothing:
            self._lazy_loaders(dst, loader)
        value = self._cache.get(src, nothing)
        if value is not nothing:
            self._cache[dst] = value

    def pop(self, key, default=None):
        result = self._cache.pop(key, default)
        return result

    def clear(self):
        self._cache.clear()

    def __getattr__(self, item):
        try:
            return self.get(item)
        except KeyError as exc:
            raise AttributeError(exc)

    def __setattr__(self, key, value):
        self.set(key, value)

    def __delattr__(self, item):
        self.pop(item, None)

    def __dir__(self):
        return self._cache.keys()

    def __contains__(self, item):
        return item in self._cache or item in self._lazy_loaders

    def register(self, key):
        def outer(func):
            return self.register_loader(key, func)

        if callable(key):
            func = key
            return self.register_loader(func.__name__, func)
        return outer

    @contextmanager
    def mock(self, key, value):
        old_value = self._cache.pop(key, nothing)
        try:
            self._cache[key] = value
            yield self
        finally:
            if old_value is nothing:
                del self._cache[key]
            else:
                self._cache[key] = old_value


del contextmanager
old_module = sys.modules[__name__]
new_module = sys.modules[__name__] = Module(__name__)
register_loader = new_module.register_loader
register = new_module.register
mock = new_module.mock
