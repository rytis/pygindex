"""Various utility classes and functions
"""
import os
import yaml


class Configuration:
    """Manage configuration"""

    def __init__(self, cfg_file="~/.pygindex.yaml"):
        self._config = self._get_config(os.path.expanduser(cfg_file))

    def _get_config(self, cfg_file):
        """Generate configuration object"""
        config = self._config_from_file(cfg_file)
        return config

    def _config_from_file(self, path):
        """Reads configuration from file"""
        try:
            with open(path, "r") as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            config = {}
        return config
