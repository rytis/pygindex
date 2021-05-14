"""Various utility classes and functions
"""

import functools
import os
import uuid
import yaml
import json
import enum
import dataclasses
from typing import Any


class PyGiJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, enum.Enum):
            return o.name
        elif dataclasses._is_dataclass_instance(o):
            return dataclasses.asdict(o)
        else:
            return json.JSONEncoder.default(self, o)


def method_labeler(obj, owner, name, label):
    """A helper function that can be used with :class:`PluggableDecorator`
    to create a list (as class property) of all decorated function names.

    :param obj: Object that contains decorated method (``self`` in method call)
    :param owner: Class that contains the decorated function
    :param name: Name of the function
    :param label: Name of the class property where the method name should be appended to
    """
    if hasattr(owner, label):
        getattr(owner, label).append(name)
    else:
        setattr(owner, label, [name])


class PluggableDecorator:
    """A pluggable decorator class that can be used to turn
    class methods in to customisable descriptors.

    Using :meth:`PluggableDecorator.build_decorator_class` factory method
    you can define custom descriptor methods to execute.

    Example of decorated method::

        class SomeClass:

            list_of_methods = []

            @my_decorator
            def my_method(self):
                pass

    Where ``my_decorator`` is an instance of :class:`PluggableDecorator`::

        my_decorator = PluggableDecorator.build_decorator_class(
            set_name_callback=some_function
        )

    And ``some_function`` is a callback function that will be executed
    when descriptor instance name is initialised. The callback function
    will be passed three parameters:

        * Instance of GENERATED :class:`PluggableDecorator`
        * Owner class of decorated method (in this example ``SomeClass``)
        * Name of the decorated method (in this example ``"my_method"``)

        def some_function(obj, owner, name):
            owner.list_of_methods.append(name)

    With the above set up, when the class is initialised all methods
    decorated with ``my_decorator`` will trigger a call to ``my_function``
    at the time when their names are initialised.

    This allows to implement custom logic, such as registration of
    such methods under custom class property. The example function above
    will create a list of decorated method names in ``SomeClass.list_of_methods``.
    """

    _set_name_callback = None
    _pre_callback = None

    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner: type, name: str):
        """Call ``set_name`` callback function when initiating
        decorated method.

        :param owner: Class object that contains decorated method
        :type owner: type
        :param name: Name of the decorated method
        :type name: str
        """
        self._set_name_callback(owner, name)

    def __get__(self, instance, owner):
        """Since we are a descriptor, whenever the method is called
        it will be looked up by calling ``__get__`` method.

        We are callable, so we create a partially initialised function
        where the first parameter is the object we are called from and return that.

        :param instance: Instance of initialised class where decorated method is defined
            (``<SomeClass object at ...>`` in the example)
        :param owner: Class object containing decorated method (``<class 'SomeClass'>)
        :return: Partially initialised function, with object instance as first parameter
        """
        partial_func = functools.partial(self, instance)
        partial_func.__doc__ = self.fn.__doc__
        return partial_func

    def __call__(self, *args, **kwargs):
        """Callable that executes pre-exec callback (if defined) and
        then calls decorated method, passing all positional and keyword arguments.
        """
        if self._pre_callback:
            self._pre_callback(*args, **kwargs)
        return self.fn(*args, **kwargs)

    @classmethod
    def build_decorator_class(cls, set_name_callback, pre_exec_callback=None):
        """Decorator class factory that generates new class, which can be used as a decorator."""
        cls._pre_callback = pre_exec_callback or None
        cls._set_name_callback = set_name_callback
        cls_name = f"{cls.__name__}-{uuid.uuid4().hex[:5]}"
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
        :rtype: :class:`Configuration`
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
