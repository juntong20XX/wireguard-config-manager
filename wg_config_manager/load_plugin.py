"""
The file 
"""
from .storage import PathMap
from .errors import ConfigParseFailException, PluginLoadingException

import os
import re
import sys
import types
import typing
import importlib
from threading import Lock
from dataclasses import dataclass
from configparser import ConfigParser


def get_plugins(parser: ConfigParser) -> tuple[str]:
    """
    get the plugin-list to be loading

    e.g.
    ```
    [Extension]
    plugins = "bar", "foo"
    ```
    ==> ("bar", "foo")
    """
    m = re.findall(r"['\"](.+?)['\"] *,? *", parser["Extension"]["plugins"])
    return m
    
    # raise ConfigParseFailException("failed to get plugin-list, check your config file")


def load_plugins(parser: ConfigParser) -> dict[str]:
    """
    load plugins from config
    """
    plugins = {}
    # read config to get `path`
    if d := parser.get("Extension"):
        path = d.get("path", "")
    # load modules
    for name in get_plugins(parser):
        plugins[name] = load_plugin(path, name)
    return plugins

def load_plugin(path:str, name: str, /, lock=Lock()) -> types.ModuleType:
    """
    load plugin

    :param path: the value of [Extension.path] in config.
    """
    path = path.format_map(PathMap)
    path = os.path.expanduser(path)
    lock.acquire()
    try:
        if path and path not in sys.path:
            sys.path.append(path)
        module = importlib.import_module(f"{name}.{name}")
    finally:
        lock.release()
    return module


@dataclass
class FunctionParamater:
    """
    The dataclass to statement a paramater.
    TODO: Finish the functions in readme.
    """
    name: str
    default: typing.Optional[str] = None
    docs: str = ""
    before_pass: typing.Optional[typing.Callable[[str], str]] = None


_RE_SPL_VERSIONS = re.compile(r" *, *")
_RE_GET_LOGIC = re.compile(r"^([<>]=?|!=|==)(\d.+)$")
# _RE_GET_VERSION: from https://semver.org
_RE_GET_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                             r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*"
                             r")(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
                             r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
def check_version_req_format(version_req: str) -> list[tuple[str | None]]:
    """
    Check version-requirement's format.
    
    :return: list of serialized version expression
    :raise: ConfigParseFailException
    """
    requirements = _RE_SPL_VERSIONS.split(version_req)  # ">=ABC, <=XYZ" -> [">=ABC", "<=XYZ"]
    ret = []
    for req in requirements:
        m = _RE_GET_LOGIC.match(req)
        if m is None:
            raise ConfigParseFailException("failed to parse version requirement"
                                           "logic part `%s`, in `%s`" % (req, version_req))
        log, ver = m.groups()
        n = _RE_GET_VERSION.match(ver)
        if n is None:
            raise ConfigParseFailException("failed to parse version requirement"
                                           "version part `%s`, in `%s`" % (ver, version_req))
        ret.append((log, *n.groups()))
    return ret


def semver_lg(version: typing.Iterable[str], other: typing.Iterable[str]) -> bool:
    """
    return `version` is larger than `other` or not
    """
    a, b, c, p, *_ = version
    x, y, z, q, *_ = other

    if a != x:
        return int(a) > int(x)
    if b != y:
        return int(b) > int(y)
    if c != z:
        return int(c) > int(z)
    
    if p is None:
        return q is not None  # 0.1.0 > 0.1.0-alpha
    elif q is None:  # here, p is not None
        return False  # 0.1.0-alpha < 0.1.0

    m = p.split(".")
    n = q.split(".")
    for i, j in zip(m, n):
        if i.isnumeric() and j.isnumeric():
            if i != j:
                return int(i) > int(j)
            continue
        elif i.isnumeric() and not j.isnumeric():
            # numeric identifiers < non-numeric identifiers
            return False
        elif (not i.isnumeric()) and j.isnumeric():
            # non-numeric identifiers > non-numeric identifiers
            return True
        if i != j:
            for u, v in zip(i, j):
                if u != v:
                    return ord(u) > ord(v)  # 0.1.0-b > 0.1.0-a
            return len(u) > len(v)  # 0.1.0-alpha > 0.1.0-a
    # if all of the preceding identifiers are equal
    # a larger set of pre-release fields has a higher precedence than a smaller set
    return len(m) > len(n)


def check_version_is_req(version_exp:typing.Iterable[str], version: str | tuple) -> bool:
    """
    Check `version` requires `version_exp` or not.

    :param version_exp: serialized version expression,
    the item of `check_version_req_format` returned.
    :param version: semantic versioning, like `version.VERSION`
    """
    log, *ver_exp, _ = version_exp  # e.p. (">=", "0", "0", "1", "alpha", "25Jan2024")
    if isinstance(version, str):
        *ver, _ = _RE_GET_VERSION.match(version).groups()
    else:
        ver = version
    if log == "!=":
        return ver_exp != ver
    elif log == "==":
        return ver_exp == ver
    
    if log.endswith("=") and ver_exp == ver:
        return True
    if log.startswith(">"):
        # > or >=
        return semver_lg(ver, ver_exp)
    if log.startswith("<"):
        # < or <=
        return not semver_lg(ver, ver_exp)

    raise ConfigParseFailException(f"unkown logic symble `{log}` in `{version_exp}`, "
                                   "use `load_plugin.check_version_req_format` to check it")

def check_version_is_req_list(version_exp_list: typing.Iterable, version: str) -> bool:
    """
    Check `version` requires all expressions in `version_exp_list` or not.

    :param version_exp_list: list of serialized version expressions,
    such as `check_version_req_format` returned.
    :param version: semantic versioning, like `version.VERSION`
    """
    *v, _ = _RE_GET_VERSION.match(version).groups()
    return all(check_version_is_req(i, v) for i in version_exp_list)


class LoadPluginMoude:
    """
    The core functions to load plugin from moudle.
    """
    def __init__(self, version=None):
        """
        set up values
        """
        if version is None:
            from .version import VERSION
            self.VERSION = VERSION
    def check_plugin_version_req(self, plugin_version_req: str):
        """
        Check whether the plugin version requirements are satisfied.
        
        To check requirements are satisfaced with functions:
        ```python
        assert (check_version_is_req_list(check_version_req_format(plugin_version_req), version.VERSION),
                PluginLoadingException)
        ```

        :param plugin_version_req: plugin.VERSION_REQ
        """
        vrf = check_version_req_format(plugin_version_req)
        for req in vrf:
            if not check_version_is_req(req, self.VERSION):
                raise PluginLoadingException(f"current version `f{self.VERSION}` doesn't satisfied the requirements `f{req}`")


def exec_plugin_moude(plugin: types.ModuleType):
    """
    
    """
    
    return #TODO
