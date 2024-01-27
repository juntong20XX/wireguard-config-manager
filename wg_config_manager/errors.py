"""
Defautl exception.
"""

class WG_CONFIG_MANAGER_BASE_EXCEPION(Exception):
    """
    Base exception for `wg_config_manager` package.
    """

class ConfigParseFailException(WG_CONFIG_MANAGER_BASE_EXCEPION):
    """
    Parse config failed.
    """


class PluginLoadingException(WG_CONFIG_MANAGER_BASE_EXCEPION):
    """
    The exception raised when loading plugin failed.
    """


# ---
errors = (ConfigParseFailException, PluginLoadingException)
