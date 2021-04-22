"""Various utility classes and functions
"""
import os
import yaml


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