"""Various utility classes and functions
"""
import functools
import os
import yaml


class MethodLabelDecorator:
    def __init__(self, label):
        self._label = label

    def __set_name__(self, owner, name):
        if hasattr(owner, self._label):
            getattr(owner, self._label).append(name)
        else:
            setattr(owner, self._label, [name])

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(self, *args, **kwargs)

        return wrapped


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
