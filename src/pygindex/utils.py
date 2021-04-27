"""Various utility classes and functions
"""
import functools
import os
import uuid
import yaml


class AttributeInjectorDecorator:

    _label = None

    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        if hasattr(owner, self._label):
            getattr(owner, self._label).append(name)
        else:
            setattr(owner, self._label, [name])

    def __get__(self, instance, owner):
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    @classmethod
    def build_decorator_class(cls, label):
        cls_name = f"{cls.__name__}-{uuid.uuid4().hex[:5]}"
        attrs = dict(cls.__dict__)
        attrs["_label"] = label
        return type(cls_name, (cls,), attrs)


def method_label(label):
    return AttributeInjectorDecorator.build_decorator_class(label)


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
