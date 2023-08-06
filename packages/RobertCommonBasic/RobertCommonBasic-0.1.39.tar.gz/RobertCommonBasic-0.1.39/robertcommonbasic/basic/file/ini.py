import ast
import os
import collections.abc

from collections import deque
from contextlib import suppress
from typing import Any, Dict, Optional, Tuple, TypeVar
from itertools import count as itertools_count
from configparser import ConfigParser
from ..os.file import check_file_exist


class SensitiveConfigParser(ConfigParser):
    """
    set ConfigParser options for case sensitive.
    """

    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


class ConfigMap(collections.abc.Mapping):
    __debug = False

    @staticmethod
    def _debug_enabled():
        return ConfigMap.__debug

    @staticmethod
    def _enable_debug(enabled: bool):
        ConfigMap.__debug = enabled

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f'Invalid key {key}')

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __iter__(self):
        return (name for name in dir(self) if not name.startswith('__') and name.isupper())

    def __len__(self):
        counter = itertools_count()
        deque(zip(self, counter), maxlen=0)  # (consume at C speed)
        return next(counter)

    def is_secret(self, key: str):
        return 'PASSWORD' in key


class ConfigNode(ConfigMap):
    def __init__(self, config: Dict = None) -> None:
        super().__init__()

        if config:
            for k in self:
                if k in config:
                    setattr(self, k, config[k])

    def __repr__(self) -> str:
        return str({k: (v if not self.is_secret(k) else '********') for k, v in self.items()})


class ConfigBase(ConfigMap):
    TAny = TypeVar('TAny')
    TNode = TypeVar('TNode', bound=ConfigNode)

    def __init__(self, env_prefix: str = None, debug: bool = False) -> None:
        self.env_prefix = env_prefix or ''
        self._debug = debug

    def node(self, node_name: str, default: TNode, update: Dict[str, Any] = None) -> TNode:
        target = default.__class__(default)

        for k, v in (update or {}).items():
            if k in target:
                target[k] = v

        for k in target:
            v, found = self._env(
                self.get_env_key(f'{node_name}_{k}' if node_name else k))
            if found:
                target[k] = v

        return target

    def env(self, name: str, default: Optional[TAny] = None) -> Optional[TAny]:
        v, found = self._env(self.get_env_key(name))
        if not found:
            v = default
        return v

    def get_env_key(self, name) -> str:
        return f'{self.env_prefix}{name}'

    def prepare_environment(self, config_data: dict):
        for name, value in (config_data or {}).items():
            env_key = self.get_env_key(name)

            if env_key not in os.environ:
                os.environ[env_key] = str(value)

    def _env(self, key: str) -> Tuple[Any, bool]:
        v = os.getenv(key)
        found = v is not None
        if found:
            with suppress(Exception):
                v = ast.literal_eval(v)
            if self._debug_enabled():
                print(f'env: {key}={v if not self.is_secret(key) else f"***{v[-5:]}"}')

        return v, found

    def __getattr__(self, __name: str) -> Any:
        return self.env(__name)

    def print(self):
        for k, v in self.items():
            print(
                f'config: {k} = {v if not self.is_secret(k) else "********"}, {type(v).__name__}')


# 读取配置
def read_ini(file_path: str) -> dict:
    values = {}
    if check_file_exist(file_path) is True:
        config = ConfigParser()
        config.read(file_path)

        for section in config.sections():
            for option in config.options(section):
                if section not in values.keys():
                    values[section] = {}
                values[section][option] = config.get(section, option)
    return values


# 读取配置
def read_init_key(file_path: str, section: str, name: str):
    if check_file_exist(file_path) is True:
        config = ConfigParser()
        config.read(file_path)
        if config.has_section(section) is True:
            if config.has_option(section, name) is True:
                return config.get(section, name)
    return None


def write_init(file_path: str, values: dict, is_update: bool = False):
    config = ConfigParser()
    if is_update:
        config.read(file_path)
    for section, params in values.items():
        if config.has_section(section) is False:
            config.add_section(section)
        for name, value in params.items():
            config.set(section, name, value)
    config.write(open(file_path, 'w'))