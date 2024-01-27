"""
This file contains the code to load the plugin and describe the plugin.
"""
from .storage import PathMap
from .errors import (ConfigParseError, PluginLoadingError,
                     EncryptionError, PluginRuntimeError)

import os
import re
import sys
import types
import typing
import importlib
from threading import Lock
from configparser import ConfigParser
from dataclasses import dataclass, asdict
from .storage import get_parser_from_config


MINIMUM_PLUGIN_VARIABLES = {"VERSION_REQ"}


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
    plugins: dict[str, LoadPluginModule] = {}
    # read config to get `path`
    if d := parser.get("Extension"):
        path = d.get("path", "")
    # load modules
    for name in get_plugins(parser):
        plugins[name] = load_plugin(path, name)
    return plugins

def load_plugin_module(path:str, name: str, /, lock=Lock()) -> types.ModuleType:
    """
    load plugin, then return the module

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


def load_plugin(path: str, name: str):
    """
    lead plugin

    :return: LoadPluginModule
    """
    return LoadPluginModule(load_plugin_module(path, name))


@dataclass
class FunctionParameter:
    """
    The dataclass to statement a parameter for callback functions.
    """
    name: str
    default: typing.Optional[typing.Any] = None
    helper: str = ""
    before_pass: typing.Optional[typing.Callable[[str], typing.Any]] = None
    user_accessible: bool = False


class AcquireValue:
    """
    The keyword for `FunctionParameter.default`.
    If `FunctionParameter.default` is instance of this class, 
    the value of default will be replaced with `mapping[arg]`.
    """
    def __init__(self, keyword: str):
        self.keyword = keyword


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
            raise ConfigParseError(
                "failed to parse version requirement"
                "logic part `%s`, in `%s`" % (req, version_req))
        log, ver = m.groups()
        n = _RE_GET_VERSION.match(ver)
        if n is None:
            raise ConfigParseError(
                "failed to parse version requirement"
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

    raise ConfigParseError(
        f"unkown logic symble `{log}` in `{version_exp}`, "
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


_RE_GET_ENCRYPT_NAME = re.compile(r"^ENCRYPT_TYPE_(.+)$")
def function_check_encrypt_type(plugin: types.ModuleType) -> dict[str, dict]:
    """
    Return the "name"-"data" mapping.

    :raise: PluginLoadingException
    """
    names = [(name, m.group(1)) for name in dir(plugin) if (m := _RE_GET_ENCRYPT_NAME.match(name))]
    ret = {}
    for n, name in names:
        data = getattr(plugin, n)
        try:
            disabled = data.get("disable", False)
        except AttributeError as err:
            raise PluginLoadingError from err
        if disabled:
            continue
        ret[name] = data
    return ret


def check_minimum_plugin_varbs(plugin:types.ModuleType):
    """
    check MINIMUM_PLUGIN_VARIABLES is satisfied or not
    """
    return not MINIMUM_PLUGIN_VARIABLES - set(dir(plugin))


def auto_execute_function(execute: typing.Callable, descriptions: list,
                          keyword_arguments: dict[str, typing.Any],
                          format_mapping = None) -> typing.Any:
    """
    TODO
    """
    call_kwargs: dict[str, dict]  # the dict finally pass to `exe`
    if not format_mapping:
        call_kwargs = {i.name: asdict(i) for i in descriptions}
    else:
        # to setup string with `format_mapping`
        call_kwargs = {}
        for des in descriptions:
            v = asdict(des)
            if isinstance(v["default"], str):
                v["default"] = v["default"].format_map(format_mapping)
            elif isinstance(v["default"], AcquireValue):
                v["default"] = format_mapping[v["default"].keyword]
            call_kwargs[des.name] = v
    update_name_list = set(call_kwargs)
    # set the values in `kwargs`
    for key, val in keyword_arguments.items():
        if key not in update_name_list:
            raise ValueError("unknown arg", key)
        # call `before_pass`
        bfp = call_kwargs[key]["before_pass"]
        if bfp is not None:
            val = bfp(val)
        # update
        call_kwargs[key] = val
        update_name_list.remove(key)
    # set the other values with default value
    for key in update_name_list:
        d = call_kwargs[key]
        val = d["default"]
        bfp = d["before_pass"]
        if bfp is not None:
            val = bfp(val)
        call_kwargs[key] = val  # update
    # call exe
    try:
        # return the encrypted bytes
        return execute(**call_kwargs)
    except Exception as err:
        raise PluginRuntimeError(f"error occured when executing {execute}") from err


class LoadPluginModule:
    """
    The core functions to load plugin from moudle.
    """
    def __init__(self, plugin_module:types.ModuleType,
                 parser: ConfigParser | None = None, version=None):
        """
        set up values

        :param parser: the config parser. If None, call `get_parser_from_config` when use config.
        """
        # check plugin
        if not check_minimum_plugin_varbs(plugin_module):
            raise PluginLoadingError("minimum plugin variables are not satisfied in", plugin_module)
        self.plugin_module = plugin_module
        self.plugin_name = plugin_module.__name__.rsplit(".", 1)[-1]
        # global config
        self.parser = parser
        # package version
        if version is None:
            from .version import VERSION
            self.VERSION = VERSION
        # cache
        self._encrypt_functions = None
    def check_plugin_version_req(self):
        """
        Check whether the plugin version requirements are satisfied.
        
        To check requirements are satisfaced with functions:
        ```python
        assert (check_version_is_req_list(check_version_req_format(plugin_version_req),
                                          version.VERSION),
                PluginLoadingException)
        ```
        
        """
        vrf = check_version_req_format(self.plugin_module.VERSION_REQ)
        *version, _ = _RE_GET_VERSION.match(self.VERSION).groups()
        for req in vrf:
            if not check_version_is_req(req, version):
                raise PluginLoadingError(
                    f"current version `f{self.VERSION}`"
                    f"doesn't satisfied the requirements `{req}`")
    def get_encrypt_types(self) -> dict[str, dict]:
        """
        Return the "name"-"data" mapping.
        """
        if self._encrypt_functions is not None:
            return self._encrypt_functions
        # no cached
        self._encrypt_functions = function_check_encrypt_type(self.plugin_module)
        return self._encrypt_functions
    def get_decrypt_types(self) -> dict[str, dict]:
        """
        same as `get_encrypt_types`
        """
        return self.get_encrypt_types()
    
    def get_from_config(self, key, default_value=None):
        """
        get the value of `key` from config
        """
        if self.parser is None:
            parser = get_parser_from_config()
        else:
            parser = self.parser
        return parser[key] if key in parser.sections() else default_value
    
    def exec_encrypt(self, name, data: bytes, **kwargs) -> bytes:
        """
        auto execute encrypt function

        :param data: the value of keyword `TARGET DATA` pass to format mapping.
        :raise: ValueError
        :raise: PluginRuntimeError
        """
        ls = self.get_encrypt_types()[name]
        exe, dec = ls["encrypt"]
        mapping = {"TARGET DATA": data}
        mapping.update(asdict(PathMap))
        mapping.update(self.get_from_config(self.plugin_name, {}))
        return auto_execute_function(exe, dec, kwargs, mapping)
    
    def exec_decrypt(self, name, data: bytes, **kwargs) -> bytes:
        """
        auto execute decrypt function

        :param data: the value of keyword `TARGET DATA` pass to format mapping.
        :raise: ValueError
        :raise: PluginRuntimeError
        """
        ls = self.get_decrypt_types()[name]
        exe, dec = ls["decrypt"]
        mapping = {"TARGET DATA": data}
        mapping.update(asdict(PathMap))
        mapping.update(self.get_from_config(self.plugin_name, {}))
        return auto_execute_function(exe, dec, kwargs, mapping)


def exec_plugin_moude(plugin: types.ModuleType):
    """
    
    """
    
    return #TODO
