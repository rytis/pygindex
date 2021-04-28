"""Various utility classes and functions
"""
import functools
import os
import uuid
import yaml


def method_labeler(obj, owner, name, label):
    if hasattr(owner, label):
        getattr(owner, label).append(name)
    else:
        setattr(owner, label, [name])


class PluggableDecorator:
    _set_name_callback = None

    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        self._set_name_callback(owner, name)

    def __get__(self, instance, owner):
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    @classmethod
    def build_decorator_class(cls, set_name_callback):
        cls_name = f"{cls.__name__}-{uuid.uuid4().hex[:5]}"
        cls._set_name_callback = set_name_callback
        return type(cls_name, (cls,), dict(cls.__dict__))


class Configuration(dict):
    """Manage configuration"""

    def __init__(self):
        super().__init__()

    @classmethod
    def from_file(cls, path="~/.pygindex.yaml"):
        path = os.path.expanduser(path)
        try:
            with open(path, "r") as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            config = {}
        obj = cls()
        for key, value in config.items():
            obj[key] = value
        return obj
