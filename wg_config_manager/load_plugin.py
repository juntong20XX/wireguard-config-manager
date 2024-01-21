"""
The file 
"""
from .storage import PATH_MAP

import re
import sys
import typing
import importlib

from threading import Lock
from dataclasses import dataclass
from configparser import ConfigParser


def load_plugins(config: ConfigParser):
    """
    load plugins from config
    """
    name_path = []
    plugin = {}
    # read config to get plugin-list
    for key in config["Extension"]:
        if m := re.match(r"^plugin_path_{.+}$", key):
            name_path.append((m.group(1), config[key]))
    # load modules
    for name, path in name_path:
        plugin[name] = load_plugin(path, name)
    return plugin

def load_plugin(path:str, name: str, /, lock=Lock()):
    """
    load plugin
    """
    path = path.format_map(PATH_MAP)
    lock.acquire()
    try:
        sys.path.append(path)
        module = importlib.import_module(name)
        sys.path.pop()
    finally:
        lock.release()
    return module


@dataclass(frozen=True)
class FunctionParamater:
    """
    The dataclass to statement a paramater.
    """
    name: str
    default: typing.Optional[str] = None
    docs: str = ""
    before_pass: typing.Optional[typing.Callable[[str], str]] = None
