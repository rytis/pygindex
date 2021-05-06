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
    _pre_callback = None

    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        self._set_name_callback(owner, name)

    def __get__(self, instance, owner):
        partial_func = functools.partial(self, instance)
        partial_func.__doc__ = self.fn.__doc__
        return partial_func

    def __call__(self, *args, **kwargs):
        if self._pre_callback:
            self._pre_callback(*args, **kwargs)
        return self.fn(*args, **kwargs)

    @classmethod
    def build_decorator_class(cls, set_name_callback, pre_exec_callback=None):
        cls_name = f"{cls.__name__}-{uuid.uuid4().hex[:5]}"
        cls._set_name_callback = set_name_callback
        return type(cls_name, (cls,), dict(cls.__dict__))


class Configuration(dict):
    """Manage configuration"""

    def __init__(self):
        super().__init__()

    @classmethod
    def from_file(cls, path: str = "~/.pygindex.yaml"):
        """Read configuration file and return initialised object.

        If the file cannot be read, return an empty dictionary.

        :param path: Path to a YAML configuration file. Default: ``~/.pygindex.yaml``
        :type path: str
        :return: Instance of :class:`utils.Configuration` initialised from the file
        """
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
