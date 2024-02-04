"""
Defautl exception.
"""


class WG_CONFIG_MANAGER_BASE_EXCEPION(Exception):
    """
    Base exception for `wg_config_manager` package.
    """


# --- IO

class EncryptionError(WG_CONFIG_MANAGER_BASE_EXCEPION):
    """
    Encrypt failed.
    """


class ConfigParseError(WG_CONFIG_MANAGER_BASE_EXCEPION):
    """
    Parse config failed.
    """


# --- Plugin

class PluginException(WG_CONFIG_MANAGER_BASE_EXCEPION):
    """
    An error occurred when loading or executing plugin.
    """


class PluginLoadingError(PluginException):
    """
    Exception occurred when loading plugin failed.
    """


class PluginRuntimeError(PluginException):
    """
    Exception occurred when executing a plugin.
    """


# --- wireguard_core

class WireguardConfError(WG_CONFIG_MANAGER_BASE_EXCEPION):
    """
    An error occurred when generating or reading a wireguard config.
    """


# ---
errors = (ConfigParseError, PluginLoadingError, PluginRuntimeError, EncryptionError, WireguardConfError)
